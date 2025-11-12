"""Simulation execution module for pyT5.

This module provides classes for configuring and executing
Tripoli-5 Monte-Carlo simulations.
"""

from pathlib import Path
from typing import Dict, List, Optional, Union
from .nuclear_data import NuclearData
from .materials import MaterialLibrary
from .cells import CellLibrary
from .geometry import GeometryBase
from .source import NeutronSource, NeutronMedia
from .visualization import Visualization
from .scores import ScoreLibrary


class Simulation:
    """Manages Tripoli-5 simulation configuration and execution.

    This class brings together all components needed for a Monte-Carlo
    simulation: geometry, materials, sources, scores, and execution
    parameters.

    Attributes:
        name: Unique identifier for the simulation.
        nuclear_data: Nuclear data library configuration.
        materials: Material library.
        cells: Cell library.
        geometry: Geometry definition.
        source: Neutron source definition.
        media: Neutron media properties.
        scores: Score library.
        visualizations: List of visualization configurations.
        n_particles: Number of particles per cycle.
        n_cycles: Total number of cycles.
        n_inactive: Number of inactive cycles for k-eigenvalue problems.
        n_threads: Number of parallel threads.
        random_seed: Random number generator seed.

    Examples:
        >>> sim = Simulation(
        ...     name="PWR_criticality",
        ...     n_particles=10000,
        ...     n_cycles=150,
        ...     n_inactive=50,
        ...     n_threads=8
        ... )
        >>> sim.set_nuclear_data(nuclear_data)
        >>> sim.set_materials(material_library)
        >>> sim.set_geometry(core_geometry)
        >>> sim.run()
    """

    def __init__(
        self,
        name: str,
        n_particles: int = 10000,
        n_cycles: int = 100,
        n_inactive: int = 20,
        n_threads: int = 1,
        random_seed: Optional[int] = None,
    ) -> None:
        """Initialize Simulation object.

        Args:
            name: Unique identifier for the simulation.
            n_particles: Number of particles per cycle. Defaults to 10000.
            n_cycles: Total number of cycles. Defaults to 100.
            n_inactive: Number of inactive cycles for criticality problems.
                Defaults to 20.
            n_threads: Number of parallel threads. Defaults to 1.
            random_seed: Random number generator seed. If None, uses
                system time. Defaults to None.

        Raises:
            ValueError: If any parameter is negative or n_inactive >= n_cycles.
        """
        if n_particles <= 0:
            raise ValueError(f"n_particles must be positive, got {n_particles}")
        if n_cycles <= 0:
            raise ValueError(f"n_cycles must be positive, got {n_cycles}")
        if n_inactive < 0:
            raise ValueError(f"n_inactive must be non-negative, got {n_inactive}")
        if n_inactive >= n_cycles:
            raise ValueError(
                f"n_inactive ({n_inactive}) must be less than n_cycles ({n_cycles})"
            )
        if n_threads <= 0:
            raise ValueError(f"n_threads must be positive, got {n_threads}")

        self.name = name
        self.n_particles = n_particles
        self.n_cycles = n_cycles
        self.n_inactive = n_inactive
        self.n_threads = n_threads
        self.random_seed = random_seed

        # Simulation components
        self.nuclear_data: Optional[NuclearData] = None
        self.materials: Optional[MaterialLibrary] = None
        self.cells: Optional[CellLibrary] = None
        self.geometry: Optional[GeometryBase] = None
        self.source: Optional[NeutronSource] = None
        self.media: Optional[NeutronMedia] = None
        self.scores: Optional[ScoreLibrary] = None
        self.visualizations: List[Visualization] = []

    def set_nuclear_data(self, nuclear_data: NuclearData) -> None:
        """Set the nuclear data library.

        Args:
            nuclear_data: NuclearData object.
        """
        self.nuclear_data = nuclear_data

    def set_materials(self, materials: MaterialLibrary) -> None:
        """Set the material library.

        Args:
            materials: MaterialLibrary object.
        """
        self.materials = materials

    def set_cells(self, cells: CellLibrary) -> None:
        """Set the cell library.

        Args:
            cells: CellLibrary object.
        """
        self.cells = cells

    def set_geometry(self, geometry: GeometryBase) -> None:
        """Set the geometry definition.

        Args:
            geometry: GeometryBase subclass object (PinCell, Assembly, Core, etc.).
        """
        self.geometry = geometry

    def set_source(self, source: NeutronSource) -> None:
        """Set the neutron source.

        Args:
            source: NeutronSource object.
        """
        self.source = source

    def set_media(self, media: NeutronMedia) -> None:
        """Set the neutron media properties.

        Args:
            media: NeutronMedia object.
        """
        self.media = media

    def set_scores(self, scores: ScoreLibrary) -> None:
        """Set the score library.

        Args:
            scores: ScoreLibrary object.
        """
        self.scores = scores

    def add_visualization(self, visualization: Visualization) -> None:
        """Add a visualization configuration.

        Args:
            visualization: Visualization object.
        """
        self.visualizations.append(visualization)

    def set_particles_per_cycle(self, n_particles: int) -> None:
        """Set the number of particles per cycle.

        Args:
            n_particles: Number of particles.

        Raises:
            ValueError: If n_particles is non-positive.
        """
        if n_particles <= 0:
            raise ValueError(f"n_particles must be positive, got {n_particles}")
        self.n_particles = n_particles

    def set_cycles(self, n_cycles: int, n_inactive: int) -> None:
        """Set the number of cycles and inactive cycles.

        Args:
            n_cycles: Total number of cycles.
            n_inactive: Number of inactive cycles.

        Raises:
            ValueError: If parameters are invalid.
        """
        if n_cycles <= 0:
            raise ValueError(f"n_cycles must be positive, got {n_cycles}")
        if n_inactive < 0:
            raise ValueError(f"n_inactive must be non-negative, got {n_inactive}")
        if n_inactive >= n_cycles:
            raise ValueError(
                f"n_inactive ({n_inactive}) must be less than n_cycles ({n_cycles})"
            )
        self.n_cycles = n_cycles
        self.n_inactive = n_inactive

    def set_threads(self, n_threads: int) -> None:
        """Set the number of parallel threads.

        Args:
            n_threads: Number of threads.

        Raises:
            ValueError: If n_threads is non-positive.
        """
        if n_threads <= 0:
            raise ValueError(f"n_threads must be positive, got {n_threads}")
        self.n_threads = n_threads

    def validate(self) -> bool:
        """Validate that all required components are set.

        Returns:
            True if validation successful.

        Raises:
            RuntimeError: If required components are missing.
        """
        if self.nuclear_data is None:
            raise RuntimeError("Nuclear data not set")
        if self.materials is None:
            raise RuntimeError("Materials not set")
        if self.geometry is None:
            raise RuntimeError("Geometry not set")
        if self.source is None:
            raise RuntimeError("Neutron source not set")

        return True

    def run(self, output_dir: Optional[Union[str, Path]] = None) -> "Results":
        """Execute the simulation.

        Args:
            output_dir: Directory for output files. If None, uses current
                directory. Defaults to None.

        Returns:
            Results object containing simulation results.

        Raises:
            RuntimeError: If simulation validation fails or execution error.
        """
        from .results import Results

        self.validate()

        # Placeholder implementation - would interface with Tripoli-5 API
        print(f"Running simulation '{self.name}'...")
        print(f"  Particles per cycle: {self.n_particles}")
        print(f"  Total cycles: {self.n_cycles} ({self.n_inactive} inactive)")
        print(f"  Threads: {self.n_threads}")

        # In real implementation, would call Tripoli-5 API here
        # and return actual results
        return Results(simulation_name=self.name)

    def __repr__(self) -> str:
        """Return string representation of Simulation object."""
        return (
            f"Simulation(name='{self.name}', particles={self.n_particles}, "
            f"cycles={self.n_cycles}, threads={self.n_threads})"
        )
