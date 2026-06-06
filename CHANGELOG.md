# Changelog

All notable changes to this project will be documented in this file.
The format follows [Keep a Changelog](https://keepachangelog.com/en/1.1.0/).

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

[1.2.0]: https://github.com/GiMattia/pyPLUTO/compare/v1.1.5...v1.2.0
[1.1.5]: https://github.com/GiMattia/pyPLUTO/compare/v1.1.4...v1.1.5
[1.1.4]: https://github.com/GiMattia/pyPLUTO/compare/v1.1.3...v1.1.4
[1.1.3]: https://github.com/GiMattia/pyPLUTO/compare/v1.1.2...v1.1.3
[1.1.2]: https://github.com/GiMattia/pyPLUTO/compare/v1.1.1...v1.1.2
[1.1.1]: https://github.com/GiMattia/pyPLUTO/compare/v1.1...v1.1.1
[1.1]: https://github.com/GiMattia/pyPLUTO/compare/v1.0.0...v1.1
[1.0.0]: https://github.com/GiMattia/pyPLUTO/releases/tag/v1.0.0
