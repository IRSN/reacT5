"""Material definition module for pyT5.

This module provides classes for defining materials used in
Tripoli-5 simulations, including their composition and properties.
"""

from typing import Dict, List, Optional, Union
import numpy as np


class Material:
    """Represents a material with its composition and physical properties.

    This class defines a material by its nuclide composition, density,
    temperature, and other physical properties needed for neutron
    transport calculations.

    Attributes:
        name: Unique identifier for the material.
        nuclides: Dictionary mapping nuclide names to their concentrations.
        temperature: Material temperature in Kelvin.
        density: Material density in g/cm³ (optional).
        state: Physical state ('solid', 'liquid', 'gas').

    Examples:
        >>> water = Material(
        ...     name="light_water",
        ...     nuclides={"H1": 2.0, "O16": 1.0},
        ...     temperature=300.0,
        ...     density=1.0,
        ...     state="liquid"
        ... )
        >>> water.normalize_concentrations()
    """

    def __init__(
        self,
        name: str,
        nuclides: Dict[str, float],
        temperature: float = 300.0,
        density: Optional[float] = None,
        state: str = "solid",
    ) -> None:
        """Initialize Material object.

        Args:
            name: Unique identifier for the material.
            nuclides: Dictionary mapping nuclide names to their atomic or
                mass concentrations.
            temperature: Material temperature in Kelvin. Defaults to 300.0 K.
            density: Material density in g/cm³. If None, will be calculated
                from composition.
            state: Physical state of the material. One of 'solid', 'liquid',
                or 'gas'. Defaults to 'solid'.

        Raises:
            ValueError: If temperature is negative, nuclides dict is empty,
                or invalid state specified.
        """
        if temperature < 0:
            raise ValueError(f"Temperature must be non-negative, got {temperature}")
        if not nuclides:
            raise ValueError("Material must contain at least one nuclide")
        if state not in ("solid", "liquid", "gas"):
            raise ValueError(f"Invalid state '{state}', must be solid, liquid, or gas")

        self.name = name
        self.nuclides = nuclides.copy()
        self.temperature = temperature
        self.density = density
        self.state = state

    def normalize_concentrations(self) -> None:
        """Normalize nuclide concentrations to sum to 1.0."""
        total = sum(self.nuclides.values())
        if total > 0:
            self.nuclides = {k: v / total for k, v in self.nuclides.items()}

    def add_nuclide(self, nuclide: str, concentration: float) -> None:
        """Add or update a nuclide in the material composition.

        Args:
            nuclide: Nuclide identifier (e.g., 'U235', 'Pu239').
            concentration: Atomic or mass concentration.

        Raises:
            ValueError: If concentration is negative.
        """
        if concentration < 0:
            raise ValueError(f"Concentration must be non-negative, got {concentration}")
        self.nuclides[nuclide] = concentration

    def remove_nuclide(self, nuclide: str) -> None:
        """Remove a nuclide from the material composition.

        Args:
            nuclide: Nuclide identifier to remove.

        Raises:
            KeyError: If nuclide not found in material.
        """
        if nuclide not in self.nuclides:
            raise KeyError(f"Nuclide '{nuclide}' not found in material '{self.name}'")
        del self.nuclides[nuclide]

    def get_concentration(self, nuclide: str) -> float:
        """Get the concentration of a specific nuclide.

        Args:
            nuclide: Nuclide identifier.

        Returns:
            Concentration of the nuclide.

        Raises:
            KeyError: If nuclide not found in material.
        """
        if nuclide not in self.nuclides:
            raise KeyError(f"Nuclide '{nuclide}' not found in material '{self.name}'")
        return self.nuclides[nuclide]

    def set_temperature(self, temperature: float) -> None:
        """Set the material temperature.

        Args:
            temperature: Temperature in Kelvin.

        Raises:
            ValueError: If temperature is negative.
        """
        if temperature < 0:
            raise ValueError(f"Temperature must be non-negative, got {temperature}")
        self.temperature = temperature

    def set_density(self, density: float) -> None:
        """Set the material density.

        Args:
            density: Density in g/cm³.

        Raises:
            ValueError: If density is negative.
        """
        if density < 0:
            raise ValueError(f"Density must be non-negative, got {density}")
        self.density = density

    def __repr__(self) -> str:
        """Return string representation of Material object."""
        nuclide_list = ", ".join(f"{k}: {v}" for k, v in list(self.nuclides.items())[:3])
        if len(self.nuclides) > 3:
            nuclide_list += ", ..."
        return (
            f"Material(name='{self.name}', nuclides={{{nuclide_list}}}, "
            f"T={self.temperature} K, density={self.density} g/cm³)"
        )


class MaterialLibrary:
    """Collection of materials for a simulation.

    This class manages a library of materials that can be referenced
    by cells in the geometry definition.

    Attributes:
        materials: Dictionary mapping material names to Material objects.

    Examples:
        >>> library = MaterialLibrary()
        >>> library.add_material(water)
        >>> library.add_material(fuel)
        >>> mat = library.get_material("light_water")
    """

    def __init__(self) -> None:
        """Initialize empty MaterialLibrary."""
        self.materials: Dict[str, Material] = {}

    def add_material(self, material: Material) -> None:
        """Add a material to the library.

        Args:
            material: Material object to add.

        Raises:
            ValueError: If material with same name already exists.
        """
        if material.name in self.materials:
            raise ValueError(f"Material '{material.name}' already exists in library")
        self.materials[material.name] = material

    def remove_material(self, name: str) -> None:
        """Remove a material from the library.

        Args:
            name: Name of the material to remove.

        Raises:
            KeyError: If material not found in library.
        """
        if name not in self.materials:
            raise KeyError(f"Material '{name}' not found in library")
        del self.materials[name]

    def get_material(self, name: str) -> Material:
        """Retrieve a material from the library.

        Args:
            name: Name of the material to retrieve.

        Returns:
            Material object.

        Raises:
            KeyError: If material not found in library.
        """
        if name not in self.materials:
            raise KeyError(f"Material '{name}' not found in library")
        return self.materials[name]

    def list_materials(self) -> List[str]:
        """Get list of all material names in the library.

        Returns:
            List of material names.
        """
        return list(self.materials.keys())

    def __len__(self) -> int:
        """Return number of materials in the library."""
        return len(self.materials)

    def __repr__(self) -> str:
        """Return string representation of MaterialLibrary object."""
        return f"MaterialLibrary(materials={len(self.materials)})"
