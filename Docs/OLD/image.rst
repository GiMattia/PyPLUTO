Plotting the data
=================

.. autoclass::  pyPLUTO.Image()

The loaded data should be plot in a complete yet efficient way.
The class ``pyPLUTO.Image`` is a quick tool in order to obtain plots
for scientific articles.

Creation of figure and axes
---------------------------

The first step of the plotting procedure is to create a figure and a list of axes
(where each element of the axes list corresponds to a subplot).
Three functions are built in order to give a good compromise between simplicity and
customization:

.. toctree::

  create_axes

The :ref:`create_axes` creates a simple figure and set of axes, given a specific number
of rows and columns. The subplots are automatically spaced evenly and the ratio between
the different subplots sizes is 1. The aspect of the single subplots is automatically determined
from the image size.

The :ref:`create_axes` allows for a better customization, since both the size ratios
of the plots and the horizontal and vertical spacing are customizable. Moreover, this function is
designed to be called multiple times for the same figure (e.g. in case of plots which span over
a different number of columns). However, in such case the :ref:`create_axes` should be
called first in order to create the figure.

Once the figure and the axes are created, they are customizable through:

.. toctree::

  set_axis

Parameters as the axes range or scale should be defined here. However, in case of simple plots
all the parameters in this function can be defined in the specific plotting functions.

The plotting procedure
----------------------

At the moment only 1D and 2D plots are available.

.. note::
   Full 3D plotting is under active development.

The standard 1D and 2D plots can be produced through the functions:

.. toctree::

  plot
  display

Parameters such as the line colors are almost fully customizable.


Useful plotting tools
---------------------

Although features such as the legend or colorbar can be easily included
during the plotting procedure, sometimes the best choice (especially for
non-trivial figures) is to add them during a later step.

.. toctree::

  legend
  colorbar


The pyPLUTO module allows for inset zooms through two functions, which, respectively,
zoom 1D and 2D plots.

.. toctree::

  zoomplot
  zoomdisplay
