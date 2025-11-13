"""
17x17 PWR Assembly Example - PyDrag-style interface.

This example shows how to model a full 17x17 PWR assembly
with guide tubes, similar to PyDrag's approach.
"""

import pytrip5 as pt5

# ============================================================================
# 1. Materials
# ============================================================================

materials = pt5.Materials()

# Fuel
materials.set_tfuel(900, 'K')
materials.UO2.set_density(10.5)
materials.UO2.set_enrichment('U235', 0.04)  # 4% enriched

# Moderator
materials.water.set_temperature(600, 'K')
materials.water.set_density(0.716)
materials.water.set_boron(600)  # 600 ppm

# Cladding
materials.Zr4.set_temperature(600, 'K')

# ============================================================================
# 2. Pin Definitions (PyDrag style)
# ============================================================================

# Fuel pin: fuel - gap - cladding
F = pt5.Pin.fuel_pin(
    fuel_radius=0.4095,
    gap_radius=0.4180,
    clad_outer_radius=0.4750,
    fuel_material='UO2',
    gap_material='void',
    clad_material='Zr4'
)

# Guide tube: water - tube wall
T = pt5.Pin.guide_tube(
    water_radius=0.5615,
    clad_outer_radius=0.6020,
    water_material='water',
    clad_material='Zr4'
)

# ============================================================================
# 3. Assembly Layout (1/8 symmetry)
# ============================================================================

# Standard 17x17 Westinghouse-type assembly with 24 guide tubes
# Using 1/8 symmetry to reduce specification
layout = [
    [T, F, F, F, T, F, F, F, F],  # Row 1
    [F, F, F, F, F, F, F, F],      # Row 2
    [F, F, T, F, F, F, F],          # Row 3
    [F, F, F, F, F, F],             # Row 4
    [T, F, F, F, T, F],             # Row 5
    [F, F, F, F, F],                # Row 6
    [F, F, F, F],                   # Row 7
    [F, F, F],                      # Row 8
    [F, F]                          # Row 9
]

# Create geometry
geometry = pt5.Geometry(
    layout,
    PinPitch=1.26,        # cm
    AssemblyPitch=21.5,   # cm
    ActiveHeight=365.76,  # cm
    symmetry='1/8'        # 1/8 octant symmetry
)

# ============================================================================
# 4. Power Specification (PyDrag style)
# ============================================================================

# Typical PWR-900 parameters
power = pt5.Power(
    nbAssemblies=157,  # Number of assemblies in core
    corePower=2785     # MWth total core power
)

print(f"Assembly power: {power.assembly_power:.2f} MWth")

# ============================================================================
# 5. Simulation Setup
# ============================================================================

sim = pt5.Simulation(
    name="assembly_17x17",
    n_cycles=500,
    n_particles=50000,
    n_inactive=50,
    n_threads=8
)

sim.add_score('keff')
sim.add_score('flux', energy_groups=100)
sim.add_score('power')

# ============================================================================
# Summary
# ============================================================================

print("=" * 70)
print("pytrip5 - 17x17 PWR Assembly Example")
print("=" * 70)
print()
print(f"Materials: {len([m for m in dir(materials) if isinstance(getattr(materials, m), pt5.Mix)])} defined")
print(f"Geometry: {geometry}")
print(f"Power: {power}")
print(f"Simulation: {sim}")
print()
print("This example demonstrates:")
print("  - PyDrag-style materials with simple setters")
print("  - Concise pin definitions using lists")
print("  - 1/8 symmetry for efficient specification")
print("  - Power normalization (PyDrag style)")
print()
print("Note: Requires Tripoli-5 for execution.")
