# pyT5 Documentation

Welcome to the pyT5 documentation! pyT5 is a Python interface for the Tripoli-5 Monte-Carlo code, designed for modeling and simulating PWR reactor systems.

## Contents

- [Getting Started](getting_started.md)
- [API Reference](api_reference.md)
- [Examples](examples/)
  - [Pin Cell Example](examples/pin_cell_example.md)
  - [Assembly Example](examples/assembly_example.md)
  - [Core Simulation Example](examples/core_simulation_example.md)
- [Best Practices](best_practices.md)
- [Integration with Tripoli-5](tripoli5_integration.md)

## Quick Links

- [GitHub Repository](https://github.com/IRSN/pyT5)
- [Tripoli-5 Documentation](https://tripoli5.asnr.dev/documentation/examples/index.html)
- [PyDrag Package](https://pydrag.asnr.dev/PyDrag/index.html)

## Overview

pyT5 provides an object-oriented interface for creating complex reactor models:

```python
import pyT5

# Create materials
fuel = pyT5.Material(name="UO2", nuclides={"U235": 0.03, "U238": 0.97, "O16": 2.0})

# Define geometry
pin = pyT5.PinCell(name="fuel_pin", pitch=1.26, height=365.76, ...)

# Set up simulation
sim = pyT5.Simulation(name="PWR", n_particles=10000)
results = sim.run()
```

## Features

- Modular, object-oriented architecture
- Support for pin cells, assemblies, and full cores
- Comprehensive material modeling
- Remote computing support
- Type-safe with full type hints
- Extensive test coverage
