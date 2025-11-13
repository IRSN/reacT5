"""
Geometry module for pytrip5 package.

This module defines hierarchical geometry classes for reactor modeling
including pin cells, assemblies, colorsets, cores, and reflectors.
"""

from typing import Optional, List, Dict, Tuple, Union
from .core import PyTrip5Object, ValidationError, Validator
from .materials import Material
from .cells import Cell, CylindricalCell


class Geometry(PyTrip5Object):
    """Base class for all geometry objects."""

    def __init__(self, name: str, **kwargs):
        """
        Initialize Geometry.

        Parameters
        ----------
        name : str
            Name of the geometry
        **kwargs
            Additional keyword arguments
        """
        super().__init__(name, **kwargs)
        self._boundary_condition = "reflective"

    @property
    def boundary_condition(self) -> str:
        """Get boundary condition."""
        return self._boundary_condition

    @boundary_condition.setter
    def boundary_condition(self, value: str):
        """Set boundary condition."""
        valid = ["reflective", "vacuum", "periodic"]
        if value not in valid:
            raise ValidationError(
                f"Boundary condition must be one of {valid}, got '{value}'"
            )
        self._boundary_condition = value


class PinCell(Geometry):
    """
    Class representing a fuel pin cell.

    A pin cell consists of concentric cylindrical regions (fuel, gap, cladding)
    surrounded by coolant in a square or hexagonal lattice.
    """

    def __init__(
        self,
        name: str,
        pitch: float,
        fuel_radius: float,
        clad_inner_radius: Optional[float] = None,
        clad_outer_radius: Optional[float] = None,
        lattice_type: str = "square",
        **kwargs
    ):
        """
        Initialize a PinCell.

        Parameters
        ----------
        name : str
            Name of the pin cell
        pitch : float
            Lattice pitch (cm)
        fuel_radius : float
            Fuel pellet radius (cm)
        clad_inner_radius : float, optional
            Inner cladding radius (cm)
        clad_outer_radius : float, optional
            Outer cladding radius (cm)
        lattice_type : str
            Lattice type: 'square' or 'hexagonal'
        **kwargs
            Additional keyword arguments
        """
        super().__init__(name, **kwargs)
        self._pitch = Validator.validate_positive(pitch, "pitch")
        self._fuel_radius = Validator.validate_positive(fuel_radius, "fuel_radius")
        self._clad_inner_radius = clad_inner_radius
        self._clad_outer_radius = clad_outer_radius
        self._lattice_type = self._validate_lattice_type(lattice_type)

        # Materials for different regions
        self._fuel_material: Optional[Material] = None
        self._gap_material: Optional[Material] = None
        self._clad_material: Optional[Material] = None
        self._coolant_material: Optional[Material] = None

        # Validate geometry consistency
        self._validate_radii()

    @property
    def pitch(self) -> float:
        """Get pin pitch."""
        return self._pitch

    @property
    def fuel_radius(self) -> float:
        """Get fuel radius."""
        return self._fuel_radius

    @property
    def clad_inner_radius(self) -> Optional[float]:
        """Get inner cladding radius."""
        return self._clad_inner_radius

    @property
    def clad_outer_radius(self) -> Optional[float]:
        """Get outer cladding radius."""
        return self._clad_outer_radius

    @property
    def lattice_type(self) -> str:
        """Get lattice type."""
        return self._lattice_type

    def _validate_radii(self):
        """Validate that radii are consistent."""
        if self._clad_inner_radius is not None:
            if self._clad_inner_radius <= self._fuel_radius:
                raise ValidationError(
                    "Clad inner radius must be greater than fuel radius"
                )

        if self._clad_outer_radius is not None:
            if self._clad_inner_radius is None:
                raise ValidationError(
                    "Must specify clad_inner_radius if clad_outer_radius is given"
                )
            if self._clad_outer_radius <= self._clad_inner_radius:
                raise ValidationError(
                    "Clad outer radius must be greater than clad inner radius"
                )

            # Check that pin fits in lattice
            if self._clad_outer_radius >= self._pitch / 2:
                raise ValidationError(
                    f"Clad outer radius ({self._clad_outer_radius}) "
                    f"exceeds half pitch ({self._pitch / 2})"
                )

    @staticmethod
    def _validate_lattice_type(lattice_type: str) -> str:
        """Validate lattice type."""
        valid = ["square", "hexagonal"]
        if lattice_type not in valid:
            raise ValidationError(
                f"Lattice type must be one of {valid}, got '{lattice_type}'"
            )
        return lattice_type

    def set_fuel_material(self, material: Material):
        """Set fuel material."""
        self._fuel_material = material

    def set_gap_material(self, material: Material):
        """Set gap material."""
        self._gap_material = material

    def set_clad_material(self, material: Material):
        """Set cladding material."""
        self._clad_material = material

    def set_coolant_material(self, material: Material):
        """Set coolant material."""
        self._coolant_material = material

    def validate(self) -> bool:
        """Validate pin cell configuration."""
        if self._fuel_material is None:
            raise ValidationError(f"Pin cell '{self.name}' has no fuel material")

        if self._coolant_material is None:
            raise ValidationError(f"Pin cell '{self.name}' has no coolant material")

        return True

    def to_tripoli5(self):
        """Convert to Tripoli-5 geometry."""
        pass

    def __repr__(self) -> str:
        """String representation."""
        return (
            f"PinCell(name='{self.name}', pitch={self._pitch}, "
            f"fuel_r={self._fuel_radius})"
        )


class Assembly(Geometry):
    """
    Class representing a fuel assembly.

    An assembly consists of a lattice of pin cells with optional
    guide tubes, instrument tubes, and burnable absorbers.
    """

    def __init__(
        self,
        name: str,
        lattice_size: Tuple[int, int],
        pitch: float,
        assembly_pitch: Optional[float] = None,
        **kwargs
    ):
        """
        Initialize an Assembly.

        Parameters
        ----------
        name : str
            Name of the assembly
        lattice_size : Tuple[int, int]
            Lattice dimensions (nx, ny), e.g., (17, 17)
        pitch : float
            Pin pitch (cm)
        assembly_pitch : float, optional
            Assembly pitch (cm). If None, computed from lattice_size and pitch.
        **kwargs
            Additional keyword arguments
        """
        super().__init__(name, **kwargs)
        self._lattice_size = self._validate_lattice_size(lattice_size)
        self._pitch = Validator.validate_positive(pitch, "pitch")

        if assembly_pitch is None:
            self._assembly_pitch = max(lattice_size) * pitch
        else:
            self._assembly_pitch = Validator.validate_positive(
                assembly_pitch, "assembly_pitch"
            )

        # Pin layout: maps (i, j) position to pin type or material
        self._pins: Dict[Tuple[int, int], Union[PinCell, str]] = {}

        # Default pin for positions not explicitly set
        self._default_pin: Optional[PinCell] = None

        # Assembly materials (water boxes, etc.)
        self._structure_material: Optional[Material] = None

    @property
    def lattice_size(self) -> Tuple[int, int]:
        """Get lattice size."""
        return self._lattice_size

    @property
    def pitch(self) -> float:
        """Get pin pitch."""
        return self._pitch

    @property
    def assembly_pitch(self) -> float:
        """Get assembly pitch."""
        return self._assembly_pitch

    @staticmethod
    def _validate_lattice_size(size: Tuple[int, int]) -> Tuple[int, int]:
        """Validate lattice size."""
        if len(size) != 2:
            raise ValidationError("Lattice size must be a tuple of 2 integers")

        nx, ny = size
        if nx <= 0 or ny <= 0:
            raise ValidationError("Lattice dimensions must be positive")

        if nx > 100 or ny > 100:
            raise ValidationError("Lattice dimensions cannot exceed 100x100")

        return (nx, ny)

    def set_default_pin(self, pin: PinCell):
        """
        Set the default pin type for all positions.

        Parameters
        ----------
        pin : PinCell
            Default pin cell
        """
        self._default_pin = pin

    def set_pin(self, pin: Union[PinCell, str], positions: Union[str, List[Tuple[int, int]]]):
        """
        Set pin type at specific positions.

        Parameters
        ----------
        pin : PinCell or str
            Pin cell or pin type identifier
        positions : str or List[Tuple[int, int]]
            Position(s) to place pin. Can be:
            - 'all': all positions
            - 'corners': corner positions
            - List of (i, j) tuples
        """
        if positions == "all":
            nx, ny = self._lattice_size
            positions = [(i, j) for i in range(nx) for j in range(ny)]
        elif positions == "corners":
            nx, ny = self._lattice_size
            positions = [(0, 0), (0, ny-1), (nx-1, 0), (nx-1, ny-1)]

        for pos in positions:
            self._validate_position(pos)
            self._pins[pos] = pin

    def _validate_position(self, pos: Tuple[int, int]):
        """Validate that position is within lattice."""
        i, j = pos
        nx, ny = self._lattice_size
        if not (0 <= i < nx and 0 <= j < ny):
            raise ValidationError(
                f"Position {pos} outside lattice bounds (0, 0) to ({nx-1}, {ny-1})"
            )

    def get_pin(self, position: Tuple[int, int]) -> Optional[Union[PinCell, str]]:
        """
        Get pin at a specific position.

        Parameters
        ----------
        position : Tuple[int, int]
            Position (i, j)

        Returns
        -------
        PinCell or str or None
            Pin at the position, or None if not set
        """
        return self._pins.get(position, self._default_pin)

    def validate(self) -> bool:
        """Validate assembly configuration."""
        if self._default_pin is None and len(self._pins) == 0:
            raise ValidationError(
                f"Assembly '{self.name}' has no pins defined"
            )

        return True

    def to_tripoli5(self):
        """Convert to Tripoli-5 geometry."""
        pass

    def __repr__(self) -> str:
        """String representation."""
        nx, ny = self._lattice_size
        return (
            f"Assembly(name='{self.name}', lattice={nx}x{ny}, "
            f"pitch={self._pitch})"
        )


class Colorset(Geometry):
    """
    Class representing a colorset (group of assemblies).

    A colorset is a collection of assemblies arranged in a pattern,
    useful for loading pattern analysis.
    """

    def __init__(
        self,
        name: str,
        layout: Tuple[int, int],
        **kwargs
    ):
        """
        Initialize a Colorset.

        Parameters
        ----------
        name : str
            Name of the colorset
        layout : Tuple[int, int]
            Layout dimensions (nx, ny) for assembly positions
        **kwargs
            Additional keyword arguments
        """
        super().__init__(name, **kwargs)
        self._layout = self._validate_layout(layout)
        self._assemblies: Dict[Tuple[int, int], Assembly] = {}

    @property
    def layout(self) -> Tuple[int, int]:
        """Get colorset layout."""
        return self._layout

    @staticmethod
    def _validate_layout(layout: Tuple[int, int]) -> Tuple[int, int]:
        """Validate layout."""
        if len(layout) != 2:
            raise ValidationError("Layout must be a tuple of 2 integers")

        nx, ny = layout
        if nx <= 0 or ny <= 0:
            raise ValidationError("Layout dimensions must be positive")

        return (nx, ny)

    def add_assembly(self, assembly: Assembly, position: Tuple[int, int]):
        """
        Add an assembly at a specific position.

        Parameters
        ----------
        assembly : Assembly
            Assembly to add
        position : Tuple[int, int]
            Position (i, j) in the colorset
        """
        self._validate_position(position)
        self._assemblies[position] = assembly

    def _validate_position(self, pos: Tuple[int, int]):
        """Validate position within layout."""
        i, j = pos
        nx, ny = self._layout
        if not (0 <= i < nx and 0 <= j < ny):
            raise ValidationError(
                f"Position {pos} outside layout bounds (0, 0) to ({nx-1}, {ny-1})"
            )

    def get_assembly(self, position: Tuple[int, int]) -> Optional[Assembly]:
        """Get assembly at position."""
        return self._assemblies.get(position)

    def validate(self) -> bool:
        """Validate colorset configuration."""
        if len(self._assemblies) == 0:
            raise ValidationError(f"Colorset '{self.name}' has no assemblies")

        for assembly in self._assemblies.values():
            assembly.validate()

        return True

    def to_tripoli5(self):
        """Convert to Tripoli-5 geometry."""
        pass

    def __repr__(self) -> str:
        """String representation."""
        nx, ny = self._layout
        return f"Colorset(name='{self.name}', layout={nx}x{ny})"


class Core(Geometry):
    """
    Class representing a reactor core.

    A core consists of multiple assemblies arranged in a pattern
    with optional reflector regions.
    """

    def __init__(
        self,
        name: str,
        core_layout: Tuple[int, int],
        active_height: float,
        **kwargs
    ):
        """
        Initialize a Core.

        Parameters
        ----------
        name : str
            Name of the core
        core_layout : Tuple[int, int]
            Core layout dimensions (nx, ny)
        active_height : float
            Active core height (cm)
        **kwargs
            Additional keyword arguments
        """
        super().__init__(name, **kwargs)
        self._core_layout = self._validate_layout(core_layout)
        self._active_height = Validator.validate_positive(active_height, "active_height")
        self._assemblies: Dict[Tuple[int, int], Assembly] = {}
        self._reflector: Optional['Reflector'] = None

    @property
    def core_layout(self) -> Tuple[int, int]:
        """Get core layout."""
        return self._core_layout

    @property
    def active_height(self) -> float:
        """Get active core height."""
        return self._active_height

    @staticmethod
    def _validate_layout(layout: Tuple[int, int]) -> Tuple[int, int]:
        """Validate layout."""
        if len(layout) != 2:
            raise ValidationError("Layout must be a tuple of 2 integers")

        nx, ny = layout
        if nx <= 0 or ny <= 0:
            raise ValidationError("Layout dimensions must be positive")

        return (nx, ny)

    def add_assembly(self, assembly: Assembly, position: Tuple[int, int]):
        """Add assembly to core."""
        self._validate_position(position)
        self._assemblies[position] = assembly

    def _validate_position(self, pos: Tuple[int, int]):
        """Validate position within core."""
        i, j = pos
        nx, ny = self._core_layout
        if not (0 <= i < nx and 0 <= j < ny):
            raise ValidationError(
                f"Position {pos} outside core bounds (0, 0) to ({nx-1}, {ny-1})"
            )

    def set_reflector(self, reflector: 'Reflector'):
        """Set core reflector."""
        self._reflector = reflector

    def validate(self) -> bool:
        """Validate core configuration."""
        if len(self._assemblies) == 0:
            raise ValidationError(f"Core '{self.name}' has no assemblies")

        for assembly in self._assemblies.values():
            assembly.validate()

        if self._reflector:
            self._reflector.validate()

        return True

    def to_tripoli5(self):
        """Convert to Tripoli-5 geometry."""
        pass

    def __repr__(self) -> str:
        """String representation."""
        nx, ny = self._core_layout
        return (
            f"Core(name='{self.name}', layout={nx}x{ny}, "
            f"height={self._active_height})"
        )


class Reflector(Geometry):
    """
    Class representing a reflector region.

    A reflector surrounds the active core and can be made of
    various materials (water, steel, etc.).
    """

    def __init__(
        self,
        name: str,
        thickness: float,
        material: Material,
        **kwargs
    ):
        """
        Initialize a Reflector.

        Parameters
        ----------
        name : str
            Name of the reflector
        thickness : float
            Reflector thickness (cm)
        material : Material
            Reflector material
        **kwargs
            Additional keyword arguments
        """
        super().__init__(name, **kwargs)
        self._thickness = Validator.validate_positive(thickness, "thickness")
        self._material = material

    @property
    def thickness(self) -> float:
        """Get reflector thickness."""
        return self._thickness

    @property
    def material(self) -> Material:
        """Get reflector material."""
        return self._material

    def validate(self) -> bool:
        """Validate reflector configuration."""
        if self._material is None:
            raise ValidationError(f"Reflector '{self.name}' has no material")

        self._material.validate()
        return True

    def to_tripoli5(self):
        """Convert to Tripoli-5 geometry."""
        pass

    def __repr__(self) -> str:
        """String representation."""
        return (
            f"Reflector(name='{self.name}', thickness={self._thickness}, "
            f"material='{self._material.name}')"
        )
