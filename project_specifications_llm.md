
# pytrip5 — project specification & Claude prompt

> Objective: build `pytrip5`, a Python high-level interface for Tripoli-5 enabling full-core PWR modelling and simulations. Use Tripoli-5 Python API and take inspiration from PyDrag (IRSN) for design patterns and API ergonomics.

---

## Quick context (sources)

* Tripoli-5 provides a **Python API** that exposes core simulation building blocks (geometry, sources, scores, simulation types, etc.). ([GitLab][1])
* Tripoli-5 is designed for reactor physics and HPC Monte-Carlo transport; the code supports neutrons, photons, electrons/positrons and includes CSG geometry, scores, and simulation features relevant to core-level modelling. ([EPJ-N][2])
* PyDrag (IRSN) is a useful reference for API ergonomics and wrapping native simulation engines into a fluent, testable Python interface. Use its structure and docs as inspiration. ([GitLab][3])
* Examples and `tripoli5.score` modules show how scores are represented and computed — useful to design `pytrip5` scoring abstractions. ([GitLab][4])

---

## How Claude should behave (system-level instructions)

You are Claude Code. Your job is to design, propose, and generate high-quality, production-ready Python code and supporting artifacts for `pytrip5`. Follow these rules:

1. **Accuracy-first** — when referencing Tripoli-5 API elements, prefer direct docstrings, examples, and the Tripoli-5 Python API docs. Cite the documentation when you use triples or make assumptions. ([GitLab][1])
2. **API ergonomics** — produce a fluent, Pythonic, typed, and well-documented interface inspired by PyDrag's modular approach. Favor small composable classes (Model, Core, Assembly, FuelPin, Material, Source, Score, Runner). ([GitLab][3])
3. **Deliverables** — produce code, unit tests, example notebooks, and a short README. Ensure tests are runnable in CI and mock Tripoli-5 where necessary.
4. **No external downloads** — do not attempt to download binary Tripoli-5 from the internet during code generation; instead, create adapter layers that call the Tripoli-5 Python API if present at runtime, and provide mocked interfaces for offline tests. ([GitLab][1])
5. **Security & safety** — avoid producing code that performs unsafe system-level operations or distributes sensitive nuclear data. Provide placeholders and clear comments where access to licensed Tripoli-5 binaries or restricted cross-section libraries is required.

---

## High-level goals (succinct)

1. Provide a `pytrip5` package that:

   * Offers high-level objects to build full-core PWR models (assemblies, core layout, materials, control rods, burnable poisons).
   * Transforms these objects into Tripoli-5 Python API inputs (geometry, sources, simulation settings).
   * Launches Tripoli-5 simulations (criticality and fixed-source) and collects scores (k-effective, flux maps, pin powers). ([GitLab][5])
2. Make API friendly for iterative research workflows (notebooks, CI, batch HPC).
3. Offer robust mocking and unit tests so development does not require a Tripoli-5 installation.

---

## Suggested package layout (files & modules)

```
pytrip5/
├─ pytrip5/__init__.py
├─ pytrip5/core.py           # high-level domain model: Core, Assembly, Pin, Material
├─ pytrip5/adapter.py        # Tripoli-5 API adapter layer (thin wrapper)
├─ pytrip5/simulation.py     # Runner, SimulationConfig, schedule & run helpers
├─ pytrip5/score.py          # Score abstractions and converters to tripoli5.score
├─ pytrip5/io.py             # import/export: assemblies, core map, statepoints
├─ pytrip5/tests/            # unit tests & fixtures (use pytest)
├─ examples/notebooks/       # example notebooks: full-core setup, run, postprocess
├─ README.md
├─ pyproject.toml
```

---

## Core design decisions / API surface (with sample signatures)

Design for **type annotations**, **dataclasses**, **immutability where appropriate**, and **pydantic** or simple validation.

### Domain dataclasses

```python
from dataclasses import dataclass
from typing import Sequence

@dataclass(frozen=True)
class Material:
    name: str
    density: float  # g/cm3
    compositions: dict[str, float]  # {'U235': 0.03, 'U238': 0.97}

@dataclass(frozen=True)
class Pin:
    id: str
    radius: float
    material: Material

@dataclass
class Assembly:
    id: str
    pitch: float
    pins: Sequence[Pin]  # 2D grid or lattice helper
```

### Core and Layout

```python
class Core:
    def __init__(self, assemblies: dict[str, Assembly], layout: Sequence[Sequence[str]]):
        ...
    def to_tripoli(self, adapter: TripoliAdapter) -> TripoliModel:
        ...
```

### Adapter pattern (Tripoli-5 interface isolation)

```python
class TripoliAdapter:
    def __init__(self, tripoli_module):
        # tripoli_module is the importable Tripoli-5 python package
        self.tripoli = tripoli_module

    def create_material(self, material: Material) -> object: ...
    def create_geometry(self, core: Core) -> object: ...
    def configure_simulation(self, config: SimulationConfig) -> object: ...
    def run(self, sim_object) -> RunResult: ...
```

* The adapter should gracefully fallback to a `MockTripoliAdapter` when `tripoli` is not importable; tests should exercise both.

---

## Example user flows (what the library must support)

1. **Notebook quickstart** — build a 3x3 core of identical assemblies, run a criticality calculation, obtain `k_eff` and per-assembly power distribution.
2. **HPC batch** — export the Tripoli input files for cluster submission (geometry, materials, run scripts), submit externally, and import statepoint results back into `pytrip5.io`.
3. **Parameter sweep** — programmatically change boron concentration or control rod insertion and re-run, providing automatic re-seeding of random number generator and result aggregation.

---

## Concrete tasks for Claude Code (step-by-step)

Produce outputs for each numbered task. Prefer to produce code with docstrings and doctest-style short examples.

1. **Scaffold code**: generate `core.py`, `adapter.py`, `simulation.py`, `score.py` with minimal but runnable logic and typed stubs for Tripoli calls. Use `MockTripoliAdapter` implementation that mirrors the Tripoli-5 Python API shapes (geometry, scores, run). Cite API doc for names used. ([GitLab][1])

2. **Adapter implementation**:

   * Provide `TripoliAdapter` which maps `pytrip5.Material` → `tripoli5.material` (or equivalent) objects, `pytrip5.Core` → Tripoli volumes/regions.
   * Implement `MockTripoliAdapter` that simulates run latency and returns plausible `k_eff` and score dictionaries (for unit tests).

3. **Score mapping**:

   * Create `pytrip5.score` classes (e.g., `KeffectiveScore`, `PinPowerScore`) that can convert to Tripoli `score` specs and parse Tripoli results into numpy arrays. Use `tripoli5.score` API examples as model. ([GitLab][4])

4. **Examples & tests**:

   * Provide one Jupyter notebook example `examples/notebooks/quickstart.ipynb` (or `.py` script) showing a simple core build and a run using `MockTripoliAdapter`.
   * Provide pytest tests verifying: dataclass validation, adapter mapping, simulation run returns expected structures (mocked numeric checks).

5. **README & usage guide**:

   * Short usage examples, installation notes (including "requires Tripoli-5 python package for real runs"), and how to configure CI to use mocked tests.

---

## Code style and constraints

* Follow **PEP8**, **PEP484** typing. Use `black` formatting, docstrings in Google or NumPy style.
* Keep the adapter thin — do not duplicate Tripoli logic; convert only.
* Tests should not require Tripoli-5 to be present — rely on `MockTripoliAdapter`. But integration tests should be flagged and optionally run only when Tripoli-5 is installed (guarded via env var `TRIPOLI_PRESENT`).
* Avoid heavy dependencies; keep runtime dependencies minimal (`numpy`, `pytest`, optionally `pydantic` for validation).

---

## Example code snippets (starter implementations)

> These are *starter* files Claude should generate in full — complete functions, docstrings, and simple tests.

### `pytrip5/adapter.py` (sketch)

```python
# (full file to be produced by Claude)
# Provide TripoliAdapter + MockTripoliAdapter
```

### `pytrip5/core.py` (sketch)

```python
# dataclasses for Material, Pin, Assembly, Core
```

### `pytrip5/simulation.py` (sketch)

```python
# SimulationConfig, Runner.run(adapter, core, config) -> RunResult
```

(Claude should expand these sketches into tested, typed code.)

---

## Unit tests & CI

* Use `pytest`. Provide test fixtures that construct a small core and assert adapter produces expected Tripoli-like structures.
* Provide CI (GitHub Actions) workflow that runs `pytest` and lints with `flake8` or `ruff`. Integration tests that require Tripoli-5 are gated behind a job that checks `python -c "import tripoli5"`.

---

## Evaluation criteria (how to grade outputs)

1. **Completeness** — Are all modules scaffolded and importable? Are docstrings present?
2. **Correct mapping to Tripoli-5** — Are the adapter method names and expected Tripoli API constructs consistent with Tripoli-5 docs? (spot-check with Tripoli docs). ([GitLab][1])
3. **Test coverage** — Are core behaviors covered by unit tests (>=70% for core modules)?
4. **Mock fidelity** — Does the mock adapter return realistic shapes and values to allow downstream code to be developed without real Tripoli?
5. **Usability** — Is the API intuitive for notebook workflows?

---

## Edge cases & notes for Claude

* **Licensing**: Tripoli-5 is produced by CEA/ASNR/EDF and may have licensing restrictions. Do not attempt to embed or redistribute Tripoli-5 binaries or protected cross-section libraries. Reference Tripoli-5 docs instead. ([GitLab][1])
* **Performance**: Full-core Monte-Carlo runs require HPC and domain decomposition; `pytrip5` should provide hooks to configure parallel/external submission but not implement cluster schedulers. See Tripoli-5 HPC goals. ([EPJ-N][2])
* **Geometry complexity**: Tripoli-5 supports multiple geometry models (AGORA, ROOT, etc.); allow users to select geometry backend in `TripoliAdapter` with configuration flags. ([GitLab][5])

---

## Example prompt snippets to add to Claude for code generation tasks

### 1) Create scaffolding (single-shot)

```
Generate the `pytrip5` package scaffolding with modules: core.py, adapter.py, simulation.py, score.py, io.py, tests. Implement dataclasses and a working MockTripoliAdapter. Provide pytest tests demonstrating a mocked criticality run returning a plausible k_eff float and a 2D array for pin powers. Use numpy for arrays. Add docstrings and type hints.
```

### 2) Implement TripoliAdapter mapping

```
Implement TripoliAdapter methods:
- create_material(material: Material) -> TripoliMaterialObject
- create_geometry(core: Core) -> TripoliGeometryObject
- configure_simulation(config: SimulationConfig) -> TripoliRunObject
- run(tripoli_run_object) -> RunResult

When Tripoli is absent, the adapter must raise ImportError only when used for a real run; otherwise the MockTripoliAdapter must be used in tests.
```

### 3) Create Score converters

```
Implement KeffectiveScore and PinPowerScore with:
- to_tripoli_score_spec()
- from_tripoli_result(tripoli_result) -> typed result (float, numpy.ndarray)
```

---

## Minimal acceptance test (what I will run locally)

```python
from pytrip5 import core, adapter, simulation
# build a small core
c = core.Core.simple_demo_3x3()
adapter = adapter.MockTripoliAdapter()
res = simulation.Runner.run(adapter, c, simulation.SimulationConfig(criticality=True))
assert isinstance(res.k_eff, float)
assert res.pin_powers.shape == (3,3)  # or expected shape
```

---

## References (key docs used)

* Tripoli-5 Python API docs — *The Python API* section. ([GitLab][1])
* Overview & capabilities of TRIPOLI-5 (EPJ/overview paper). ([EPJ-N][2])
* PyDrag (IRSN) documentation & repo — used for API ergonomics inspiration. ([GitLab][3])
* Tripoli-5 scores & examples (score module). ([GitLab][4])
* Tripoli-5 changelog / features summary (geometry, scores, simulation types). ([GitLab][5])

---

## Next steps I can do for you (choose one)

* Generate the *complete* initial codebase (all modules + tests + CI) as files (I will output them in the chat).
* Produce a compact system+developer+user prompt split (if you want to feed Claude with separate role prompts).
* Produce one fully worked Jupyter notebook `quickstart.ipynb` that uses `MockTripoliAdapter` demonstrating a full flow.

Tell me which of the three you'd like me to start generating right now and I will produce the code and tests immediately.

[1]: https://tripoli5.asnr.dev/documentation/api/python-api.html?utm_source=chatgpt.com "The Python API — TRIPOLI-5 user guide 0.2.0-wip ... - asnr.dev"
[2]: https://www.epj-n.org/10.1051/epjn/2024028?utm_source=chatgpt.com "Overview of TRIPOLI-5, a Monte Carlo code for HPC"
[3]: https://gitlab.extra.irsn.fr/PyDrag/PyDrag/-/tree/3e529c52e61acf3665ded882c4270202960804ec/docs/source?utm_source=chatgpt.com "docs/source · 3e529c52e61acf3665ded882c4270202960804ec"
[4]: https://tripoli5.asnr.dev/documentation/examples/features/score.html?utm_source=chatgpt.com "Scores — TRIPOLI-5 user guide 0.2.0-wip documentation"
[5]: https://tripoli5.asnr.dev/documentation/release/changelog.html?utm_source=chatgpt.com "Changelog — TRIPOLI-5 user guide 0.2.0-wip ... - asnr.dev"
