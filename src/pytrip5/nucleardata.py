"""
Nuclear data module for pytrip5 package.

This module handles nuclear data including cross-sections and decay data.
"""

from typing import Optional, List, Dict
from pathlib import Path
from .core import PyTrip5Object, ValidationError, ConfigurationError


class NuclearData(PyTrip5Object):
    """
    Class for managing nuclear data (cross-sections, decay data).

    This class provides an interface to nuclear data libraries required
    for Tripoli-5 calculations.
    """

    def __init__(
        self,
        name: str,
        cross_section_file: Optional[str] = None,
        decay_data_file: Optional[str] = None,
        **kwargs
    ):
        """
        Initialize NuclearData.

        Parameters
        ----------
        name : str
            Name of the nuclear data set
        cross_section_file : str, optional
            Path to cross-section data file
        decay_data_file : str, optional
            Path to decay data file
        **kwargs
            Additional keyword arguments
        """
        super().__init__(name, **kwargs)
        self._cross_section_file = cross_section_file
        self._decay_data_file = decay_data_file
        self._temperature_interpolation = True
        self._energy_groups: Optional[List[float]] = None

    @property
    def cross_section_file(self) -> Optional[str]:
        """Get the cross-section file path."""
        return self._cross_section_file

    @cross_section_file.setter
    def cross_section_file(self, value: str):
        """Set the cross-section file path."""
        self._validate_file_path(value, "Cross-section")
        self._cross_section_file = value

    @property
    def decay_data_file(self) -> Optional[str]:
        """Get the decay data file path."""
        return self._decay_data_file

    @decay_data_file.setter
    def decay_data_file(self, value: str):
        """Set the decay data file path."""
        self._validate_file_path(value, "Decay data")
        self._decay_data_file = value

    @staticmethod
    def _validate_file_path(file_path: str, file_type: str):
        """
        Validate that a file path exists.

        Parameters
        ----------
        file_path : str
            File path to validate
        file_type : str
            Type of file for error messages

        Raises
        ------
        ValidationError
            If file doesn't exist or is invalid
        """
        if not file_path:
            return
        path = Path(file_path)
        if not path.exists():
            raise ValidationError(f"{file_type} file not found: {file_path}")
        if not path.is_file():
            raise ValidationError(f"{file_type} path is not a file: {file_path}")

    def set_temperature_interpolation(self, enabled: bool):
        """
        Enable or disable temperature interpolation.

        Parameters
        ----------
        enabled : bool
            Whether to enable temperature interpolation
        """
        self._temperature_interpolation = enabled

    def set_energy_groups(self, energy_bounds: List[float]):
        """
        Set custom energy group structure.

        Parameters
        ----------
        energy_bounds : List[float]
            Energy group boundaries in eV (must be monotonically increasing)

        Raises
        ------
        ValidationError
            If energy bounds are invalid
        """
        if not energy_bounds:
            raise ValidationError("Energy bounds cannot be empty")

        # Check monotonicity
        for i in range(len(energy_bounds) - 1):
            if energy_bounds[i] >= energy_bounds[i + 1]:
                raise ValidationError(
                    "Energy bounds must be monotonically increasing"
                )

        self._energy_groups = energy_bounds

    def validate(self) -> bool:
        """
        Validate the nuclear data configuration.

        Returns
        -------
        bool
            True if valid

        Raises
        ------
        ValidationError
            If configuration is invalid
        """
        if not self._cross_section_file:
            raise ValidationError(
                f"Nuclear data '{self.name}' must have a cross-section file"
            )

        # Validate files exist
        if self._cross_section_file:
            self._validate_file_path(self._cross_section_file, "Cross-section")

        if self._decay_data_file:
            self._validate_file_path(self._decay_data_file, "Decay data")

        return True

    def to_tripoli5(self):
        """
        Convert to Tripoli-5 nuclear data object.

        Returns
        -------
        object
            Tripoli-5 nuclear data object

        Raises
        ------
        ConfigurationError
            If Tripoli-5 is not available
        """
        try:
            # This is a placeholder for actual Tripoli-5 API integration
            # When Tripoli-5 is available, this would use the actual API
            # Example: import tripoli5; return tripoli5.NuclearData(...)
            pass
        except ImportError:
            raise ConfigurationError(
                "Tripoli-5 is not installed. Cannot create Tripoli-5 objects."
            )

    def __repr__(self) -> str:
        """String representation."""
        return (
            f"NuclearData(name='{self.name}', "
            f"cross_sections='{self._cross_section_file}')"
        )


class CrossSectionLibrary:
    """
    Class for managing multiple nuclear data libraries.

    This class provides a registry of available nuclear data sets.
    """

    def __init__(self):
        """Initialize CrossSectionLibrary."""
        self._libraries: Dict[str, NuclearData] = {}
        self._default_library: Optional[str] = None

    def add_library(self, nuclear_data: NuclearData):
        """
        Add a nuclear data library to the registry.

        Parameters
        ----------
        nuclear_data : NuclearData
            Nuclear data object to add
        """
        self._libraries[nuclear_data.name] = nuclear_data

        # Set as default if it's the first one
        if self._default_library is None:
            self._default_library = nuclear_data.name

    def get_library(self, name: Optional[str] = None) -> NuclearData:
        """
        Get a nuclear data library by name.

        Parameters
        ----------
        name : str, optional
            Name of the library. If None, returns default library.

        Returns
        -------
        NuclearData
            Nuclear data object

        Raises
        ------
        KeyError
            If library not found
        """
        if name is None:
            if self._default_library is None:
                raise KeyError("No default library set")
            name = self._default_library

        if name not in self._libraries:
            raise KeyError(f"Nuclear data library '{name}' not found")

        return self._libraries[name]

    def set_default(self, name: str):
        """
        Set the default nuclear data library.

        Parameters
        ----------
        name : str
            Name of the library to set as default

        Raises
        ------
        KeyError
            If library not found
        """
        if name not in self._libraries:
            raise KeyError(f"Nuclear data library '{name}' not found")
        self._default_library = name

    def list_libraries(self) -> List[str]:
        """
        Get list of available library names.

        Returns
        -------
        List[str]
            List of library names
        """
        return list(self._libraries.keys())

    def __repr__(self) -> str:
        """String representation."""
        return (
            f"CrossSectionLibrary(libraries={self.list_libraries()}, "
            f"default='{self._default_library}')"
        )
