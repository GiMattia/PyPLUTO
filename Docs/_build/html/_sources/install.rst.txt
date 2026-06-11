.. _installation:

Install
=======

PyPLUTO requires **Python 3.11 or newer** and is tested on 3.12, 3.13, and 3.14.

Core dependencies installed automatically:

- ``astropy``
- ``contourpy``
- ``h5py``
- ``inifix``
- ``matplotlib``
- ``numexpr``
- ``numpy``
- ``scipy``

The GUI requires the optional dependency ``PySide6``, which must be requested
explicitly (see below).

|

----

From PyPI
---------

The recommended way to install PyPLUTO for most users:

.. code-block:: console

   $ pip install py-pluto

To include the GUI:

.. code-block:: console

   $ pip install py-pluto[gui]

To upgrade an existing installation to the latest release:

.. code-block:: console

   $ pip install py-pluto --upgrade

It is good practice to install into a dedicated virtual environment so that
PyPLUTO's dependencies do not conflict with other projects:

.. code-block:: console

   $ python -m venv .venv
   $ source .venv/bin/activate      # Windows: .venv\Scripts\activate
   $ pip install py-pluto

|

----

With ``uv``
-----------

`uv <https://github.com/astral-sh/uv>`_ is a fast, modern Python package and
project manager. There are two common workflows depending on whether you are
working inside a project or in a standalone environment.

**Inside a uv project** (directory contains a ``pyproject.toml``):

.. code-block:: console

   $ uv add py-pluto

To include the GUI:

.. code-block:: console

   $ uv add py-pluto[gui]

``uv add`` records the dependency in ``pyproject.toml`` and updates
``uv.lock``.  If you do not yet have a project, create one first with
``uv init``.

**Without a project** (standalone virtual environment):

.. code-block:: console

   $ uv venv                        # creates .venv in the current directory
   $ source .venv/bin/activate      # Windows: .venv\Scripts\activate
   $ uv pip install py-pluto

Or, to run a one-off script without modifying any environment:

.. code-block:: console

   $ uv run --with py-pluto python my_script.py

|

----

With ``conda``
--------------

Create and activate a dedicated environment, then install via pip:

.. code-block:: console

   $ conda create -n pypluto python=3.12
   $ conda activate pypluto
   $ pip install py-pluto

To include the GUI add ``[gui]``:

.. code-block:: console

   $ pip install py-pluto[gui]

|

----

From Source
-----------

For development or to work with the latest code, clone the repository and
install in editable mode:

.. code-block:: console

   $ git clone https://github.com/GiMattia/PyPLUTO.git
   $ cd PyPLUTO
   $ pip install -e .

With ``uv`` (recommended for contributors):

.. code-block:: console

   $ git clone https://github.com/GiMattia/PyPLUTO.git
   $ cd PyPLUTO
   $ uv sync --all-extras --all-groups

``uv sync`` creates an isolated virtual environment and installs all
dependencies (including optional extras and development tools) in one step.
See :ref:`contributing <contributing>` for the full contributor workflow.

|

----

Issues
------

If you encounter any issues during installation, make sure ``pip`` is up to
date:

.. code-block:: console

   $ pip install --upgrade pip

If the problem persists, open an issue on the
`GitHub repository <https://github.com/GiMattia/PyPLUTO>`_
or contact the maintainers.

.. This is a comment to prevent the document from ending with a transition.
