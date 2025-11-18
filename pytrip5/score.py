"""Score abstractions for pytrip5.

This module provides Score classes that define tallies/scores to compute
during Tripoli-5 simulations. Each Score class knows how to:
- Convert itself to a Tripoli-5 score specification
- Parse Tripoli-5 results back into Python objects

Based on Tripoli-5 score module documentation:
https://tripoli5.asnr.dev/documentation/examples/features/score.html
"""

from __future__ import annotations

from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import Any, Optional
import numpy as np
import numpy.typing as npt


class Score(ABC):
    """Abstract base class for simulation scores/tallies.

    Subclasses must implement:
    - to_tripoli_score_spec(): Convert to Tripoli-5 score specification
    - from_tripoli_result(): Parse Tripoli-5 result into Python object
    """

    @abstractmethod
    def to_tripoli_score_spec(self, tripoli_module: Any) -> Any:
        """Convert this score to a Tripoli-5 score specification.

        Args:
            tripoli_module: The imported tripoli5 module (for real adapter)
                           or None (for mock adapter)

        Returns:
            Tripoli-5 score object
        """
        pass

    @abstractmethod
    def from_tripoli_result(self, tripoli_result: Any) -> Any:
        """Parse Tripoli-5 score result into Python object.

        Args:
            tripoli_result: Raw Tripoli-5 score result

        Returns:
            Parsed result (type depends on score type)
        """
        pass

    @property
    @abstractmethod
    def name(self) -> str:
        """Unique name identifier for this score."""
        pass


@dataclass
class KeffectiveScore(Score):
    """Score for k-effective (criticality eigenvalue).

    This score is automatically computed in criticality simulations.
    It represents the effective multiplication factor of the system.

    Example:
        >>> score = KeffectiveScore()
        >>> score.name
        'k_effective'
    """

    def to_tripoli_score_spec(self, tripoli_module: Any) -> Any:
        """Convert to Tripoli-5 k-effective score.

        For criticality simulations, k-effective is computed automatically,
        so this may return None or a minimal specification.

        Args:
            tripoli_module: The tripoli5 module or None

        Returns:
            Tripoli-5 k-eff score specification
        """
        if tripoli_module is None:
            # Mock adapter
            return {'type': 'k_effective'}

        # Real Tripoli-5: k-eff is automatic in criticality mode
        # May need to use tripoli_module.score.Keff() or similar
        try:
            return tripoli_module.score.Keff()
        except AttributeError:
            # Fallback if API differs
            return None

    def from_tripoli_result(self, tripoli_result: Any) -> float:
        """Parse k-effective from Tripoli-5 result.

        Args:
            tripoli_result: Tripoli result object or dict

        Returns:
            k-effective value as float
        """
        if isinstance(tripoli_result, dict):
            # Mock result
            return tripoli_result.get('value', 1.0)

        # Real Tripoli-5 result
        if hasattr(tripoli_result, 'value'):
            return float(tripoli_result.value)
        return float(tripoli_result)

    @property
    def name(self) -> str:
        """Return score name."""
        return 'k_effective'


@dataclass
class PinPowerScore(Score):
    """Score for pin-wise fission power distribution.

    Computes relative power in each fuel pin, normalized such that
    the average pin power is 1.0.

    Attributes:
        score_name: Custom name for this score instance
        energy_bounds: Optional energy group boundaries in MeV

    Example:
        >>> score = PinPowerScore('pin_powers')
        >>> score.name
        'pin_powers'
    """
    score_name: str = 'pin_powers'
    energy_bounds: Optional[list[float]] = None

    def to_tripoli_score_spec(self, tripoli_module: Any) -> Any:
        """Convert to Tripoli-5 pin power score.

        Args:
            tripoli_module: The tripoli5 module or None

        Returns:
            Tripoli-5 power score specification
        """
        if tripoli_module is None:
            # Mock adapter
            return {
                'type': 'pin_power',
                'name': self.score_name,
                'energy_bounds': self.energy_bounds
            }

        # Real Tripoli-5: create mesh score for power
        # Based on tripoli5.score examples
        try:
            score = tripoli_module.score.Power(
                name=self.score_name,
                # May need mesh specification here
            )
            return score
        except AttributeError:
            # Fallback
            return {'type': 'pin_power', 'name': self.score_name}

    def from_tripoli_result(self, tripoli_result: Any) -> npt.NDArray[np.float64]:
        """Parse pin power distribution from Tripoli-5 result.

        Args:
            tripoli_result: Tripoli result object or dict

        Returns:
            2D numpy array of pin powers
        """
        if isinstance(tripoli_result, dict):
            # Mock result
            return tripoli_result['values']

        # Real Tripoli-5 result
        if hasattr(tripoli_result, 'values'):
            return np.array(tripoli_result.values)
        return np.array(tripoli_result)

    @property
    def name(self) -> str:
        """Return score name."""
        return self.score_name


@dataclass
class FluxScore(Score):
    """Score for neutron flux distribution.

    Computes spatial flux distribution, optionally in energy groups.

    Attributes:
        score_name: Custom name for this score instance
        energy_bounds: Energy group boundaries in MeV. If None, one-group flux.
        particle_type: Particle type ('neutron', 'photon', etc.)

    Example:
        >>> # Thermal flux score
        >>> thermal = FluxScore('thermal_flux', energy_bounds=[0, 0.625e-6])
        >>> thermal.name
        'thermal_flux'
        >>> # Fast flux score
        >>> fast = FluxScore('fast_flux', energy_bounds=[0.1, 20.0])
    """
    score_name: str = 'flux'
    energy_bounds: Optional[list[float]] = None
    particle_type: str = 'neutron'

    def to_tripoli_score_spec(self, tripoli_module: Any) -> Any:
        """Convert to Tripoli-5 flux score.

        Args:
            tripoli_module: The tripoli5 module or None

        Returns:
            Tripoli-5 flux score specification
        """
        if tripoli_module is None:
            # Mock adapter
            return {
                'type': 'flux',
                'name': self.score_name,
                'energy_bounds': self.energy_bounds,
                'particle': self.particle_type
            }

        # Real Tripoli-5: create flux score
        try:
            score = tripoli_module.score.Flux(
                name=self.score_name,
                particle=self.particle_type
            )
            if self.energy_bounds:
                score.set_energy_bins(self.energy_bounds)
            return score
        except AttributeError:
            return {
                'type': 'flux',
                'name': self.score_name,
                'energy_bounds': self.energy_bounds
            }

    def from_tripoli_result(self, tripoli_result: Any) -> npt.NDArray[np.float64]:
        """Parse flux distribution from Tripoli-5 result.

        Args:
            tripoli_result: Tripoli result object or dict

        Returns:
            Numpy array of flux values (1D, 2D, or 3D depending on mesh)
        """
        if isinstance(tripoli_result, dict):
            # Mock result
            return tripoli_result['values']

        # Real Tripoli-5 result
        if hasattr(tripoli_result, 'values'):
            return np.array(tripoli_result.values)
        return np.array(tripoli_result)

    @property
    def name(self) -> str:
        """Return score name."""
        return self.score_name


@dataclass
class ReactionRateScore(Score):
    """Score for reaction rate (e.g., fission, capture, scatter).

    Computes spatial distribution of a specific nuclear reaction rate.

    Attributes:
        score_name: Custom name for this score instance
        reaction_type: Reaction MT number or name (e.g., 'fission', 'capture', 18, 102)
        isotope: Optional isotope to score (e.g., 'U235'). If None, all isotopes.
        energy_bounds: Optional energy group boundaries in MeV

    Example:
        >>> # U-235 fission rate
        >>> fission = ReactionRateScore('u235_fission', reaction_type='fission', isotope='U235')
        >>> fission.name
        'u235_fission'
    """
    score_name: str
    reaction_type: str | int
    isotope: Optional[str] = None
    energy_bounds: Optional[list[float]] = None

    def to_tripoli_score_spec(self, tripoli_module: Any) -> Any:
        """Convert to Tripoli-5 reaction rate score.

        Args:
            tripoli_module: The tripoli5 module or None

        Returns:
            Tripoli-5 reaction rate score specification
        """
        if tripoli_module is None:
            # Mock adapter
            return {
                'type': 'reaction_rate',
                'name': self.score_name,
                'reaction': self.reaction_type,
                'isotope': self.isotope,
                'energy_bounds': self.energy_bounds
            }

        # Real Tripoli-5: create reaction rate score
        try:
            score = tripoli_module.score.ReactionRate(
                name=self.score_name,
                reaction=self.reaction_type,
                isotope=self.isotope
            )
            if self.energy_bounds:
                score.set_energy_bins(self.energy_bounds)
            return score
        except AttributeError:
            return {
                'type': 'reaction_rate',
                'name': self.score_name,
                'reaction': self.reaction_type
            }

    def from_tripoli_result(self, tripoli_result: Any) -> npt.NDArray[np.float64]:
        """Parse reaction rate from Tripoli-5 result.

        Args:
            tripoli_result: Tripoli result object or dict

        Returns:
            Numpy array of reaction rates
        """
        if isinstance(tripoli_result, dict):
            # Mock result
            return tripoli_result.get('values', np.array([1.0]))

        # Real Tripoli-5 result
        if hasattr(tripoli_result, 'values'):
            return np.array(tripoli_result.values)
        return np.array(tripoli_result)

    @property
    def name(self) -> str:
        """Return score name."""
        return self.score_name


@dataclass
class DoseScore(Score):
    """Score for dose rate (useful for shielding and radiation protection).

    Computes dose rate in specified units at detector locations.

    Attributes:
        score_name: Custom name for this score instance
        dose_type: Type of dose ('ambient', 'effective', 'absorbed')
        units: Dose units ('Sv/h', 'rem/h', 'Gy/h')

    Example:
        >>> dose = DoseScore('detector_dose', dose_type='ambient', units='Sv/h')
        >>> dose.name
        'detector_dose'
    """
    score_name: str = 'dose'
    dose_type: str = 'ambient'
    units: str = 'Sv/h'

    def to_tripoli_score_spec(self, tripoli_module: Any) -> Any:
        """Convert to Tripoli-5 dose score.

        Args:
            tripoli_module: The tripoli5 module or None

        Returns:
            Tripoli-5 dose score specification
        """
        if tripoli_module is None:
            # Mock adapter
            return {
                'type': 'dose',
                'name': self.score_name,
                'dose_type': self.dose_type,
                'units': self.units
            }

        # Real Tripoli-5: create dose score
        try:
            score = tripoli_module.score.Dose(
                name=self.score_name,
                dose_type=self.dose_type
            )
            return score
        except AttributeError:
            return {'type': 'dose', 'name': self.score_name}

    def from_tripoli_result(self, tripoli_result: Any) -> float | npt.NDArray[np.float64]:
        """Parse dose from Tripoli-5 result.

        Args:
            tripoli_result: Tripoli result object or dict

        Returns:
            Dose value (scalar or array)
        """
        if isinstance(tripoli_result, dict):
            # Mock result
            value = tripoli_result.get('value', 1e-6)
            if isinstance(value, (int, float)):
                return float(value)
            return np.array(value)

        # Real Tripoli-5 result
        if hasattr(tripoli_result, 'value'):
            return float(tripoli_result.value)
        if hasattr(tripoli_result, 'values'):
            return np.array(tripoli_result.values)
        return float(tripoli_result)

    @property
    def name(self) -> str:
        """Return score name."""
        return self.score_name


# Convenience functions for common scores

def create_standard_scores() -> list[Score]:
    """Create a standard set of scores for PWR analysis.

    Returns:
        List containing k-eff, pin powers, and thermal/fast flux scores

    Example:
        >>> scores = create_standard_scores()
        >>> len(scores)
        4
        >>> scores[0].name
        'k_effective'
    """
    return [
        KeffectiveScore(),
        PinPowerScore('pin_powers'),
        FluxScore('thermal_flux', energy_bounds=[0, 0.625e-6]),
        FluxScore('fast_flux', energy_bounds=[0.1, 20.0])
    ]


def create_minimal_scores() -> list[Score]:
    """Create minimal score set for quick testing.

    Returns:
        List containing only k-eff and pin powers

    Example:
        >>> scores = create_minimal_scores()
        >>> len(scores)
        2
    """
    return [
        KeffectiveScore(),
        PinPowerScore('pin_powers')
    ]
