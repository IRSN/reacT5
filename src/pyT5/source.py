"""Neutron source definition module for pyT5.

This module provides classes for defining initial neutron sources
for Tripoli-5 Monte-Carlo simulations.
"""

from typing import List, Optional, Tuple
import numpy as np


class NeutronSource:
    """Defines the initial neutron source for a simulation.

    The neutron source specifies the spatial, energy, and angular
    distribution of source neutrons at the start of the simulation.

    Attributes:
        name: Unique identifier for the source.
        source_type: Type of source ('point', 'volume', 'surface', 'criticality').
        position: Source position coordinates (x, y, z) in cm.
        energy: Source energy in MeV (None for fission spectrum).
        intensity: Source intensity (neutrons/s).

    Examples:
        >>> source = NeutronSource(
        ...     name="fission_source",
        ...     source_type="criticality",
        ...     intensity=1e6
        ... )
    """

    def __init__(
        self,
        name: str,
        source_type: str = "criticality",
        position: Optional[Tuple[float, float, float]] = None,
        energy: Optional[float] = None,
        intensity: float = 1.0e6,
    ) -> None:
        """Initialize NeutronSource object.

        Args:
            name: Unique identifier for the source.
            source_type: Type of source. One of 'point', 'volume', 'surface',
                or 'criticality'. Defaults to 'criticality'.
            position: (x, y, z) coordinates of source position in cm.
                Required for 'point' source type.
            energy: Source neutron energy in MeV. If None, uses fission
                spectrum. Defaults to None.
            intensity: Source intensity in neutrons/s. Defaults to 1e6.

        Raises:
            ValueError: If source_type is invalid or required parameters
                are missing.
        """
        valid_types = ("point", "volume", "surface", "criticality")
        if source_type not in valid_types:
            raise ValueError(
                f"Invalid source_type '{source_type}', must be one of {valid_types}"
            )

        if source_type == "point" and position is None:
            raise ValueError("Point source requires position to be specified")

        if intensity <= 0:
            raise ValueError(f"Intensity must be positive, got {intensity}")

        self.name = name
        self.source_type = source_type
        self.position = position
        self.energy = energy
        self.intensity = intensity

    def set_position(self, x: float, y: float, z: float) -> None:
        """Set the source position.

        Args:
            x: X-coordinate in cm.
            y: Y-coordinate in cm.
            z: Z-coordinate in cm.
        """
        self.position = (x, y, z)

    def set_energy(self, energy: float) -> None:
        """Set the source energy.

        Args:
            energy: Energy in MeV.

        Raises:
            ValueError: If energy is negative.
        """
        if energy < 0:
            raise ValueError(f"Energy must be non-negative, got {energy}")
        self.energy = energy

    def set_intensity(self, intensity: float) -> None:
        """Set the source intensity.

        Args:
            intensity: Intensity in neutrons/s.

        Raises:
            ValueError: If intensity is non-positive.
        """
        if intensity <= 0:
            raise ValueError(f"Intensity must be positive, got {intensity}")
        self.intensity = intensity

    def __repr__(self) -> str:
        """Return string representation of NeutronSource object."""
        pos_str = f" at {self.position}" if self.position else ""
        energy_str = f" {self.energy} MeV" if self.energy else " (fission spectrum)"
        return (
            f"NeutronSource(name='{self.name}', type='{self.source_type}'{pos_str}, "
            f"energy={energy_str}, intensity={self.intensity:.2e} n/s)"
        )


class NeutronMedia:
    """Defines the neutron transport media properties.

    This class configures properties related to neutron transport
    in different media, including scattering treatment and thermal
    scattering laws.

    Attributes:
        name: Unique identifier for the media.
        thermal_scattering: Enable S(alpha, beta) thermal scattering treatment.
        free_gas_scattering: Enable free gas scattering model.

    Examples:
        >>> media = NeutronMedia(
        ...     name="thermal_media",
        ...     thermal_scattering=True
        ... )
    """

    def __init__(
        self,
        name: str,
        thermal_scattering: bool = False,
        free_gas_scattering: bool = False,
    ) -> None:
        """Initialize NeutronMedia object.

        Args:
            name: Unique identifier for the media.
            thermal_scattering: If True, enables S(alpha, beta) thermal
                scattering treatment for materials below ~4 eV.
                Defaults to False.
            free_gas_scattering: If True, enables free gas scattering model.
                Defaults to False.
        """
        self.name = name
        self.thermal_scattering = thermal_scattering
        self.free_gas_scattering = free_gas_scattering

    def enable_thermal_scattering(self) -> None:
        """Enable thermal scattering treatment."""
        self.thermal_scattering = True

    def disable_thermal_scattering(self) -> None:
        """Disable thermal scattering treatment."""
        self.thermal_scattering = False

    def enable_free_gas_scattering(self) -> None:
        """Enable free gas scattering model."""
        self.free_gas_scattering = True

    def disable_free_gas_scattering(self) -> None:
        """Disable free gas scattering model."""
        self.free_gas_scattering = False

    def __repr__(self) -> str:
        """Return string representation of NeutronMedia object."""
        return (
            f"NeutronMedia(name='{self.name}', "
            f"thermal_scattering={self.thermal_scattering}, "
            f"free_gas={self.free_gas_scattering})"
        )
