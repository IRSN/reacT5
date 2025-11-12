"""Results retrieval module for pyT5.

This module provides classes for retrieving and analyzing results
from Tripoli-5 simulations.
"""

from typing import Dict, List, Optional, Tuple
import numpy as np


class Results:
    """Handles retrieval and analysis of simulation results.

    This class provides methods to extract computed quantities from
    completed simulations, including k-effective, fluxes, reaction
    rates, and their statistical uncertainties.

    Attributes:
        simulation_name: Name of the simulation these results belong to.
        k_effective: Effective multiplication factor (mean, std dev).
        scores: Dictionary of score results.

    Examples:
        >>> results = Results(simulation_name="PWR_core")
        >>> keff, keff_std = results.get_k_effective()
        >>> flux = results.get_score("fuel_flux")
    """

    def __init__(self, simulation_name: str) -> None:
        """Initialize Results object.

        Args:
            simulation_name: Name of the simulation.
        """
        self.simulation_name = simulation_name
        self.k_effective: Optional[Tuple[float, float]] = None
        self.scores: Dict[str, np.ndarray] = {}
        self._score_uncertainties: Dict[str, np.ndarray] = {}

    def set_k_effective(self, mean: float, std_dev: float) -> None:
        """Set the k-effective value and standard deviation.

        Args:
            mean: Mean k-effective value.
            std_dev: Standard deviation of k-effective.

        Raises:
            ValueError: If mean is negative or std_dev is non-positive.
        """
        if mean < 0:
            raise ValueError(f"k-effective mean must be non-negative, got {mean}")
        if std_dev < 0:
            raise ValueError(f"Standard deviation must be non-negative, got {std_dev}")

        self.k_effective = (mean, std_dev)

    def get_k_effective(self) -> Tuple[float, float]:
        """Get the k-effective value and standard deviation.

        Returns:
            Tuple of (mean, std_dev) for k-effective.

        Raises:
            RuntimeError: If k-effective has not been set.
        """
        if self.k_effective is None:
            raise RuntimeError("k-effective has not been set")
        return self.k_effective

    def get_k_effective_mean(self) -> float:
        """Get the mean k-effective value.

        Returns:
            Mean k-effective value.

        Raises:
            RuntimeError: If k-effective has not been set.
        """
        if self.k_effective is None:
            raise RuntimeError("k-effective has not been set")
        return self.k_effective[0]

    def get_k_effective_std(self) -> float:
        """Get the k-effective standard deviation.

        Returns:
            Standard deviation of k-effective.

        Raises:
            RuntimeError: If k-effective has not been set.
        """
        if self.k_effective is None:
            raise RuntimeError("k-effective has not been set")
        return self.k_effective[1]

    def add_score(
        self,
        score_name: str,
        values: np.ndarray,
        uncertainties: Optional[np.ndarray] = None,
    ) -> None:
        """Add a score result.

        Args:
            score_name: Name of the score.
            values: Array of score values.
            uncertainties: Array of relative uncertainties (optional).

        Raises:
            ValueError: If score already exists or array shapes don't match.
        """
        if score_name in self.scores:
            raise ValueError(f"Score '{score_name}' already exists in results")

        if uncertainties is not None and values.shape != uncertainties.shape:
            raise ValueError("Values and uncertainties arrays must have same shape")

        self.scores[score_name] = values
        if uncertainties is not None:
            self._score_uncertainties[score_name] = uncertainties

    def get_score(self, score_name: str) -> np.ndarray:
        """Get the values for a specific score.

        Args:
            score_name: Name of the score to retrieve.

        Returns:
            Array of score values.

        Raises:
            KeyError: If score not found in results.
        """
        if score_name not in self.scores:
            raise KeyError(f"Score '{score_name}' not found in results")
        return self.scores[score_name]

    def get_score_uncertainty(self, score_name: str) -> np.ndarray:
        """Get the uncertainties for a specific score.

        Args:
            score_name: Name of the score.

        Returns:
            Array of relative uncertainties.

        Raises:
            KeyError: If score not found or uncertainties not available.
        """
        if score_name not in self._score_uncertainties:
            raise KeyError(
                f"Uncertainties for score '{score_name}' not found in results"
            )
        return self._score_uncertainties[score_name]

    def has_score(self, score_name: str) -> bool:
        """Check if a score exists in the results.

        Args:
            score_name: Name of the score.

        Returns:
            True if score exists, False otherwise.
        """
        return score_name in self.scores

    def list_scores(self) -> List[str]:
        """Get list of all available score names.

        Returns:
            List of score names.
        """
        return list(self.scores.keys())

    def get_score_statistics(self, score_name: str) -> Dict[str, float]:
        """Get statistical summary for a score.

        Args:
            score_name: Name of the score.

        Returns:
            Dictionary with 'mean', 'std', 'min', 'max' statistics.

        Raises:
            KeyError: If score not found in results.
        """
        values = self.get_score(score_name)
        return {
            "mean": float(np.mean(values)),
            "std": float(np.std(values)),
            "min": float(np.min(values)),
            "max": float(np.max(values)),
        }

    def export_to_file(self, filepath: str, score_name: Optional[str] = None) -> None:
        """Export results to a file.

        Args:
            filepath: Path to output file.
            score_name: Name of specific score to export. If None, exports
                all results. Defaults to None.

        Raises:
            KeyError: If specified score not found.
        """
        # Placeholder implementation - would write to file
        print(f"Exporting results to {filepath}...")
        if score_name:
            values = self.get_score(score_name)
            print(f"  Score '{score_name}': shape {values.shape}")
        else:
            print(f"  All scores: {len(self.scores)}")
            if self.k_effective:
                print(f"  k-effective: {self.k_effective[0]:.5f} ± {self.k_effective[1]:.5f}")

    def __repr__(self) -> str:
        """Return string representation of Results object."""
        keff_str = ""
        if self.k_effective:
            keff_str = f", k-eff={self.k_effective[0]:.5f}±{self.k_effective[1]:.5f}"
        return (
            f"Results(simulation='{self.simulation_name}', "
            f"scores={len(self.scores)}{keff_str})"
        )
