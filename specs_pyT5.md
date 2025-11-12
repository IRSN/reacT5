# pyT5: description

Python interface for Tripoli-5 Monte-Carlo code computing.

pyT5 handles modeling and simulation of PWR reactors at different levels:
* pin cells,
* fuel assemblies,
* colorset of several fuel assemblies,
* reactor core.
These objects may be surrounded by reflective materials.

To make a computation, the user must define :
* The nuclear data to be used (cross-sections, decay-data) based on input files provided by the user in the required format,
* The materials used in the computation (name, temperature, nuclide concentrations, ...) in the different parts of the geometry,
* The cells used in the computation in the different parts of the geometry (the cells contain the different materials),
* The geometry of the objects to be modeled (pin cell, assembly, colorset of assemblies, core, reflector). They contain the cells.
* The initial neutron source,
* The simulation parameters (number of cycles, number of events, name, number of threads, ...),
* The instructions to run the calculation on remote ressources,
* The instruction to get the desired results (e.g. the k-effective mean valeu and its variance).

