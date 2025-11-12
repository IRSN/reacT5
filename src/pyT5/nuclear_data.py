"""Nuclear data handling module for pyT5.

This module provides classes for managing nuclear data including
cross-sections and decay data required for Tripoli-5 simulations.
"""

from pathlib import Path
from typing import Dict, List, Optional, Union


class NuclearData:
    """Handles nuclear data for Tripoli-5 simulations.

    This class manages cross-section libraries and decay data files
    required for Monte-Carlo neutron transport calculations.

    Attributes:
        cross_section_library: Path to the cross-section library file.
        decay_data_library: Path to the decay data library file (optional).
        temperature: Reference temperature for cross-sections in Kelvin.
        data_format: Format of the nuclear data files.

    Examples:
        >>> nuclear_data = NuclearData(
        ...     cross_section_library="path/to/xsections.dat",
        ...     temperature=300.0
        ... )
        >>> nuclear_data.validate()
    """

    def __init__(
        self,
        cross_section_library: Union[str, Path],
        decay_data_library: Optional[Union[str, Path]] = None,
        temperature: float = 300.0,
        data_format: str = "ENDF",
    ) -> None:
        """Initialize NuclearData object.

        Args:
            cross_section_library: Path to the cross-section library file.
            decay_data_library: Path to the decay data library file (optional).
            temperature: Reference temperature for cross-sections in Kelvin.
                Defaults to 300.0 K.
            data_format: Format of the nuclear data files. Defaults to "ENDF".

        Raises:
            ValueError: If temperature is negative or invalid format specified.
        """
        if temperature < 0:
            raise ValueError(f"Temperature must be non-negative, got {temperature}")

        self.cross_section_library = Path(cross_section_library)
        self.decay_data_library = (
            Path(decay_data_library) if decay_data_library else None
        )
        self.temperature = temperature
        self.data_format = data_format
        self._validated = False

    def validate(self) -> bool:
        """Validate that nuclear data files exist and are accessible.

        Returns:
            True if validation successful, False otherwise.

        Raises:
            FileNotFoundError: If required data files are not found.
        """
        if not self.cross_section_library.exists():
            raise FileNotFoundError(
                f"Cross-section library not found: {self.cross_section_library}"
            )

        if self.decay_data_library and not self.decay_data_library.exists():
            raise FileNotFoundError(
                f"Decay data library not found: {self.decay_data_library}"
            )

        self._validated = True
        return True

    def get_available_nuclides(self) -> List[str]:
        """Get list of available nuclides in the cross-section library.

        Returns:
            List of nuclide identifiers available in the library.

        Raises:
            RuntimeError: If nuclear data has not been validated.
        """
        if not self._validated:
            raise RuntimeError("Nuclear data must be validated before use")

        # Placeholder implementation - would parse actual library file
        return []

    def set_temperature(self, temperature: float) -> None:
        """Set the reference temperature for cross-sections.

        Args:
            temperature: Temperature in Kelvin.

        Raises:
            ValueError: If temperature is negative.
        """
        if temperature < 0:
            raise ValueError(f"Temperature must be non-negative, got {temperature}")
        self.temperature = temperature

    def __repr__(self) -> str:
        """Return string representation of NuclearData object."""
        return (
            f"NuclearData(cross_section_library={self.cross_section_library}, "
            f"temperature={self.temperature} K, format={self.data_format})"
        )
