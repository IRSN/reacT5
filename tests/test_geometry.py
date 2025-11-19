"""Tests for geometry module."""

import pytest
import numpy as np
from pyT5 import PinCell, Assembly, Colorset, Core, Reflector


class TestPinCell:
    """Tests for PinCell class."""

    def test_pin_cell_creation(self, sample_pin_cell: PinCell) -> None:
        """Test creating a pin cell."""
        assert sample_pin_cell.name == "standard_pin"
        assert sample_pin_cell.pitch == 1.26
        assert sample_pin_cell.height == 365.76
        assert sample_pin_cell.fuel_radius == 0.4096

    def test_pin_cell_invalid_dimensions(self) -> None:
        """Test that invalid dimensions raise error."""
        with pytest.raises(ValueError, match="must be positive"):
            PinCell(
                name="test",
                pitch=-1.0,
                height=100.0,
                fuel_radius=0.4,
                clad_inner_radius=0.42,
                clad_outer_radius=0.48,
            )

    def test_pin_cell_invalid_radii(self) -> None:
        """Test that inconsistent radii raise error."""
        with pytest.raises(ValueError, match="Invalid radii"):
            PinCell(
                name="test",
                pitch=1.26,
                height=365.76,
                fuel_radius=0.5,  # Too large
                clad_inner_radius=0.418,
                clad_outer_radius=0.475,
            )

    def test_get_fuel_volume(self, sample_pin_cell: PinCell) -> None:
        """Test fuel volume calculation."""
        volume = sample_pin_cell.get_fuel_volume()
        expected = np.pi * sample_pin_cell.fuel_radius**2 * sample_pin_cell.height
        assert volume == pytest.approx(expected)

    def test_get_gap_volume(self, sample_pin_cell: PinCell) -> None:
        """Test gap volume calculation."""
        volume = sample_pin_cell.get_gap_volume()
        expected = np.pi * (
            sample_pin_cell.clad_inner_radius**2 - sample_pin_cell.fuel_radius**2
        ) * sample_pin_cell.height
        assert volume == pytest.approx(expected)

    def test_get_clad_volume(self, sample_pin_cell: PinCell) -> None:
        """Test cladding volume calculation."""
        volume = sample_pin_cell.get_clad_volume()
        expected = np.pi * (
            sample_pin_cell.clad_outer_radius**2 - sample_pin_cell.clad_inner_radius**2
        ) * sample_pin_cell.height
        assert volume == pytest.approx(expected)


class TestAssembly:
    """Tests for Assembly class."""

    def test_assembly_creation(self, sample_assembly: Assembly) -> None:
        """Test creating an assembly."""
        assert sample_assembly.name == "17x17_assembly"
        assert sample_assembly.lattice_type == "square"
        assert sample_assembly.n_pins_x == 17
        assert sample_assembly.n_pins_y == 17

    def test_assembly_invalid_lattice_type(self) -> None:
        """Test that invalid lattice type raises error."""
        with pytest.raises(ValueError, match="Invalid lattice_type"):
            Assembly(
                name="test",
                lattice_type="triangular",
                n_pins_x=17,
                n_pins_y=17,
            )

    def test_set_pin(self, sample_assembly: Assembly, sample_pin_cell: PinCell) -> None:
        """Test setting a pin in the assembly."""
        sample_assembly.set_pin(0, 0, sample_pin_cell)
        pin = sample_assembly.get_pin(0, 0)
        assert pin is not None
        assert pin.name == "standard_pin"

    def test_set_pin_out_of_range(self, sample_assembly: Assembly, sample_pin_cell: PinCell) -> None:
        """Test that setting pin out of range raises error."""
        with pytest.raises(IndexError):
            sample_assembly.set_pin(20, 20, sample_pin_cell)

    def test_get_pin_empty_position(self, sample_assembly: Assembly) -> None:
        """Test getting pin from empty position."""
        pin = sample_assembly.get_pin(0, 0)
        assert pin is None

    def test_count_pins(self, sample_assembly: Assembly, sample_pin_cell: PinCell) -> None:
        """Test counting pins in assembly."""
        assert sample_assembly.count_pins() == 0
        sample_assembly.set_pin(0, 0, sample_pin_cell)
        sample_assembly.set_pin(1, 1, sample_pin_cell)
        assert sample_assembly.count_pins() == 2


class TestColorset:
    """Tests for Colorset class."""

    def test_colorset_creation(self) -> None:
        """Test creating a colorset."""
        colorset = Colorset(name="test_colorset")
        assert colorset.name == "test_colorset"
        assert colorset.count_assemblies() == 0

    def test_add_assembly(self, sample_assembly: Assembly) -> None:
        """Test adding assembly to colorset."""
        colorset = Colorset(name="test")
        colorset.add_assembly((0, 0), sample_assembly)
        assert colorset.count_assemblies() == 1

    def test_add_assembly_duplicate_position(self, sample_assembly: Assembly) -> None:
        """Test that adding assembly to occupied position raises error."""
        colorset = Colorset(name="test")
        colorset.add_assembly((0, 0), sample_assembly)
        with pytest.raises(ValueError, match="already occupied"):
            colorset.add_assembly((0, 0), sample_assembly)

    def test_get_assembly(self, sample_assembly: Assembly) -> None:
        """Test getting assembly from colorset."""
        colorset = Colorset(name="test")
        colorset.add_assembly((0, 0), sample_assembly)
        asm = colorset.get_assembly((0, 0))
        assert asm is not None
        assert asm.name == "17x17_assembly"

    def test_remove_assembly(self, sample_assembly: Assembly) -> None:
        """Test removing assembly from colorset."""
        colorset = Colorset(name="test")
        colorset.add_assembly((0, 0), sample_assembly)
        colorset.remove_assembly((0, 0))
        assert colorset.count_assemblies() == 0


class TestCore:
    """Tests for Core class."""

    def test_core_creation(self) -> None:
        """Test creating a core."""
        core = Core(name="PWR_core", core_type="square", n_assemblies_x=15, n_assemblies_y=15)
        assert core.name == "PWR_core"
        assert core.core_type == "square"
        assert core.n_assemblies_x == 15

    def test_core_invalid_type(self) -> None:
        """Test that invalid core type raises error."""
        with pytest.raises(ValueError, match="Invalid core_type"):
            Core(name="test", core_type="triangular")

    def test_set_assembly(self, sample_assembly: Assembly) -> None:
        """Test setting assembly in core."""
        core = Core(name="test", n_assemblies_x=15, n_assemblies_y=15)
        core.set_assembly((0, 0), sample_assembly)
        assert core.count_assemblies() == 1

    def test_get_assembly(self, sample_assembly: Assembly) -> None:
        """Test getting assembly from core."""
        core = Core(name="test", n_assemblies_x=15, n_assemblies_y=15)
        core.set_assembly((5, 5), sample_assembly)
        asm = core.get_assembly((5, 5))
        assert asm is not None
        assert asm.name == "17x17_assembly"


class TestReflector:
    """Tests for Reflector class."""

    def test_reflector_creation(self) -> None:
        """Test creating a reflector."""
        reflector = Reflector(
            name="water_reflector",
            thickness=20.0,
            material_name="light_water",
        )
        assert reflector.name == "water_reflector"
        assert reflector.thickness == 20.0
        assert reflector.material_name == "light_water"

    def test_reflector_invalid_thickness(self) -> None:
        """Test that invalid thickness raises error."""
        with pytest.raises(ValueError, match="Thickness must be positive"):
            Reflector(
                name="test",
                thickness=-10.0,
                material_name="water",
            )
