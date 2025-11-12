# pyT5: description

Python interface for Tripoli-5 Monte-Carlo code computing.

pyT5 handles modeling and simulation of PWR reactors at different levels:
* pin cells,
* fuel assemblies,
* colorset of several fuel assemblies,
* reactor core.
These objects may be surrounded by reflective materials.

To make a computation, the user must define:
* The nuclear data to be used (cross-sections, decay-data) based on input files provided by the user in the required format,
* The materials used in the computation (name, temperature, nuclide concentrations, ...) in the different parts of the geometry,
* The cells used in the computation in the different parts of the geometry (the cells contain the different materials),
* The geometry of the objects to be modeled (pin cell, assembly, colorset of assemblies, core, reflector). They contain the cells.
* The initial neutron source,
* The neutron media,
* The instructions to visualize the geometry,
* The scores of the simulation,
* The simulation parameters (number of cycles, number of events, name, number of threads, ...),
* The instructions to run the calculation on remote ressources,
* The instruction to get the desired results (e.g. the k-effective mean valeu and its variance).

The Tripoli-5 features required to perform these various tasks are described in the Tripoli-5 code documentation (see Features sub-section of the Examples section): https://tripoli5.asnr.dev/documentation/examples/index.html
These features use Python API of Tripoli-5: https://tripoli5.asnr.dev/documentation/api/python-api.html
Some examples of Tripoli-5 models and simulations can be found in the Tripoli-5 documentation (see Geometries and Criticality sub-sections of the Examples section): https://tripoli5.asnr.dev/documentation/examples/index.html

The pyT5 interface should be user-friendly and inspired by the Python PyDrag package in its philosophy. It should be seen as a higher-level modeling overlay.
The PyDrag documentation can be found at: https://pydrag.asnr.dev/PyDrag/index.html. The associated PyDrag project can be found here: https://gitlab.asnr.fr/PyDrag/PyDrag
Particularly, the methods and functions used in PyDrag are described here: https://pydrag.asnr.dev/PyDrag/functions.html. The associated Python sources can be found here: https://gitlab.asnr.fr/PyDrag/PyDrag/-/tree/main/src/Python?ref_type=heads
Some examples (assembly and core modeling) in the documentation are described here: https://pydrag.asnr.dev/PyDrag/exemple0.html, https://pydrag.asnr.dev/PyDrag/exemple1.html, https://pydrag.asnr.dev/PyDrag/exemple2.html
Full python examples can be found here: https://gitlab.asnr.fr/PyDrag/PyDrag/-/tree/main/data?ref_type=heads

The pyT5 package must be written in an object-oriented manner with maximum modularity, in order to facilitate its use and subsequent maintenance.
As an example, one can define classes for the definition of the geometry, materials, cells, objects to be modeled (fuel rods, assemblies, reactor core, etc.), scores, plots, neutron source, calculation, etc.