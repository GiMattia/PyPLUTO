Loading the data
================

PLUTO has several output files, depending on the users' needs.
With pyPLUTO the data loading is done through the ``pyPLUTO.Load()`` class and it
is available for dbl, vtk and flt files.

.. note::
   So far the AMR has not been included yet.

.. _loadclass:

The ``pyPLUTO.Load()`` class
----------------------------

The ``pyPLUTO.Load()`` class is design to load the data in the standard PLUTO
formats. The formats available are dbl, vtk and flt (for now):

.. autoclass:: pyPLUTO.Load()
