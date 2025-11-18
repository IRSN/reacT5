"""pytrip5 - Python high-level interface for Tripoli-5.

pytrip5 provides a fluent, Pythonic API for building and simulating
full-core PWR models using the Tripoli-5 Monte Carlo transport code.

Basic usage:
    >>> from pytrip5 import Core, MockTripoliAdapter, SimulationConfig, Runner
    >>> from pytrip5.score import KeffectiveScore, PinPowerScore
    >>>
    >>> # Create a simple core
    >>> core = Core.simple_demo_3x3()
    >>>
    >>> # Configure simulation
    >>> config = SimulationConfig.quick_criticality(
    ...     scores=[KeffectiveScore(), PinPowerScore('pin_powers')]
    ... )
    >>>
    >>> # Run with mock adapter (for testing/development)
    >>> adapter = MockTripoliAdapter()
    >>> result = Runner.run(adapter, core, config)
    >>>
    >>> print(f"k-eff: {result.k_eff:.4f}")
    >>> print(f"Pin powers shape: {result.pin_powers.shape}")

For production runs with real Tripoli-5:
    >>> from pytrip5 import TripoliAdapter  # Requires tripoli5 package
    >>> adapter = TripoliAdapter()  # doctest: +SKIP
    >>> result = Runner.run(adapter, core, config)  # doctest: +SKIP
"""

__version__ = '0.1.0'
__author__ = 'IRSN'

# Core domain models
from pytrip5.core import (
    Material,
    Pin,
    Assembly,
    Core
)

# Adapters
from pytrip5.adapter import (
    TripoliAdapter,
    MockTripoliAdapter,
    TripoliModel,
    TripoliSimulation
)

# Simulation
from pytrip5.simulation import (
    SimulationConfig,
    RunResult,
    Runner
)

# Scores
from pytrip5.score import (
    Score,
    KeffectiveScore,
    PinPowerScore,
    FluxScore,
    ReactionRateScore,
    DoseScore,
    create_standard_scores,
    create_minimal_scores
)

# I/O
from pytrip5 import io

__all__ = [
    # Version
    '__version__',
    '__author__',

    # Core models
    'Material',
    'Pin',
    'Assembly',
    'Core',

    # Adapters
    'TripoliAdapter',
    'MockTripoliAdapter',
    'TripoliModel',
    'TripoliSimulation',

    # Simulation
    'SimulationConfig',
    'RunResult',
    'Runner',

    # Scores
    'Score',
    'KeffectiveScore',
    'PinPowerScore',
    'FluxScore',
    'ReactionRateScore',
    'DoseScore',
    'create_standard_scores',
    'create_minimal_scores',

    # I/O module
    'io',
]
