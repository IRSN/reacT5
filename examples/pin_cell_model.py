#!/usr/bin/env python3
"""Example: Basic pin cell model with pyT5.

This example demonstrates how to create a simple fuel pin cell model
and calculate basic geometric properties.
"""

import pyT5


def main() -> None:
    """Create and analyze a fuel pin cell."""
    print("=" * 60)
    print("pyT5 Example: Pin Cell Model")
    print("=" * 60)

    # Define fuel material
    print("\n1. Defining materials...")
    fuel = pyT5.Material(
        name="UO2_fuel",
        nuclides={
            "U235": 0.03,  # 3% enrichment
            "U238": 0.97,
            "O16": 2.0,
        },
        temperature=900.0,  # Kelvin
        density=10.4,  # g/cm³
        state="solid",
    )
    print(f"   Created material: {fuel}")

    # Define cladding material (Zircaloy-4)
    clad = pyT5.Material(
        name="Zircaloy4",
        nuclides={
            "Zr90": 0.5145,
            "Zr91": 0.1122,
            "Zr92": 0.1715,
            "Zr94": 0.1738,
            "Zr96": 0.0280,
        },
        temperature=600.0,
        density=6.56,
        state="solid",
    )
    print(f"   Created material: {clad}")

    # Define moderator (water)
    water = pyT5.Material(
        name="light_water",
        nuclides={"H1": 2.0, "O16": 1.0},
        temperature=580.0,  # PWR operating temperature
        density=0.74,  # g/cm³ at operating conditions
        state="liquid",
    )
    print(f"   Created material: {water}")

    # Create material library
    materials = pyT5.MaterialLibrary()
    materials.add_material(fuel)
    materials.add_material(clad)
    materials.add_material(water)
    print(f"\n   Material library contains {len(materials)} materials")

    # Define pin cell geometry (typical PWR dimensions)
    print("\n2. Creating pin cell geometry...")
    pin = pyT5.PinCell(
        name="PWR_fuel_pin",
        pitch=1.26,  # cm
        height=365.76,  # cm (active fuel height)
        fuel_radius=0.4096,  # cm
        clad_inner_radius=0.4178,  # cm
        clad_outer_radius=0.4750,  # cm
    )
    print(f"   Created pin: {pin}")

    # Calculate volumes
    print("\n3. Calculating volumes...")
    fuel_volume = pin.get_fuel_volume()
    gap_volume = pin.get_gap_volume()
    clad_volume = pin.get_clad_volume()
    moderator_volume = (pin.pitch**2 * pin.height) - (
        3.14159 * pin.clad_outer_radius**2 * pin.height
    )

    print(f"   Fuel volume:      {fuel_volume:.2f} cm³")
    print(f"   Gap volume:       {gap_volume:.2f} cm³")
    print(f"   Cladding volume:  {clad_volume:.2f} cm³")
    print(f"   Moderator volume: {moderator_volume:.2f} cm³")

    # Calculate fuel-to-moderator ratio
    fm_ratio = fuel_volume / moderator_volume
    print(f"\n   Fuel-to-moderator ratio: {fm_ratio:.4f}")

    print("\n" + "=" * 60)
    print("Example completed successfully!")
    print("=" * 60)


if __name__ == "__main__":
    main()
