# ---
# jupyter:
#   jupytext:
#     text_representation:
#       extension: .py
#       format_name: percent
#       format_version: '1.3'
#   kernelspec:
#     display_name: Python 3
#     language: python
#     name: python3
# ---

# %% [markdown]
# # pytrip5 Quickstart Example
#
# This notebook demonstrates the basic workflow for using pytrip5 to build
# and simulate a PWR core model using the Tripoli-5 Monte Carlo code.
#
# We'll use the `MockTripoliAdapter` for this example, which allows us to
# run simulations without having Tripoli-5 installed.

# %% [markdown]
# ## Setup and Imports

# %%
import numpy as np
import matplotlib.pyplot as plt

from pytrip5 import (
    Material, Pin, Assembly, Core,
    MockTripoliAdapter,
    SimulationConfig, Runner,
    KeffectiveScore, PinPowerScore, FluxScore
)
from pytrip5 import io

# %% [markdown]
# ## 1. Building a Simple Core
#
# Let's start by creating a simple 3x3 core using the built-in demo constructor.

# %%
# Create a simple 3x3 core
core = Core.simple_demo_3x3()

print(f"Core shape: {core.shape}")
print(f"Number of assemblies: {len(core.assemblies)}")
print(f"Boron concentration: {core.boron_concentration} ppm")

# Inspect the assembly
asm = core.assemblies['ASM_3.1']
print(f"\nAssembly ID: {asm.id}")
print(f"Assembly pitch: {asm.pitch} cm")
print(f"Pin lattice shape: {asm.shape}")
print(f"Enrichment: {asm.enrichment}%")

# %% [markdown]
# ## 2. Creating a Custom Material
#
# You can also create custom materials with specific compositions.

# %%
# Create a fuel material with 4.5% enrichment
fuel_45 = Material(
    name='UO2_4.5%',
    density=10.4,
    compositions={
        'U235': 0.045,
        'U238': 0.955,
        'O16': 2.0
    },
    temperature=900.0  # Kelvin
)

print(f"Material: {fuel_45.name}")
print(f"Density: {fuel_45.density} g/cm³")
print(f"U-235 fraction: {fuel_45.compositions['U235']}")

# %% [markdown]
# ## 3. Setting Up the Simulation
#
# Configure a criticality simulation with scores for k-effective and pin powers.

# %%
# Create simulation configuration
config = SimulationConfig.quick_criticality(
    scores=[
        KeffectiveScore(),
        PinPowerScore('pin_powers'),
        FluxScore('thermal_flux', energy_bounds=[0, 0.625e-6]),
        FluxScore('fast_flux', energy_bounds=[0.1, 20.0])
    ],
    seed=42  # For reproducibility
)

print(f"Simulation type: {'Criticality' if config.criticality else 'Fixed source'}")
print(f"Particles per batch: {config.particles_per_batch}")
print(f"Active batches: {config.active_batches}")
print(f"Inactive batches: {config.inactive_batches}")
print(f"Total particles: {config.total_particles:,}")
print(f"Scores: {[score.name for score in config.scores]}")

# %% [markdown]
# ## 4. Running the Simulation
#
# Use the MockTripoliAdapter to run the simulation without requiring Tripoli-5.

# %%
# Create mock adapter
adapter = MockTripoliAdapter(simulate_latency=True)

# Run simulation
print("Running simulation...")
result = Runner.run(adapter, core, config)
print("Simulation complete!")

# Display results
print(f"\nk-effective: {result.k_eff_with_uncertainty}")

# %% [markdown]
# ## 5. Analyzing Results
#
# Let's examine the pin power distribution.

# %%
# Get pin powers
pin_powers = result.pin_powers

print(f"Pin power array shape: {pin_powers.shape}")
print(f"Mean power: {pin_powers.mean():.4f}")
print(f"Max power: {pin_powers.max():.4f}")
print(f"Min power: {pin_powers.min():.4f}")
print(f"Power peaking factor: {pin_powers.max() / pin_powers.mean():.4f}")

# %% [markdown]
# ## 6. Visualizing Pin Powers

# %%
# Plot pin power distribution
fig, ax = plt.subplots(figsize=(8, 7))

im = ax.imshow(pin_powers, cmap='hot', interpolation='nearest')
ax.set_title('Pin Power Distribution', fontsize=14, fontweight='bold')
ax.set_xlabel('Column Index')
ax.set_ylabel('Row Index')

# Add colorbar
cbar = plt.colorbar(im, ax=ax)
cbar.set_label('Relative Power', rotation=270, labelpad=20)

# Add text annotations
for i in range(pin_powers.shape[0]):
    for j in range(pin_powers.shape[1]):
        text = ax.text(j, i, f'{pin_powers[i, j]:.3f}',
                      ha="center", va="center", color="white", fontsize=10)

plt.tight_layout()
plt.show()

# %% [markdown]
# ## 7. Parameter Sweep: Boron Concentration
#
# Let's run a parameter sweep to see how boron concentration affects reactivity.

# %%
# Define boron concentrations to sweep (ppm)
boron_values = [0, 250, 500, 750, 1000, 1250, 1500]

# Run parameter sweep
print("Running boron concentration sweep...")
sweep_results = Runner.parameter_sweep(
    adapter,
    core,
    'boron_concentration',
    boron_values,
    SimulationConfig.quick_criticality(seed=100)
)
print("Sweep complete!")

# Extract k-eff values
k_effs = [sweep_results[boron].k_eff for boron in boron_values]
k_effs_std = [sweep_results[boron].k_eff_std for boron in boron_values]

# %% [markdown]
# ## 8. Visualizing Boron Worth

# %%
# Plot boron worth curve
fig, ax = plt.subplots(figsize=(10, 6))

ax.errorbar(boron_values, k_effs, yerr=k_effs_std,
            marker='o', linestyle='-', linewidth=2, markersize=8,
            capsize=5, capthick=2, label='k-eff')

ax.axhline(y=1.0, color='red', linestyle='--', linewidth=1.5, label='Critical')
ax.set_xlabel('Boron Concentration (ppm)', fontsize=12, fontweight='bold')
ax.set_ylabel('k-effective', fontsize=12, fontweight='bold')
ax.set_title('Reactivity vs Boron Concentration', fontsize=14, fontweight='bold')
ax.grid(True, alpha=0.3)
ax.legend()

plt.tight_layout()
plt.show()

# Calculate boron worth (pcm/ppm)
# pcm = (dk/k) * 100,000
if len(k_effs) >= 2:
    boron_worth_pcm_per_ppm = ((k_effs[0] - k_effs[-1]) / k_effs[0]) * 100000 / (boron_values[-1] - boron_values[0])
    print(f"\nEstimated boron worth: {boron_worth_pcm_per_ppm:.2f} pcm/ppm")

# %% [markdown]
# ## 9. Saving Results
#
# Save the core configuration and results for later use.

# %%
# Save core configuration to JSON
io.save_core_json(core, '/tmp/core_config.json')
print("Core configuration saved to /tmp/core_config.json")

# Save simulation results
io.save_results_json(result, '/tmp/simulation_results.json')
print("Results saved to /tmp/simulation_results.json")

# Export pin powers to CSV
io.export_pin_powers_csv(pin_powers, '/tmp/pin_powers.csv')
print("Pin powers exported to /tmp/pin_powers.csv")

# Export text summary
io.export_summary_txt(result, '/tmp/summary.txt')
print("Summary exported to /tmp/summary.txt")

# Display summary content
with open('/tmp/summary.txt', 'r') as f:
    print("\n" + "="*60)
    print(f.read())

# %% [markdown]
# ## 10. Loading Saved Data

# %%
# Load core configuration
loaded_core = io.load_core_json('/tmp/core_config.json')
print(f"Loaded core shape: {loaded_core.shape}")
print(f"Loaded boron concentration: {loaded_core.boron_concentration} ppm")

# Load results
loaded_result = io.load_results_json('/tmp/simulation_results.json')
print(f"\nLoaded k-eff: {loaded_result.k_eff_with_uncertainty}")

# Load pin powers
loaded_powers = io.import_pin_powers_csv('/tmp/pin_powers.csv')
print(f"Loaded pin powers shape: {loaded_powers.shape}")

# Verify they match
assert np.allclose(loaded_powers, pin_powers)
print("✓ Loaded data matches original data")

# %% [markdown]
# ## 11. Running with Real Tripoli-5 (Optional)
#
# To run with the real Tripoli-5 installation (if available):
#
# ```python
# from pytrip5 import TripoliAdapter
#
# try:
#     # Create real adapter (requires tripoli5 package)
#     real_adapter = TripoliAdapter()
#
#     # Run the same simulation with real Tripoli-5
#     real_result = Runner.run(real_adapter, core, config)
#
#     print(f"Real Tripoli-5 k-eff: {real_result.k_eff_with_uncertainty}")
# except ImportError:
#     print("Tripoli-5 not installed. Use MockTripoliAdapter for testing.")
# ```

# %% [markdown]
# ## Summary
#
# This notebook demonstrated:
#
# 1. ✓ Creating a simple PWR core model
# 2. ✓ Defining custom materials
# 3. ✓ Configuring criticality simulations
# 4. ✓ Running simulations with MockTripoliAdapter
# 5. ✓ Analyzing pin power distributions
# 6. ✓ Running parameter sweeps (boron worth)
# 7. ✓ Visualizing results
# 8. ✓ Saving and loading data
#
# For production runs, replace `MockTripoliAdapter` with `TripoliAdapter`
# and ensure Tripoli-5 is properly installed.
#
# For more information, see the pytrip5 documentation and examples.
