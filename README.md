# pytrip5

Python interface for Tripoli-5 Monte-Carlo code for PWR reactor simulations.

## Description

**pytrip5** is a high-level Python package that provides a user-friendly interface for modeling and simulating Pressurized Water Reactors (PWR) using the Tripoli-5 Monte-Carlo particle transport code. The package is inspired by the PyDrag package and built on top of the Tripoli-5 Python API.

## Features

pytrip5 enables modeling and simulation of PWR reactors at multiple levels:

- **Pin cells**: Individual fuel pin modeling
- **Fuel assemblies**: Support for different fuel compositions (UOX, MOX, etc.) and assembly geometries (17×17, 15×15, etc.)
- **Colorsets**: Groups of fuel assemblies
- **Reactor cores**: Full core modeling with reflectors

## Key Components

The package provides object-oriented classes for:

- **Nuclear Data**: Cross-sections and decay data management
- **Materials**: Nuclide compositions with temperature-dependent properties
- **Cells**: Geometric cells containing materials
- **Geometry**: Hierarchical geometry definition (pin cells, assemblies, colorsets, cores, reflectors)
- **Neutron Source**: Initial neutron source specification
- **Neutron Media**: Transport media definition
- **Scores**: Tally and scoring definitions
- **Visualization**: Geometry visualization tools
- **Simulation**: Calculation parameters and execution
- **Results**: Output processing and analysis (k-effective, fluxes, etc.)

## Installation

```bash
# From source
git clone https://gitlab.asnr.fr/IRSN/pytrip5.git
cd pytrip5
pip install -e .

# With visualization support
pip install -e ".[viz]"

# With development dependencies
pip install -e ".[dev]"
```

## Requirements

- Python >= 3.8
- NumPy >= 1.20.0
- SciPy >= 1.7.0
- Tripoli-5 (must be installed separately)

## Quick Start

```python
import pytrip5 as pt5

# Load nuclear data
nuclear_data = pt5.NuclearData("path/to/cross_sections.data")

# Define materials
fuel = pt5.Material("UO2", temperature=900.0)
fuel.add_nuclide("U235", 0.04)
fuel.add_nuclide("U238", 0.96)
fuel.add_nuclide("O16", 2.0)

water = pt5.Material("H2O", temperature=600.0)
water.add_nuclide("H1", 2.0)
water.add_nuclide("O16", 1.0)

# Create a pin cell geometry
pin = pt5.PinCell(
    name="fuel_pin",
    fuel_radius=0.4095,
    clad_inner_radius=0.4180,
    clad_outer_radius=0.4750,
    pitch=1.26
)

# Assign materials to regions
pin.set_fuel_material(fuel)
pin.set_clad_material(clad)
pin.set_coolant_material(water)

# Create an assembly
assembly = pt5.Assembly(
    name="UOX_17x17",
    pin_layout=(17, 17),
    pitch=21.5
)
assembly.add_pin(pin, positions="all")

# Set up simulation
sim = pt5.Simulation(
    name="pin_cell_calc",
    n_cycles=500,
    n_particles_per_cycle=10000,
    n_threads=8
)

# Add scores
sim.add_score(pt5.Score.keff())
sim.add_score(pt5.Score.flux(energy_groups=50))

# Run calculation
results = sim.run(assembly)

# Get results
k_eff = results.get_keff()
print(f"k-effective: {k_eff.mean} ± {k_eff.std}")
```

## Examples

See the `examples/` directory for detailed examples:

- `examples/pin_cell_example.py`: Simple pin cell calculation
- `examples/assembly_example.py`: Full assembly modeling
- `examples/core_example.py`: Reactor core simulation

## Documentation

Full documentation is available at: https://pytrip5.readthedocs.io

- [User Guide](https://pytrip5.readthedocs.io/guide)
- [API Reference](https://pytrip5.readthedocs.io/api)
- [Examples](https://pytrip5.readthedocs.io/examples)

## Development

pytrip5 follows Python best practices with:

- Object-oriented design with maximum modularity
- Type hints for better code quality
- Comprehensive documentation
- Unit tests
- Clean, readable code

## References

- Tripoli-5 Documentation: https://tripoli5.asnr.dev/documentation/index.html
- PyDrag Package: https://pydrag.asnr.dev/PyDrag/index.html

## License

MIT License - see LICENSE file for details

## Contributing

Contributions are welcome! Please feel free to submit issues or pull requests.

## Contact

For questions and support, please contact IRSN.
