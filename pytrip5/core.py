"""Core domain model for pytrip5.

This module provides high-level dataclasses representing PWR reactor components:
materials, fuel pins, assemblies, and full cores. These objects can be transformed
into Tripoli-5 Python API inputs via the adapter layer.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Sequence, Optional
import numpy as np
import numpy.typing as npt


@dataclass(frozen=True)
class Material:
    """Represents a material with isotopic composition.

    Attributes:
        name: Unique material identifier (e.g., 'UO2_3.1%', 'Zircaloy-4')
        density: Material density in g/cm³
        compositions: Isotopic composition as mass or atom fractions.
                     Keys are isotope identifiers (e.g., 'U235', 'U238', 'O16')
        temperature: Optional temperature in Kelvin

    Example:
        >>> fuel = Material(
        ...     name='UO2_3.1%',
        ...     density=10.4,
        ...     compositions={'U235': 0.031, 'U238': 0.969, 'O16': 2.0},
        ...     temperature=900.0
        ... )
        >>> fuel.name
        'UO2_3.1%'
    """
    name: str
    density: float
    compositions: dict[str, float]
    temperature: Optional[float] = None

    def __post_init__(self) -> None:
        """Validate material properties."""
        if self.density <= 0:
            raise ValueError(f"Material density must be positive, got {self.density}")
        if not self.compositions:
            raise ValueError("Material must have at least one isotope composition")


@dataclass(frozen=True)
class Pin:
    """Represents a cylindrical fuel pin or guide tube.

    Attributes:
        id: Unique pin identifier within an assembly
        radius: Pin outer radius in cm
        material: Material filling this pin
        pitch: Optional pin pitch (center-to-center distance) in cm

    Example:
        >>> fuel_mat = Material('UO2', 10.4, {'U235': 0.03, 'U238': 0.97})
        >>> pin = Pin(id='fuel_std', radius=0.475, material=fuel_mat, pitch=1.26)
        >>> pin.radius
        0.475
    """
    id: str
    radius: float
    material: Material
    pitch: Optional[float] = None

    def __post_init__(self) -> None:
        """Validate pin geometry."""
        if self.radius <= 0:
            raise ValueError(f"Pin radius must be positive, got {self.radius}")
        if self.pitch is not None and self.pitch <= 0:
            raise ValueError(f"Pin pitch must be positive, got {self.pitch}")


@dataclass
class Assembly:
    """Represents a fuel assembly with a lattice of pins.

    Attributes:
        id: Unique assembly identifier
        pitch: Assembly pitch (lattice spacing) in cm
        pins: 2D array of Pin objects arranged in a square lattice.
              Shape should be (N, N) for NxN lattice
        enrichment: Optional U-235 enrichment in %

    Example:
        >>> fuel_mat = Material('UO2', 10.4, {'U235': 0.03, 'U238': 0.97})
        >>> pin = Pin('fuel', 0.475, fuel_mat)
        >>> # Create 3x3 assembly with identical pins
        >>> pins_grid = [[pin for _ in range(3)] for _ in range(3)]
        >>> asm = Assembly(id='ASM_A', pitch=21.5, pins=pins_grid, enrichment=3.1)
        >>> len(asm.pins)
        3
    """
    id: str
    pitch: float
    pins: Sequence[Sequence[Pin]]
    enrichment: Optional[float] = None

    def __post_init__(self) -> None:
        """Validate assembly structure."""
        if self.pitch <= 0:
            raise ValueError(f"Assembly pitch must be positive, got {self.pitch}")
        if not self.pins:
            raise ValueError("Assembly must contain at least one pin")
        # Check that pins form a rectangular grid
        row_lengths = [len(row) for row in self.pins]
        if len(set(row_lengths)) > 1:
            raise ValueError(f"Assembly pins must form rectangular grid, got row lengths {row_lengths}")

    @property
    def shape(self) -> tuple[int, int]:
        """Return the (rows, cols) shape of the pin lattice."""
        return (len(self.pins), len(self.pins[0]) if self.pins else 0)

    def get_pin(self, row: int, col: int) -> Pin:
        """Get pin at specified (row, col) position.

        Args:
            row: Row index (0-based)
            col: Column index (0-based)

        Returns:
            Pin at the specified position
        """
        return self.pins[row][col]


@dataclass
class Core:
    """Represents a full reactor core with multiple assemblies.

    Attributes:
        assemblies: Dictionary mapping assembly IDs to Assembly objects
        layout: 2D grid of assembly IDs specifying core loading pattern.
                Use None or empty string for positions without assemblies
        boron_concentration: Boron concentration in coolant (ppm)
        control_rod_positions: Optional dict mapping control rod bank IDs to insertion depth

    Example:
        >>> # Create simple 3x3 core
        >>> asm = Assembly('ASM_A', 21.5, [[Pin('p', 0.5, Material('UO2', 10.4, {'U': 1}))]])
        >>> core = Core(
        ...     assemblies={'A': asm},
        ...     layout=[['A', 'A', 'A'], ['A', 'A', 'A'], ['A', 'A', 'A']],
        ...     boron_concentration=500.0
        ... )
        >>> core.shape
        (3, 3)
    """
    assemblies: dict[str, Assembly]
    layout: Sequence[Sequence[Optional[str]]]
    boron_concentration: float = 0.0
    control_rod_positions: dict[str, float] = field(default_factory=dict)

    def __post_init__(self) -> None:
        """Validate core configuration."""
        if not self.layout:
            raise ValueError("Core layout cannot be empty")

        # Validate layout is rectangular
        row_lengths = [len(row) for row in self.layout]
        if len(set(row_lengths)) > 1:
            raise ValueError(f"Core layout must be rectangular, got row lengths {row_lengths}")

        # Validate all assembly IDs in layout exist in assemblies dict
        for row in self.layout:
            for asm_id in row:
                if asm_id and asm_id not in self.assemblies:
                    raise ValueError(f"Assembly ID '{asm_id}' in layout not found in assemblies dict")

        if self.boron_concentration < 0:
            raise ValueError(f"Boron concentration cannot be negative, got {self.boron_concentration}")

    @property
    def shape(self) -> tuple[int, int]:
        """Return the (rows, cols) shape of the core layout."""
        return (len(self.layout), len(self.layout[0]) if self.layout else 0)

    def get_assembly(self, row: int, col: int) -> Optional[Assembly]:
        """Get assembly at specified (row, col) position in core layout.

        Args:
            row: Row index (0-based)
            col: Column index (0-based)

        Returns:
            Assembly at the specified position, or None if position is empty
        """
        asm_id = self.layout[row][col]
        if not asm_id:
            return None
        return self.assemblies.get(asm_id)

    def to_tripoli(self, adapter: 'TripoliAdapter') -> 'TripoliModel':
        """Convert this Core to Tripoli-5 API objects via adapter.

        Args:
            adapter: TripoliAdapter instance to use for conversion

        Returns:
            TripoliModel object containing geometry, materials, and configuration

        Note:
            This method delegates to the adapter layer to maintain separation
            between domain model and Tripoli-5 API specifics.
        """
        from pytrip5.adapter import TripoliModel

        # Collect all unique materials from all assemblies
        materials_dict = {}
        for asm_id, assembly in self.assemblies.items():
            for row in assembly.pins:
                for pin in row:
                    materials_dict[pin.material.name] = pin.material

        # Convert materials
        tripoli_materials = {
            name: adapter.create_material(mat)
            for name, mat in materials_dict.items()
        }

        # Convert geometry
        tripoli_geometry = adapter.create_geometry(self)

        return TripoliModel(
            materials=tripoli_materials,
            geometry=tripoli_geometry,
            core=self
        )

    @classmethod
    def simple_demo_3x3(cls) -> Core:
        """Create a simple 3x3 core for testing and demonstrations.

        Returns:
            Core object with 3x3 layout of identical assemblies

        Example:
            >>> core = Core.simple_demo_3x3()
            >>> core.shape
            (3, 3)
            >>> core.boron_concentration
            500.0
        """
        # Create simple fuel material
        fuel_mat = Material(
            name='UO2_3.1%',
            density=10.4,
            compositions={'U235': 0.031, 'U238': 0.969, 'O16': 2.0},
            temperature=900.0
        )

        # Create fuel pin
        fuel_pin = Pin(
            id='fuel_std',
            radius=0.475,
            material=fuel_mat,
            pitch=1.26
        )

        # Create 17x17 pin lattice (typical PWR assembly)
        pins_grid = [[fuel_pin for _ in range(17)] for _ in range(17)]

        # Create assembly
        assembly = Assembly(
            id='ASM_3.1',
            pitch=21.5,
            pins=pins_grid,
            enrichment=3.1
        )

        # Create 3x3 core layout
        layout = [
            ['ASM_3.1', 'ASM_3.1', 'ASM_3.1'],
            ['ASM_3.1', 'ASM_3.1', 'ASM_3.1'],
            ['ASM_3.1', 'ASM_3.1', 'ASM_3.1']
        ]

        return cls(
            assemblies={'ASM_3.1': assembly},
            layout=layout,
            boron_concentration=500.0
        )


# Type alias for forward references
TripoliAdapter = 'TripoliAdapter'
