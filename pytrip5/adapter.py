"""Adapter layer for Tripoli-5 Python API.

This module provides thin wrappers that convert pytrip5 domain objects
(Material, Core, etc.) into Tripoli-5 Python API objects. It includes:

- TripoliAdapter: Real adapter that interfaces with Tripoli-5
- MockTripoliAdapter: Mock implementation for testing without Tripoli-5
- TripoliModel: Container for converted Tripoli objects
"""

from __future__ import annotations

import time
import warnings
from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import Any, Optional
import numpy as np
import numpy.typing as npt

from pytrip5.core import Material, Core, Assembly, Pin


@dataclass
class TripoliModel:
    """Container for Tripoli-5 model components.

    Attributes:
        materials: Dictionary mapping material names to Tripoli material objects
        geometry: Tripoli geometry object representing the core
        core: Original pytrip5 Core object for reference
    """
    materials: dict[str, Any]
    geometry: Any
    core: Core


@dataclass
class TripoliSimulation:
    """Container for a configured Tripoli-5 simulation.

    Attributes:
        model: TripoliModel containing geometry and materials
        config: Simulation configuration object
        simulation_object: Native Tripoli simulation object
    """
    model: TripoliModel
    config: Any
    simulation_object: Any


class BaseTripoliAdapter(ABC):
    """Abstract base class for Tripoli-5 adapters."""

    @abstractmethod
    def create_material(self, material: Material) -> Any:
        """Convert pytrip5.Material to Tripoli material object.

        Args:
            material: pytrip5 Material instance

        Returns:
            Tripoli material object
        """
        pass

    @abstractmethod
    def create_geometry(self, core: Core) -> Any:
        """Convert pytrip5.Core to Tripoli geometry object.

        Args:
            core: pytrip5 Core instance

        Returns:
            Tripoli geometry object
        """
        pass

    @abstractmethod
    def configure_simulation(self, model: TripoliModel, config: 'SimulationConfig') -> TripoliSimulation:
        """Configure a Tripoli simulation from model and config.

        Args:
            model: TripoliModel containing geometry and materials
            config: SimulationConfig specifying simulation parameters

        Returns:
            TripoliSimulation ready to run
        """
        pass

    @abstractmethod
    def run(self, simulation: TripoliSimulation) -> 'RunResult':
        """Execute a Tripoli simulation.

        Args:
            simulation: Configured TripoliSimulation

        Returns:
            RunResult containing simulation outputs
        """
        pass


class TripoliAdapter(BaseTripoliAdapter):
    """Real adapter for Tripoli-5 Python API.

    This adapter converts pytrip5 domain objects to Tripoli-5 API calls.
    It requires the Tripoli-5 Python package to be installed and importable.

    Attributes:
        tripoli: The imported tripoli5 module

    Raises:
        ImportError: If tripoli5 package cannot be imported

    Example:
        >>> try:
        ...     adapter = TripoliAdapter()
        ...     # Use adapter for real simulations
        ... except ImportError:
        ...     # Fall back to MockTripoliAdapter for testing
        ...     adapter = MockTripoliAdapter()
    """

    def __init__(self):
        """Initialize adapter and import Tripoli-5 module.

        Raises:
            ImportError: If tripoli5 cannot be imported
        """
        try:
            import tripoli5
            self.tripoli = tripoli5
        except ImportError as e:
            raise ImportError(
                "Tripoli-5 Python API not found. Install tripoli5 package or use "
                "MockTripoliAdapter for testing. See installation instructions at "
                "https://tripoli5.asnr.dev/documentation/api/python-api.html"
            ) from e

    def create_material(self, material: Material) -> Any:
        """Convert pytrip5.Material to Tripoli material object.

        Based on Tripoli-5 documentation, materials are defined using:
        - Composition (isotopes and fractions)
        - Density
        - Temperature (optional)

        Args:
            material: pytrip5 Material instance

        Returns:
            Tripoli material object (tripoli5.Material or similar)

        References:
            https://tripoli5.asnr.dev/documentation/api/python-api.html
        """
        # Create Tripoli material using the API
        # NOTE: Actual API may differ; this is based on typical MC code patterns
        tripoli_mat = self.tripoli.Material(name=material.name)

        # Set composition
        for isotope, fraction in material.compositions.items():
            tripoli_mat.add_nuclide(isotope, fraction)

        # Set density
        tripoli_mat.set_density(material.density)

        # Set temperature if provided
        if material.temperature is not None:
            tripoli_mat.set_temperature(material.temperature)

        return tripoli_mat

    def create_geometry(self, core: Core) -> Any:
        """Convert pytrip5.Core to Tripoli geometry object.

        Creates CSG (Constructive Solid Geometry) representation of the core
        using Tripoli-5 geometry primitives.

        Args:
            core: pytrip5 Core instance

        Returns:
            Tripoli geometry object

        References:
            https://tripoli5.asnr.dev/documentation/examples/geometry.html
        """
        # Create root geometry
        geometry = self.tripoli.Geometry()

        # Build core geometry from assemblies
        for row_idx, row in enumerate(core.layout):
            for col_idx, asm_id in enumerate(row):
                if not asm_id:
                    continue

                assembly = core.assemblies[asm_id]

                # Create assembly geometry (simplified; real implementation
                # would create detailed pin lattice)
                asm_pos_x = col_idx * assembly.pitch
                asm_pos_y = row_idx * assembly.pitch

                # Add assembly volume to geometry
                # NOTE: Actual Tripoli-5 API for geometry construction may differ
                for pin_row_idx, pin_row in enumerate(assembly.pins):
                    for pin_col_idx, pin in enumerate(pin_row):
                        pin_x = asm_pos_x + pin_col_idx * (pin.pitch or 1.26)
                        pin_y = asm_pos_y + pin_row_idx * (pin.pitch or 1.26)

                        # Create cylindrical pin volume
                        pin_volume = self.tripoli.Cylinder(
                            radius=pin.radius,
                            position=(pin_x, pin_y, 0),
                            height=365.76  # Typical PWR active height in cm
                        )
                        geometry.add_volume(pin_volume, material_name=pin.material.name)

        return geometry

    def configure_simulation(self, model: TripoliModel, config: 'SimulationConfig') -> TripoliSimulation:
        """Configure Tripoli simulation from model and config.

        Args:
            model: TripoliModel with geometry and materials
            config: SimulationConfig with simulation parameters

        Returns:
            TripoliSimulation ready to run
        """
        # Create simulation object
        if config.criticality:
            sim = self.tripoli.CriticalitySimulation(geometry=model.geometry)
            sim.set_neutrons_per_cycle(config.particles_per_batch)
            sim.set_inactive_cycles(config.inactive_batches)
            sim.set_active_cycles(config.active_batches)
        else:
            sim = self.tripoli.FixedSourceSimulation(geometry=model.geometry)
            sim.set_particles(config.particles_per_batch * config.active_batches)

        # Add scores
        for score in config.scores:
            tripoli_score = score.to_tripoli_score_spec(self.tripoli)
            sim.add_score(tripoli_score)

        # Set random seed if provided
        if config.seed is not None:
            sim.set_seed(config.seed)

        return TripoliSimulation(
            model=model,
            config=config,
            simulation_object=sim
        )

    def run(self, simulation: TripoliSimulation) -> 'RunResult':
        """Execute Tripoli simulation.

        Args:
            simulation: Configured TripoliSimulation

        Returns:
            RunResult with simulation outputs
        """
        from pytrip5.simulation import RunResult

        # Run the simulation
        result = simulation.simulation_object.run()

        # Extract results
        k_eff = None
        k_eff_std = None
        scores_data = {}

        if simulation.config.criticality:
            k_eff = result.get_keff()
            k_eff_std = result.get_keff_std()

        # Extract score data
        for score in simulation.config.scores:
            score_result = result.get_score(score.name)
            scores_data[score.name] = score.from_tripoli_result(score_result)

        return RunResult(
            k_eff=k_eff,
            k_eff_std=k_eff_std,
            scores=scores_data,
            raw_result=result
        )


class MockTripoliAdapter(BaseTripoliAdapter):
    """Mock Tripoli-5 adapter for testing without real Tripoli installation.

    This adapter simulates Tripoli-5 behavior by returning plausible values
    for k-effective, pin powers, and other scores. Useful for:
    - Unit testing pytrip5 code without Tripoli-5
    - Developing and prototyping workflows
    - CI/CD pipelines

    The mock adapter introduces artificial latency to simulate real computation time.

    Example:
        >>> adapter = MockTripoliAdapter()
        >>> from pytrip5.core import Core
        >>> core = Core.simple_demo_3x3()
        >>> model = core.to_tripoli(adapter)
        >>> # model contains mocked Tripoli objects
    """

    def __init__(self, simulate_latency: bool = True):
        """Initialize mock adapter.

        Args:
            simulate_latency: If True, introduce artificial delays to simulate
                             real computation time
        """
        self.simulate_latency = simulate_latency
        self._rng = np.random.default_rng(42)  # Reproducible random results

    def create_material(self, material: Material) -> dict[str, Any]:
        """Create mock Tripoli material object.

        Args:
            material: pytrip5 Material instance

        Returns:
            Dictionary representing a mock Tripoli material
        """
        return {
            'type': 'MockTripoliMaterial',
            'name': material.name,
            'density': material.density,
            'compositions': material.compositions.copy(),
            'temperature': material.temperature
        }

    def create_geometry(self, core: Core) -> dict[str, Any]:
        """Create mock Tripoli geometry object.

        Args:
            core: pytrip5 Core instance

        Returns:
            Dictionary representing a mock Tripoli geometry
        """
        # Count total pins for geometry info
        total_pins = 0
        total_assemblies = 0

        for row in core.layout:
            for asm_id in row:
                if asm_id:
                    total_assemblies += 1
                    assembly = core.assemblies[asm_id]
                    total_pins += assembly.shape[0] * assembly.shape[1]

        return {
            'type': 'MockTripoliGeometry',
            'core_shape': core.shape,
            'total_assemblies': total_assemblies,
            'total_pins': total_pins,
            'boron_ppm': core.boron_concentration
        }

    def configure_simulation(self, model: TripoliModel, config: 'SimulationConfig') -> TripoliSimulation:
        """Configure mock Tripoli simulation.

        Args:
            model: TripoliModel with geometry and materials
            config: SimulationConfig with parameters

        Returns:
            TripoliSimulation with mock simulation object
        """
        sim_object = {
            'type': 'MockTripoliSimulation',
            'criticality': config.criticality,
            'particles_per_batch': config.particles_per_batch,
            'active_batches': config.active_batches,
            'inactive_batches': config.inactive_batches,
            'seed': config.seed,
            'scores': [score.name for score in config.scores]
        }

        return TripoliSimulation(
            model=model,
            config=config,
            simulation_object=sim_object
        )

    def run(self, simulation: TripoliSimulation) -> 'RunResult':
        """Execute mock simulation with plausible results.

        Generates realistic-looking results:
        - k_eff around 1.0 ± 0.1 for criticality simulations
        - Pin powers normalized to average 1.0
        - Flux distributions with spatial variation

        Args:
            simulation: Configured TripoliSimulation

        Returns:
            RunResult with mocked outputs
        """
        from pytrip5.simulation import RunResult

        # Simulate computation time
        if self.simulate_latency:
            # Scale latency with problem size
            geometry = simulation.model.geometry
            base_time = 0.1  # 100ms base
            size_factor = geometry.get('total_pins', 100) / 100.0
            batch_factor = simulation.config.active_batches / 10.0
            latency = base_time * size_factor * batch_factor
            time.sleep(min(latency, 2.0))  # Cap at 2 seconds for testing

        # Generate results
        k_eff = None
        k_eff_std = None
        scores_data = {}

        if simulation.config.criticality:
            # Generate plausible k_eff
            # Use seed for reproducibility
            if simulation.config.seed is not None:
                rng = np.random.default_rng(simulation.config.seed)
            else:
                rng = self._rng

            # k_eff depends on boron concentration (simplified model)
            boron_ppm = simulation.model.geometry.get('boron_ppm', 0)
            # Rough correlation: k_eff decreases ~0.0001 per ppm boron
            base_k_eff = 1.05
            k_eff_mean = base_k_eff - (boron_ppm * 0.0001)

            # Add statistical uncertainty (decreases with more batches)
            uncertainty = 0.001 / np.sqrt(simulation.config.active_batches)
            k_eff = k_eff_mean + rng.normal(0, uncertainty)
            k_eff_std = uncertainty

        # Generate score data
        for score in simulation.config.scores:
            score_result = self._generate_mock_score_result(
                score,
                simulation.model.core,
                simulation.config.seed
            )
            scores_data[score.name] = score.from_tripoli_result(score_result)

        return RunResult(
            k_eff=k_eff,
            k_eff_std=k_eff_std,
            scores=scores_data,
            raw_result={'type': 'MockTripoliResult', 'simulation': simulation.simulation_object}
        )

    def _generate_mock_score_result(
        self,
        score: 'Score',
        core: Core,
        seed: Optional[int]
    ) -> dict[str, Any]:
        """Generate mock score result data.

        Args:
            score: Score object to generate data for
            core: Core object for sizing
            seed: Random seed for reproducibility

        Returns:
            Dictionary with mock score data
        """
        rng = np.random.default_rng(seed) if seed is not None else self._rng

        score_type = type(score).__name__

        if score_type == 'KeffectiveScore':
            # Already handled in main run method
            return {'value': 1.0, 'std': 0.001}

        elif score_type == 'PinPowerScore':
            # Generate 2D pin power distribution
            # Size based on core layout
            rows, cols = core.shape

            # Generate realistic power distribution (higher in center)
            x = np.linspace(-1, 1, cols)
            y = np.linspace(-1, 1, rows)
            X, Y = np.meshgrid(x, y)
            R = np.sqrt(X**2 + Y**2)

            # Radial power profile (cosine-like)
            power = 1.0 + 0.3 * np.cos(np.pi * R / 2)

            # Add statistical noise
            noise = rng.normal(0, 0.02, power.shape)
            power = power + noise

            # Normalize to average 1.0
            power = power / power.mean()

            # Generate uncertainties (smaller in high-power regions)
            std = 0.01 / np.sqrt(power)

            return {
                'values': power,
                'std': std
            }

        elif score_type == 'FluxScore':
            # Generate flux distribution
            rows, cols = core.shape
            flux = rng.exponential(1e14, size=(rows, cols))
            std = flux * 0.05  # 5% relative uncertainty

            return {
                'values': flux,
                'std': std
            }

        else:
            # Generic score
            return {
                'value': rng.normal(1.0, 0.1),
                'std': 0.05
            }


# Forward reference resolution
from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from pytrip5.simulation import SimulationConfig, RunResult
    from pytrip5.score import Score
