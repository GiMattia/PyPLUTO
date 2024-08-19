Loading the data
================

PLUTO has several output files, depending on the users' needs.
With PyPLUTO the data loading is done through the ``pyPLUTO.Load()`` class and 
it is available for dbl, vtk and flt files.

.. note::
   So far the AMR has not been included yet.

.. _loadclass:

The ``pyPLUTO.Load()`` class is one of the key components of the PyPLUTO 
package, designed to load the data in the standard PLUTO formats. The formats 
available are dbl, vtk and flt.
Once loaded, the data can be manipulated with various Tools and plotted through 
the ``pyPLUTO.Image()`` class.

|

----

The ``pyPLUTO.Load()`` class
----------------------------

.. autoclass:: pyPLUTO.Load()

|

----