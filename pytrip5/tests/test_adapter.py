"""Unit tests for pytrip5.adapter module."""

import pytest
import numpy as np

from pytrip5.core import Material, Core
from pytrip5.adapter import MockTripoliAdapter, TripoliAdapter, TripoliModel
from pytrip5.simulation import SimulationConfig
from pytrip5.score import KeffectiveScore, PinPowerScore


class TestMockTripoliAdapter:
    """Tests for MockTripoliAdapter."""

    def test_create_material(self):
        """Test material conversion."""
        adapter = MockTripoliAdapter()
        mat = Material('UO2', 10.4, {'U235': 0.03, 'U238': 0.97})
        tripoli_mat = adapter.create_material(mat)

        assert tripoli_mat['type'] == 'MockTripoliMaterial'
        assert tripoli_mat['name'] == 'UO2'
        assert tripoli_mat['density'] == 10.4
        assert tripoli_mat['compositions']['U235'] == 0.03

    def test_create_geometry(self):
        """Test geometry conversion."""
        adapter = MockTripoliAdapter()
        core = Core.simple_demo_3x3()
        geometry = adapter.create_geometry(core)

        assert geometry['type'] == 'MockTripoliGeometry'
        assert geometry['core_shape'] == (3, 3)
        assert geometry['total_assemblies'] == 9
        assert geometry['boron_ppm'] == 500.0

    def test_configure_simulation(self):
        """Test simulation configuration."""
        adapter = MockTripoliAdapter()
        core = Core.simple_demo_3x3()
        model = core.to_tripoli(adapter)

        config = SimulationConfig(
            criticality=True,
            particles_per_batch=1000,
            active_batches=10,
            scores=[KeffectiveScore()]
        )

        simulation = adapter.configure_simulation(model, config)

        assert simulation.model is model
        assert simulation.config is config
        assert simulation.simulation_object['type'] == 'MockTripoliSimulation'
        assert simulation.simulation_object['criticality'] is True
        assert simulation.simulation_object['particles_per_batch'] == 1000

    def test_run_criticality_simulation(self):
        """Test running a criticality simulation."""
        adapter = MockTripoliAdapter(simulate_latency=False)
        core = Core.simple_demo_3x3()
        model = core.to_tripoli(adapter)

        config = SimulationConfig.quick_criticality(
            scores=[KeffectiveScore()],
            seed=42
        )

        simulation = adapter.configure_simulation(model, config)
        result = adapter.run(simulation)

        assert result.k_eff is not None
        assert 0.9 < result.k_eff < 1.1  # Reasonable range
        assert result.k_eff_std is not None
        assert result.k_eff_std > 0

    def test_run_with_pin_powers(self):
        """Test simulation with pin power score."""
        adapter = MockTripoliAdapter(simulate_latency=False)
        core = Core.simple_demo_3x3()
        model = core.to_tripoli(adapter)

        config = SimulationConfig.quick_criticality(
            scores=[KeffectiveScore(), PinPowerScore('pin_powers')],
            seed=42
        )

        simulation = adapter.configure_simulation(model, config)
        result = adapter.run(simulation)

        assert 'pin_powers' in result.scores
        powers = result.scores['pin_powers']
        assert isinstance(powers, np.ndarray)
        assert powers.shape == (3, 3)
        # Check normalization (average should be close to 1.0)
        assert 0.9 < powers.mean() < 1.1

    def test_reproducibility_with_seed(self):
        """Test that same seed gives same results."""
        adapter = MockTripoliAdapter(simulate_latency=False)
        core = Core.simple_demo_3x3()

        config1 = SimulationConfig.quick_criticality(seed=12345)
        config2 = SimulationConfig.quick_criticality(seed=12345)

        model = core.to_tripoli(adapter)
        sim1 = adapter.configure_simulation(model, config1)
        result1 = adapter.run(sim1)

        sim2 = adapter.configure_simulation(model, config2)
        result2 = adapter.run(sim2)

        # Results with same seed should be identical
        assert result1.k_eff == result2.k_eff

    def test_different_seeds_give_different_results(self):
        """Test that different seeds give different results."""
        adapter = MockTripoliAdapter(simulate_latency=False)
        core = Core.simple_demo_3x3()

        config1 = SimulationConfig.quick_criticality(seed=111)
        config2 = SimulationConfig.quick_criticality(seed=222)

        model = core.to_tripoli(adapter)
        sim1 = adapter.configure_simulation(model, config1)
        result1 = adapter.run(sim1)

        sim2 = adapter.configure_simulation(model, config2)
        result2 = adapter.run(sim2)

        # Results with different seeds should differ
        assert result1.k_eff != result2.k_eff

    def test_boron_effect_on_keff(self):
        """Test that boron concentration affects k-eff."""
        adapter = MockTripoliAdapter(simulate_latency=False)

        # Create cores with different boron concentrations
        core1 = Core.simple_demo_3x3()
        # Modify boron (need to recreate Core as it uses dataclass)
        asm = core1.assemblies['ASM_3.1']
        core2 = Core(
            assemblies={'ASM_3.1': asm},
            layout=core1.layout,
            boron_concentration=1000.0  # Higher boron
        )

        config = SimulationConfig.quick_criticality(seed=42)

        model1 = core1.to_tripoli(adapter)
        sim1 = adapter.configure_simulation(model1, config)
        result1 = adapter.run(sim1)

        model2 = core2.to_tripoli(adapter)
        sim2 = adapter.configure_simulation(model2, config)
        result2 = adapter.run(sim2)

        # Higher boron should reduce k-eff
        assert result2.k_eff < result1.k_eff


class TestTripoliAdapter:
    """Tests for real TripoliAdapter (skipped if Tripoli-5 not available)."""

    def test_adapter_import_error(self):
        """Test that TripoliAdapter raises ImportError when Tripoli-5 unavailable."""
        # This will likely raise ImportError unless Tripoli-5 is installed
        try:
            adapter = TripoliAdapter()
            # If we get here, Tripoli-5 is installed
            assert hasattr(adapter, 'tripoli')
        except ImportError as e:
            # Expected when Tripoli-5 is not installed
            assert 'tripoli5' in str(e).lower()


class TestTripoliModel:
    """Tests for TripoliModel container."""

    def test_tripoli_model_creation(self):
        """Test TripoliModel creation."""
        adapter = MockTripoliAdapter()
        core = Core.simple_demo_3x3()

        mat = Material('UO2', 10.4, {'U': 1})
        tripoli_mat = adapter.create_material(mat)
        geometry = adapter.create_geometry(core)

        model = TripoliModel(
            materials={'UO2': tripoli_mat},
            geometry=geometry,
            core=core
        )

        assert 'UO2' in model.materials
        assert model.geometry is not None
        assert model.core is core


if __name__ == '__main__':
    pytest.main([__file__, '-v'])
