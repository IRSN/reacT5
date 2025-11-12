"""Visualization module for pyT5.

This module provides classes for visualizing geometry and simulation
results in Tripoli-5.
"""

from typing import List, Optional, Tuple


class Visualization:
    """Handles geometry visualization and plotting instructions.

    This class configures visualization parameters for rendering
    the simulation geometry in 2D or 3D views.

    Attributes:
        name: Unique identifier for the visualization.
        plot_type: Type of plot ('2D' or '3D').
        plane: Plane for 2D plots ('xy', 'xz', 'yz').
        position: Position along the perpendicular axis for 2D plots.
        extent: Spatial extent of the plot region.
        resolution: Plot resolution in pixels.

    Examples:
        >>> viz = Visualization(
        ...     name="xy_midplane",
        ...     plot_type="2D",
        ...     plane="xy",
        ...     position=182.88,
        ...     extent=(-150, 150, -150, 150),
        ...     resolution=(800, 800)
        ... )
    """

    def __init__(
        self,
        name: str,
        plot_type: str = "2D",
        plane: str = "xy",
        position: float = 0.0,
        extent: Optional[Tuple[float, float, float, float]] = None,
        resolution: Tuple[int, int] = (800, 800),
    ) -> None:
        """Initialize Visualization object.

        Args:
            name: Unique identifier for the visualization.
            plot_type: Type of plot. Either '2D' or '3D'. Defaults to '2D'.
            plane: Plotting plane for 2D plots. One of 'xy', 'xz', or 'yz'.
                Defaults to 'xy'.
            position: Position along perpendicular axis for 2D plots in cm.
                Defaults to 0.0.
            extent: Spatial extent as (xmin, xmax, ymin, ymax) for 2D plots
                in cm. If None, will be auto-determined. Defaults to None.
            resolution: Plot resolution as (width, height) in pixels.
                Defaults to (800, 800).

        Raises:
            ValueError: If plot_type or plane is invalid, or resolution is
                non-positive.
        """
        if plot_type not in ("2D", "3D"):
            raise ValueError(f"Invalid plot_type '{plot_type}', must be '2D' or '3D'")
        if plane not in ("xy", "xz", "yz"):
            raise ValueError(f"Invalid plane '{plane}', must be 'xy', 'xz', or 'yz'")
        if resolution[0] <= 0 or resolution[1] <= 0:
            raise ValueError("Resolution must have positive width and height")

        self.name = name
        self.plot_type = plot_type
        self.plane = plane
        self.position = position
        self.extent = extent
        self.resolution = resolution

    def set_plane(self, plane: str, position: float) -> None:
        """Set the plotting plane and position.

        Args:
            plane: Plotting plane ('xy', 'xz', or 'yz').
            position: Position along perpendicular axis in cm.

        Raises:
            ValueError: If plane is invalid.
        """
        if plane not in ("xy", "xz", "yz"):
            raise ValueError(f"Invalid plane '{plane}', must be 'xy', 'xz', or 'yz'")
        self.plane = plane
        self.position = position

    def set_extent(
        self, xmin: float, xmax: float, ymin: float, ymax: float
    ) -> None:
        """Set the spatial extent of the plot.

        Args:
            xmin: Minimum x-coordinate in cm.
            xmax: Maximum x-coordinate in cm.
            ymin: Minimum y-coordinate in cm.
            ymax: Maximum y-coordinate in cm.

        Raises:
            ValueError: If max values are not greater than min values.
        """
        if xmax <= xmin or ymax <= ymin:
            raise ValueError("Max coordinates must be greater than min coordinates")
        self.extent = (xmin, xmax, ymin, ymax)

    def set_resolution(self, width: int, height: int) -> None:
        """Set the plot resolution.

        Args:
            width: Plot width in pixels.
            height: Plot height in pixels.

        Raises:
            ValueError: If width or height is non-positive.
        """
        if width <= 0 or height <= 0:
            raise ValueError("Resolution must have positive width and height")
        self.resolution = (width, height)

    def __repr__(self) -> str:
        """Return string representation of Visualization object."""
        if self.plot_type == "2D":
            return (
                f"Visualization(name='{self.name}', type='2D', plane='{self.plane}', "
                f"position={self.position} cm, resolution={self.resolution})"
            )
        else:
            return f"Visualization(name='{self.name}', type='3D')"
