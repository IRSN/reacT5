"""Unit tests for pytrip5.simulation module."""

import pytest
import numpy as np

from pytrip5.core import Core
from pytrip5.adapter import MockTripoliAdapter
from pytrip5.simulation import SimulationConfig, RunResult, Runner
from pytrip5.score import KeffectiveScore, PinPowerScore


class TestSimulationConfig:
    """Tests for SimulationConfig."""

    def test_config_creation(self):
        """Test basic configuration creation."""
        config = SimulationConfig(
            criticality=True,
            particles_per_batch=10000,
            active_batches=50,
            inactive_batches=20,
            seed=12345
        )

        assert config.criticality is True
        assert config.particles_per_batch == 10000
        assert config.active_batches == 50
        assert config.inactive_batches == 20
        assert config.seed == 12345

    def test_config_total_particles(self):
        """Test total_particles property."""
        config = SimulationConfig(
            particles_per_batch=1000,
            active_batches=10
        )
        assert config.total_particles == 10000

    def test_config_total_batches(self):
        """Test total_batches property for criticality."""
        config = SimulationConfig(
            criticality=True,
            active_batches=50,
            inactive_batches=20
        )
        assert config.total_batches == 70

    def test_config_total_batches_fixed_source(self):
        """Test total_batches for fixed source (no inactive)."""
        config = SimulationConfig(
            criticality=False,
            active_batches=50
        )
        assert config.total_batches == 50

    def test_config_negative_particles_raises(self):
        """Test that negative particles raises ValueError."""
        with pytest.raises(ValueError, match="must be positive"):
            SimulationConfig(particles_per_batch=-1000)

    def test_config_negative_batches_raises(self):
        """Test that negative active batches raises ValueError."""
        with pytest.raises(ValueError, match="must be positive"):
            SimulationConfig(active_batches=-10)

    def test_quick_criticality_factory(self):
        """Test quick_criticality factory method."""
        config = SimulationConfig.quick_criticality(seed=42)

        assert config.criticality is True
        assert config.particles_per_batch == 1000
        assert config.active_batches == 10
        assert config.inactive_batches == 5
        assert config.seed == 42

    def test_production_criticality_factory(self):
        """Test production_criticality factory method."""
        config = SimulationConfig.production_criticality(seed=42)

        assert config.criticality is True
        assert config.particles_per_batch == 100000
        assert config.active_batches == 200
        assert config.inactive_batches == 50


class TestRunResult:
    """Tests for RunResult."""

    def test_result_creation(self):
        """Test basic result creation."""
        result = RunResult(
            k_eff=1.0234,
            k_eff_std=0.0012,
            scores={'pin_powers': np.array([[1.0, 1.1]])}
        )

        assert result.k_eff == 1.0234
        assert result.k_eff_std == 0.0012
        assert 'pin_powers' in result.scores

    def test_result_k_eff_with_uncertainty(self):
        """Test k_eff_with_uncertainty property."""
        result = RunResult(k_eff=1.0234, k_eff_std=0.0012)
        formatted = result.k_eff_with_uncertainty

        assert '1.0234' in formatted
        assert '0.0012' in formatted
        assert '±' in formatted

    def test_result_k_eff_with_uncertainty_none(self):
        """Test k_eff_with_uncertainty when k_eff is None."""
        result = RunResult()
        assert result.k_eff_with_uncertainty is None

    def test_result_get_score(self):
        """Test get_score method."""
        powers = np.array([[1.0, 1.1]])
        result = RunResult(scores={'pin_powers': powers})

        retrieved = result.get_score('pin_powers')
        assert np.array_equal(retrieved, powers)

    def test_result_get_score_missing_raises(self):
        """Test that getting missing score raises KeyError."""
        result = RunResult()
        with pytest.raises(KeyError):
            result.get_score('nonexistent')

    def test_result_pin_powers_property(self):
        """Test pin_powers convenience property."""
        powers = np.array([[1.0, 1.1]])
        result = RunResult(scores={'pin_powers': powers})

        assert np.array_equal(result.pin_powers, powers)

    def test_result_pin_powers_none(self):
        """Test pin_powers when not present."""
        result = RunResult()
        assert result.pin_powers is None


class TestRunner:
    """Tests for Runner."""

    def test_runner_run_basic(self):
        """Test basic simulation run."""
        adapter = MockTripoliAdapter(simulate_latency=False)
        core = Core.simple_demo_3x3()
        config = SimulationConfig.quick_criticality(
            scores=[KeffectiveScore()],
            seed=42
        )

        result = Runner.run(adapter, core, config)

        assert isinstance(result, RunResult)
        assert result.k_eff is not None
        assert result.k_eff_std is not None

    def test_runner_run_with_scores(self):
        """Test run with multiple scores."""
        adapter = MockTripoliAdapter(simulate_latency=False)
        core = Core.simple_demo_3x3()
        config = SimulationConfig.quick_criticality(
            scores=[KeffectiveScore(), PinPowerScore('pin_powers')],
            seed=42
        )

        result = Runner.run(adapter, core, config)

        assert result.k_eff is not None
        assert 'pin_powers' in result.scores
        assert result.pin_powers is not None

    def test_runner_run_batch(self):
        """Test running batch of simulations."""
        adapter = MockTripoliAdapter(simulate_latency=False)

        cores = [Core.simple_demo_3x3() for _ in range(3)]
        configs = [SimulationConfig.quick_criticality(seed=i) for i in range(3)]

        results = Runner.run_batch(adapter, cores, configs)

        assert len(results) == 3
        for result in results:
            assert isinstance(result, RunResult)
            assert result.k_eff is not None

    def test_runner_run_batch_length_mismatch_raises(self):
        """Test that mismatched batch lengths raise ValueError."""
        adapter = MockTripoliAdapter(simulate_latency=False)

        cores = [Core.simple_demo_3x3() for _ in range(3)]
        configs = [SimulationConfig.quick_criticality() for _ in range(2)]

        with pytest.raises(ValueError, match="must match"):
            Runner.run_batch(adapter, cores, configs)

    def test_runner_parameter_sweep(self):
        """Test parameter sweep functionality."""
        adapter = MockTripoliAdapter(simulate_latency=False)
        core = Core.simple_demo_3x3()
        config = SimulationConfig.quick_criticality(seed=100)

        results = Runner.parameter_sweep(
            adapter,
            core,
            'boron_concentration',
            [0, 500, 1000],
            config
        )

        assert len(results) == 3
        assert 0 in results
        assert 500 in results
        assert 1000 in results

        # Check that k_eff decreases with boron
        assert results[0].k_eff > results[500].k_eff > results[1000].k_eff

    def test_acceptance_test(self):
        """Minimal acceptance test from specification."""
        from pytrip5 import core, adapter, simulation

        # Build a small core
        c = core.Core.simple_demo_3x3()
        a = adapter.MockTripoliAdapter(simulate_latency=False)
        res = simulation.Runner.run(
            a, c,
            simulation.SimulationConfig(criticality=True)
        )

        assert isinstance(res.k_eff, float)
        # Note: pin_powers won't exist unless we add the score
        # So let's test with the score:
        config = simulation.SimulationConfig(
            criticality=True,
            scores=[PinPowerScore('pin_powers')]
        )
        res = simulation.Runner.run(a, c, config)
        assert res.pin_powers.shape == (3, 3)


if __name__ == '__main__':
    pytest.main([__file__, '-v'])
