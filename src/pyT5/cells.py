"""Cell definition module for pyT5.

This module provides classes for defining cells that contain materials
and define regions in the geometry for Tripoli-5 simulations.
"""

from typing import Dict, List, Optional, Union
from .materials import Material


class Cell:
    """Represents a geometric cell containing a material.

    A cell is a region of space defined by boundary surfaces and filled
    with a specific material. Cells are the building blocks of geometry
    in Monte-Carlo simulations.

    Attributes:
        name: Unique identifier for the cell.
        material: Material filling the cell (None for void).
        volume: Cell volume in cm³ (optional).
        importance: Neutron importance for variance reduction.

    Examples:
        >>> fuel_cell = Cell(
        ...     name="fuel_pin",
        ...     material=uo2_material,
        ...     volume=100.0,
        ...     importance=1.0
        ... )
    """

    def __init__(
        self,
        name: str,
        material: Optional[Material] = None,
        volume: Optional[float] = None,
        importance: float = 1.0,
    ) -> None:
        """Initialize Cell object.

        Args:
            name: Unique identifier for the cell.
            material: Material object filling the cell. None represents void.
            volume: Cell volume in cm³. If None, will be calculated by
                Tripoli-5 during simulation.
            importance: Neutron importance for variance reduction. Values > 1
                increase sampling, < 1 decrease sampling. Defaults to 1.0.

        Raises:
            ValueError: If volume or importance is negative.
        """
        if volume is not None and volume < 0:
            raise ValueError(f"Volume must be non-negative, got {volume}")
        if importance < 0:
            raise ValueError(f"Importance must be non-negative, got {importance}")

        self.name = name
        self.material = material
        self.volume = volume
        self.importance = importance

    def set_material(self, material: Optional[Material]) -> None:
        """Set or update the material filling the cell.

        Args:
            material: Material object, or None for void.
        """
        self.material = material

    def set_volume(self, volume: float) -> None:
        """Set the cell volume.

        Args:
            volume: Volume in cm³.

        Raises:
            ValueError: If volume is negative.
        """
        if volume < 0:
            raise ValueError(f"Volume must be non-negative, got {volume}")
        self.volume = volume

    def set_importance(self, importance: float) -> None:
        """Set the neutron importance for variance reduction.

        Args:
            importance: Importance weight factor.

        Raises:
            ValueError: If importance is negative.
        """
        if importance < 0:
            raise ValueError(f"Importance must be non-negative, got {importance}")
        self.importance = importance

    def is_void(self) -> bool:
        """Check if the cell is void (contains no material).

        Returns:
            True if cell is void, False otherwise.
        """
        return self.material is None

    def __repr__(self) -> str:
        """Return string representation of Cell object."""
        material_name = self.material.name if self.material else "void"
        return (
            f"Cell(name='{self.name}', material='{material_name}', "
            f"volume={self.volume} cm³, importance={self.importance})"
        )


class CellLibrary:
    """Collection of cells for a simulation.

    This class manages a library of cells that can be used to build
    complex geometries in Tripoli-5 simulations.

    Attributes:
        cells: Dictionary mapping cell names to Cell objects.

    Examples:
        >>> library = CellLibrary()
        >>> library.add_cell(fuel_cell)
        >>> library.add_cell(clad_cell)
        >>> cell = library.get_cell("fuel_pin")
    """

    def __init__(self) -> None:
        """Initialize empty CellLibrary."""
        self.cells: Dict[str, Cell] = {}

    def add_cell(self, cell: Cell) -> None:
        """Add a cell to the library.

        Args:
            cell: Cell object to add.

        Raises:
            ValueError: If cell with same name already exists.
        """
        if cell.name in self.cells:
            raise ValueError(f"Cell '{cell.name}' already exists in library")
        self.cells[cell.name] = cell

    def remove_cell(self, name: str) -> None:
        """Remove a cell from the library.

        Args:
            name: Name of the cell to remove.

        Raises:
            KeyError: If cell not found in library.
        """
        if name not in self.cells:
            raise KeyError(f"Cell '{name}' not found in library")
        del self.cells[name]

    def get_cell(self, name: str) -> Cell:
        """Retrieve a cell from the library.

        Args:
            name: Name of the cell to retrieve.

        Returns:
            Cell object.

        Raises:
            KeyError: If cell not found in library.
        """
        if name not in self.cells:
            raise KeyError(f"Cell '{name}' not found in library")
        return self.cells[name]

    def list_cells(self) -> List[str]:
        """Get list of all cell names in the library.

        Returns:
            List of cell names.
        """
        return list(self.cells.keys())

    def get_cells_by_material(self, material_name: str) -> List[Cell]:
        """Get all cells containing a specific material.

        Args:
            material_name: Name of the material to search for.

        Returns:
            List of Cell objects containing the specified material.
        """
        return [
            cell
            for cell in self.cells.values()
            if cell.material and cell.material.name == material_name
        ]

    def get_void_cells(self) -> List[Cell]:
        """Get all void cells (cells with no material).

        Returns:
            List of void Cell objects.
        """
        return [cell for cell in self.cells.values() if cell.is_void()]

    def __len__(self) -> int:
        """Return number of cells in the library."""
        return len(self.cells)

    def __repr__(self) -> str:
        """Return string representation of CellLibrary object."""
        return f"CellLibrary(cells={len(self.cells)})"
