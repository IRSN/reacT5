"""
Materials module for pytrip5 - PyDrag-inspired simple interface.

This module provides a simplified, user-friendly interface for material definitions,
inspired by PyDrag's philosophy of simplicity.
"""

from typing import Optional, Dict
from .core import PyTrip5Object, ValidationError, Validator


class Materials:
    """
    Main materials manager with pre-defined common materials.

    Inspired by PyDrag's Materials() class for simplicity.

    Example:
        >>> materials = Materials(catalog_path="path/to/catalog.yaml")
        >>> materials.UO2.set_density(10.5)
        >>> materials.UO2.set_enrichment('U235', 0.04)
        >>> materials.water.set_temperature(600.0)
    """

    def __init__(self, catalog_path: Optional[str] = None):
        """
        Initialize Materials manager.

        Parameters
        ----------
        catalog_path : str, optional
            Path to Tripoli-5 nuclear data catalog (YAML file)
        """
        self._catalog_path = catalog_path
        self._catalog = None
        self._fuel_temperature = 900.0  # K

        # Pre-defined materials (PyDrag style)
        self.UO2 = Mix('UO2', temperature=900.0)
        self.water = Mix('water', temperature=600.0)
        self.Zr4 = Mix('Zircaloy-4', temperature=600.0)
        self.void = Mix('void', temperature=300.0)
        self.SS304 = Mix('SS304', temperature=600.0)
        self.Inconel = Mix('Inconel', temperature=600.0)
        self.AIC = Mix('AIC', temperature=600.0)  # Ag-In-Cd
        self.B4C = Mix('B4C', temperature=600.0)
        self.Pyrex = Mix('Pyrex', temperature=600.0)

        # Store custom materials
        self._custom_materials: Dict[str, 'Mix'] = {}

        # Initialize default compositions
        self._init_default_materials()

    def _init_default_materials(self):
        """Initialize default material compositions."""
        # UO2 defaults
        self.UO2.set_density(10.5)
        self.UO2._composition = {
            'U235': 0.04,
            'U238': 0.96,
            'O16': 2.0
        }

        # Water defaults
        self.water.set_density(0.7)
        self.water._composition = {
            'H1': 2.0,
            'O16': 1.0
        }

        # Zircaloy-4 defaults
        self.Zr4.set_density(6.5)
        self.Zr4._composition = {
            'Zr90': 0.5145,
            'Zr91': 0.1122,
            'Zr92': 0.1715,
            'Zr94': 0.1738,
            'Zr96': 0.0280
        }

        # Void (vacuum)
        self.void.set_density(0.0)
        self.void._composition = {}

    def set_tfuel(self, temperature: float, unit: str = 'K'):
        """
        Set fuel temperature (PyDrag compatibility).

        Parameters
        ----------
        temperature : float
            Temperature value
        unit : str
            Temperature unit: 'K' (Kelvin) or 'C' (Celsius)
        """
        if unit == 'C':
            temperature = temperature + 273.15
        self._fuel_temperature = Validator.validate_temperature(temperature)
        self.UO2.set_temperature(temperature)

    def make_mix(self, name: str, temperature: float = 300.0) -> 'Mix':
        """
        Create a custom material mix.

        Parameters
        ----------
        name : str
            Material name
        temperature : float
            Temperature in Kelvin

        Returns
        -------
        Mix
            New material mix
        """
        mix = Mix(name, temperature=temperature)
        self._custom_materials[name] = mix
        return mix

    def load_catalog(self, catalog_path: str):
        """
        Load Tripoli-5 nuclear data catalog.

        Parameters
        ----------
        catalog_path : str
            Path to catalog YAML file
        """
        self._catalog_path = catalog_path
        try:
            import tripoli5.delos
            self._catalog = tripoli5.delos.Catalog.fromFile(catalog_path)
        except ImportError:
            raise ValidationError(
                "Tripoli-5 not available. Cannot load catalog."
            )

    def to_tripoli5_materials(self) -> Dict[str, 'tripoli5.materials.Mixture']:
        """
        Convert all materials to Tripoli-5 Mixture objects.

        Returns
        -------
        Dict[str, Mixture]
            Dictionary of material name to Tripoli-5 Mixture
        """
        if self._catalog is None:
            raise ValidationError(
                "No catalog loaded. Call load_catalog() first."
            )

        materials = {}

        # Convert pre-defined materials
        for attr_name in dir(self):
            attr = getattr(self, attr_name)
            if isinstance(attr, Mix) and not attr.name.startswith('_'):
                materials[attr.name] = attr.to_tripoli5(self._catalog)

        # Convert custom materials
        for name, mix in self._custom_materials.items():
            materials[name] = mix.to_tripoli5(self._catalog)

        return materials


class Mix(PyTrip5Object):
    """
    Material mixture class (PyDrag-style).

    Provides simple setters for material properties.
    """

    def __init__(self, name: str, temperature: float = 300.0, **kwargs):
        """
        Initialize Mix.

        Parameters
        ----------
        name : str
            Material name
        temperature : float
            Temperature in Kelvin
        """
        super().__init__(name, **kwargs)
        self._temperature = Validator.validate_temperature(temperature)
        self._density: Optional[float] = None
        self._composition: Dict[str, float] = {}
        self._enrichment: Dict[str, float] = {}
        self._boron_ppm: float = 0.0
        self._pressure: Optional[float] = None

    def set_density(self, density: float):
        """
        Set material density (g/cm³).

        Parameters
        ----------
        density : float
            Density in g/cm³
        """
        self._density = Validator.validate_non_negative(density, "density")

    def set_temperature(self, temperature: float, unit: str = 'K'):
        """
        Set material temperature.

        Parameters
        ----------
        temperature : float
            Temperature value
        unit : str
            'K' for Kelvin or 'C' for Celsius
        """
        if unit == 'C':
            temperature = temperature + 273.15
        self._temperature = Validator.validate_temperature(temperature)

    def set_enrichment(self, isotope: str, fraction: float):
        """
        Set isotope enrichment (PyDrag style).

        Parameters
        ----------
        isotope : str
            Isotope name (e.g., 'U235', 'U238')
        fraction : float
            Atomic or weight fraction
        """
        self._enrichment[isotope] = fraction
        self._composition[isotope] = fraction

    def set_boron(self, ppm: float):
        """
        Set boron concentration in ppm (for water).

        Parameters
        ----------
        ppm : float
            Boron concentration in parts per million
        """
        self._boron_ppm = Validator.validate_non_negative(ppm, "boron ppm")

    def set_pressure(self, pressure: float):
        """
        Set pressure (bar).

        Parameters
        ----------
        pressure : float
            Pressure in bar
        """
        self._pressure = Validator.validate_positive(pressure, "pressure")

    def set_compo(self, isotope: str, concentration: float):
        """
        Set isotope composition/concentration.

        Parameters
        ----------
        isotope : str
            Isotope name
        concentration : float
            Atomic concentration
        """
        self._composition[isotope] = concentration

    def add_element(self, element: str, fraction: float):
        """
        Add element to composition.

        Parameters
        ----------
        element : str
            Element name or isotope
        fraction : float
            Atomic fraction
        """
        self._composition[element] = fraction

    @property
    def temperature(self) -> float:
        """Get temperature in Kelvin."""
        return self._temperature

    @property
    def density(self) -> Optional[float]:
        """Get density in g/cm³."""
        return self._density

    @property
    def composition(self) -> Dict[str, float]:
        """Get composition dictionary."""
        return self._composition.copy()

    def validate(self) -> bool:
        """Validate material configuration."""
        if self._density is None and self.name != 'void':
            raise ValidationError(f"Material '{self.name}' has no density set")

        if not self._composition and self.name != 'void':
            raise ValidationError(f"Material '{self.name}' has no composition")

        return True

    def to_tripoli5(self, catalog=None):
        """
        Convert to Tripoli-5 Mixture using MixtureBuilder.

        Parameters
        ----------
        catalog : tripoli5.delos.Catalog, optional
            Nuclear data catalog

        Returns
        -------
        tripoli5.materials.Mixture
            Tripoli-5 Mixture object
        """
        try:
            import tripoli5.materials
            from tripoli5.core.literals import K

            builder = (
                tripoli5.materials.MixtureBuilder("concentrations")
                .withName(self.name)
                .withTemperature(self._temperature * K)
            )

            if catalog is not None:
                builder = builder.withCatalog(catalog)

            # Add all isotopes/elements
            for isotope, conc in self._composition.items():
                builder = builder.add(isotope, conc)

            return builder.build()

        except ImportError:
            raise ValidationError(
                "Tripoli-5 not available. Cannot create Tripoli-5 materials."
            )

    def __repr__(self) -> str:
        """String representation."""
        return (
            f"Mix(name='{self.name}', T={self._temperature}K, "
            f"ρ={self._density}, n_isotopes={len(self._composition)})"
        )


# Convenience functions for creating common materials
def create_uo2(enrichment: float = 4.0, temperature: float = 900.0,
               density: float = 10.5, name: str = "UO2") -> Mix:
    """
    Create UO2 fuel material.

    Parameters
    ----------
    enrichment : float
        U-235 enrichment in percent (default: 4.0%)
    temperature : float
        Temperature in Kelvin (default: 900 K)
    density : float
        Density in g/cm³ (default: 10.5)
    name : str
        Material name

    Returns
    -------
    Mix
        UO2 material
    """
    if not 0 < enrichment <= 20:
        raise ValidationError(f"Enrichment must be 0-20%, got {enrichment}")

    fuel = Mix(name, temperature=temperature)
    fuel.set_density(density)

    u235_frac = enrichment / 100.0
    u238_frac = 1.0 - u235_frac

    fuel.set_enrichment('U234', 0.0002 * u235_frac)  # Natural U234
    fuel.set_enrichment('U235', u235_frac)
    fuel.set_enrichment('U238', u238_frac)
    fuel.set_enrichment('U236', 0.0001 * u235_frac)  # Trace U236
    fuel.add_element('O16', 2.0)

    return fuel


def create_water(temperature: float = 600.0, density: float = 0.7,
                 boron_ppm: float = 0.0, name: str = "H2O") -> Mix:
    """
    Create water material.

    Parameters
    ----------
    temperature : float
        Temperature in Kelvin
    density : float
        Density in g/cm³
    boron_ppm : float
        Boron concentration in ppm
    name : str
        Material name

    Returns
    -------
    Mix
        Water material
    """
    water = Mix(name, temperature=temperature)
    water.set_density(density)
    water.add_element('H1', 2.0)
    water.add_element('O16', 1.0)

    if boron_ppm > 0:
        water.set_boron(boron_ppm)
        # Add boron isotopes (simplified)
        b_fraction = boron_ppm * 1e-6
        water.add_element('B10', 0.199 * b_fraction)
        water.add_element('B11', 0.801 * b_fraction)

    return water


def create_zircaloy(temperature: float = 600.0, density: float = 6.5,
                    name: str = "Zircaloy-4") -> Mix:
    """
    Create Zircaloy-4 cladding material.

    Parameters
    ----------
    temperature : float
        Temperature in Kelvin
    density : float
        Density in g/cm³
    name : str
        Material name

    Returns
    -------
    Mix
        Zircaloy material
    """
    zr = Mix(name, temperature=temperature)
    zr.set_density(density)

    # Natural zirconium isotopic composition
    zr.add_element('Zr90', 0.5145)
    zr.add_element('Zr91', 0.1122)
    zr.add_element('Zr92', 0.1715)
    zr.add_element('Zr94', 0.1738)
    zr.add_element('Zr96', 0.0280)

    return zr
