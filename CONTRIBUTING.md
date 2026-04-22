# Contributing to PyPLUTO

[![pre-commit](https://img.shields.io/badge/pre--commit-enabled-brightgreen?logo=pre-commit&logoColor=white)](https://github.com/GiMattia/PyPLUTO/actions/workflows/pre-commit.yml)
[![Ruff](https://img.shields.io/endpoint?url=https://raw.githubusercontent.com/astral-sh/ruff/main/assets/badge/v2.json)](https://github.com/astral-sh/ruff)
[![uv](https://img.shields.io/endpoint?url=https://raw.githubusercontent.com/astral-sh/uv/main/assets/badge/v0.json)](https://github.com/astral-sh/uv)
[![pixi](https://img.shields.io/endpoint?url=https://raw.githubusercontent.com/prefix-dev/pixi/main/assets/badge/v0.json)](https://github.com/prefix-dev/pixi)
[![pyrefly](https://img.shields.io/endpoint?url=https://pyrefly.org/badge.json)](https://github.com/facebook/pyrefly)
[![ty](https://img.shields.io/endpoint?url=https://raw.githubusercontent.com/astral-sh/ty/main/assets/badge/v0.json)](https://github.com/astral-sh/ty)

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
git clone https://github.com/<your-user>/PyPLUTO.git
cd PyPLUTO
```

Replace <your-user> with your own GitHub username (your fork of the repository).

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

### Option C: `pip` fallback (not lockfile-based)

If you prefer a classic setup:

```bash
pip install -r requirements_dev.txt
```

`requirements_dev.txt` installs the project in editable mode with development extras.

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
- `ty` type checking (`pre-push` and `manual`)
- `pytest` with coverage threshold (`manual`, fail-under `45`)

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

## Publishing on conda-forge

If you want to publish PyPLUTO on conda-forge, use the recipe template in this
repository:

- `conda-forge/recipe/meta.yaml`

Suggested flow:

1. Fork `conda-forge/staged-recipes` and create a new branch.
2. Copy `conda-forge/recipe/meta.yaml` into
   `staged-recipes/recipes/py-pluto/meta.yaml`.
3. Replace `source.sha256` with the checksum of the corresponding PyPI sdist.
4. Commit and open a PR against `conda-forge/staged-recipes`.
5. Address CI/lint feedback from conda-forge reviewers.

When the staged-recipes PR is merged, conda-forge will create
`py-pluto-feedstock` automatically. Future version updates should then be done
in that feedstock repository.

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

- `pyPLUTO/`: main package code
- `Tests/`: test suite and test data
- `Examples/`: runnable examples and sample outputs
- `Docs/`: Sphinx documentation

## Questions

For questions or suggestions, open an issue in this repository.
