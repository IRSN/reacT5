# pyT5: Python Interface for Tripoli-5 Monte-Carlo Code

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Python 3.9+](https://img.shields.io/badge/python-3.9+-blue.svg)](https://www.python.org/downloads/)

## Overview

**pyT5** is a user-friendly, object-oriented Python interface for the Tripoli-5 Monte-Carlo code, designed for modeling and simulating Pressurized Water Reactor (PWR) systems. It provides a high-level API for creating complex reactor geometries, from individual pin cells to full reactor cores.

### Key Features

- **Modular Architecture**: Object-oriented design with maximum modularity for easy use and maintenance
- **Multiple Geometry Levels**: Support for pin cells, fuel assemblies, colorsets, and full cores
- **Comprehensive Material Modeling**: Flexible material definition with temperature and nuclide composition
- **Simulation Control**: Full control over Monte-Carlo parameters, sources, and scores
- **Remote Computing**: Built-in support for HPC cluster execution
- **Type-Safe**: Complete type hints throughout the codebase
- **Well-Tested**: Comprehensive test suite with pytest

## Installation

### From Source

```bash
git clone https://github.com/IRSN/pyT5.git
cd pyT5
pip install -e .
```

### Development Installation

```bash
pip install -e ".[dev]"
```

## Quick Start

### Basic Pin Cell Model

```python
import pyT5

# Define materials
fuel = pyT5.Material(
    name="UO2_fuel",
    nuclides={"U235": 0.03, "U238": 0.97, "O16": 2.0},
    temperature=900.0,
    density=10.4,
    state="solid"
)

water = pyT5.Material(
    name="light_water",
    nuclides={"H1": 2.0, "O16": 1.0},
    temperature=300.0,
    density=1.0,
    state="liquid"
)

# Create material library
materials = pyT5.MaterialLibrary()
materials.add_material(fuel)
materials.add_material(water)

# Define pin cell geometry
pin = pyT5.PinCell(
    name="fuel_pin",
    pitch=1.26,
    height=365.76,
    fuel_radius=0.4096,
    clad_inner_radius=0.418,
    clad_outer_radius=0.475
)

# Calculate volumes
fuel_volume = pin.get_fuel_volume()
print(f"Fuel volume: {fuel_volume:.2f} cm³")
```

### Assembly Definition

```python
# Create a 17x17 assembly
assembly = pyT5.Assembly(
    name="17x17_assembly",
    lattice_type="square",
    n_pins_x=17,
    n_pins_y=17,
    pin_pitch=1.26,
    assembly_pitch=21.5
)

# Populate assembly with pins
for i in range(17):
    for j in range(17):
        # Skip guide tube positions
        if (i, j) not in [(5, 5), (8, 8), (11, 11)]:
            assembly.set_pin(i, j, pin)

print(f"Assembly contains {assembly.count_pins()} pins")
```

### Full Core Simulation

```python
# Define nuclear data
nuclear_data = pyT5.NuclearData(
    cross_section_library="path/to/xsections.dat",
    temperature=300.0
)
nuclear_data.validate()

# Create core geometry
core = pyT5.Core(
    name="PWR_core",
    core_type="square",
    n_assemblies_x=15,
    n_assemblies_y=15
)

# Place assemblies in core
for i in range(15):
    for j in range(15):
        core.set_assembly((i, j), assembly)

# Define neutron source
source = pyT5.NeutronSource(
    name="fission_source",
    source_type="criticality",
    intensity=1.0e6
)

# Define scores
scores = pyT5.ScoreLibrary()
keff_score = pyT5.Score(name="k_effective", score_type="keff")
flux_score = pyT5.Score(
    name="core_flux",
    score_type="flux",
    cells=["fuel_cell"]
)
scores.add_score(keff_score)
scores.add_score(flux_score)

# Set up simulation
sim = pyT5.Simulation(
    name="PWR_criticality",
    n_particles=10000,
    n_cycles=150,
    n_inactive=50,
    n_threads=8
)

sim.set_nuclear_data(nuclear_data)
sim.set_materials(materials)
sim.set_geometry(core)
sim.set_source(source)
sim.set_scores(scores)

# Run simulation
results = sim.run()

# Extract results
keff, keff_std = results.get_k_effective()
print(f"k-effective: {keff:.5f} ± {keff_std:.5f}")
```

### Visualization

```python
# Add geometry visualization
viz = pyT5.Visualization(
    name="xy_midplane",
    plot_type="2D",
    plane="xy",
    position=182.88,  # cm
    extent=(-150, 150, -150, 150),
    resolution=(1000, 1000)
)

sim.add_visualization(viz)
```

### Remote Computing

```python
# Configure remote execution
remote = pyT5.RemoteCompute(
    name="hpc_cluster",
    host="cluster.example.com",
    username="user",
    scheduler="slurm",
    queue="standard",
    walltime=24.0,
    nodes=4,
    cores_per_node=32
)

# Submit job
job_id = remote.submit_job(sim)
print(f"Job submitted with ID: {job_id}")

# Check status
status = remote.check_status(job_id)
print(f"Job status: {status}")

# Retrieve results when complete
results_dir = remote.retrieve_results(job_id)
```

## Core Components

### Materials (`pyT5.Material`)
- Define materials with nuclide composition
- Specify temperature and density
- Support for solid, liquid, and gas states

### Cells (`pyT5.Cell`)
- Geometric regions containing materials
- Volume and importance specifications
- Void cell support

### Geometry Classes
- **`PinCell`**: Cylindrical fuel pin geometry
- **`Assembly`**: Square or hexagonal pin lattices
- **`Colorset`**: Collections of assemblies
- **`Core`**: Full reactor core layout
- **`Reflector`**: Core reflector regions

### Simulation (`pyT5.Simulation`)
- Monte-Carlo parameter control
- Multi-threaded execution
- Integration of all simulation components

### Scores (`pyT5.Score`)
- Flux tallies
- Reaction rates
- k-effective calculations
- Energy-dependent scores
- Spatial mesh tallies

### Results (`pyT5.Results`)
- k-effective extraction with uncertainties
- Score value retrieval
- Statistical analysis
- Export functionality

## Documentation

Full documentation is available in the `docs/` directory and includes:

- API Reference
- Detailed Examples
- Best Practices
- Integration with Tripoli-5

## Development

### Running Tests

```bash
pytest
```

### Code Quality

```bash
# Run linting
ruff check src/

# Run type checking
mypy src/

# Format code
black src/ tests/
```

## Design Philosophy

pyT5 is inspired by the [PyDrag](https://pydrag.asnr.dev/PyDrag/index.html) package, providing a user-friendly, high-level modeling overlay for the Tripoli-5 API. The package emphasizes:

- **Simplicity**: Intuitive API for common reactor modeling tasks
- **Modularity**: Independent, reusable components
- **Type Safety**: Comprehensive type hints for IDE support
- **Extensibility**: Easy to extend with custom components

## Related Projects

- [Tripoli-5 Documentation](https://tripoli5.asnr.dev/documentation/examples/index.html)
- [Tripoli-5 Python API](https://tripoli5.asnr.dev/documentation/api/python-api.html)
- [PyDrag Package](https://pydrag.asnr.dev/PyDrag/index.html)

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## Citation

If you use pyT5 in your research, please cite:

```bibtex
@software{pyT5,
  title = {pyT5: Python Interface for Tripoli-5 Monte-Carlo Code},
  author = {IRSN},
  year = {2025},
  url = {https://github.com/IRSN/pyT5}
}
```

## Support

For issues, questions, or contributions, please visit our [GitHub repository](https://github.com/IRSN/pyT5).
