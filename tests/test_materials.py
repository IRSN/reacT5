"""Tests for materials module."""

import pytest
from pyT5 import Material, MaterialLibrary


class TestMaterial:
    """Tests for Material class."""

    def test_material_creation(self, sample_material: Material) -> None:
        """Test creating a material."""
        assert sample_material.name == "UO2_fuel"
        assert sample_material.temperature == 900.0
        assert sample_material.density == 10.4
        assert sample_material.state == "solid"
        assert "U235" in sample_material.nuclides

    def test_material_invalid_temperature(self) -> None:
        """Test that negative temperature raises error."""
        with pytest.raises(ValueError, match="Temperature must be non-negative"):
            Material(
                name="test",
                nuclides={"U235": 1.0},
                temperature=-10.0,
            )

    def test_material_empty_nuclides(self) -> None:
        """Test that empty nuclides dict raises error."""
        with pytest.raises(ValueError, match="must contain at least one nuclide"):
            Material(name="test", nuclides={})

    def test_material_invalid_state(self) -> None:
        """Test that invalid state raises error."""
        with pytest.raises(ValueError, match="Invalid state"):
            Material(
                name="test",
                nuclides={"U235": 1.0},
                state="plasma",
            )

    def test_normalize_concentrations(self) -> None:
        """Test concentration normalization."""
        mat = Material(name="test", nuclides={"U235": 2.0, "U238": 8.0})
        mat.normalize_concentrations()
        assert mat.nuclides["U235"] == pytest.approx(0.2)
        assert mat.nuclides["U238"] == pytest.approx(0.8)

    def test_add_nuclide(self, sample_material: Material) -> None:
        """Test adding a nuclide."""
        sample_material.add_nuclide("Pu239", 0.01)
        assert "Pu239" in sample_material.nuclides
        assert sample_material.nuclides["Pu239"] == 0.01

    def test_remove_nuclide(self, sample_material: Material) -> None:
        """Test removing a nuclide."""
        sample_material.remove_nuclide("U235")
        assert "U235" not in sample_material.nuclides

    def test_remove_nonexistent_nuclide(self, sample_material: Material) -> None:
        """Test removing nonexistent nuclide raises error."""
        with pytest.raises(KeyError):
            sample_material.remove_nuclide("Pu239")

    def test_get_concentration(self, sample_material: Material) -> None:
        """Test getting nuclide concentration."""
        conc = sample_material.get_concentration("U235")
        assert conc == 0.03

    def test_set_temperature(self, sample_material: Material) -> None:
        """Test setting temperature."""
        sample_material.set_temperature(1200.0)
        assert sample_material.temperature == 1200.0

    def test_set_density(self, sample_material: Material) -> None:
        """Test setting density."""
        sample_material.set_density(11.0)
        assert sample_material.density == 11.0


class TestMaterialLibrary:
    """Tests for MaterialLibrary class."""

    def test_library_creation(self) -> None:
        """Test creating an empty library."""
        lib = MaterialLibrary()
        assert len(lib) == 0

    def test_add_material(self, sample_material: Material) -> None:
        """Test adding material to library."""
        lib = MaterialLibrary()
        lib.add_material(sample_material)
        assert len(lib) == 1
        assert "UO2_fuel" in lib.list_materials()

    def test_add_duplicate_material(self, material_library: MaterialLibrary, sample_material: Material) -> None:
        """Test that adding duplicate material raises error."""
        with pytest.raises(ValueError, match="already exists"):
            material_library.add_material(sample_material)

    def test_get_material(self, material_library: MaterialLibrary) -> None:
        """Test retrieving material from library."""
        mat = material_library.get_material("UO2_fuel")
        assert mat.name == "UO2_fuel"

    def test_get_nonexistent_material(self, material_library: MaterialLibrary) -> None:
        """Test getting nonexistent material raises error."""
        with pytest.raises(KeyError):
            material_library.get_material("nonexistent")

    def test_remove_material(self, material_library: MaterialLibrary) -> None:
        """Test removing material from library."""
        material_library.remove_material("UO2_fuel")
        assert "UO2_fuel" not in material_library.list_materials()

    def test_list_materials(self, material_library: MaterialLibrary) -> None:
        """Test listing all materials."""
        materials = material_library.list_materials()
        assert len(materials) == 2
        assert "UO2_fuel" in materials
        assert "light_water" in materials
