"""Tests for simulation module."""

import pytest
from pyT5 import Simulation, NuclearData, MaterialLibrary, Core, NeutronSource


class TestSimulation:
    """Tests for Simulation class."""

    def test_simulation_creation(self) -> None:
        """Test creating a simulation."""
        sim = Simulation(
            name="test_sim",
            n_particles=10000,
            n_cycles=100,
            n_inactive=20,
            n_threads=4,
        )
        assert sim.name == "test_sim"
        assert sim.n_particles == 10000
        assert sim.n_cycles == 100
        assert sim.n_inactive == 20
        assert sim.n_threads == 4

    def test_simulation_invalid_particles(self) -> None:
        """Test that invalid particle count raises error."""
        with pytest.raises(ValueError, match="n_particles must be positive"):
            Simulation(name="test", n_particles=-100)

    def test_simulation_invalid_cycles(self) -> None:
        """Test that invalid cycle counts raise error."""
        with pytest.raises(ValueError, match="n_inactive.*must be less than n_cycles"):
            Simulation(name="test", n_cycles=100, n_inactive=150)

    def test_simulation_invalid_threads(self) -> None:
        """Test that invalid thread count raises error."""
        with pytest.raises(ValueError, match="n_threads must be positive"):
            Simulation(name="test", n_threads=0)

    def test_set_particles_per_cycle(self) -> None:
        """Test setting particles per cycle."""
        sim = Simulation(name="test")
        sim.set_particles_per_cycle(20000)
        assert sim.n_particles == 20000

    def test_set_cycles(self) -> None:
        """Test setting cycle counts."""
        sim = Simulation(name="test")
        sim.set_cycles(n_cycles=200, n_inactive=50)
        assert sim.n_cycles == 200
        assert sim.n_inactive == 50

    def test_set_threads(self) -> None:
        """Test setting thread count."""
        sim = Simulation(name="test")
        sim.set_threads(8)
        assert sim.n_threads == 8

    def test_validate_missing_components(self) -> None:
        """Test that validation fails when components missing."""
        sim = Simulation(name="test")
        with pytest.raises(RuntimeError, match="Nuclear data not set"):
            sim.validate()

    def test_validate_complete_simulation(
        self,
        temp_nuclear_data_file,
        material_library: MaterialLibrary,
        sample_neutron_source: NeutronSource,
    ) -> None:
        """Test validation with all components set."""
        sim = Simulation(name="test")
        nuclear_data = NuclearData(cross_section_library=temp_nuclear_data_file)
        nuclear_data.validate()

        core = Core(name="test_core")

        sim.set_nuclear_data(nuclear_data)
        sim.set_materials(material_library)
        sim.set_geometry(core)
        sim.set_source(sample_neutron_source)

        assert sim.validate() is True
