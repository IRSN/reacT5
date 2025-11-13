"""
Simple pin cell example - PyDrag-style interface.

This example demonstrates the simplified pytrip5 API for
modeling a PWR pin cell, inspired by PyDrag's simplicity.
"""

import pytrip5 as pt5

# ============================================================================
# 1. Define Materials (PyDrag style - simple and intuitive)
# ============================================================================

materials = pt5.Materials()

# Set fuel properties
materials.set_tfuel(900, 'K')  # Fuel temperature
materials.UO2.set_density(10.5)  # g/cm³
materials.UO2.set_enrichment('U235', 0.04)  # 4% enrichment
materials.UO2.set_enrichment('U238', 0.96)

# Set water properties
materials.water.set_temperature(600, 'K')
materials.water.set_density(0.7)  # g/cm³
materials.water.set_boron(600)  # 600 ppm boron

# Zircaloy cladding (already has defaults)
materials.Zr4.set_temperature(600, 'K')

# ============================================================================
# 2. Define Geometry (PyDrag style - list notation)
# ============================================================================

# Define pin as list: [material, radius, material, radius, ...]
# This is PyDrag's concise pin definition style
F = ['UO2', 0.4095,      # Fuel pellet radius
     'void', 0.4180,      # Gap
     'Zr4', 0.4750]      # Cladding

# Single pin cell with 1/4 symmetry
pin_layout = [[F]]

# Create geometry
geometry = pt5.Geometry(
    pin_layout,
    PinPitch=1.26,        # cm
    AssemblyPitch=1.26,   # cm (single pin)
    ActiveHeight=20.0,    # cm
    symmetry='full'
)

# ============================================================================
# 3. Set up Simulation
# ============================================================================

# Create simulation (criticality calculation)
sim = pt5.Simulation(
    name="pin_cell_keff",
    n_cycles=500,         # Number of cycles
    n_particles=10000,    # Particles per cycle
    n_inactive=50,        # Inactive cycles
    n_threads=4           # Parallel threads
)

# Add scores/tallies
sim.add_score('keff')
sim.add_score('flux', energy_groups=50)

# ============================================================================
# 4. Run Calculation (would require Tripoli-5)
# ============================================================================

print("=" * 70)
print("pytrip5 - Simple Pin Cell Example")
print("=" * 70)
print()
print("Materials defined:")
print(f"  - {materials.UO2}")
print(f"  - {materials.water}")
print(f"  - {materials.Zr4}")
print()
print("Geometry:")
print(f"  {geometry}")
print()
print("Simulation:")
print(f"  {sim}")
print()
print("Note: Actual execution requires Tripoli-5 installation.")
print("This example demonstrates the PyDrag-style API.")
print()

# When Tripoli-5 is available:
# try:
#     # Load nuclear data catalog
#     catalog_path = "/path/to/tripoli5/catalog.yaml"
#     materials.load_catalog(catalog_path)
#
#     # Run simulation
#     results = sim.run(materials, geometry)
#
#     # Get results
#     keff = results.get_keff()
#     print(f"k-effective = {keff.mean:.5f} ± {keff.std:.5f}")
#     print(f"95% CI: [{keff.confidence_interval_95[0]:.5f}, "
#           f"{keff.confidence_interval_95[1]:.5f}]")
#
# except pt5.ConfigurationError as e:
#     print(f"Configuration error: {e}")
