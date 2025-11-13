"""
Materials module for pytrip5 package.

This module handles material definitions including nuclide compositions,
temperatures, and densities.
"""

from typing import Dict, Optional, List, Union
from .core import PyTrip5Object, ValidationError, Validator


class Material(PyTrip5Object):
    """
    Class representing a material with nuclide composition.

    A material consists of one or more nuclides with specified concentrations
    and physical properties such as temperature and density.
    """

    def __init__(
        self,
        name: str,
        temperature: float = 300.0,
        density: Optional[float] = None,
        density_unit: str = "g/cm3",
        **kwargs
    ):
        """
        Initialize a Material.

        Parameters
        ----------
        name : str
            Name of the material
        temperature : float
            Temperature in Kelvin (default: 300.0 K)
        density : float, optional
            Material density
        density_unit : str
            Unit for density ('g/cm3', 'atoms/barn-cm', or 'kg/m3')
        **kwargs
            Additional keyword arguments
        """
        super().__init__(name, **kwargs)
        self._temperature = Validator.validate_temperature(temperature)
        self._density = density
        self._density_unit = self._validate_density_unit(density_unit)
        self._nuclides: Dict[str, float] = {}
        self._is_void = False

    @property
    def temperature(self) -> float:
        """Get material temperature in Kelvin."""
        return self._temperature

    @temperature.setter
    def temperature(self, value: float):
        """Set material temperature."""
        self._temperature = Validator.validate_temperature(value)

    @property
    def density(self) -> Optional[float]:
        """Get material density."""
        return self._density

    @density.setter
    def density(self, value: float):
        """Set material density."""
        self._density = Validator.validate_positive(value, "Density")

    @property
    def density_unit(self) -> str:
        """Get density unit."""
        return self._density_unit

    @property
    def nuclides(self) -> Dict[str, float]:
        """Get dictionary of nuclides and their concentrations."""
        return self._nuclides.copy()

    @staticmethod
    def _validate_density_unit(unit: str) -> str:
        """
        Validate density unit.

        Parameters
        ----------
        unit : str
            Density unit string

        Returns
        -------
        str
            Validated unit

        Raises
        ------
        ValidationError
            If unit is invalid
        """
        valid_units = ['g/cm3', 'atoms/barn-cm', 'kg/m3']
        if unit not in valid_units:
            raise ValidationError(
                f"Invalid density unit '{unit}'. Must be one of {valid_units}"
            )
        return unit

    def add_nuclide(self, nuclide: str, concentration: float):
        """
        Add a nuclide to the material.

        Parameters
        ----------
        nuclide : str
            Nuclide name (e.g., 'U235', 'H1', 'O16')
        concentration : float
            Nuclide concentration (atomic fraction or number density)

        Raises
        ------
        ValidationError
            If concentration is invalid
        """
        if concentration < 0:
            raise ValidationError(
                f"Nuclide concentration must be non-negative, got {concentration}"
            )

        if not nuclide:
            raise ValidationError("Nuclide name cannot be empty")

        self._nuclides[nuclide] = concentration

    def remove_nuclide(self, nuclide: str):
        """
        Remove a nuclide from the material.

        Parameters
        ----------
        nuclide : str
            Nuclide name to remove

        Raises
        ------
        KeyError
            If nuclide not found in material
        """
        if nuclide not in self._nuclides:
            raise KeyError(f"Nuclide '{nuclide}' not found in material '{self.name}'")
        del self._nuclides[nuclide]

    def get_concentration(self, nuclide: str) -> float:
        """
        Get concentration of a specific nuclide.

        Parameters
        ----------
        nuclide : str
            Nuclide name

        Returns
        -------
        float
            Nuclide concentration

        Raises
        ------
        KeyError
            If nuclide not found
        """
        if nuclide not in self._nuclides:
            raise KeyError(f"Nuclide '{nuclide}' not found in material '{self.name}'")
        return self._nuclides[nuclide]

    def normalize_concentrations(self):
        """
        Normalize nuclide concentrations to sum to 1.0.

        This is useful when working with atomic fractions.
        """
        total = sum(self._nuclides.values())
        if total == 0:
            raise ValidationError("Cannot normalize: total concentration is zero")

        self._nuclides = {
            nuclide: conc / total
            for nuclide, conc in self._nuclides.items()
        }

    def scale_concentrations(self, factor: float):
        """
        Scale all nuclide concentrations by a factor.

        Parameters
        ----------
        factor : float
            Scaling factor

        Raises
        ------
        ValidationError
            If factor is not positive
        """
        if factor <= 0:
            raise ValidationError(f"Scaling factor must be positive, got {factor}")

        self._nuclides = {
            nuclide: conc * factor
            for nuclide, conc in self._nuclides.items()
        }

    def set_void(self):
        """Set material as void (no nuclides)."""
        self._is_void = True
        self._nuclides = {}
        self._density = 0.0

    def is_void(self) -> bool:
        """
        Check if material is void.

        Returns
        -------
        bool
            True if material is void
        """
        return self._is_void or len(self._nuclides) == 0

    def validate(self) -> bool:
        """
        Validate the material configuration.

        Returns
        -------
        bool
            True if valid

        Raises
        ------
        ValidationError
            If configuration is invalid
        """
        if not self._is_void and len(self._nuclides) == 0:
            raise ValidationError(
                f"Material '{self.name}' has no nuclides defined"
            )

        # Check temperature is reasonable
        Validator.validate_temperature(self._temperature)

        return True

    def to_tripoli5(self):
        """
        Convert to Tripoli-5 material object.

        Returns
        -------
        object
            Tripoli-5 material object
        """
        # Placeholder for actual Tripoli-5 API integration
        # Example: import tripoli5; return tripoli5.Material(...)
        pass

    def __repr__(self) -> str:
        """String representation."""
        n_nuclides = len(self._nuclides)
        return (
            f"Material(name='{self.name}', T={self._temperature}K, "
            f"nuclides={n_nuclides})"
        )


class MaterialLibrary:
    """
    Class for managing a library of materials.

    This provides a registry of predefined materials that can be reused.
    """

    def __init__(self):
        """Initialize MaterialLibrary."""
        self._materials: Dict[str, Material] = {}

    def add_material(self, material: Material):
        """
        Add a material to the library.

        Parameters
        ----------
        material : Material
            Material to add
        """
        self._materials[material.name] = material

    def get_material(self, name: str) -> Material:
        """
        Get a material from the library.

        Parameters
        ----------
        name : str
            Material name

        Returns
        -------
        Material
            Material object

        Raises
        ------
        KeyError
            If material not found
        """
        if name not in self._materials:
            raise KeyError(f"Material '{name}' not found in library")
        return self._materials[name]

    def remove_material(self, name: str):
        """
        Remove a material from the library.

        Parameters
        ----------
        name : str
            Material name to remove
        """
        if name not in self._materials:
            raise KeyError(f"Material '{name}' not found in library")
        del self._materials[name]

    def list_materials(self) -> List[str]:
        """
        Get list of available materials.

        Returns
        -------
        List[str]
            List of material names
        """
        return list(self._materials.keys())

    def __contains__(self, name: str) -> bool:
        """Check if a material exists in the library."""
        return name in self._materials

    def __repr__(self) -> str:
        """String representation."""
        return f"MaterialLibrary(materials={self.list_materials()})"


# Predefined common materials
def create_water(temperature: float = 600.0, name: str = "H2O") -> Material:
    """
    Create a water material.

    Parameters
    ----------
    temperature : float
        Temperature in Kelvin
    name : str
        Material name

    Returns
    -------
    Material
        Water material
    """
    water = Material(name, temperature=temperature, density=0.7)
    water.add_nuclide("H1", 2.0)
    water.add_nuclide("O16", 1.0)
    return water


def create_uo2_fuel(enrichment: float = 4.0, temperature: float = 900.0,
                    name: str = "UO2") -> Material:
    """
    Create a UO2 fuel material.

    Parameters
    ----------
    enrichment : float
        U-235 enrichment in percent
    temperature : float
        Temperature in Kelvin
    name : str
        Material name

    Returns
    -------
    Material
        UO2 fuel material
    """
    if not 0 < enrichment <= 20:
        raise ValidationError(
            f"Enrichment must be between 0 and 20%, got {enrichment}"
        )

    fuel = Material(name, temperature=temperature, density=10.5)
    u235_frac = enrichment / 100.0
    u238_frac = 1.0 - u235_frac

    fuel.add_nuclide("U235", u235_frac)
    fuel.add_nuclide("U238", u238_frac)
    fuel.add_nuclide("O16", 2.0)

    return fuel


def create_zircaloy(temperature: float = 600.0, name: str = "Zircaloy") -> Material:
    """
    Create a Zircaloy cladding material.

    Parameters
    ----------
    temperature : float
        Temperature in Kelvin
    name : str
        Material name

    Returns
    -------
    Material
        Zircaloy material
    """
    zr = Material(name, temperature=temperature, density=6.5)
    zr.add_nuclide("Zr90", 0.5145)
    zr.add_nuclide("Zr91", 0.1122)
    zr.add_nuclide("Zr92", 0.1715)
    zr.add_nuclide("Zr94", 0.1738)
    zr.add_nuclide("Zr96", 0.0280)
    return zr
