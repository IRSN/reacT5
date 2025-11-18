# pytrip5

[![CI](https://github.com/IRSN/reacT5/actions/workflows/ci.yml/badge.svg)](https://github.com/IRSN/reacT5/actions/workflows/ci.yml)
[![Python 3.9+](https://img.shields.io/badge/python-3.9+-blue.svg)](https://www.python.org/downloads/)
[![License](https://img.shields.io/badge/license-MIT-green.svg)](LICENSE)

**pytrip5** is a Python high-level interface for [Tripoli-5](https://tripoli5.asnr.dev/) enabling full-core PWR (Pressurized Water Reactor) modelling and simulations.

## Features

- **Fluent, Pythonic API** for building reactor core models
- **Type-annotated** domain models (Material, Pin, Assembly, Core)
- **Adapter pattern** for clean separation from Tripoli-5 API
- **Mock adapter** for testing and development without Tripoli-5 installation
- **Comprehensive scoring** (k-eff, pin powers, flux distributions, reaction rates)
- **I/O utilities** for JSON, HDF5, and CSV data exchange
- **Parameter sweeps** for sensitivity studies
- **Full test coverage** with pytest
- **Example notebooks** for quick start

## Quick Start

### Installation

```bash
pip install -e .
```

For development with testing dependencies:

```bash
pip install -e ".[dev]"
```

### Basic Usage

```python
from pytrip5 import Core, MockTripoliAdapter, SimulationConfig, Runner
from pytrip5.score import KeffectiveScore, PinPowerScore

# Create a simple 3x3 core
core = Core.simple_demo_3x3()

# Configure simulation
config = SimulationConfig.quick_criticality(
    scores=[KeffectiveScore(), PinPowerScore('pin_powers')],
    seed=42
)

# Run with mock adapter (for testing/development)
adapter = MockTripoliAdapter()
result = Runner.run(adapter, core, config)

print(f"k-effective: {result.k_eff_with_uncertainty}")
print(f"Pin powers shape: {result.pin_powers.shape}")
```

### Using Real Tripoli-5

For production runs with real Tripoli-5:

```python
from pytrip5 import TripoliAdapter

# Requires tripoli5 package installed
adapter = TripoliAdapter()
result = Runner.run(adapter, core, config)
```

## Architecture

```
pytrip5/
├── core.py           # Domain model: Material, Pin, Assembly, Core
├── adapter.py        # Tripoli-5 API adapter (real + mock)
├── simulation.py     # Runner, SimulationConfig, RunResult
├── score.py          # Score abstractions (k-eff, flux, power, etc.)
├── io.py             # Import/export utilities
└── tests/            # Comprehensive unit tests
```

## Creating Custom Models

### Materials

```python
from pytrip5 import Material

fuel = Material(
    name='UO2_4.5%',
    density=10.4,  # g/cm³
    compositions={
        'U235': 0.045,
        'U238': 0.955,
        'O16': 2.0
    },
    temperature=900.0  # Kelvin
)
```

### Assemblies and Cores

```python
from pytrip5 import Pin, Assembly, Core

# Create fuel pin
pin = Pin(id='fuel_std', radius=0.475, material=fuel, pitch=1.26)

# Create 17x17 pin lattice
pins = [[pin for _ in range(17)] for _ in range(17)]
assembly = Assembly(id='ASM_4.5', pitch=21.5, pins=pins, enrichment=4.5)

# Create core layout
layout = [
    ['ASM_4.5', 'ASM_4.5', 'ASM_4.5'],
    ['ASM_4.5', 'ASM_4.5', 'ASM_4.5'],
    ['ASM_4.5', 'ASM_4.5', 'ASM_4.5']
]

core = Core(
    assemblies={'ASM_4.5': assembly},
    layout=layout,
    boron_concentration=500.0  # ppm
)
```

## Simulation Configuration

### Quick Testing

```python
config = SimulationConfig.quick_criticality(
    scores=[KeffectiveScore(), PinPowerScore('pin_powers')],
    seed=42
)
```

### Production Runs

```python
config = SimulationConfig.production_criticality(
    scores=[
        KeffectiveScore(),
        PinPowerScore('pin_powers'),
        FluxScore('thermal_flux', energy_bounds=[0, 0.625e-6]),
        FluxScore('fast_flux', energy_bounds=[0.1, 20.0])
    ],
    seed=12345
)
```

### Custom Configuration

```python
config = SimulationConfig(
    criticality=True,
    particles_per_batch=100000,
    active_batches=200,
    inactive_batches=50,
    scores=[...],
    seed=42,
    parallel_tasks=8  # For HPC runs
)
```

## Parameter Sweeps

```python
from pytrip5 import Runner

# Sweep boron concentration
boron_values = [0, 500, 1000, 1500]
results = Runner.parameter_sweep(
    adapter,
    core,
    'boron_concentration',
    boron_values,
    config
)

# Analyze results
for boron, result in results.items():
    print(f"Boron {boron} ppm: k-eff = {result.k_eff:.5f}")
```

## Saving and Loading

### Core Configuration

```python
from pytrip5 import io

# Save
io.save_core_json(core, 'core_config.json')

# Load
core = io.load_core_json('core_config.json')
```

### Simulation Results

```python
# Save to JSON
io.save_results_json(result, 'results.json')

# Save to HDF5 (requires h5py)
io.save_results_hdf5(result, 'results.h5')

# Export pin powers to CSV
io.export_pin_powers_csv(result.pin_powers, 'pin_powers.csv')

# Export summary
io.export_summary_txt(result, 'summary.txt')
```

## Examples

See `examples/notebooks/quickstart.py` for a comprehensive tutorial covering:

- Building core models
- Running simulations
- Analyzing results
- Visualizing pin powers
- Parameter sweeps
- Data I/O

To run the notebook:

```bash
# Convert to Jupyter notebook (requires jupytext)
jupytext --to notebook examples/notebooks/quickstart.py

# Or run as Python script
python examples/notebooks/quickstart.py
```

## Testing

Run the test suite:

```bash
pytest pytrip5/tests/ -v
```

Run with coverage:

```bash
pytest pytrip5/tests/ --cov=pytrip5 --cov-report=html
```

### Testing Without Tripoli-5

All tests use `MockTripoliAdapter` by default and don't require Tripoli-5 installation. For integration tests with real Tripoli-5, set:

```bash
export TRIPOLI_PRESENT=1
pytest pytrip5/tests/ -v -m integration
```

## Requirements

### Runtime

- Python ≥ 3.9
- numpy
- (Optional) h5py for HDF5 I/O

### Development

- pytest
- pytest-cov
- black (formatting)
- ruff (linting)

### Production

- Tripoli-5 Python API (for real simulations)

## Tripoli-5 Installation

pytrip5 requires the Tripoli-5 Python API for production runs. Tripoli-5 is developed by CEA/ASNR/EDF and may have licensing restrictions.

See [Tripoli-5 documentation](https://tripoli5.asnr.dev/documentation/api/python-api.html) for installation instructions.

**Note:** Development and testing can be done entirely with `MockTripoliAdapter` without Tripoli-5.

## Design Principles

1. **API Ergonomics** — Inspired by [PyDrag](https://gitlab.extra.irsn.fr/PyDrag/PyDrag), pytrip5 provides a fluent, composable API
2. **Type Safety** — Full PEP 484 type annotations for IDE support and type checking
3. **Testability** — Mock adapter enables testing without Tripoli-5
4. **Separation of Concerns** — Adapter pattern isolates Tripoli-5 API details
5. **Production Ready** — Comprehensive tests, documentation, and CI/CD

## Contributing

Contributions are welcome! Please:

1. Fork the repository
2. Create a feature branch
3. Add tests for new functionality
4. Ensure all tests pass
5. Submit a pull request

## References

- [Tripoli-5 Documentation](https://tripoli5.asnr.dev/)
- [Tripoli-5 Python API](https://tripoli5.asnr.dev/documentation/api/python-api.html)
- [Tripoli-5 Scores](https://tripoli5.asnr.dev/documentation/examples/features/score.html)
- [PyDrag (IRSN)](https://gitlab.extra.irsn.fr/PyDrag/PyDrag)

## License

MIT License. See LICENSE file for details.

## Citation

If you use pytrip5 in your research, please cite:

```bibtex
@software{pytrip5,
  title = {pytrip5: Python Interface for Tripoli-5 Monte Carlo Code},
  author = {IRSN},
  year = {2024},
  url = {https://github.com/IRSN/reacT5}
}
```

## Support

For issues, questions, or feature requests, please open an issue on GitHub.

## Acknowledgments

- CEA/ASNR/EDF for Tripoli-5 development
- IRSN for PyDrag API design inspiration
