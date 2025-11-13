# pytrip5

**Python Interface for Tripoli-5 Monte Carlo Code** - A PyDrag-inspired, user-friendly API for PWR reactor simulations.

## Description

**pytrip5** is a high-level Python package that provides a simplified, PyDrag-style interface for modeling and simulating Pressurized Water Reactors (PWR) using the Tripoli-5 Monte Carlo particle transport code. Inspired by IRSN's PyDrag package, pytrip5 aims for maximum simplicity and user-friendliness while leveraging the power of Tripoli-5.

**Design Philosophy**: Like PyDrag does for Dragon, pytrip5 provides a high-level modeling overlay for Tripoli-5, allowing users to express complex reactor models in just a few lines of simple, intuitive Python code.

## Key Features

- **PyDrag-style simplicity**: Define full reactor models in ~30 lines of code
- **Pre-defined materials**: `materials.UO2`, `materials.water`, `materials.Zr4` with simple setters
- **Concise geometry**: Pin cells and assemblies defined as nested lists
- **Single-call execution**: `Deplete(materials, geometry, power)` or `Simulation.run()`
- **Wraps Tripoli-5**: High-level interface backed by Tripoli-5's robust Monte Carlo engine

## Modeling Capabilities

pytrip5 enables modeling and simulation of PWR reactors at multiple levels:

- **Pin cells**: Individual fuel pin modeling
- **Fuel assemblies**: 17×17, 15×15, and custom configurations
- **Colorsets**: Groups of fuel assemblies
- **Reactor cores**: Full core modeling with reflectors

## Installation

```bash
# Clone the repository
git clone https://gitlab.asnr.fr/IRSN/pytrip5.git
cd pytrip5

# Install the package
pip install -e .

# With development dependencies
pip install -e ".[dev]"
```

**Requirements:**
- Python >= 3.8
- NumPy >= 1.20.0
- SciPy >= 1.7.0
- **Tripoli-5** (must be installed separately)

## Quick Start - PyDrag Style

Here's a complete pin cell calculation in PyDrag style:

```python
import pytrip5 as pt5

# 1. Define materials (simple setters)
materials = pt5.Materials()
materials.set_tfuel(900, 'K')
materials.UO2.set_density(10.5)
materials.UO2.set_enrichment('U235', 0.04)  # 4% enriched

materials.water.set_temperature(600, 'K')
materials.water.set_density(0.7)
materials.water.set_boron(600)  # ppm

# 2. Define geometry (concise list notation)
F = ['UO2', 0.4095, 'void', 0.4180, 'Zr4', 0.4750]  # Fuel pin
geometry = pt5.Geometry([[F]], PinPitch=1.26, AssemblyPitch=1.26, ActiveHeight=20.0)

# 3. Run simulation
sim = pt5.Simulation("pin_cell", n_cycles=500, n_particles=10000)
results = sim.run(materials, geometry)

# 4. Get results
keff = results.get_keff()
print(f"k-effective = {keff.mean:.5f} ± {keff.std:.5f}")
```

## 17x17 Assembly Example

```python
import pytrip5 as pt5

# Materials
materials = pt5.Materials()
materials.UO2.set_enrichment('U235', 0.04)
materials.water.set_boron(600)

# Pin definitions
F = pt5.Pin.fuel_pin(0.4095, 0.4180, 0.4750)
T = pt5.Pin.guide_tube(0.5615, 0.6020)

# Assembly layout (1/8 symmetry)
layout = [
    [T, F, F, F, T, F, F, F, F],
    [F, F, F, F, F, F, F, F],
    [F, F, T, F, F, F, F],
    # ... 1/8 octant specification
]

geometry = pt5.Geometry(layout, PinPitch=1.26, AssemblyPitch=21.5,
                        ActiveHeight=365.76, symmetry='1/8')

power = pt5.Power(nbAssemblies=157, corePower=2785)

# Depletion calculation (PyDrag-style)
burnup, keff = pt5.Deplete(materials, geometry, power)
```

## API Overview

### Materials (PyDrag-inspired)

```python
materials = pt5.Materials()

# Pre-defined materials with simple setters
materials.UO2.set_density(10.5)
materials.UO2.set_enrichment('U235', 0.04)
materials.water.set_temperature(600, 'K')
materials.water.set_boron(600)  # ppm
materials.Zr4.set_temperature(600, 'K')

# Also available: Inconel, SS304, B4C, AIC, Pyrex, void

# Create custom materials
mox = materials.make_mix('MOX', temperature=900)
mox.set_density(10.4)
mox.add_element('Pu239', 0.05)
```

### Geometry (Simplified)

```python
# Pin cell definition (PyDrag style - lists)
F = ['UO2', 0.4095, 'void', 0.4180, 'Zr4', 0.4750]
T = ['water', 0.5615, 'Zr4', 0.6020]

# Or using helper
F = pt5.Pin.fuel_pin(0.4095, 0.4180, 0.4750)
T = pt5.Pin.guide_tube(0.5615, 0.6020)

# Assembly layout (nested lists with symmetry)
layout = [[F, F, T], [F, F], [T]]  # 1/8 symmetry

geom = pt5.Geometry(layout, PinPitch=1.26, AssemblyPitch=21.5,
                    ActiveHeight=365.76, symmetry='1/8')
```

### Simulation

```python
# Criticality calculation
sim = pt5.Simulation("calc_name", n_cycles=500, n_particles=10000)
sim.add_score('keff')
sim.add_score('flux', energy_groups=50)
results = sim.run(materials, geometry)

# Depletion (PyDrag-style function)
burnup, keff = pt5.Deplete(materials, geometry, power)
```

## Examples

See the `examples/` directory for detailed examples:

- `examples/simple_pin_cell.py` - Basic pin cell calculation
- `examples/assembly_17x17.py` - Full 17×17 assembly
- `examples/core_example.py` - Full core modeling (coming soon)

## Relationship to Tripoli-5

pytrip5 is a **high-level interface** that wraps Tripoli-5:

- **pytrip5**: Provides PyDrag-style simplicity for PWR modeling
- **Tripoli-5**: Underlying Monte Carlo engine (must be installed)

```
┌─────────────────────────────────────┐
│  User Code (PyDrag-style)          │
│  materials = pt5.Materials()        │
│  geom = pt5.Geometry(...)           │
└─────────────────┬───────────────────┘
                  │
┌─────────────────▼───────────────────┐
│  pytrip5 (High-level API)          │
│  - Materials, Geometry, Simulation  │
│  - PyDrag-inspired simplicity       │
└─────────────────┬───────────────────┘
                  │
┌─────────────────▼───────────────────┐
│  Tripoli-5 Python API               │
│  - tripoli5.agora (Geometry)        │
│  - tripoli5.materials               │
│  - tripoli5.delos (Nuclear data)    │
└─────────────────────────────────────┘
```

## Comparison: PyDrag for Dragon vs pytrip5 for Tripoli-5

| Feature | PyDrag (Dragon) | pytrip5 (Tripoli-5) |
|---------|-----------------|---------------------|
| Purpose | Deterministic transport | Monte Carlo transport |
| Code | Dragon 5 | Tripoli-5 |
| Style | Simple, ~30 lines | Simple, ~30 lines |
| Materials | `materials.UO2.set_*()` | `materials.UO2.set_*()` |
| Geometry | List-based pins | List-based pins |
| Execution | `Deplete(m, g, p)` | `Deplete(m, g, p)` |
| Philosophy | High-level overlay | High-level overlay |

## Documentation

- **User Guide**: [docs/user_guide.md](docs/user_guide.md) (coming soon)
- **API Reference**: [docs/api.md](docs/api.md) (coming soon)
- **Examples**: [examples/](examples/)
- **Tripoli-5 Docs**: https://tripoli5.asnr.dev/documentation/
- **PyDrag Reference**: https://pydrag.asnr.dev/PyDrag/

## Development

pytrip5 follows Python best practices:

- **Object-oriented** design with maximum modularity
- **Type hints** for better code quality
- **PyDrag-inspired** API for ease of use
- **Comprehensive** examples and documentation

```bash
# Run tests (coming soon)
pytest tests/

# Code formatting
black src/

# Type checking
mypy src/
```

## Project Status

**Status**: Alpha - Active Development

- ✅ Core architecture and PyDrag-style API design
- ✅ Materials module with simple setters
- ✅ Simplified geometry module
- ✅ Simulation framework
- 🚧 Full Tripoli-5 AGORA integration (requires Tripoli-5 access)
- 🚧 Complete examples and test suite
- 📋 Documentation

## References

- **Tripoli-5**: https://tripoli5.asnr.dev/documentation/
- **PyDrag**: https://pydrag.asnr.dev/PyDrag/
- **Dragon**: Deterministic lattice code by École Polytechnique de Montréal

## License

MIT License - see [LICENSE](LICENSE) file for details

## Contributing

Contributions are welcome! Please feel free to submit issues or pull requests.

## Contact

**IRSN** - Institut de Radioprotection et de Sûreté Nucléaire

For questions about pytrip5, please open an issue on the repository.

---

**Note**: pytrip5 provides the interface but requires Tripoli-5 to run actual simulations. Tripoli-5 must be installed separately and is developed by CEA/IRSN/EDF.
