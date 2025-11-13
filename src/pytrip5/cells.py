"""
Cells module for pytrip5 package.

This module defines geometric cells that contain materials.
"""

from typing import Optional, List
from .core import PyTrip5Object, ValidationError
from .materials import Material


class Cell(PyTrip5Object):
    """
    Class representing a geometric cell containing a material.

    A cell is a region of space filled with a specific material.
    Cells are the building blocks of geometry in Monte Carlo transport.
    """

    def __init__(
        self,
        name: str,
        material: Optional[Material] = None,
        importance: float = 1.0,
        **kwargs
    ):
        """
        Initialize a Cell.

        Parameters
        ----------
        name : str
            Name of the cell
        material : Material, optional
            Material filling the cell
        importance : float
            Importance for variance reduction (default: 1.0)
        **kwargs
            Additional keyword arguments
        """
        super().__init__(name, **kwargs)
        self._material = material
        self._importance = self._validate_importance(importance)
        self._surfaces: List[str] = []
        self._volume: Optional[float] = None

    @property
    def material(self) -> Optional[Material]:
        """Get the cell material."""
        return self._material

    @material.setter
    def material(self, value: Material):
        """Set the cell material."""
        if value is not None and not isinstance(value, Material):
            raise ValidationError("Cell material must be a Material object")
        self._material = value

    @property
    def importance(self) -> float:
        """Get the cell importance."""
        return self._importance

    @importance.setter
    def importance(self, value: float):
        """Set the cell importance."""
        self._importance = self._validate_importance(value)

    @property
    def volume(self) -> Optional[float]:
        """Get the cell volume."""
        return self._volume

    @volume.setter
    def volume(self, value: float):
        """Set the cell volume."""
        if value <= 0:
            raise ValidationError(f"Cell volume must be positive, got {value}")
        self._volume = value

    @staticmethod
    def _validate_importance(importance: float) -> float:
        """
        Validate importance value.

        Parameters
        ----------
        importance : float
            Importance value

        Returns
        -------
        float
            Validated importance

        Raises
        ------
        ValidationError
            If importance is invalid
        """
        if importance < 0:
            raise ValidationError(
                f"Importance must be non-negative, got {importance}"
            )
        return importance

    def is_void(self) -> bool:
        """
        Check if cell is void (no material).

        Returns
        -------
        bool
            True if cell is void
        """
        return self._material is None or self._material.is_void()

    def validate(self) -> bool:
        """
        Validate the cell configuration.

        Returns
        -------
        bool
            True if valid

        Raises
        ------
        ValidationError
            If configuration is invalid
        """
        if self._material is not None:
            self._material.validate()

        return True

    def to_tripoli5(self):
        """
        Convert to Tripoli-5 cell object.

        Returns
        -------
        object
            Tripoli-5 cell object
        """
        # Placeholder for actual Tripoli-5 API integration
        pass

    def __repr__(self) -> str:
        """String representation."""
        mat_name = self._material.name if self._material else "void"
        return f"Cell(name='{self.name}', material='{mat_name}')"


class CylindricalCell(Cell):
    """
    Cylindrical cell for pin-type geometries.

    This is a convenience class for creating cylindrical regions
    commonly used in fuel pin modeling.
    """

    def __init__(
        self,
        name: str,
        radius: float,
        height: Optional[float] = None,
        material: Optional[Material] = None,
        **kwargs
    ):
        """
        Initialize a CylindricalCell.

        Parameters
        ----------
        name : str
            Name of the cell
        radius : float
            Radius of the cylinder (cm)
        height : float, optional
            Height of the cylinder (cm). If None, infinite height.
        material : Material, optional
            Material filling the cell
        **kwargs
            Additional keyword arguments
        """
        super().__init__(name, material=material, **kwargs)
        self._radius = self._validate_radius(radius)
        self._height = height if height is None else self._validate_height(height)

        # Calculate volume if height is specified
        if self._height is not None:
            import math
            self._volume = math.pi * self._radius ** 2 * self._height

    @property
    def radius(self) -> float:
        """Get cylinder radius."""
        return self._radius

    @property
    def height(self) -> Optional[float]:
        """Get cylinder height."""
        return self._height

    @staticmethod
    def _validate_radius(radius: float) -> float:
        """Validate radius."""
        if radius <= 0:
            raise ValidationError(f"Radius must be positive, got {radius}")
        return radius

    @staticmethod
    def _validate_height(height: float) -> float:
        """Validate height."""
        if height <= 0:
            raise ValidationError(f"Height must be positive, got {height}")
        return height

    def __repr__(self) -> str:
        """String representation."""
        mat_name = self._material.name if self._material else "void"
        h_str = f", h={self._height}" if self._height else ""
        return (
            f"CylindricalCell(name='{self.name}', r={self._radius}{h_str}, "
            f"material='{mat_name}')"
        )


class RectangularCell(Cell):
    """
    Rectangular cell for assembly lattices.

    This is a convenience class for creating rectangular regions
    in assembly geometries.
    """

    def __init__(
        self,
        name: str,
        width: float,
        height: float,
        depth: Optional[float] = None,
        material: Optional[Material] = None,
        **kwargs
    ):
        """
        Initialize a RectangularCell.

        Parameters
        ----------
        name : str
            Name of the cell
        width : float
            Width in x-direction (cm)
        height : float
            Height in y-direction (cm)
        depth : float, optional
            Depth in z-direction (cm). If None, infinite depth.
        material : Material, optional
            Material filling the cell
        **kwargs
            Additional keyword arguments
        """
        super().__init__(name, material=material, **kwargs)
        self._width = self._validate_positive(width, "width")
        self._height = self._validate_positive(height, "height")
        self._depth = None if depth is None else self._validate_positive(depth, "depth")

        # Calculate volume if depth is specified
        if self._depth is not None:
            self._volume = self._width * self._height * self._depth

    @property
    def width(self) -> float:
        """Get cell width."""
        return self._width

    @property
    def height(self) -> float:
        """Get cell height."""
        return self._height

    @property
    def depth(self) -> Optional[float]:
        """Get cell depth."""
        return self._depth

    @staticmethod
    def _validate_positive(value: float, name: str) -> float:
        """Validate positive value."""
        if value <= 0:
            raise ValidationError(f"{name} must be positive, got {value}")
        return value

    def __repr__(self) -> str:
        """String representation."""
        mat_name = self._material.name if self._material else "void"
        d_str = f", d={self._depth}" if self._depth else ""
        return (
            f"RectangularCell(name='{self.name}', "
            f"w={self._width}, h={self._height}{d_str}, "
            f"material='{mat_name}')"
        )
