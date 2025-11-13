"""
Core module for pytrip5 package.

This module provides base classes and utilities used throughout the package.
"""

from abc import ABC, abstractmethod
from typing import Dict, Any, Optional, List
import warnings


class PyTrip5Exception(Exception):
    """Base exception class for pytrip5 package."""
    pass


class ValidationError(PyTrip5Exception):
    """Exception raised when validation fails."""
    pass


class ConfigurationError(PyTrip5Exception):
    """Exception raised when configuration is invalid."""
    pass


class SimulationError(PyTrip5Exception):
    """Exception raised when simulation fails or encounters an error."""
    pass


class PyTrip5Object(ABC):
    """
    Abstract base class for all pytrip5 objects.

    Provides common functionality for naming, validation, and string representation.
    """

    def __init__(self, name: str, **kwargs):
        """
        Initialize a PyTrip5Object.

        Parameters
        ----------
        name : str
            Name of the object
        **kwargs
            Additional keyword arguments
        """
        self._name = self._validate_name(name)
        self._metadata: Dict[str, Any] = {}
        self._initialized = False

    @property
    def name(self) -> str:
        """Get the name of the object."""
        return self._name

    @name.setter
    def name(self, value: str):
        """Set the name of the object."""
        self._name = self._validate_name(value)

    @staticmethod
    def _validate_name(name: str) -> str:
        """
        Validate object name.

        Parameters
        ----------
        name : str
            Name to validate

        Returns
        -------
        str
            Validated name

        Raises
        ------
        ValidationError
            If name is invalid
        """
        if not isinstance(name, str):
            raise ValidationError(f"Name must be a string, got {type(name)}")
        if not name.strip():
            raise ValidationError("Name cannot be empty")
        if len(name) > 100:
            raise ValidationError("Name cannot exceed 100 characters")
        return name.strip()

    def add_metadata(self, key: str, value: Any):
        """
        Add metadata to the object.

        Parameters
        ----------
        key : str
            Metadata key
        value : Any
            Metadata value
        """
        self._metadata[key] = value

    def get_metadata(self, key: str, default: Any = None) -> Any:
        """
        Get metadata value.

        Parameters
        ----------
        key : str
            Metadata key
        default : Any, optional
            Default value if key not found

        Returns
        -------
        Any
            Metadata value
        """
        return self._metadata.get(key, default)

    @abstractmethod
    def validate(self) -> bool:
        """
        Validate the object configuration.

        Returns
        -------
        bool
            True if valid

        Raises
        ------
        ValidationError
            If validation fails
        """
        pass

    @abstractmethod
    def to_tripoli5(self):
        """
        Convert to Tripoli-5 object/representation.

        This method should be implemented by subclasses to provide
        conversion to native Tripoli-5 objects.
        """
        pass

    def __repr__(self) -> str:
        """String representation of the object."""
        return f"{self.__class__.__name__}(name='{self._name}')"

    def __str__(self) -> str:
        """Human-readable string representation."""
        return self.__repr__()


class Validator:
    """Utility class for common validation tasks."""

    @staticmethod
    def validate_positive(value: float, name: str = "value") -> float:
        """
        Validate that a value is positive.

        Parameters
        ----------
        value : float
            Value to validate
        name : str
            Name of the value for error messages

        Returns
        -------
        float
            Validated value

        Raises
        ------
        ValidationError
            If value is not positive
        """
        if value <= 0:
            raise ValidationError(f"{name} must be positive, got {value}")
        return value

    @staticmethod
    def validate_non_negative(value: float, name: str = "value") -> float:
        """
        Validate that a value is non-negative.

        Parameters
        ----------
        value : float
            Value to validate
        name : str
            Name of the value for error messages

        Returns
        -------
        float
            Validated value

        Raises
        ------
        ValidationError
            If value is negative
        """
        if value < 0:
            raise ValidationError(f"{name} must be non-negative, got {value}")
        return value

    @staticmethod
    def validate_range(value: float, min_val: float, max_val: float,
                      name: str = "value") -> float:
        """
        Validate that a value is within a range.

        Parameters
        ----------
        value : float
            Value to validate
        min_val : float
            Minimum allowed value
        max_val : float
            Maximum allowed value
        name : str
            Name of the value for error messages

        Returns
        -------
        float
            Validated value

        Raises
        ------
        ValidationError
            If value is outside range
        """
        if not min_val <= value <= max_val:
            raise ValidationError(
                f"{name} must be between {min_val} and {max_val}, got {value}"
            )
        return value

    @staticmethod
    def validate_temperature(temperature: float) -> float:
        """
        Validate temperature value.

        Parameters
        ----------
        temperature : float
            Temperature in Kelvin

        Returns
        -------
        float
            Validated temperature

        Raises
        ------
        ValidationError
            If temperature is physically invalid
        """
        if temperature < 0:
            raise ValidationError(
                f"Temperature must be positive (in Kelvin), got {temperature}"
            )
        if temperature > 10000:
            warnings.warn(
                f"Unusually high temperature: {temperature} K",
                UserWarning
            )
        return temperature


def format_value(value: float, precision: int = 6) -> str:
    """
    Format a numerical value for output.

    Parameters
    ----------
    value : float
        Value to format
    precision : int
        Number of significant digits

    Returns
    -------
    str
        Formatted value string
    """
    if abs(value) < 1e-10:
        return "0.0"
    elif abs(value) >= 1e6 or abs(value) < 1e-4:
        return f"{value:.{precision}e}"
    else:
        return f"{value:.{precision}f}"


def check_tripoli5_available() -> bool:
    """
    Check if Tripoli-5 is available.

    Returns
    -------
    bool
        True if Tripoli-5 is available
    """
    try:
        import tripoli5  # noqa: F401
        return True
    except ImportError:
        return False


def ensure_tripoli5():
    """
    Ensure Tripoli-5 is available.

    Raises
    ------
    ConfigurationError
        If Tripoli-5 is not available
    """
    if not check_tripoli5_available():
        raise ConfigurationError(
            "Tripoli-5 is not installed or not available. "
            "Please install Tripoli-5 to use pytrip5."
        )
