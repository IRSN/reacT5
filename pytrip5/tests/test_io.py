"""Unit tests for pytrip5.io module."""

import pytest
import tempfile
from pathlib import Path
import numpy as np

from pytrip5.core import Core
from pytrip5.simulation import RunResult
from pytrip5 import io


class TestCoreIO:
    """Tests for Core serialization/deserialization."""

    def test_save_load_core_json(self):
        """Test saving and loading core to/from JSON."""
        core = Core.simple_demo_3x3()

        with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
            filepath = f.name

        try:
            # Save
            io.save_core_json(core, filepath)

            # Load
            loaded_core = io.load_core_json(filepath)

            # Verify
            assert loaded_core.shape == core.shape
            assert loaded_core.boron_concentration == core.boron_concentration
            assert len(loaded_core.assemblies) == len(core.assemblies)

            # Check assembly details
            for asm_id, asm in core.assemblies.items():
                loaded_asm = loaded_core.assemblies[asm_id]
                assert loaded_asm.id == asm.id
                assert loaded_asm.pitch == asm.pitch
                assert loaded_asm.shape == asm.shape
                assert loaded_asm.enrichment == asm.enrichment

        finally:
            Path(filepath).unlink(missing_ok=True)


class TestResultIO:
    """Tests for RunResult serialization/deserialization."""

    def test_save_load_results_json(self):
        """Test saving and loading results to/from JSON."""
        result = RunResult(
            k_eff=1.0234,
            k_eff_std=0.0012,
            scores={
                'pin_powers': np.array([[1.0, 1.1], [0.9, 1.0]]),
                'scalar_score': 42.5
            }
        )

        with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
            filepath = f.name

        try:
            # Save
            io.save_results_json(result, filepath)

            # Load
            loaded_result = io.load_results_json(filepath)

            # Verify
            assert loaded_result.k_eff == result.k_eff
            assert loaded_result.k_eff_std == result.k_eff_std
            assert 'pin_powers' in loaded_result.scores
            assert np.allclose(loaded_result.scores['pin_powers'], result.scores['pin_powers'])
            assert loaded_result.scores['scalar_score'] == 42.5

        finally:
            Path(filepath).unlink(missing_ok=True)


class TestPinPowerIO:
    """Tests for pin power CSV export/import."""

    def test_export_import_pin_powers_with_position(self):
        """Test exporting and importing pin powers with position indices."""
        powers = np.array([[1.0, 1.1, 1.2], [0.9, 1.0, 1.1], [0.8, 0.9, 1.0]])

        with tempfile.NamedTemporaryFile(mode='w', suffix='.csv', delete=False) as f:
            filepath = f.name

        try:
            # Export
            io.export_pin_powers_csv(powers, filepath, include_position=True)

            # Import
            loaded_powers = io.import_pin_powers_csv(filepath, has_header=True)

            # Verify
            assert np.allclose(loaded_powers, powers)

        finally:
            Path(filepath).unlink(missing_ok=True)

    def test_export_import_pin_powers_matrix(self):
        """Test exporting and importing pin powers as matrix."""
        powers = np.array([[1.0, 1.1], [0.9, 1.0]])

        with tempfile.NamedTemporaryFile(mode='w', suffix='.csv', delete=False) as f:
            filepath = f.name

        try:
            # Export
            io.export_pin_powers_csv(powers, filepath, include_position=False)

            # Import
            loaded_powers = io.import_pin_powers_csv(filepath, has_header=False)

            # Verify
            assert np.allclose(loaded_powers, powers)

        finally:
            Path(filepath).unlink(missing_ok=True)


class TestSummaryExport:
    """Tests for summary text export."""

    def test_export_summary_txt(self):
        """Test exporting summary to text file."""
        result = RunResult(
            k_eff=1.0234,
            k_eff_std=0.0012,
            scores={
                'pin_powers': np.array([[1.0, 1.1], [0.9, 1.0]]),
                'flux': np.array([1e14, 2e14, 3e14])
            }
        )

        with tempfile.NamedTemporaryFile(mode='w', suffix='.txt', delete=False) as f:
            filepath = f.name

        try:
            # Export
            io.export_summary_txt(result, filepath)

            # Read and verify content
            with open(filepath, 'r') as f:
                content = f.read()

            assert 'pytrip5 Simulation Results' in content
            assert '1.0234' in content
            assert '0.0012' in content
            assert 'pin_powers' in content
            assert 'flux' in content
            assert 'Shape:' in content
            assert 'Mean:' in content

        finally:
            Path(filepath).unlink(missing_ok=True)


class TestHDF5IO:
    """Tests for HDF5 I/O (requires h5py)."""

    @pytest.mark.skipif(not _has_h5py(), reason="h5py not installed")
    def test_save_load_results_hdf5(self):
        """Test saving and loading results to/from HDF5."""
        result = RunResult(
            k_eff=1.0234,
            k_eff_std=0.0012,
            scores={
                'pin_powers': np.array([[1.0, 1.1], [0.9, 1.0]]),
                'flux': np.array([1e14, 2e14, 3e14])
            }
        )

        with tempfile.NamedTemporaryFile(suffix='.h5', delete=False) as f:
            filepath = f.name

        try:
            # Save
            io.save_results_hdf5(result, filepath)

            # Load
            loaded_result = io.load_results_hdf5(filepath)

            # Verify
            assert loaded_result.k_eff == result.k_eff
            assert loaded_result.k_eff_std == result.k_eff_std
            assert np.allclose(loaded_result.scores['pin_powers'], result.scores['pin_powers'])
            assert np.allclose(loaded_result.scores['flux'], result.scores['flux'])

        finally:
            Path(filepath).unlink(missing_ok=True)

    def test_hdf5_import_error_when_not_installed(self):
        """Test that helpful error is raised when h5py not available."""
        if _has_h5py():
            pytest.skip("h5py is installed, cannot test import error")

        result = RunResult(k_eff=1.0)

        with tempfile.NamedTemporaryFile(suffix='.h5', delete=False) as f:
            filepath = f.name

        try:
            with pytest.raises(ImportError, match="h5py"):
                io.save_results_hdf5(result, filepath)
        finally:
            Path(filepath).unlink(missing_ok=True)


def _has_h5py():
    """Check if h5py is available."""
    try:
        import h5py
        return True
    except ImportError:
        return False


if __name__ == '__main__':
    pytest.main([__file__, '-v'])
