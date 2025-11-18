"""I/O utilities for pytrip5.

This module provides functions for importing and exporting pytrip5 objects
to/from various file formats:
- JSON: For serializing core configurations, results
- HDF5: For large numerical data (flux maps, pin powers)
- CSV: For tabular data export
"""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any, Optional
import numpy as np

from pytrip5.core import Material, Pin, Assembly, Core
from pytrip5.simulation import RunResult


def save_core_json(core: Core, filepath: str | Path) -> None:
    """Save Core object to JSON file.

    Args:
        core: Core object to save
        filepath: Output file path

    Example:
        >>> from pytrip5.core import Core
        >>> core = Core.simple_demo_3x3()
        >>> save_core_json(core, 'core_config.json')
    """
    filepath = Path(filepath)

    # Serialize core to dict
    core_dict = {
        'assemblies': {},
        'layout': [[asm_id for asm_id in row] for row in core.layout],
        'boron_concentration': core.boron_concentration,
        'control_rod_positions': core.control_rod_positions
    }

    # Serialize assemblies
    for asm_id, assembly in core.assemblies.items():
        # Collect unique materials and pins
        materials_dict = {}
        pins_dict = {}

        for row in assembly.pins:
            for pin in row:
                if pin.material.name not in materials_dict:
                    materials_dict[pin.material.name] = {
                        'name': pin.material.name,
                        'density': pin.material.density,
                        'compositions': pin.material.compositions,
                        'temperature': pin.material.temperature
                    }
                if pin.id not in pins_dict:
                    pins_dict[pin.id] = {
                        'id': pin.id,
                        'radius': pin.radius,
                        'material_name': pin.material.name,
                        'pitch': pin.pitch
                    }

        core_dict['assemblies'][asm_id] = {
            'id': assembly.id,
            'pitch': assembly.pitch,
            'enrichment': assembly.enrichment,
            'shape': assembly.shape,
            'materials': materials_dict,
            'pins': pins_dict,
            'pin_layout': [[pin.id for pin in row] for row in assembly.pins]
        }

    # Write to file
    with open(filepath, 'w') as f:
        json.dump(core_dict, f, indent=2)


def load_core_json(filepath: str | Path) -> Core:
    """Load Core object from JSON file.

    Args:
        filepath: Input JSON file path

    Returns:
        Reconstructed Core object

    Example:
        >>> core = load_core_json('core_config.json')
        >>> core.shape
        (3, 3)
    """
    filepath = Path(filepath)

    with open(filepath, 'r') as f:
        core_dict = json.load(f)

    # Reconstruct assemblies
    assemblies = {}

    for asm_id, asm_data in core_dict['assemblies'].items():
        # Reconstruct materials
        materials = {
            name: Material(
                name=mat['name'],
                density=mat['density'],
                compositions=mat['compositions'],
                temperature=mat['temperature']
            )
            for name, mat in asm_data['materials'].items()
        }

        # Reconstruct pins
        pins_by_id = {
            pin_id: Pin(
                id=pin_data['id'],
                radius=pin_data['radius'],
                material=materials[pin_data['material_name']],
                pitch=pin_data['pitch']
            )
            for pin_id, pin_data in asm_data['pins'].items()
        }

        # Reconstruct pin layout
        pin_layout = [
            [pins_by_id[pin_id] for pin_id in row]
            for row in asm_data['pin_layout']
        ]

        # Create assembly
        assemblies[asm_id] = Assembly(
            id=asm_data['id'],
            pitch=asm_data['pitch'],
            pins=pin_layout,
            enrichment=asm_data['enrichment']
        )

    # Reconstruct core
    core = Core(
        assemblies=assemblies,
        layout=core_dict['layout'],
        boron_concentration=core_dict['boron_concentration'],
        control_rod_positions=core_dict['control_rod_positions']
    )

    return core


def save_results_json(result: RunResult, filepath: str | Path) -> None:
    """Save RunResult to JSON file.

    Note: Large arrays (pin powers, flux) are saved as nested lists.
    For large datasets, consider using save_results_hdf5 instead.

    Args:
        result: RunResult to save
        filepath: Output file path

    Example:
        >>> from pytrip5.simulation import RunResult
        >>> result = RunResult(k_eff=1.0234, k_eff_std=0.0012)
        >>> save_results_json(result, 'results.json')
    """
    filepath = Path(filepath)

    # Convert result to dict
    result_dict = {
        'k_eff': result.k_eff,
        'k_eff_std': result.k_eff_std,
        'scores': {}
    }

    # Convert numpy arrays to lists
    for score_name, score_value in result.scores.items():
        if isinstance(score_value, np.ndarray):
            result_dict['scores'][score_name] = score_value.tolist()
        else:
            result_dict['scores'][score_name] = score_value

    with open(filepath, 'w') as f:
        json.dump(result_dict, f, indent=2)


def load_results_json(filepath: str | Path) -> RunResult:
    """Load RunResult from JSON file.

    Args:
        filepath: Input JSON file path

    Returns:
        Reconstructed RunResult

    Example:
        >>> result = load_results_json('results.json')
        >>> result.k_eff
        1.0234
    """
    filepath = Path(filepath)

    with open(filepath, 'r') as f:
        result_dict = json.load(f)

    # Convert lists back to numpy arrays
    scores = {}
    for score_name, score_value in result_dict['scores'].items():
        if isinstance(score_value, list):
            scores[score_name] = np.array(score_value)
        else:
            scores[score_name] = score_value

    return RunResult(
        k_eff=result_dict.get('k_eff'),
        k_eff_std=result_dict.get('k_eff_std'),
        scores=scores
    )


def export_pin_powers_csv(
    pin_powers: np.ndarray,
    filepath: str | Path,
    include_position: bool = True
) -> None:
    """Export pin power distribution to CSV file.

    Args:
        pin_powers: 2D array of pin powers
        filepath: Output CSV file path
        include_position: If True, include row/col indices in output

    Example:
        >>> import numpy as np
        >>> powers = np.array([[1.0, 1.1], [0.9, 1.0]])
        >>> export_pin_powers_csv(powers, 'pin_powers.csv')
    """
    filepath = Path(filepath)

    rows, cols = pin_powers.shape

    with open(filepath, 'w') as f:
        # Write header
        if include_position:
            f.write('row,col,power\n')
            # Write data
            for i in range(rows):
                for j in range(cols):
                    f.write(f'{i},{j},{pin_powers[i, j]:.6f}\n')
        else:
            # Write as matrix
            for i in range(rows):
                row_str = ','.join(f'{pin_powers[i, j]:.6f}' for j in range(cols))
                f.write(row_str + '\n')


def import_pin_powers_csv(filepath: str | Path, has_header: bool = True) -> np.ndarray:
    """Import pin power distribution from CSV file.

    Args:
        filepath: Input CSV file path
        has_header: If True, skip first row as header

    Returns:
        2D numpy array of pin powers

    Example:
        >>> powers = import_pin_powers_csv('pin_powers.csv')
        >>> powers.shape
        (17, 17)
    """
    filepath = Path(filepath)

    with open(filepath, 'r') as f:
        lines = f.readlines()

    if has_header:
        lines = lines[1:]

    # Try to detect format (row,col,value vs matrix)
    first_line = lines[0].strip()
    if ',' in first_line and len(first_line.split(',')) == 3:
        # row,col,value format
        data = {}
        max_row = 0
        max_col = 0

        for line in lines:
            parts = line.strip().split(',')
            row, col, value = int(parts[0]), int(parts[1]), float(parts[2])
            data[(row, col)] = value
            max_row = max(max_row, row)
            max_col = max(max_col, col)

        # Create array
        powers = np.zeros((max_row + 1, max_col + 1))
        for (row, col), value in data.items():
            powers[row, col] = value

        return powers
    else:
        # Matrix format
        powers = []
        for line in lines:
            row_values = [float(x) for x in line.strip().split(',')]
            powers.append(row_values)
        return np.array(powers)


# HDF5 I/O (optional, requires h5py)

def save_results_hdf5(result: RunResult, filepath: str | Path) -> None:
    """Save RunResult to HDF5 file.

    Requires h5py package. This format is efficient for large arrays.

    Args:
        result: RunResult to save
        filepath: Output HDF5 file path

    Example:
        >>> result = RunResult(k_eff=1.0234, k_eff_std=0.0012)
        >>> save_results_hdf5(result, 'results.h5')  # doctest: +SKIP
    """
    try:
        import h5py
    except ImportError:
        raise ImportError(
            "h5py is required for HDF5 I/O. Install with: pip install h5py"
        )

    filepath = Path(filepath)

    with h5py.File(filepath, 'w') as f:
        # Save scalars
        if result.k_eff is not None:
            f.attrs['k_eff'] = result.k_eff
        if result.k_eff_std is not None:
            f.attrs['k_eff_std'] = result.k_eff_std

        # Save scores
        scores_group = f.create_group('scores')
        for score_name, score_value in result.scores.items():
            if isinstance(score_value, np.ndarray):
                scores_group.create_dataset(score_name, data=score_value)
            else:
                scores_group.attrs[score_name] = score_value


def load_results_hdf5(filepath: str | Path) -> RunResult:
    """Load RunResult from HDF5 file.

    Requires h5py package.

    Args:
        filepath: Input HDF5 file path

    Returns:
        Reconstructed RunResult

    Example:
        >>> result = load_results_hdf5('results.h5')  # doctest: +SKIP
        >>> result.k_eff
        1.0234
    """
    try:
        import h5py
    except ImportError:
        raise ImportError(
            "h5py is required for HDF5 I/O. Install with: pip install h5py"
        )

    filepath = Path(filepath)

    with h5py.File(filepath, 'r') as f:
        # Load scalars
        k_eff = f.attrs.get('k_eff')
        k_eff_std = f.attrs.get('k_eff_std')

        # Load scores
        scores = {}
        scores_group = f['scores']
        for score_name in scores_group.keys():
            scores[score_name] = np.array(scores_group[score_name])

        # Load scalar scores from attributes
        for attr_name, attr_value in scores_group.attrs.items():
            scores[attr_name] = attr_value

    return RunResult(
        k_eff=k_eff,
        k_eff_std=k_eff_std,
        scores=scores
    )


# Utility functions

def export_summary_txt(result: RunResult, filepath: str | Path) -> None:
    """Export a human-readable text summary of results.

    Args:
        result: RunResult to summarize
        filepath: Output text file path

    Example:
        >>> result = RunResult(k_eff=1.0234, k_eff_std=0.0012)
        >>> export_summary_txt(result, 'summary.txt')
    """
    filepath = Path(filepath)

    with open(filepath, 'w') as f:
        f.write('='*60 + '\n')
        f.write('pytrip5 Simulation Results Summary\n')
        f.write('='*60 + '\n\n')

        # k-effective
        if result.k_eff is not None:
            f.write(f'k-effective: {result.k_eff:.5f} ± {result.k_eff_std:.5f}\n\n')

        # Scores
        f.write('Scores:\n')
        f.write('-'*60 + '\n')
        for score_name, score_value in result.scores.items():
            if isinstance(score_value, np.ndarray):
                f.write(f'{score_name}:\n')
                f.write(f'  Shape: {score_value.shape}\n')
                f.write(f'  Mean:  {score_value.mean():.6e}\n')
                f.write(f'  Min:   {score_value.min():.6e}\n')
                f.write(f'  Max:   {score_value.max():.6e}\n')
                f.write(f'  Std:   {score_value.std():.6e}\n\n')
            else:
                f.write(f'{score_name}: {score_value}\n\n')
