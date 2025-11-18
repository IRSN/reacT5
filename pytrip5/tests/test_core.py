"""Unit tests for pytrip5.core module."""

import pytest
import numpy as np

from pytrip5.core import Material, Pin, Assembly, Core


class TestMaterial:
    """Tests for Material dataclass."""

    def test_material_creation(self):
        """Test basic material creation."""
        mat = Material(
            name='UO2',
            density=10.4,
            compositions={'U235': 0.03, 'U238': 0.97},
            temperature=900.0
        )
        assert mat.name == 'UO2'
        assert mat.density == 10.4
        assert mat.compositions['U235'] == 0.03
        assert mat.temperature == 900.0

    def test_material_without_temperature(self):
        """Test material creation without temperature."""
        mat = Material(
            name='Water',
            density=1.0,
            compositions={'H1': 2, 'O16': 1}
        )
        assert mat.temperature is None

    def test_material_negative_density_raises(self):
        """Test that negative density raises ValueError."""
        with pytest.raises(ValueError, match="density must be positive"):
            Material(
                name='Invalid',
                density=-1.0,
                compositions={'U': 1}
            )

    def test_material_empty_composition_raises(self):
        """Test that empty composition raises ValueError."""
        with pytest.raises(ValueError, match="at least one isotope"):
            Material(
                name='Invalid',
                density=1.0,
                compositions={}
            )


class TestPin:
    """Tests for Pin dataclass."""

    def test_pin_creation(self):
        """Test basic pin creation."""
        mat = Material('UO2', 10.4, {'U': 1})
        pin = Pin(id='fuel', radius=0.475, material=mat, pitch=1.26)
        assert pin.id == 'fuel'
        assert pin.radius == 0.475
        assert pin.material.name == 'UO2'
        assert pin.pitch == 1.26

    def test_pin_without_pitch(self):
        """Test pin creation without pitch."""
        mat = Material('UO2', 10.4, {'U': 1})
        pin = Pin(id='fuel', radius=0.475, material=mat)
        assert pin.pitch is None

    def test_pin_negative_radius_raises(self):
        """Test that negative radius raises ValueError."""
        mat = Material('UO2', 10.4, {'U': 1})
        with pytest.raises(ValueError, match="radius must be positive"):
            Pin(id='fuel', radius=-0.5, material=mat)

    def test_pin_negative_pitch_raises(self):
        """Test that negative pitch raises ValueError."""
        mat = Material('UO2', 10.4, {'U': 1})
        with pytest.raises(ValueError, match="pitch must be positive"):
            Pin(id='fuel', radius=0.5, material=mat, pitch=-1.0)


class TestAssembly:
    """Tests for Assembly dataclass."""

    def test_assembly_creation(self):
        """Test basic assembly creation."""
        mat = Material('UO2', 10.4, {'U': 1})
        pin = Pin('fuel', 0.475, mat)
        pins = [[pin for _ in range(3)] for _ in range(3)]
        asm = Assembly(id='ASM_A', pitch=21.5, pins=pins, enrichment=3.1)

        assert asm.id == 'ASM_A'
        assert asm.pitch == 21.5
        assert asm.shape == (3, 3)
        assert asm.enrichment == 3.1

    def test_assembly_get_pin(self):
        """Test getting pin at specific position."""
        mat = Material('UO2', 10.4, {'U': 1})
        pin1 = Pin('fuel1', 0.475, mat)
        pin2 = Pin('fuel2', 0.480, mat)
        pins = [[pin1, pin2], [pin2, pin1]]
        asm = Assembly(id='ASM_A', pitch=21.5, pins=pins)

        assert asm.get_pin(0, 0).id == 'fuel1'
        assert asm.get_pin(0, 1).id == 'fuel2'
        assert asm.get_pin(1, 0).id == 'fuel2'

    def test_assembly_negative_pitch_raises(self):
        """Test that negative pitch raises ValueError."""
        mat = Material('UO2', 10.4, {'U': 1})
        pin = Pin('fuel', 0.475, mat)
        pins = [[pin]]

        with pytest.raises(ValueError, match="pitch must be positive"):
            Assembly(id='ASM_A', pitch=-21.5, pins=pins)

    def test_assembly_non_rectangular_raises(self):
        """Test that non-rectangular pin grid raises ValueError."""
        mat = Material('UO2', 10.4, {'U': 1})
        pin = Pin('fuel', 0.475, mat)
        pins = [[pin, pin], [pin]]  # Non-rectangular

        with pytest.raises(ValueError, match="rectangular grid"):
            Assembly(id='ASM_A', pitch=21.5, pins=pins)


class TestCore:
    """Tests for Core dataclass."""

    def test_core_creation(self):
        """Test basic core creation."""
        mat = Material('UO2', 10.4, {'U': 1})
        pin = Pin('fuel', 0.475, mat)
        pins = [[pin]]
        asm = Assembly(id='ASM_A', pitch=21.5, pins=pins)

        layout = [['ASM_A', 'ASM_A'], ['ASM_A', 'ASM_A']]
        core = Core(
            assemblies={'ASM_A': asm},
            layout=layout,
            boron_concentration=500.0
        )

        assert core.shape == (2, 2)
        assert core.boron_concentration == 500.0

    def test_core_get_assembly(self):
        """Test getting assembly at specific position."""
        mat = Material('UO2', 10.4, {'U': 1})
        pin = Pin('fuel', 0.475, mat)
        pins = [[pin]]
        asm_a = Assembly(id='ASM_A', pitch=21.5, pins=pins)
        asm_b = Assembly(id='ASM_B', pitch=21.5, pins=pins)

        layout = [['ASM_A', 'ASM_B'], [None, 'ASM_A']]
        core = Core(
            assemblies={'ASM_A': asm_a, 'ASM_B': asm_b},
            layout=layout
        )

        assert core.get_assembly(0, 0).id == 'ASM_A'
        assert core.get_assembly(0, 1).id == 'ASM_B'
        assert core.get_assembly(1, 0) is None
        assert core.get_assembly(1, 1).id == 'ASM_A'

    def test_core_invalid_assembly_id_raises(self):
        """Test that invalid assembly ID in layout raises ValueError."""
        mat = Material('UO2', 10.4, {'U': 1})
        pin = Pin('fuel', 0.475, mat)
        pins = [[pin]]
        asm = Assembly(id='ASM_A', pitch=21.5, pins=pins)

        layout = [['ASM_A', 'ASM_B']]  # ASM_B doesn't exist

        with pytest.raises(ValueError, match="not found in assemblies"):
            Core(assemblies={'ASM_A': asm}, layout=layout)

    def test_core_negative_boron_raises(self):
        """Test that negative boron concentration raises ValueError."""
        mat = Material('UO2', 10.4, {'U': 1})
        pin = Pin('fuel', 0.475, mat)
        pins = [[pin]]
        asm = Assembly(id='ASM_A', pitch=21.5, pins=pins)

        with pytest.raises(ValueError, match="cannot be negative"):
            Core(
                assemblies={'ASM_A': asm},
                layout=[['ASM_A']],
                boron_concentration=-100.0
            )

    def test_core_simple_demo_3x3(self):
        """Test the simple_demo_3x3 factory method."""
        core = Core.simple_demo_3x3()

        assert core.shape == (3, 3)
        assert core.boron_concentration == 500.0
        assert len(core.assemblies) == 1
        assert 'ASM_3.1' in core.assemblies

        # Check assembly properties
        asm = core.assemblies['ASM_3.1']
        assert asm.shape == (17, 17)
        assert asm.enrichment == 3.1

    def test_core_to_tripoli(self):
        """Test conversion to Tripoli model."""
        from pytrip5.adapter import MockTripoliAdapter

        core = Core.simple_demo_3x3()
        adapter = MockTripoliAdapter()
        model = core.to_tripoli(adapter)

        assert model.core is core
        assert 'UO2_3.1%' in model.materials
        assert model.geometry is not None


if __name__ == '__main__':
    pytest.main([__file__, '-v'])
