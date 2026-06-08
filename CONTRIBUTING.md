# Contributing to PyPLUTO

[![pre-commit](https://img.shields.io/badge/pre--commit-enabled-brightgreen?logo=pre-commit&logoColor=white)](https://github.com/GiMattia/PyPLUTO/actions/workflows/pre-commit.yml)
[![Ruff](https://img.shields.io/endpoint?url=https://raw.githubusercontent.com/astral-sh/ruff/main/assets/badge/v2.json)](https://github.com/astral-sh/ruff)
[![uv](https://img.shields.io/endpoint?url=https://raw.githubusercontent.com/astral-sh/uv/main/assets/badge/v0.json)](https://github.com/astral-sh/uv)
[![pixi](https://img.shields.io/endpoint?url=https://raw.githubusercontent.com/prefix-dev/pixi/main/assets/badge/v0.json)](https://github.com/prefix-dev/pixi)
[![pyright](https://img.shields.io/badge/type%20checker-pyright-blue)](https://github.com/microsoft/pyright)

Thank you for considering a contribution to PyPLUTO.

We welcome:

- bug reports
- feature requests
- documentation improvements
- tests
- code contributions

If you find a bug or have an idea, open an issue first (or go straight to a pull request if you already have a fix).

## Code of Conduct

Please follow our community guidelines in [`CODE_OF_CONDUCT.md`](CODE_OF_CONDUCT.md).

## Use of AI

The use of AI (for example, LLMs) is allowed if used responsibly.

Every contributor remains responsible for what they submit: all generated code and text must be reviewed by a human before being published.

This also applies to communication (issues, pull requests, and emails). AI-assisted translation is acceptable, but please make sure the final text matches your intent.

To keep PyPLUTO maintainable, autonomous agents must not contribute without human supervision.

## Prerequisites

- Python `>=3.11` (the CI matrix currently tests `3.12`, `3.13`, and `3.14`)
- Git
- A virtual environment tool (`uv`, `pixi`, `venv`, `conda`, etc.)

## Local Setup

1. Fork and clone:

```bash
git clone https://github.com/GiMattia/PyPLUTO.git
cd PyPLUTO
```

### Option A: `uv` (recommended)

Create a reproducible environment from the lockfile:

```bash
uv sync --all-extras --all-groups
```

Run commands inside the synced environment with `uv run`, for example:

```bash
uv run pre-commit run --all-files
uv run pytest -v ./Tests
```

### Option B: `pixi` (uses `pixi.lock`)

Install the `all` environment declared in `pyproject.toml`:

```bash
pixi install -e full
```

Run tools in that environment:

```bash
pixi run -e all pre-commit run --all-files
pixi run -e all pytest -v ./Tests
```

### Option C: `pip` (no lockfile)

uv (Option A) is the recommended setup, but if you prefer plain `pip` you can
install the project together with its dependency groups (requires `pip >= 25.1`,
which understands PEP 735 dependency groups):

```bash
pip install -e ".[gui]" --group dev --group test --group docs
```

This installs PyPLUTO in editable mode with the development, test and
documentation tooling. Unlike Options A and B it is not lockfile-based.

## Pre-commit and Quality Checks

Install hooks:

```bash
pre-commit install
pre-commit install --hook-type pre-push
```

Run all standard checks locally:

```bash
pre-commit run --all-files
```

Run manual-stage checks before opening a PR:

```bash
pre-commit run --all-files --hook-stage manual
```

Current checks include:

- standard `pre-commit-hooks` sanity checks
- `ruff` lint/format
- lock consistency checks (`uv lock --check`, `pixi lock --check`)
- `pyright` type checking (`pre-push` and `manual`)
- `pytest` with coverage threshold (`manual`, fail-under `45`)

## Type checking

PyPLUTO uses **[pyright](https://github.com/microsoft/pyright)** as its standard
type checker. Run it locally with the `dev` dependency group installed:

```bash
pyright
```

The configuration lives in the `[tool.pyright]` section of `pyproject.toml`, so
the same settings are used from the CLI, CI, and editors.

pyright was chosen because it is currently the only checker that validates the
patterns PyPLUTO relies on — notably `Generic` classes with overloaded `__new__`
(used to type loaded variables such as `Data.rho` from the constructor) and the
rejection of unknown `Unpack[TypedDict]` keyword arguments (e.g. catching
`Load(format=2)`).

**pyrefly and ty** (the `typefuture` dependency group) are kept installable but
are **not** the source of truth yet. Every issue they would currently report is
already covered by pyright, and they do not yet fully validate the patterns
above. The intent is to switch to one of them once they mature. Install them
only if you want to experiment:

```bash
uv sync --group typefuture     # or: pixi install -e typefuture
```

A couple of legacy modules (`amr.py`, `nabla.py`) are excluded from type
checking via a file-level `# type: ignore` until they are reworked.

## Running Tests

Run the full suite:

```bash
pytest -v ./Tests
```

Run with coverage:

```bash
pytest --cov=pyPLUTO --cov-report=term-missing Tests/
```

## Documentation

Docs are in `Docs/source`. To build locally:

```bash
make -C Docs html
```

## Workflow for Pull Requests

1. Create a branch from `master`.
2. Keep changes focused and small when possible.
3. Add or update tests for behavioral changes.
4. Run:
   - `pre-commit run --all-files`
   - `pre-commit run --all-files --hook-stage manual`
5. Push and open a pull request with:
   - a clear summary of changes
   - why the change is needed
   - notes on tests performed

CI runs style checks and tests across multiple OSes and Python versions. A PR is expected to pass all checks.

## Project Structure (Quick Guide)

Top-level layout:

- `src/pyPLUTO/`: main package code
- `Tests/`: test suite and test data
- `Examples/`: runnable examples and sample outputs
- `Docs/`: Sphinx documentation

Package subfolders inside `src/pyPLUTO/`:

- `gui/`: GUI panels, widgets, and main window logic
- `imagefuncs/`: image/plot manager classes
- `loadfuncs/`: data loading and parsing
- `toolfuncs/`: analysis tools (derivatives, transforms, units, etc.)
- `utils/`: shared utilities

`Load`, `LoadPart`, and `Image` follow the same architecture: a state class
(`LoadState` / `BaseLoadState` / `ImageState`) holds all data; a mixin class
(`LoadMixin` / `BaseLoadMixin` / `ImageMixin`) exposes the public interface;
manager classes in the subfolders implement individual operations and receive
the state object at construction time.

## Questions

For questions or suggestions, open an issue in this repository or directly contact the developers.
