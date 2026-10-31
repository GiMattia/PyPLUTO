.. _contributing:

Contribute
==========

Thank you for considering a contribution to **PyPLUTO**!

We welcome:

- bug reports
- feature requests
- documentation improvements
- tests
- code contributions

If you find a bug or have an idea, open an issue first (or go straight to a pull
request if you already have a fix).

|

----

Code of Conduct
---------------

Please follow our community guidelines in the ``CODE_OF_CONDUCT.md`` file at
the root of the repository.

|

----

Use of AI
---------

The use of AI (for example, LLMs) is allowed if used responsibly.

Every contributor remains responsible for what they submit: all generated code
and text must be reviewed by a human before being published.

This also applies to communication (issues, pull requests, and emails).
AI-assisted translation is acceptable, but please make sure the final text
matches your intent.

To keep PyPLUTO maintainable, autonomous agents must not contribute without
human supervision.

|

----

Prerequisites
-------------

- Python ``>=3.11`` (the CI matrix currently tests ``3.12``, ``3.13``, and ``3.14``)
- Git
- `uv <https://docs.astral.sh/uv/>`_ (required); `pixi <https://pixi.sh>`_ is optional

|

----

Local Setup
-----------

Fork PyPLUTO on GitHub, then clone your fork and set it up:

.. code-block:: console

   $ git clone https://github.com/<your-username>/PyPLUTO.git
   $ cd PyPLUTO
   $ ./dev-sync.sh

**uv (required)**

``./dev-sync.sh`` creates a reproducible environment from ``uv.lock``, the same
as:

.. code-block:: console

   $ uv sync --all-extras --all-groups

Run commands inside the synced environment with ``uv run``, for example:

.. code-block:: console

   $ uv run pre-commit run --all-files
   $ uv run pytest -v ./Tests

**pixi (optional)**

For those who already use pixi: ``pixi.lock`` gives the development
environment (tests, docs, pre-commit) as ``local-dev``. If pixi is installed,
``./dev-sync.sh`` installs it too:

.. code-block:: console

   $ pixi install -e local-dev
   $ pixi run -e local-dev pytest -v ./Tests

|

----

Pre-commit and Quality Checks
------------------------------

Install hooks:

.. code-block:: console

   $ pre-commit install
   $ pre-commit install --hook-type pre-push

Run all standard checks locally:

.. code-block:: console

   $ pre-commit run --all-files

Run manual-stage checks before opening a PR:

.. code-block:: console

   $ pre-commit run --all-files --hook-stage manual

Current checks include:

- standard ``pre-commit-hooks`` sanity checks
- ``ruff`` lint/format
- lock consistency checks: ``uv lock --check``; ``pixi lock --check`` only
  where pixi is installed, and always in CI
- ``pyright`` type checking (``pre-push`` and ``manual`` stages)
- ``pytest`` with coverage threshold (``manual``, fail-under 45 %)

|

----

Type checking
-------------

PyPLUTO uses `pyright <https://github.com/microsoft/pyright>`_ as its standard
type checker. Run it locally with the ``dev`` dependency group installed:

.. code-block:: console

   $ pyright

The configuration lives in the ``[tool.pyright]`` section of ``pyproject.toml``,
so the same settings are used from the CLI, CI, and editors.

pyright was chosen because it is currently the only checker that validates the
patterns PyPLUTO relies on — notably ``Generic`` classes with overloaded
``__new__`` (used to type loaded variables such as ``Data.rho`` from the
constructor) and the rejection of unknown ``Unpack[TypedDict]`` keyword
arguments (e.g. catching ``Load(format=2)``).

**pyrefly** and **ty** (the ``typefuture`` dependency group) are kept
installable but are **not** the source of truth yet. Every issue they would
currently report is already covered by pyright, and they do not yet fully
validate the patterns above. The intent is to switch to one of them once they
mature.

A couple of legacy modules (``amr.py``, ``nabla.py``) are excluded from type
checking via a file-level ``# type: ignore`` until they are reworked.

|

----

Running Tests
-------------

Run the full suite:

.. code-block:: console

   $ pytest -v ./Tests

Run with coverage:

.. code-block:: console

   $ pytest --cov=pyPLUTO --cov-report=term-missing Tests/

Please ensure that all tests pass before submitting a pull request.

|

----

Documentation
-------------

Docs are in ``Docs/source``. To build locally:

.. code-block:: console

   $ make -C Docs html

|

----

Workflow for Pull Requests
--------------------------

1. Create a branch from ``master``.
2. Keep changes focused and small when possible.
3. Add or update tests for behavioral changes.
4. Run pre-commit checks (see above).
5. Push and open a pull request with:

   - a clear summary of changes
   - why the change is needed
   - notes on tests performed

CI runs style checks and tests across multiple OSes and Python versions.
A PR is expected to pass all checks.

If your PR changes the dependencies in ``pyproject.toml``, the pixi lock check
in CI may fail. Nothing to do on your side: the maintainers update
``pixi.lock`` on your branch, so please leave "Allow edits by maintainers"
checked.

|

----

Project Structure
-----------------

Top-level layout:

- ``src/pyPLUTO/``: main package code
- ``Tests/``: test suite and test data
- ``Examples/``: runnable examples and sample outputs
- ``Docs/``: Sphinx documentation

Package subfolders inside ``src/pyPLUTO/``:

- ``gui/``: GUI panels, widgets, and main window logic
- ``imagefuncs/``: image/plot manager classes
- ``loadfuncs/``: data loading and parsing
- ``toolfuncs/``: analysis tools (derivatives, transforms, units, etc.)
- ``utils/``: shared utilities

``Load``, ``LoadPart``, and ``Image`` follow the same architecture: a state
class (``LoadState`` / ``BaseLoadState`` / ``ImageState``) holds all data; a
mixin class (``LoadMixin`` / ``BaseLoadMixin`` / ``ImageMixin``) exposes the
public interface; manager classes in the subfolders implement individual
operations and receive the state object at construction time.

|

----

Questions
---------

For questions or suggestions, open an issue in the
`GitHub repository <https://github.com/GiMattia/PyPLUTO>`_ or contact the
developers directly.

|

----

.. This is a comment to prevent the document from ending with a transition.
