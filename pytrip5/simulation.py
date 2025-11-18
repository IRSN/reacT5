"""Simulation configuration and execution for pytrip5.

This module provides classes and functions for configuring and running
Tripoli-5 simulations through the adapter layer.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Optional, Any
import numpy.typing as npt

from pytrip5.core import Core
from pytrip5.adapter import BaseTripoliAdapter, TripoliModel
from pytrip5.score import Score


@dataclass
class SimulationConfig:
    """Configuration for a Tripoli-5 simulation run.

    Attributes:
        criticality: If True, run k-eigenvalue (criticality) calculation.
                    If False, run fixed-source simulation.
        particles_per_batch: Number of particles (neutrons) per batch/cycle
        active_batches: Number of active batches for statistics
        inactive_batches: Number of inactive batches for settling (criticality only)
        scores: List of Score objects to tally during simulation
        seed: Random number generator seed for reproducibility
        parallel_tasks: Number of parallel tasks for domain decomposition (HPC)

    Example:
        >>> from pytrip5.score import KeffectiveScore, PinPowerScore
        >>> config = SimulationConfig(
        ...     criticality=True,
        ...     particles_per_batch=10000,
        ...     active_batches=50,
        ...     inactive_batches=20,
        ...     scores=[KeffectiveScore(), PinPowerScore('pin_powers')],
        ...     seed=12345
        ... )
        >>> config.total_particles
        500000
    """
    criticality: bool = True
    particles_per_batch: int = 10000
    active_batches: int = 50
    inactive_batches: int = 20
    scores: list[Score] = field(default_factory=list)
    seed: Optional[int] = None
    parallel_tasks: int = 1

    def __post_init__(self) -> None:
        """Validate configuration parameters."""
        if self.particles_per_batch <= 0:
            raise ValueError(f"particles_per_batch must be positive, got {self.particles_per_batch}")
        if self.active_batches <= 0:
            raise ValueError(f"active_batches must be positive, got {self.active_batches}")
        if self.criticality and self.inactive_batches < 0:
            raise ValueError(f"inactive_batches cannot be negative, got {self.inactive_batches}")
        if self.parallel_tasks <= 0:
            raise ValueError(f"parallel_tasks must be positive, got {self.parallel_tasks}")

    @property
    def total_particles(self) -> int:
        """Calculate total number of particles simulated in active batches."""
        return self.particles_per_batch * self.active_batches

    @property
    def total_batches(self) -> int:
        """Calculate total number of batches (active + inactive)."""
        return self.active_batches + (self.inactive_batches if self.criticality else 0)

    @classmethod
    def quick_criticality(
        cls,
        scores: Optional[list[Score]] = None,
        seed: Optional[int] = None
    ) -> SimulationConfig:
        """Create a quick criticality configuration for testing.

        Uses reduced particle counts suitable for fast turnaround.

        Args:
            scores: Optional list of scores to tally
            seed: Optional random seed

        Returns:
            SimulationConfig with reduced settings

        Example:
            >>> config = SimulationConfig.quick_criticality()
            >>> config.particles_per_batch
            1000
        """
        return cls(
            criticality=True,
            particles_per_batch=1000,
            active_batches=10,
            inactive_batches=5,
            scores=scores or [],
            seed=seed
        )

    @classmethod
    def production_criticality(
        cls,
        scores: Optional[list[Score]] = None,
        seed: Optional[int] = None
    ) -> SimulationConfig:
        """Create a production-quality criticality configuration.

        Uses particle counts appropriate for publication-quality results.

        Args:
            scores: Optional list of scores to tally
            seed: Optional random seed

        Returns:
            SimulationConfig with production settings

        Example:
            >>> config = SimulationConfig.production_criticality()
            >>> config.particles_per_batch
            100000
        """
        return cls(
            criticality=True,
            particles_per_batch=100000,
            active_batches=200,
            inactive_batches=50,
            scores=scores or [],
            seed=seed
        )


@dataclass
class RunResult:
    """Results from a Tripoli-5 simulation run.

    Attributes:
        k_eff: Effective multiplication factor (criticality simulations only)
        k_eff_std: Standard deviation of k_eff
        scores: Dictionary mapping score names to their computed values
        raw_result: Raw Tripoli-5 result object for advanced access

    Example:
        >>> # Typically created by Runner.run(), not directly
        >>> result = RunResult(
        ...     k_eff=1.0234,
        ...     k_eff_std=0.0012,
        ...     scores={'pin_powers': np.array([[1.0, 1.1], [0.9, 1.0]])}
        ... )
        >>> result.k_eff
        1.0234
    """
    k_eff: Optional[float] = None
    k_eff_std: Optional[float] = None
    scores: dict[str, Any] = field(default_factory=dict)
    raw_result: Optional[Any] = None

    @property
    def k_eff_with_uncertainty(self) -> Optional[str]:
        """Format k_eff with uncertainty for display.

        Returns:
            Formatted string like "1.0234 ± 0.0012" or None if not available

        Example:
            >>> result = RunResult(k_eff=1.0234, k_eff_std=0.0012)
            >>> result.k_eff_with_uncertainty
            '1.0234 ± 0.0012'
        """
        if self.k_eff is None or self.k_eff_std is None:
            return None
        return f"{self.k_eff:.4f} ± {self.k_eff_std:.4f}"

    def get_score(self, name: str) -> Any:
        """Retrieve score result by name.

        Args:
            name: Score name as specified in SimulationConfig

        Returns:
            Score value (type depends on score type)

        Raises:
            KeyError: If score name not found in results

        Example:
            >>> result = RunResult(scores={'pin_powers': np.array([[1.0, 1.1]])})
            >>> powers = result.get_score('pin_powers')
            >>> powers.shape
            (1, 2)
        """
        return self.scores[name]

    @property
    def pin_powers(self) -> Optional[npt.NDArray]:
        """Convenience property to get pin powers if available.

        Returns:
            Pin power array if 'pin_powers' score exists, else None

        Example:
            >>> result = RunResult(scores={'pin_powers': np.array([[1.0, 1.1]])})
            >>> result.pin_powers.shape
            (1, 2)
        """
        return self.scores.get('pin_powers')


class Runner:
    """Simulation runner for executing Tripoli-5 calculations.

    The Runner class provides static methods for executing simulations
    through the adapter layer. It handles the workflow:
    1. Convert Core to TripoliModel via adapter
    2. Configure simulation with SimulationConfig
    3. Execute simulation
    4. Return results as RunResult

    Example:
        >>> from pytrip5.core import Core
        >>> from pytrip5.adapter import MockTripoliAdapter
        >>> from pytrip5.score import KeffectiveScore
        >>>
        >>> core = Core.simple_demo_3x3()
        >>> adapter = MockTripoliAdapter()
        >>> config = SimulationConfig.quick_criticality(
        ...     scores=[KeffectiveScore()]
        ... )
        >>> result = Runner.run(adapter, core, config)
        >>> isinstance(result.k_eff, float)
        True
    """

    @staticmethod
    def run(
        adapter: BaseTripoliAdapter,
        core: Core,
        config: SimulationConfig
    ) -> RunResult:
        """Run a simulation with the given adapter, core, and configuration.

        Args:
            adapter: TripoliAdapter or MockTripoliAdapter instance
            core: Core object to simulate
            config: SimulationConfig specifying simulation parameters

        Returns:
            RunResult containing simulation outputs

        Example:
            >>> from pytrip5.core import Core
            >>> from pytrip5.adapter import MockTripoliAdapter
            >>>
            >>> core = Core.simple_demo_3x3()
            >>> adapter = MockTripoliAdapter()
            >>> config = SimulationConfig.quick_criticality()
            >>> result = Runner.run(adapter, core, config)
            >>> result.k_eff is not None
            True
        """
        # Step 1: Convert core to Tripoli model
        model = core.to_tripoli(adapter)

        # Step 2: Configure simulation
        simulation = adapter.configure_simulation(model, config)

        # Step 3: Run simulation
        result = adapter.run(simulation)

        return result

    @staticmethod
    def run_batch(
        adapter: BaseTripoliAdapter,
        cores: list[Core],
        configs: list[SimulationConfig]
    ) -> list[RunResult]:
        """Run multiple simulations in sequence.

        Useful for parameter sweeps or batch processing.

        Args:
            adapter: TripoliAdapter or MockTripoliAdapter instance
            cores: List of Core objects to simulate
            configs: List of SimulationConfig objects (one per core)

        Returns:
            List of RunResult objects

        Raises:
            ValueError: If cores and configs lists have different lengths

        Example:
            >>> from pytrip5.core import Core
            >>> from pytrip5.adapter import MockTripoliAdapter
            >>>
            >>> cores = [Core.simple_demo_3x3() for _ in range(3)]
            >>> configs = [SimulationConfig.quick_criticality() for _ in range(3)]
            >>> adapter = MockTripoliAdapter()
            >>> results = Runner.run_batch(adapter, cores, configs)
            >>> len(results)
            3
        """
        if len(cores) != len(configs):
            raise ValueError(
                f"Number of cores ({len(cores)}) must match number of configs ({len(configs)})"
            )

        results = []
        for core, config in zip(cores, configs):
            result = Runner.run(adapter, core, config)
            results.append(result)

        return results

    @staticmethod
    def parameter_sweep(
        adapter: BaseTripoliAdapter,
        base_core: Core,
        parameter_name: str,
        parameter_values: list[Any],
        config: SimulationConfig
    ) -> dict[Any, RunResult]:
        """Run parameter sweep by varying a single core parameter.

        Args:
            adapter: TripoliAdapter or MockTripoliAdapter instance
            base_core: Base Core object to modify
            parameter_name: Name of core attribute to vary (e.g., 'boron_concentration')
            parameter_values: List of values to sweep over
            config: SimulationConfig (same for all runs, but seeds auto-incremented)

        Returns:
            Dictionary mapping parameter values to RunResult objects

        Example:
            >>> from pytrip5.core import Core
            >>> from pytrip5.adapter import MockTripoliAdapter
            >>>
            >>> core = Core.simple_demo_3x3()
            >>> adapter = MockTripoliAdapter()
            >>> config = SimulationConfig.quick_criticality(seed=100)
            >>>
            >>> results = Runner.parameter_sweep(
            ...     adapter, core, 'boron_concentration',
            ...     [0, 500, 1000], config
            ... )
            >>> len(results)
            3
        """
        results = {}

        for i, value in enumerate(parameter_values):
            # Create modified core
            # Note: Core is a dataclass, so we need to recreate it
            core_dict = {
                'assemblies': base_core.assemblies,
                'layout': base_core.layout,
                'boron_concentration': base_core.boron_concentration,
                'control_rod_positions': base_core.control_rod_positions
            }
            core_dict[parameter_name] = value
            modified_core = Core(**core_dict)

            # Create config with incremented seed
            sweep_config = SimulationConfig(
                criticality=config.criticality,
                particles_per_batch=config.particles_per_batch,
                active_batches=config.active_batches,
                inactive_batches=config.inactive_batches,
                scores=config.scores,
                seed=config.seed + i if config.seed is not None else None,
                parallel_tasks=config.parallel_tasks
            )

            # Run simulation
            result = Runner.run(adapter, modified_core, sweep_config)
            results[value] = result

        return results
