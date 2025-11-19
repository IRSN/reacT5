"""pyT5: Python interface for Tripoli-5 Monte-Carlo code computing.

pyT5 provides a user-friendly, object-oriented interface for modeling
and simulating PWR reactors at different levels: pin cells, fuel assemblies,
colorsets, and full reactor cores.

Example:
    >>> import pyT5
    >>> # Define materials
    >>> fuel = pyT5.Material("UO2", {"U235": 0.03, "U238": 0.97, "O16": 2.0})
    >>> # Create geometry
    >>> pin = pyT5.PinCell("fuel_pin", pitch=1.26, height=365.76, ...)
    >>> # Set up simulation
    >>> sim = pyT5.Simulation("PWR_criticality", n_particles=10000)
    >>> results = sim.run()
"""

__version__ = "0.1.0"
__author__ = "pyT5 Development Team"

# Core imports
from .nuclear_data import NuclearData
from .materials import Material, MaterialLibrary
from .cells import Cell, CellLibrary
from .geometry import (
    GeometryBase,
    PinCell,
    Assembly,
    Colorset,
    Core,
    Reflector,
)
from .source import NeutronSource, NeutronMedia
from .visualization import Visualization
from .scores import Score, ScoreLibrary
from .simulation import Simulation
from .remote import RemoteCompute
from .results import Results

# Define public API
__all__ = [
    # Version info
    "__version__",
    "__author__",
    # Nuclear data
    "NuclearData",
    # Materials
    "Material",
    "MaterialLibrary",
    # Cells
    "Cell",
    "CellLibrary",
    # Geometry
    "GeometryBase",
    "PinCell",
    "Assembly",
    "Colorset",
    "Core",
    "Reflector",
    # Source
    "NeutronSource",
    "NeutronMedia",
    # Visualization
    "Visualization",
    # Scores
    "Score",
    "ScoreLibrary",
    # Simulation
    "Simulation",
    # Remote computing
    "RemoteCompute",
    # Results
    "Results",
]
