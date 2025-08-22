Install
=======

The latest version of the *PyPLUTO* code is officially distributed with the
*gPLUTO* code. This can be downloaded from gPlutoDownload_.

.. _gPlutoDownload: https://gitlab.com/PLUTO-code/gPLUTO

The current version of *PyPLUTO* has been updated to support Python version 3.10
or newer.
Additional packages that are required are numpy, matplotlib, scipy, pandas, 
Pyqt6 and h5py.

All the relevant files are stored in the PyPLUTO directory, which can be 
accessed by typing:

.. code-block:: console

   $ cd $PLUTO_DIR/Tools/PyPLUTO

Alternatively, the PyPLUTO directory can be cloned from the GitHub repository:

.. code-block:: console

   $ git clone https://github.com/GiMattia/PyPLUTO.git

For the sake of simplicity, we will assume to be in the PyPLUTO directory from
now until the end of the installation process.

|

----

Creating a Conda Environment
----------------------------

If you use conda, you can set up a dedicated environment using
`conda <https://docs.conda.io/en/latest/>`_:

1. Create the environment:

   .. code-block:: console

      $ conda create -n pypluto python=3.10

2. Activate the environment:

   .. code-block:: console

      $ conda activate pypluto

|

----


Installation with pip
---------------------

The recommended installation method is using `pip`, directly from the root of 
the PyPLUTO project. Make sure you are in a clean virtual environment:

.. code-block:: console

   (.venv) $ pip install -e .

This installs *PyPLUTO* in **editable mode**, meaning local changes to the 
source files are immediately reflected without reinstalling.

|

----

Installing with `pipenv`
------------------------

If you use `pipenv` as your dependency manager, you can install *PyPLUTO* from a
local path using:

.. code-block:: console

   $ pipenv install -e .

To enter the virtual environment:

.. code-block:: console

   $ pipenv shell

|

----

Installing with `uv`
--------------------

If you prefer a fast, modern alternative, you can use 
[`uv`](https://github.com/astral-sh/uv):

1. Create and activate a virtual environment:

   .. code-block:: console

      $ uv venv
      $ source .venv/bin/activate  # or .venv\Scripts\activate on Windows

2. Install *PyPLUTO* in editable mode:

   .. code-block:: console

      (.venv) $ uv pip install -e .

|

----

Issues
------

If you encounter any issues during the installation, please check that you have
the required dependencies installed, and run the command

.. code-block:: console

    (.venv) $ pip install --upgrade pip setuptools wheel

If the problem persists, feel free to open an issue on the GitHub repository
or contact the maintainers.

.. This is a comment to prevent the document from ending with a transition.
