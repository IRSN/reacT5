#!/usr/bin/env python3
"""Example: 17x17 PWR assembly model with pyT5.

This example demonstrates how to create a typical 17x17 PWR fuel assembly
with fuel pins and guide tubes.
"""

import pyT5


def main() -> None:
    """Create a 17x17 PWR assembly."""
    print("=" * 60)
    print("pyT5 Example: 17x17 PWR Assembly")
    print("=" * 60)

    # Define materials
    print("\n1. Defining materials...")
    fuel = pyT5.Material(
        name="UO2_fuel",
        nuclides={"U235": 0.03, "U238": 0.97, "O16": 2.0},
        temperature=900.0,
        density=10.4,
        state="solid",
    )

    water = pyT5.Material(
        name="light_water",
        nuclides={"H1": 2.0, "O16": 1.0},
        temperature=580.0,
        density=0.74,
        state="liquid",
    )

    # Create material library
    materials = pyT5.MaterialLibrary()
    materials.add_material(fuel)
    materials.add_material(water)
    print(f"   Created {len(materials)} materials")

    # Create fuel pin
    print("\n2. Creating pin cells...")
    fuel_pin = pyT5.PinCell(
        name="fuel_pin",
        pitch=1.26,
        height=365.76,
        fuel_radius=0.4096,
        clad_inner_radius=0.4178,
        clad_outer_radius=0.4750,
    )
    print(f"   Fuel pin created: pitch={fuel_pin.pitch} cm")

    # Create guide tube (larger diameter, no fuel)
    guide_tube = pyT5.PinCell(
        name="guide_tube",
        pitch=1.26,
        height=365.76,
        fuel_radius=0.001,  # Small dummy value
        clad_inner_radius=0.561,
        clad_outer_radius=0.602,
    )
    print(f"   Guide tube created")

    # Create 17x17 assembly
    print("\n3. Creating 17x17 assembly...")
    assembly = pyT5.Assembly(
        name="17x17_PWR_assembly",
        lattice_type="square",
        n_pins_x=17,
        n_pins_y=17,
        pin_pitch=1.26,
        assembly_pitch=21.50,
    )

    # Guide tube positions in a typical 17x17 assembly (24 positions)
    guide_tube_positions = [
        (2, 5), (2, 8), (2, 11),
        (5, 2), (5, 5), (5, 8), (5, 11), (5, 14),
        (8, 2), (8, 5), (8, 8), (8, 11), (8, 14),
        (11, 2), (11, 5), (11, 8), (11, 11), (11, 14),
        (14, 5), (14, 8), (14, 11),
    ]

    # Populate assembly
    print("\n4. Populating assembly with pins...")
    fuel_count = 0
    guide_count = 0

    for i in range(17):
        for j in range(17):
            if (i, j) in guide_tube_positions:
                assembly.set_pin(i, j, guide_tube)
                guide_count += 1
            else:
                assembly.set_pin(i, j, fuel_pin)
                fuel_count += 1

    print(f"   Fuel pins:    {fuel_count}")
    print(f"   Guide tubes:  {guide_count}")
    print(f"   Total pins:   {assembly.count_pins()}")

    # Assembly statistics
    print("\n5. Assembly statistics...")
    total_fuel_volume = fuel_count * fuel_pin.get_fuel_volume()
    assembly_volume = assembly.assembly_pitch**2 * assembly.n_pins_x * fuel_pin.height

    print(f"   Assembly pitch:       {assembly.assembly_pitch:.2f} cm")
    print(f"   Total fuel volume:    {total_fuel_volume:.2f} cm³")
    print(f"   Assembly volume:      {assembly_volume:.2f} cm³")

    print("\n" + "=" * 60)
    print("Example completed successfully!")
    print("=" * 60)


if __name__ == "__main__":
    main()
