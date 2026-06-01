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

The recommended way to install PyPLUTO for end users:

.. code-block:: console

   $ pip install py-pluto

To include the GUI:

.. code-block:: console

   $ pip install py-pluto[gui]

|

----

With ``uv``
-----------

`uv <https://github.com/astral-sh/uv>`_ is a fast, modern package manager.
To add PyPLUTO to a project:

.. code-block:: console

   $ uv add py-pluto

To include the GUI:

.. code-block:: console

   $ uv add py-pluto[gui]

|

----

With ``conda``
--------------

Create and activate a dedicated environment, then install via pip:

.. code-block:: console

   $ conda create -n pypluto python=3.12
   $ conda activate pypluto
   $ pip install py-pluto

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

For a fully reproducible development environment including all optional extras
and development tools, prefer ``uv`` or ``pixi`` (see
:ref:`contributing <contributing>` for details).

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
