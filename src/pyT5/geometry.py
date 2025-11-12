"""Geometry definition module for pyT5.

This module provides classes for defining various geometric objects
in PWR reactor simulations, from pin cells to full cores.
"""

from typing import Dict, List, Optional, Tuple, Union
import numpy as np
from .cells import Cell


class GeometryBase:
    """Base class for all geometry objects.

    Provides common functionality for geometric objects in the simulation.

    Attributes:
        name: Unique identifier for the geometry object.
        cells: List of Cell objects contained in this geometry.
    """

    def __init__(self, name: str) -> None:
        """Initialize GeometryBase object.

        Args:
            name: Unique identifier for the geometry object.
        """
        self.name = name
        self.cells: List[Cell] = []

    def add_cell(self, cell: Cell) -> None:
        """Add a cell to the geometry.

        Args:
            cell: Cell object to add.
        """
        self.cells.append(cell)

    def get_cells(self) -> List[Cell]:
        """Get all cells in the geometry.

        Returns:
            List of Cell objects.
        """
        return self.cells

    def __repr__(self) -> str:
        """Return string representation of geometry object."""
        return f"{self.__class__.__name__}(name='{self.name}', cells={len(self.cells)})"


class PinCell(GeometryBase):
    """Represents a fuel pin cell geometry.

    A pin cell typically consists of concentric cylindrical regions
    (fuel, gap, cladding) surrounded by moderator.

    Attributes:
        name: Unique identifier for the pin cell.
        pitch: Pin cell pitch (distance between pin centers) in cm.
        height: Pin cell height in cm.
        fuel_radius: Fuel pellet radius in cm.
        clad_inner_radius: Inner radius of cladding in cm.
        clad_outer_radius: Outer radius of cladding in cm.

    Examples:
        >>> pin = PinCell(
        ...     name="standard_pin",
        ...     pitch=1.26,
        ...     height=365.76,
        ...     fuel_radius=0.4096,
        ...     clad_inner_radius=0.418,
        ...     clad_outer_radius=0.475
        ... )
    """

    def __init__(
        self,
        name: str,
        pitch: float,
        height: float,
        fuel_radius: float,
        clad_inner_radius: float,
        clad_outer_radius: float,
    ) -> None:
        """Initialize PinCell object.

        Args:
            name: Unique identifier for the pin cell.
            pitch: Pin cell pitch in cm.
            height: Pin cell height in cm.
            fuel_radius: Fuel pellet radius in cm.
            clad_inner_radius: Inner radius of cladding in cm.
            clad_outer_radius: Outer radius of cladding in cm.

        Raises:
            ValueError: If dimensions are invalid or inconsistent.
        """
        super().__init__(name)

        if pitch <= 0 or height <= 0:
            raise ValueError("Pitch and height must be positive")
        if not (0 < fuel_radius < clad_inner_radius < clad_outer_radius < pitch / 2):
            raise ValueError("Invalid radii: must satisfy 0 < r_fuel < r_clad_in < r_clad_out < pitch/2")

        self.pitch = pitch
        self.height = height
        self.fuel_radius = fuel_radius
        self.clad_inner_radius = clad_inner_radius
        self.clad_outer_radius = clad_outer_radius

    def get_fuel_volume(self) -> float:
        """Calculate the fuel volume.

        Returns:
            Fuel volume in cm³.
        """
        return np.pi * self.fuel_radius**2 * self.height

    def get_gap_volume(self) -> float:
        """Calculate the gap volume between fuel and cladding.

        Returns:
            Gap volume in cm³.
        """
        return np.pi * (self.clad_inner_radius**2 - self.fuel_radius**2) * self.height

    def get_clad_volume(self) -> float:
        """Calculate the cladding volume.

        Returns:
            Cladding volume in cm³.
        """
        return np.pi * (self.clad_outer_radius**2 - self.clad_inner_radius**2) * self.height


class Assembly(GeometryBase):
    """Represents a fuel assembly geometry.

    A fuel assembly consists of an array of pin cells arranged in a
    rectangular or hexagonal lattice.

    Attributes:
        name: Unique identifier for the assembly.
        lattice_type: Type of lattice ('square' or 'hexagonal').
        n_pins_x: Number of pins in x-direction (for square lattice).
        n_pins_y: Number of pins in y-direction (for square lattice).
        pin_pitch: Distance between pin centers in cm.
        assembly_pitch: Overall assembly pitch in cm.

    Examples:
        >>> assembly = Assembly(
        ...     name="17x17_assembly",
        ...     lattice_type="square",
        ...     n_pins_x=17,
        ...     n_pins_y=17,
        ...     pin_pitch=1.26,
        ...     assembly_pitch=21.5
        ... )
    """

    def __init__(
        self,
        name: str,
        lattice_type: str = "square",
        n_pins_x: int = 17,
        n_pins_y: int = 17,
        pin_pitch: float = 1.26,
        assembly_pitch: float = 21.5,
    ) -> None:
        """Initialize Assembly object.

        Args:
            name: Unique identifier for the assembly.
            lattice_type: Type of lattice arrangement. Either 'square' or
                'hexagonal'. Defaults to 'square'.
            n_pins_x: Number of pins in x-direction. Defaults to 17.
            n_pins_y: Number of pins in y-direction. Defaults to 17.
            pin_pitch: Distance between pin centers in cm. Defaults to 1.26.
            assembly_pitch: Overall assembly pitch in cm. Defaults to 21.5.

        Raises:
            ValueError: If lattice_type is invalid or dimensions are non-positive.
        """
        super().__init__(name)

        if lattice_type not in ("square", "hexagonal"):
            raise ValueError(f"Invalid lattice_type '{lattice_type}', must be 'square' or 'hexagonal'")
        if n_pins_x <= 0 or n_pins_y <= 0:
            raise ValueError("Number of pins must be positive")
        if pin_pitch <= 0 or assembly_pitch <= 0:
            raise ValueError("Pitches must be positive")

        self.lattice_type = lattice_type
        self.n_pins_x = n_pins_x
        self.n_pins_y = n_pins_y
        self.pin_pitch = pin_pitch
        self.assembly_pitch = assembly_pitch
        self.pin_map: List[List[Optional[PinCell]]] = [
            [None for _ in range(n_pins_y)] for _ in range(n_pins_x)
        ]

    def set_pin(self, i: int, j: int, pin: Optional[PinCell]) -> None:
        """Place a pin cell at position (i, j) in the assembly lattice.

        Args:
            i: Row index (0-based).
            j: Column index (0-based).
            pin: PinCell object to place, or None for empty position.

        Raises:
            IndexError: If indices are out of range.
        """
        if not (0 <= i < self.n_pins_x and 0 <= j < self.n_pins_y):
            raise IndexError(f"Pin position ({i}, {j}) out of range")
        self.pin_map[i][j] = pin

    def get_pin(self, i: int, j: int) -> Optional[PinCell]:
        """Get the pin cell at position (i, j).

        Args:
            i: Row index (0-based).
            j: Column index (0-based).

        Returns:
            PinCell object at the position, or None if empty.

        Raises:
            IndexError: If indices are out of range.
        """
        if not (0 <= i < self.n_pins_x and 0 <= j < self.n_pins_y):
            raise IndexError(f"Pin position ({i}, {j}) out of range")
        return self.pin_map[i][j]

    def count_pins(self) -> int:
        """Count the number of non-empty pin positions.

        Returns:
            Number of pins in the assembly.
        """
        return sum(1 for row in self.pin_map for pin in row if pin is not None)


class Colorset(GeometryBase):
    """Represents a colorset of multiple fuel assemblies.

    A colorset is a collection of assemblies that may have different
    properties (fuel enrichment, burnup, etc.).

    Attributes:
        name: Unique identifier for the colorset.
        assemblies: Dictionary mapping assembly positions to Assembly objects.

    Examples:
        >>> colorset = Colorset(name="quarter_core")
        >>> colorset.add_assembly((0, 0), assembly1)
        >>> colorset.add_assembly((0, 1), assembly2)
    """

    def __init__(self, name: str) -> None:
        """Initialize Colorset object.

        Args:
            name: Unique identifier for the colorset.
        """
        super().__init__(name)
        self.assemblies: Dict[Tuple[int, int], Assembly] = {}

    def add_assembly(self, position: Tuple[int, int], assembly: Assembly) -> None:
        """Add an assembly at a specific position in the colorset.

        Args:
            position: (i, j) position tuple for the assembly.
            assembly: Assembly object to place.

        Raises:
            ValueError: If position is already occupied.
        """
        if position in self.assemblies:
            raise ValueError(f"Position {position} is already occupied")
        self.assemblies[position] = assembly

    def get_assembly(self, position: Tuple[int, int]) -> Optional[Assembly]:
        """Get the assembly at a specific position.

        Args:
            position: (i, j) position tuple.

        Returns:
            Assembly object at the position, or None if empty.
        """
        return self.assemblies.get(position)

    def remove_assembly(self, position: Tuple[int, int]) -> None:
        """Remove an assembly from the colorset.

        Args:
            position: (i, j) position tuple.

        Raises:
            KeyError: If no assembly exists at the position.
        """
        if position not in self.assemblies:
            raise KeyError(f"No assembly at position {position}")
        del self.assemblies[position]

    def count_assemblies(self) -> int:
        """Count the number of assemblies in the colorset.

        Returns:
            Number of assemblies.
        """
        return len(self.assemblies)


class Core(GeometryBase):
    """Represents a full reactor core geometry.

    A core consists of multiple assemblies or colorsets arranged in a
    specific configuration.

    Attributes:
        name: Unique identifier for the core.
        core_type: Type of core layout ('square' or 'hexagonal').
        n_assemblies_x: Number of assemblies in x-direction.
        n_assemblies_y: Number of assemblies in y-direction.

    Examples:
        >>> core = Core(
        ...     name="PWR_core",
        ...     core_type="square",
        ...     n_assemblies_x=15,
        ...     n_assemblies_y=15
        ... )
    """

    def __init__(
        self,
        name: str,
        core_type: str = "square",
        n_assemblies_x: int = 15,
        n_assemblies_y: int = 15,
    ) -> None:
        """Initialize Core object.

        Args:
            name: Unique identifier for the core.
            core_type: Type of core layout. Either 'square' or 'hexagonal'.
                Defaults to 'square'.
            n_assemblies_x: Number of assemblies in x-direction. Defaults to 15.
            n_assemblies_y: Number of assemblies in y-direction. Defaults to 15.

        Raises:
            ValueError: If core_type is invalid or dimensions are non-positive.
        """
        super().__init__(name)

        if core_type not in ("square", "hexagonal"):
            raise ValueError(f"Invalid core_type '{core_type}', must be 'square' or 'hexagonal'")
        if n_assemblies_x <= 0 or n_assemblies_y <= 0:
            raise ValueError("Number of assemblies must be positive")

        self.core_type = core_type
        self.n_assemblies_x = n_assemblies_x
        self.n_assemblies_y = n_assemblies_y
        self.assembly_map: Dict[Tuple[int, int], Union[Assembly, Colorset]] = {}

    def set_assembly(
        self, position: Tuple[int, int], assembly: Union[Assembly, Colorset]
    ) -> None:
        """Place an assembly or colorset at a specific position in the core.

        Args:
            position: (i, j) position tuple.
            assembly: Assembly or Colorset object to place.

        Raises:
            IndexError: If position is out of range.
        """
        i, j = position
        if not (0 <= i < self.n_assemblies_x and 0 <= j < self.n_assemblies_y):
            raise IndexError(f"Assembly position {position} out of range")
        self.assembly_map[position] = assembly

    def get_assembly(self, position: Tuple[int, int]) -> Optional[Union[Assembly, Colorset]]:
        """Get the assembly or colorset at a specific position.

        Args:
            position: (i, j) position tuple.

        Returns:
            Assembly or Colorset object at the position, or None if empty.
        """
        return self.assembly_map.get(position)

    def count_assemblies(self) -> int:
        """Count the number of assemblies/colorsets in the core.

        Returns:
            Number of assemblies/colorsets.
        """
        return len(self.assembly_map)


class Reflector(GeometryBase):
    """Represents a reflector surrounding the core.

    A reflector is a region of material (typically water or steel)
    surrounding the active core to reduce neutron leakage.

    Attributes:
        name: Unique identifier for the reflector.
        thickness: Reflector thickness in cm.
        material_name: Name of the reflector material.

    Examples:
        >>> reflector = Reflector(
        ...     name="water_reflector",
        ...     thickness=20.0,
        ...     material_name="light_water"
        ... )
    """

    def __init__(
        self,
        name: str,
        thickness: float,
        material_name: str,
    ) -> None:
        """Initialize Reflector object.

        Args:
            name: Unique identifier for the reflector.
            thickness: Reflector thickness in cm.
            material_name: Name of the reflector material.

        Raises:
            ValueError: If thickness is non-positive.
        """
        super().__init__(name)

        if thickness <= 0:
            raise ValueError(f"Thickness must be positive, got {thickness}")

        self.thickness = thickness
        self.material_name = material_name

    def __repr__(self) -> str:
        """Return string representation of Reflector object."""
        return (
            f"Reflector(name='{self.name}', thickness={self.thickness} cm, "
            f"material='{self.material_name}')"
        )
