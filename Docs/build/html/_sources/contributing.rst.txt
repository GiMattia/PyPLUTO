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
- A virtual environment tool (``uv``, ``pixi``, ``venv``, ``conda``, etc.)

|

----

Local Setup
-----------

Fork and clone the repository:

.. code-block:: console

   $ git clone https://github.com/GiMattia/PyPLUTO.git
   $ cd PyPLUTO

**Option A: uv (recommended)**

Create a reproducible environment from the lockfile:

.. code-block:: console

   $ uv sync --all-extras --all-groups

Run commands inside the synced environment with ``uv run``, for example:

.. code-block:: console

   $ uv run pre-commit run --all-files
   $ uv run pytest -v ./Tests

**Option B: pixi**

Install the ``full`` environment declared in ``pyproject.toml``:

.. code-block:: console

   $ pixi install -e full

Run tools in that environment:

.. code-block:: console

   $ pixi run -e all pre-commit run --all-files
   $ pixi run -e all pytest -v ./Tests

**Option C: pip fallback (not lockfile-based)**

.. code-block:: console

   $ pip install -r requirements_dev.txt

``requirements_dev.txt`` installs the project in editable mode with development
extras.

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
- lock consistency checks (``uv lock --check``, ``pixi lock --check``)
- ``ty`` type checking (``pre-push`` and ``manual`` stages)
- ``pytest`` with coverage threshold (``manual``, fail-under 45 %)

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
