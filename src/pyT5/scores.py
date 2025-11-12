"""Scores and tallies module for pyT5.

This module provides classes for defining scores (tallies) to be
computed during Tripoli-5 simulations.
"""

from typing import Dict, List, Optional, Union


class Score:
    """Represents a score (tally) to be computed in the simulation.

    Scores define what physical quantities should be computed during
    the Monte-Carlo simulation (e.g., flux, reaction rates, k-effective).

    Attributes:
        name: Unique identifier for the score.
        score_type: Type of score to compute.
        cells: List of cell names where the score is computed.
        energy_bins: Energy bin boundaries in MeV (optional).
        spatial_mesh: Spatial mesh specification (optional).

    Examples:
        >>> flux_score = Score(
        ...     name="fuel_flux",
        ...     score_type="flux",
        ...     cells=["fuel_cell_1", "fuel_cell_2"]
        ... )
        >>> keff_score = Score(
        ...     name="k_effective",
        ...     score_type="keff"
        ... )
    """

    def __init__(
        self,
        name: str,
        score_type: str,
        cells: Optional[List[str]] = None,
        energy_bins: Optional[List[float]] = None,
        spatial_mesh: Optional[Dict[str, int]] = None,
    ) -> None:
        """Initialize Score object.

        Args:
            name: Unique identifier for the score.
            score_type: Type of score. Common types include 'flux',
                'fission_rate', 'absorption_rate', 'keff', 'power'.
            cells: List of cell names where the score is computed.
                Not needed for global scores like 'keff'.
            energy_bins: List of energy bin boundaries in MeV for
                energy-dependent scores. Defaults to None (integrated).
            spatial_mesh: Dictionary specifying spatial mesh for mesh
                tallies, e.g., {'nx': 10, 'ny': 10, 'nz': 10}.

        Raises:
            ValueError: If score_type is empty or energy_bins are not
                in ascending order.
        """
        if not score_type:
            raise ValueError("score_type cannot be empty")

        if energy_bins is not None and len(energy_bins) > 1:
            if not all(energy_bins[i] < energy_bins[i + 1] for i in range(len(energy_bins) - 1)):
                raise ValueError("energy_bins must be in ascending order")

        self.name = name
        self.score_type = score_type
        self.cells = cells or []
        self.energy_bins = energy_bins
        self.spatial_mesh = spatial_mesh

    def add_cell(self, cell_name: str) -> None:
        """Add a cell to the score computation.

        Args:
            cell_name: Name of the cell to add.
        """
        if cell_name not in self.cells:
            self.cells.append(cell_name)

    def remove_cell(self, cell_name: str) -> None:
        """Remove a cell from the score computation.

        Args:
            cell_name: Name of the cell to remove.

        Raises:
            ValueError: If cell not found in score.
        """
        if cell_name not in self.cells:
            raise ValueError(f"Cell '{cell_name}' not found in score '{self.name}'")
        self.cells.remove(cell_name)

    def set_energy_bins(self, energy_bins: List[float]) -> None:
        """Set energy bin boundaries for the score.

        Args:
            energy_bins: List of energy bin boundaries in MeV.

        Raises:
            ValueError: If energy_bins are not in ascending order.
        """
        if len(energy_bins) > 1:
            if not all(energy_bins[i] < energy_bins[i + 1] for i in range(len(energy_bins) - 1)):
                raise ValueError("energy_bins must be in ascending order")
        self.energy_bins = energy_bins

    def set_spatial_mesh(self, nx: int, ny: int, nz: int) -> None:
        """Set spatial mesh for mesh tally.

        Args:
            nx: Number of mesh cells in x-direction.
            ny: Number of mesh cells in y-direction.
            nz: Number of mesh cells in z-direction.

        Raises:
            ValueError: If any mesh dimension is non-positive.
        """
        if nx <= 0 or ny <= 0 or nz <= 0:
            raise ValueError("Mesh dimensions must be positive")
        self.spatial_mesh = {"nx": nx, "ny": ny, "nz": nz}

    def __repr__(self) -> str:
        """Return string representation of Score object."""
        cells_str = f", cells={len(self.cells)}" if self.cells else ""
        energy_str = f", energy_bins={len(self.energy_bins)}" if self.energy_bins else ""
        return f"Score(name='{self.name}', type='{self.score_type}'{cells_str}{energy_str})"


class ScoreLibrary:
    """Collection of scores for a simulation.

    This class manages a library of scores that will be computed
    during the Tripoli-5 simulation.

    Attributes:
        scores: Dictionary mapping score names to Score objects.

    Examples:
        >>> library = ScoreLibrary()
        >>> library.add_score(flux_score)
        >>> library.add_score(keff_score)
        >>> score = library.get_score("fuel_flux")
    """

    def __init__(self) -> None:
        """Initialize empty ScoreLibrary."""
        self.scores: Dict[str, Score] = {}

    def add_score(self, score: Score) -> None:
        """Add a score to the library.

        Args:
            score: Score object to add.

        Raises:
            ValueError: If score with same name already exists.
        """
        if score.name in self.scores:
            raise ValueError(f"Score '{score.name}' already exists in library")
        self.scores[score.name] = score

    def remove_score(self, name: str) -> None:
        """Remove a score from the library.

        Args:
            name: Name of the score to remove.

        Raises:
            KeyError: If score not found in library.
        """
        if name not in self.scores:
            raise KeyError(f"Score '{name}' not found in library")
        del self.scores[name]

    def get_score(self, name: str) -> Score:
        """Retrieve a score from the library.

        Args:
            name: Name of the score to retrieve.

        Returns:
            Score object.

        Raises:
            KeyError: If score not found in library.
        """
        if name not in self.scores:
            raise KeyError(f"Score '{name}' not found in library")
        return self.scores[name]

    def list_scores(self) -> List[str]:
        """Get list of all score names in the library.

        Returns:
            List of score names.
        """
        return list(self.scores.keys())

    def __len__(self) -> int:
        """Return number of scores in the library."""
        return len(self.scores)

    def __repr__(self) -> str:
        """Return string representation of ScoreLibrary object."""
        return f"ScoreLibrary(scores={len(self.scores)})"
