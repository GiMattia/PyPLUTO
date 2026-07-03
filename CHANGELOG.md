# Changelog

All notable changes to this project will be documented in this file.
The format follows [Keep a Changelog](https://keepachangelog.com/en/1.1.0/).

---

## [Unreleased]

Work in progress on the `3D` branch (`pyproject.toml` version `1.2.4`, not yet
tagged/released), which diverged from `master` right after `v1.2.1`. Two of
the fixes below (Qt canvas backend, `set_axis` `tight` handling) were applied
independently on both `master` (released as `v1.2.2`/`v1.2.3`) and here;
they will collapse into one history once this branch merges. Per project
convention, everything below that is not a bug fix is **preliminary** and
subject to change before release.

### Added (preliminary)
- Volume rendering: `MPLVolumeRenderer` and the `Image.volume` method (`imagefuncs/volengine.py`, `imagefuncs/volume.py`), with new example scripts and tests
- GUI: slider-based playback controls for stepping/replaying outputs (`⏮ ◀ ▶ ⏸ ⏩ ⏭`), lock lines, and color pinning
- `GridPlotManager.showgrid`: new method drawing the cell interfaces of a 2D grid; supports `CARTESIAN`, `POLAR`, `CYLINDRICAL`, and `SPHERICAL` geometries, and draws all lines of each direction with a single `PlotManager.plot` call (instead of one call per line) for a large speedup on dense grids
- `PlotManager.plot`: documented support for 2D `x`/`y` input to draw multiple lines sharing one style in a single call (the primitive `showgrid`'s fast path relies on)
- `src/pyPLUTO/template.py`: reference template documenting the State/Kwargs/Mixin/Manager/Facade architecture used to add a new class

### Changed (preliminary)
- Removed the not-yet-flexible units handling added to `defh` reading in 1.2.0 (partial walkback pending a more general implementation)
- Updated golden reference images and the example test harness for a newer matplotlib version

### Fixed
- GUI: Qt canvas now uses `FigureCanvasQTAgg` from `matplotlib.backends.backend_qtagg` instead of an incorrect `backend_qt`/`backend_template` import; added a GUI canvas regression test
- `set_axis`: the `tight` keyword now updates `self.state.tight` before deciding whether to reinforce `tight_layout()`
- Particles: fixed bug in `offsetpart.py`
- `Image.showgrid`/`GridPlotManager.showgrid`: `geom` no longer overrides a `Load`'s actual geometry with a hardcoded `"CARTESIAN"` default when `data` is given; fixed a `Data`/`data` keyword-name mismatch in the `Image` facade that bypassed the explicit `data` parameter

---

## [1.2.3] — 2026-06-11

### Fixed
- `set_axis`: the `tight` keyword now updates `self.state.tight` before deciding whether to reinforce `tight_layout()`, fixing interactive re-runs that passed `tight=False`

### Changed
- Documentation build configuration and installation instructions updated

---

## [1.2.2] — 2026-06-09

### Fixed
- GUI: Qt canvas now uses `FigureCanvasQTAgg` from `matplotlib.backends.backend_qtagg` instead of an incorrect `backend_qt`/`backend_template` import

### Added
- GUI canvas regression test

---

## [1.2.1] — 2026-06-08

### Changed
- Updated citation info in `README.md` to point to the published JOSS paper instead of the arXiv preprint

---

## [1.2.0] — 2026-06-06

### Added
- `@track_kwargs` decorator applied to all public `**kwargs` methods; warns on unknown kwargs at call sites
- `_check: bool = True` explicit parameter on every `**kwargs` function; internal calls pass `_check=False`
- `from __future__ import annotations` in all package modules
- Units support (first implementation)
- Multiple-output chunk loading
- `set_text(text)` public function to control logging verbosity at any point in a session
- `__repr__` on `Load`, `LoadPart`, and `Image`

### Changed
- Complete refactoring of `Load` and `LoadPart` into manager subclasses
- GUI refactored to controller/service pattern
- Removed `pandas`/`dask` and `gridout` dependencies
- Replaced all library-level `print()` calls with `logging.getLogger(__name__)`; the package logger is wired to stdout automatically at import time
- `text` parameter semantics unified across `Load`, `LoadPart`, and `Image`: `None` (default) → standard INFO output, `False` → silent, `True` → full DEBUG logging
- `_kwargs_state` global mutable dict replaced with `contextvars.ContextVar` for thread- and async-safe kwargs tracking
- `track_kwargs` precomputes signature metadata at decoration time instead of per call
- `_check` hidden from public introspection (`help()`, IDE autocomplete, `@overload` stubs)
- Version single source of truth moved to `pyproject.toml`; `__version__` reads from `importlib.metadata` at runtime

### Fixed
- Custom variables bug in GUI
- Small bug in particles + `self.state` handling
- `LoadPart`: requesting a non-existent `chnk` now emits a `UserWarning` listing available chunks instead of silently producing an empty object that raises `AttributeError` on attribute access; for multi-output loads, only outputs that contain the requested chunk are loaded

---

## [1.1.5] — 2026-04-29

### Added
- Python 3.11 support
- Windows golden test environment via `uv`

### Changed
- Renamed `format` parameter to `datatype` throughout the loading API
- Moved all CI/CD workflows from `pip` to `uv`

### Fixed
- GUI bug fixes (general)

---

## [1.1.4] — 2026-04-19

### Changed
- Automated dependency updates via Dependabot for GitHub Actions
- CI: pinned all GitHub Actions to immutable commit hashes
- Updated `setuptools` requirement to `>=82.0.1`
- Added `uv.lock` upgrade automation

---

## [1.1.3] — 2026-04-19

### Changed
- Updated `CONTRIBUTING.md`
- Added `uv` and `pixi` installation badges to README
- Switched lock-file check to `uv`

---

## [1.1.2] — 2026-04-18

### Added
- Full `Load` class refactoring into dedicated manager classes
- `LoadPart` improvements and refactoring
- 1D, 2D, and 3D automated test suites
- ECHO code loader (`EchoLoadManager`)
- Support for `idefix.ini` alongside `pluto.ini` via `inifix`
- `inifix` as a hard dependency
- Windows compatibility fix for tab-file reading
- Parallel test execution via `pytest-xdist`

### Fixed
- `.T` transpose bug in HDF5 file loading
- Type annotation error in ECHO loader
- Warning formatting for `pluto.ini`

---

## [1.1.1] — 2025-09-16

### Fixed
- Minor corrections following JOSS paper proofs review
- Version string updated in `configure.py`

---

## [1.1] — 2025-07-22

### Added
- `Configure` class for package initialisation (session detection, coloured warnings/errors)
- `coverage_tests.py` and automated coverage badge via GitHub Actions
- `mypy` strict check integration
- Documentation table and docstring completeness check

### Changed
- Full refactoring of `Image` and related managers (`ImageTools`, `Range`, `Figure`)
- Switched error colouring from `black` to `ruff` + `ty` in pre-commit hooks
- Removed Windows Server 2019 from CI matrix

### Fixed
- Typo in `configure.py`

---

## [1.0.0] — 2025-01-17

Initial public release.

### Features
- `Load` class: fluid data loading for PLUTO/gPLUTO binary, HDF5, and tab formats
- `LoadPart` class: particle data loading
- `Image` class: full 1D/2D plotting pipeline (display, contour, plot, scatter, streamplot, zoom, colorbar, legend)
- Field-line integration (`find_fieldlines`) and contour extraction (`find_contour`)
- Fourier transform, nabla operators, coordinate transforms
- AMR box overplotting (`oplotbox`)
- GUI (PySide6-based) for interactive data exploration
- Sphinx documentation with worked examples
- CI on Linux, macOS, Windows across Python 3.11–3.13

[Unreleased]: https://github.com/GiMattia/pyPLUTO/compare/v1.2.3...HEAD
[1.2.3]: https://github.com/GiMattia/pyPLUTO/compare/v1.2.2...v1.2.3
[1.2.2]: https://github.com/GiMattia/pyPLUTO/compare/v1.2.1...v1.2.2
[1.2.1]: https://github.com/GiMattia/pyPLUTO/compare/v1.2.0...v1.2.1
[1.2.0]: https://github.com/GiMattia/pyPLUTO/compare/v1.1.5...v1.2.0
[1.1.5]: https://github.com/GiMattia/pyPLUTO/compare/v1.1.4...v1.1.5
[1.1.4]: https://github.com/GiMattia/pyPLUTO/compare/v1.1.3...v1.1.4
[1.1.3]: https://github.com/GiMattia/pyPLUTO/compare/v1.1.2...v1.1.3
[1.1.2]: https://github.com/GiMattia/pyPLUTO/compare/v1.1.1...v1.1.2
[1.1.1]: https://github.com/GiMattia/pyPLUTO/compare/v1.1...v1.1.1
[1.1]: https://github.com/GiMattia/pyPLUTO/compare/v1.0.0...v1.1
[1.0.0]: https://github.com/GiMattia/pyPLUTO/releases/tag/v1.0.0
