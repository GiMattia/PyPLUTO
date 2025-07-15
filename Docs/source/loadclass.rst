.. _loadclass:

Loading
=======

PLUTO has several output files (for both fluids and particles), depending on the
users' needs. The fluid variables can be written into binary files (in double or
single precision), vtk files or h5 files (in double or single precision).
The particles' variables can be written in binary files (in double or single
precision) and vtk files.
All the formats can be opened with PyPLUTO, with or without the .out file (if
the fluid varibales are written on vtk or h5 files).
Additionally, PyPLUTO loads hdf5 created with CHOMBO for simulations performed
with AMR, and .tab files (for both 1D and 2D data).

Loading the fluid files
-----------------------

The :ref:`Load <load>` class is one of the key components of the PyPLUTO
package, designed to load the fluid data in the standard PLUTO formats. The
formats  available are dbl, vtk, flt, dbl.h5, flt.h5 hdf5 and tab.

.. toctree::
   :hidden:

   load
   read_file
   write_file

The vtk and h5 filed can be loaded as standalones (i.e. without the .out files).
However, we highly discourage the users to do so, especially if the simulation
is run in non-cartesian coordinates.

The dat files (e.g., the ones written in the function analysis.c of the PLUTO
code) can be read and the data can be stored into a dictionary.
Other h5 files can also be read through the :ref:`read_file <read_file>` method
(only h5 are possible for now) and written through the
:ref:`write_file <write_file>` method (only h5 and dat are possible for now).

Note that multiple fluid files can be loaded (e.g. to have interactive plots) at
the same time.

Additionally, the definitions.h(pp) and the pluto.ini (although for the latter
only the "boundary", "time", "parameters" and "solver" blocks) can be inspected.
If so, the data are stored in two dictionaries (defs and plini) as class
attributes.

Loading the particles files
---------------------------

The :ref:`LoadPart <loadpart>` class is one of the key components of the PyPLUTO
package, designed to load the particles data in the standard PLUTO formats. The
formats available are dbl, vtk, flt.
Particles are loaded as standalones, i.e. no additional file is necessary.

.. toctree::
   :hidden:

   loadpart

A note on the PLUTO output
--------------------------

PLUTO simulations produce a wide range of output formats for both fluid and
particle data. Descriptor files are generated alongside the main fluid data,
providing essential information about the grid structure and variable
layout. Although descriptor files are essential only for the binary output
files, is recommended to include them, especially in presence of simulations
performed in non-cartesian geometry.
Binary and vtk fluid files can be produced with the "multiple files" option. In
such case, each fluid variable is saved in a separate file rather than combining
all variables into a single output file.

.. list-table::
   :widths: 20 20 20 20 20
   :header-rows: 1

   * - Format
     - Fluid/particles
     - Fluid descriptor
     - Single/multiple files
     - Staggered variables
   * - dbl
     - both
     - required
     - both
     - yes
   * - flt
     - both
     - required
     - both
     - no
   * - vtk
     - both
     - optional
     - both
     - no
   * - dbl.h5
     - only fluid
     - optional
     - single file only
     - yes
   * - flt.h5
     - only fluid
     - optional
     - single file only
     - no
   * - hdf5 (AMR)
     - only fluid
     - optional
     - single file only
     - no
   * - tab (serial, no 3D)
     - only fluid
     - optional
     - single file only
     - no

What about other codes?
-----------------------

PypLUTO is tailored for the PLUTO code output, therefore major efforts will be
dedicated to the PLUTO code files. However, being the :ref:`Image <imageclass>`
class code independent, extensions to other codes can be done with minimal
efforts.
Currently, the following codes can be used in combination with PyPLUTO:

- ECHO (parameters: nout, path, vars)
- IDEFIX

|

----

.. This is a comment to prevent the document from ending with a transition.
