"""
Simplified Geometry module for pytrip5 - PyDrag-inspired interface.

This module provides simplified geometry definitions for PWR modeling,
wrapping Tripoli-5 AGORA API with PyDrag-style simplicity.
"""

from typing import List, Tuple, Optional, Union
from .core import PyTrip5Object, ValidationError, Validator


class Geometry:
    """
    Simplified geometry definition (PyDrag-style).

    Handles pin layouts, assembly geometry, and core configuration.

    Example:
        >>> # Define pin types
        >>> F = ['UO2', 0.4095, 'void', 0.4180, 'Zr4', 0.4750]
        >>> T = ['water', 0.5615, 'Zr4', 0.6020]
        >>>
        >>> # Define layout
        >>> layout = [[F, F, T, F], [F, F, F], [T, F], [F]]
        >>>
        >>> # Create geometry
        >>> geom = Geometry(layout, PinPitch=1.26, AssemblyPitch=21.5, ActiveHeight=365.76)
    """

    def __init__(
        self,
        pin_layout: List[List],
        PinPitch: float,
        AssemblyPitch: float,
        ActiveHeight: float,
        symmetry: str = '1/8',
        **kwargs
    ):
        """
        Initialize Geometry.

        Parameters
        ----------
        pin_layout : List[List]
            Nested list defining pin layout with symmetry
        PinPitch : float
            Pin-to-pin spacing in cm
        AssemblyPitch : float
            Assembly pitch in cm
        ActiveHeight : float
            Active fuel height in cm
        symmetry : str
            Symmetry type: '1/8', '1/4', 'full'
        **kwargs
            Additional parameters
        """
        self.pin_layout = pin_layout
        self.pin_pitch = Validator.validate_positive(PinPitch, "PinPitch")
        self.assembly_pitch = Validator.validate_positive(AssemblyPitch, "AssemblyPitch")
        self.active_height = Validator.validate_positive(ActiveHeight, "ActiveHeight")
        self.symmetry = symmetry

        # Parse pin layout
        self._pins = self._parse_pin_layout(pin_layout)
        self._lattice_size = self._compute_lattice_size()

    def _parse_pin_layout(self, layout: List[List]) -> List:
        """
        Parse pin layout into pin definitions.

        Parameters
        ----------
        layout : List[List]
            Pin layout

        Returns
        -------
        List
            Parsed pin definitions
        """
        pins = []
        for row in layout:
            pins.extend(row)
        return pins

    def _compute_lattice_size(self) -> Tuple[int, int]:
        """
        Compute lattice size based on symmetry and layout.

        Returns
        -------
        Tuple[int, int]
            (nx, ny) lattice dimensions
        """
        # For 1/8 symmetry, expand to full
        if self.symmetry == '1/8':
            n_rows = len(self.pin_layout)
            nx = ny = n_rows * 2 - 1
        elif self.symmetry == '1/4':
            n_rows = len(self.pin_layout)
            nx = ny = n_rows * 2
        else:  # full
            nx = ny = len(self.pin_layout)

        return (nx, ny)

    @property
    def lattice_size(self) -> Tuple[int, int]:
        """Get lattice size (nx, ny)."""
        return self._lattice_size

    def to_tripoli5(self, materials_dict):
        """
        Convert to Tripoli-5 AGORA Geometry.

        Parameters
        ----------
        materials_dict : dict
            Dictionary mapping material names to Tripoli-5 Mixtures

        Returns
        -------
        tripoli5.agora.Geometry
            Tripoli-5 Geometry object
        """
        try:
            import tripoli5.agora
            from tripoli5.core.euclide import Point

            # Create universes and volumes for pin cell
            volumes = []

            # This is a simplified placeholder - actual implementation
            # would build the full AGORA geometry hierarchy
            # See Tripoli-5 pin_cell example for full details

            # For now, return placeholder
            raise NotImplementedError(
                "Full Tripoli-5 geometry conversion requires "
                "detailed AGORA API integration. "
                "See Tripoli-5 pin_cell example."
            )

        except ImportError:
            raise ValidationError(
                "Tripoli-5 not available. Cannot create geometry."
            )

    def __repr__(self) -> str:
        """String representation."""
        nx, ny = self._lattice_size
        return (
            f"Geometry(lattice={nx}x{ny}, "
            f"pin_pitch={self.pin_pitch}, "
            f"assy_pitch={self.assembly_pitch})"
        )


class Pin:
    """
    Pin cell definition helper.

    Provides convenient pin definition using list notation.
    """

    @staticmethod
    def fuel_pin(
        fuel_radius: float,
        gap_radius: float,
        clad_outer_radius: float,
        fuel_material: str = 'UO2',
        gap_material: str = 'void',
        clad_material: str = 'Zr4'
    ) -> List:
        """
        Create fuel pin definition.

        Parameters
        ----------
        fuel_radius : float
            Fuel pellet outer radius (cm)
        gap_radius : float
            Gap outer radius (cm)
        clad_outer_radius : float
            Cladding outer radius (cm)
        fuel_material : str
            Fuel material name
        gap_material : str
            Gap material name
        clad_material : str
            Cladding material name

        Returns
        -------
        List
            Pin definition [material, radius, ...]
        """
        return [
            fuel_material, fuel_radius,
            gap_material, gap_radius,
            clad_material, clad_outer_radius
        ]

    @staticmethod
    def guide_tube(
        water_radius: float,
        clad_outer_radius: float,
        water_material: str = 'water',
        clad_material: str = 'Zr4'
    ) -> List:
        """
        Create guide tube definition.

        Parameters
        ----------
        water_radius : float
            Inner water radius (cm)
        clad_outer_radius : float
            Tube outer radius (cm)
        water_material : str
            Water material name
        clad_material : str
            Tube material name

        Returns
        -------
        List
            Pin definition
        """
        return [
            water_material, water_radius,
            clad_material, clad_outer_radius
        ]


class Power:
    """
    Power specification for reactor calculations (PyDrag-style).

    Example:
        >>> power = Power(nbAssemblies=157, corePower=2652)
    """

    def __init__(self, nbAssemblies: int, corePower: float):
        """
        Initialize Power.

        Parameters
        ----------
        nbAssemblies : int
            Number of assemblies in core
        corePower : float
            Total core power in MWth
        """
        self.nb_assemblies = nbAssemblies
        self.core_power = Validator.validate_positive(corePower, "corePower")
        self.power_density = self.core_power / self.nb_assemblies

    @property
    def assembly_power(self) -> float:
        """Get average assembly power (MWth)."""
        return self.power_density

    def __repr__(self) -> str:
        """String representation."""
        return (
            f"Power(assemblies={self.nb_assemblies}, "
            f"core={self.core_power}MW, "
            f"assy={self.power_density:.2f}MW)"
        )


# Convenience functions for common geometries

def create_pincell_geometry(
    pin_pitch: float,
    fuel_radius: float,
    clad_inner_radius: float,
    clad_outer_radius: float,
    height: float = 20.0
) -> Geometry:
    """
    Create simple pin cell geometry.

    Parameters
    ----------
    pin_pitch : float
        Pin pitch (cm)
    fuel_radius : float
        Fuel radius (cm)
    clad_inner_radius : float
        Clad inner radius (cm)
    clad_outer_radius : float
        Clad outer radius (cm)
    height : float
        Pin height (cm)

    Returns
    -------
    Geometry
        Pin cell geometry
    """
    # Single pin
    pin_def = [
        'UO2', fuel_radius,
        'void', clad_inner_radius,
        'Zr4', clad_outer_radius
    ]

    layout = [[pin_def]]

    return Geometry(
        layout,
        PinPitch=pin_pitch,
        AssemblyPitch=pin_pitch,
        ActiveHeight=height,
        symmetry='full'
    )


def create_assembly_17x17(
    pin_pitch: float = 1.26,
    assembly_pitch: float = 21.5,
    active_height: float = 365.76,
    fuel_radius: float = 0.4095,
    clad_inner: float = 0.4180,
    clad_outer: float = 0.4750,
    guide_tube_positions: Optional[List[Tuple[int, int]]] = None
) -> Geometry:
    """
    Create 17x17 PWR assembly geometry.

    Parameters
    ----------
    pin_pitch : float
        Pin pitch (cm)
    assembly_pitch : float
        Assembly pitch (cm)
    active_height : float
        Active height (cm)
    fuel_radius : float
        Fuel pellet radius (cm)
    clad_inner : float
        Cladding inner radius (cm)
    clad_outer : float
        Cladding outer radius (cm)
    guide_tube_positions : List[Tuple[int, int]], optional
        Guide tube positions

    Returns
    -------
    Geometry
        17x17 assembly geometry
    """
    # Define pins
    F = Pin.fuel_pin(fuel_radius, clad_inner, clad_outer)
    T = Pin.guide_tube(0.5615, 0.6020)

    # Standard 17x17 layout with 1/8 symmetry
    # 24 guide tubes in typical pattern
    layout = [
        [T, F, F, F, T, F, F, F, F],
        [F, F, F, F, F, F, F, F],
        [F, F, T, F, F, F, F],
        [F, F, F, F, F, F],
        [T, F, F, F, T, F],
        [F, F, F, F, F],
        [F, F, F, F],
        [F, F, F],
        [F, F]
    ]

    return Geometry(
        layout,
        PinPitch=pin_pitch,
        AssemblyPitch=assembly_pitch,
        ActiveHeight=active_height,
        symmetry='1/8'
    )
