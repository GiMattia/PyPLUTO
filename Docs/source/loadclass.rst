.. _loadclass:

Loading the data
================

PLUTO has several output files (for both fluids and particles), depending on the users' needs.
The fluid variables can be written into binary files (in double or single precision),
vtk files or hdf5 files (in double or single precision).
The particles' variables can be written in binary files (in double or single precision) and
vtk files.
All the formats can be opened with PyPLUTO, with or without the .out file (if the fluid
varibales are written on vtk or hdf5 files).

.. note::
   So far the AMR has not been included yet.

Loading the fluid files
-----------------------

The :ref:`Load <load>` class is one of the key components of the PyPLUTO 
package, designed to load the fluid data in the standard PLUTO formats. The formats 
available are dbl, vtk, flt, dbl.h5 and flt.h5.

.. toctree::
   :hidden:

   load
   read_file
   write_file
   
The vtk and h5 filed can be loaded as standalones (i.e. without the .out files).
However, we highly discourage the users to do so, especially if the simulation is
run in non-cartesian coordinates.

Other h5 files can also be read through the :ref:`read_file <read_file>` method
(only h5 are possible for now) and written through the :ref:`write_file <write_file>` 
method (only h5 are possible for now).

   
Loading the particles files
---------------------------
   
The :ref:`LoadPart <loadpart>` class is one of the key components of the PyPLUTO 
package, designed to load the particles data in the standard PLUTO formats. The formats 
available are dbl, vtk, flt.
Particles are loaded as standalones, i.e. no additional file is necessary.

.. toctree::
   :hidden:

   loadpart

|

----

.. This is a comment to prevent the document from ending with a transition.
