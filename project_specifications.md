# pytrip5: description

This project is for a python higher level interface for Tripoli-5 Monte-Carlo code computing. Tripoli-5 is a Monte-Carlo particle transport code developed by CEA (French Atomic Energy Commission) for neutron, photon, electron, and positron transport simulations. The code is mainly used for reactor physics, radiation shielding, dosimetry, and other applications in nuclear engineering. The Tripoli-5 code documentation can be found here: https://tripoli5.asnr.dev/documentation/index.html. The
main objective of this project is to develop a python package named "pytrip5" that allows users to easily model and simulate Pressurized Water Reactors (PWR) using Tripoli-5, at a full core level. The work should be leviated on existing Tripoli-5 python public API and inspired by the PyDrag package developed at IRSN (French Institute for Radiological Protection and Nuclear Safety).

pytrip5 should be able to handle modeling and simulation of PWR reactors at different levels:
* pin cells,
* fuel assemblies, for different fuel compositions (UOX, MOX, etc.), and assembly shapes (17x17, 15x15, etc.),
* colorsets of several fuel assemblies,
* reactor core.
These objects may be surrounded by reflective materials.

To make a computation, the user must define: (take inspiration from PyDrag structure and methods and examples provided in Tripoli-5 documentation)
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

The Tripoli-5 features required to perform these various tasks are described in the Tripoli-5 code documentation (see Features subsection of the Examples section): https://tripoli5.asnr.dev/documentation/examples/index.html. These features use Python API of Tripoli-5: https://tripoli5.asnr.dev/documentation/api/python-api.html. Some examples of Tripoli-5 models and simulations can be found in the Tripoli-5 documentation (see Geometries and Criticality subsections of the Examples section): https://tripoli5.asnr.dev/documentation/examples/index.html.

The pytrip5 interface should be user-friendly and inspired by the Python PyDrag package in its philosophy with doing the same work on deterministic transport code Dragon. Therefore, it should be seen as a higher-level modeling overlay backed by Tripoli5 primitives.

The PyDrag documentation can be found at: https://pydrag.asnr.dev/PyDrag/index.html. The associated PyDrag project and sources can be found here: https://gitlab.asnr.fr/PyDrag/PyDrag. Particularly, the methods and functions used in PyDrag are described here: https://pydrag.asnr.dev/PyDrag/functions.html. Some examples (assembly and core modeling) in the documentation are described here: https://pydrag.asnr.dev/PyDrag/exemple0.html, https://pydrag.asnr.dev/PyDrag/exemple1.html, https://pydrag.asnr.dev/PyDrag/exemple2.html
Full python examples can be found in the "data" folder within : https://gitlab.asnr.fr/PyDrag/PyDrag.

We do not reinvinte the wheel. We should prefer using existing methods provides by Tripoli5 package. Since similar work has been performed on pyDrag, we should take inspiration.

The package should follow pythonic best practices, should be written in an object-oriented manner with maximum modularity, in order to facilitate its use and subsequent maintenance. As an example, one can define classes for the definition of the geometry, materials, cells, objects to be modeled (fuel rods, assemblies, reactor core, etc.), scores, plots, neutron source, calculation, etc.