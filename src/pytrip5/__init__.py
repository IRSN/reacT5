"""
pytrip5 - Python Interface for Tripoli-5 Monte Carlo Code

A user-friendly, PyDrag-inspired interface for PWR reactor modeling
with Tripoli-5 Monte Carlo code.

Example:
    >>> import pytrip5 as pt5
    >>>
    >>> # Define materials (PyDrag style)
    >>> materials = pt5.Materials()
    >>> materials.UO2.set_enrichment('U235', 0.04)
    >>> materials.water.set_temperature(600, 'K')
    >>>
    >>> # Define geometry
    >>> F = ['UO2', 0.4095, 'void', 0.4180, 'Zr4', 0.4750]
    >>> geom = pt5.Geometry([[F]], PinPitch=1.26, AssemblyPitch=1.26, ActiveHeight=20.0)
    >>>
    >>> # Run simulation
    >>> sim = pt5.Simulation("pin_cell", n_cycles=100, n_particles=10000)
    >>> results = sim.run(materials, geom)
"""

__version__ = "0.1.0"
__author__ = "IRSN"

# Core exceptions
from .core import (
    PyTrip5Exception,
    ValidationError,
    ConfigurationError,
    SimulationError,
)

# Materials module - PyDrag style
from .materials import (
    Materials,
    Mix,
    create_uo2,
    create_water,
    create_zircaloy,
)

# Geometry module - simplified interface
from .geometry_simple import (
    Geometry,
    Pin,
    Power,
    create_pincell_geometry,
    create_assembly_17x17,
)

# Simulation module
from .simulation import (
    Simulation,
    Deplete,
    CriticalityCalculation,
    Score,
    SimulationResults,
    KeffResult,
)

# Keep old geometry for backward compatibility (mark as deprecated)
from . import geometry as _geometry_detailed
from . import cells
from . import nucleardata

__all__ = [
    # Version
    '__version__',

    # Exceptions
    'PyTrip5Exception',
    'ValidationError',
    'ConfigurationError',
    'SimulationError',

    # Materials (PyDrag-style)
    'Materials',
    'Mix',
    'create_uo2',
    'create_water',
    'create_zircaloy',

    # Geometry (simplified)
    'Geometry',
    'Pin',
    'Power',
    'create_pincell_geometry',
    'create_assembly_17x17',

    # Simulation
    'Simulation',
    'Deplete',
    'CriticalityCalculation',
    'Score',
    'SimulationResults',
    'KeffResult',

    # Legacy modules (for advanced users)
    'cells',
    'nucleardata',
]


def check_tripoli5():
    """
    Check if Tripoli-5 is installed and accessible.

    Returns
    -------
    bool
        True if Tripoli-5 is available
    """
    try:
        import tripoli5
        return True
    except ImportError:
        return False


def get_info():
    """
    Get package information.

    Returns
    -------
    dict
        Package information including version and dependencies
    """
    info = {
        'version': __version__,
        'tripoli5_available': check_tripoli5(),
        'description': 'Python interface for Tripoli-5 Monte Carlo code',
        'style': 'PyDrag-inspired simplified API',
    }

    if info['tripoli5_available']:
        try:
            import tripoli5
            info['tripoli5_version'] = getattr(tripoli5, '__version__', 'unknown')
        except:
            pass

    return info


# Print warning if Tripoli-5 not available
if not check_tripoli5():
    import warnings
    warnings.warn(
        "Tripoli-5 is not installed or not accessible. "
        "pytrip5 provides the interface but requires Tripoli-5 "
        "to run actual simulations.",
        UserWarning
    )
