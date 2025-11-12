"""Pytest configuration and fixtures for pyT5 tests."""

import pytest
import numpy as np
from pathlib import Path
from pyT5 import (
    Material,
    MaterialLibrary,
    Cell,
    CellLibrary,
    NuclearData,
    NeutronSource,
    PinCell,
    Assembly,
)


@pytest.fixture
def sample_material() -> Material:
    """Create a sample UO2 fuel material."""
    return Material(
        name="UO2_fuel",
        nuclides={"U235": 0.03, "U238": 0.97, "O16": 2.0},
        temperature=900.0,
        density=10.4,
        state="solid",
    )


@pytest.fixture
def sample_water_material() -> Material:
    """Create a sample water material."""
    return Material(
        name="light_water",
        nuclides={"H1": 2.0, "O16": 1.0},
        temperature=300.0,
        density=1.0,
        state="liquid",
    )


@pytest.fixture
def material_library(sample_material: Material, sample_water_material: Material) -> MaterialLibrary:
    """Create a material library with sample materials."""
    library = MaterialLibrary()
    library.add_material(sample_material)
    library.add_material(sample_water_material)
    return library


@pytest.fixture
def sample_cell(sample_material: Material) -> Cell:
    """Create a sample cell."""
    return Cell(
        name="fuel_cell",
        material=sample_material,
        volume=100.0,
        importance=1.0,
    )


@pytest.fixture
def cell_library(sample_cell: Cell) -> CellLibrary:
    """Create a cell library with a sample cell."""
    library = CellLibrary()
    library.add_cell(sample_cell)
    return library


@pytest.fixture
def sample_pin_cell() -> PinCell:
    """Create a sample pin cell."""
    return PinCell(
        name="standard_pin",
        pitch=1.26,
        height=365.76,
        fuel_radius=0.4096,
        clad_inner_radius=0.418,
        clad_outer_radius=0.475,
    )


@pytest.fixture
def sample_assembly() -> Assembly:
    """Create a sample 17x17 assembly."""
    return Assembly(
        name="17x17_assembly",
        lattice_type="square",
        n_pins_x=17,
        n_pins_y=17,
        pin_pitch=1.26,
        assembly_pitch=21.5,
    )


@pytest.fixture
def sample_neutron_source() -> NeutronSource:
    """Create a sample neutron source."""
    return NeutronSource(
        name="fission_source",
        source_type="criticality",
        intensity=1.0e6,
    )


@pytest.fixture
def temp_nuclear_data_file(tmp_path: Path) -> Path:
    """Create a temporary nuclear data file."""
    data_file = tmp_path / "test_xsections.dat"
    data_file.write_text("# Mock nuclear data file\n")
    return data_file
