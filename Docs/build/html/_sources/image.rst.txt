Plotting the data
=================

.. autoclass:: pyPLUTO.Image

The loaded data should be visualized in a complete yet efficient way.
The class ``pyPLUTO.Image`` is a quick tool in order to obtain simple plots
suitable for scientific articles.

Image initialization
--------------------

For the sake of simplicity, every Image class corresponds to one single figure.
The reason behind such choice is that an Image including multiple figures would
not be efficient in order to effectively remember where all the potential
subplots are located.


Subplots creation and customization
-----------------------------------

The first step of the plotting procedure is to create a list of axes
(where each element of the axes list corresponds to a subplot).
Three functions are built in order to give a good compromise between simplicity and
customization:

.. toctree::
   :maxdepth: 1

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
  :maxdepth: 1

  set_axis

Parameters as the axes range or scale should be defined here. However, in case of simple plots
all the parameters in this function can be defined in the specific plotting functions.

The plotting procedure
----------------------

At the moment only 1D and 2D plots are available.

.. note::
   Full 3D plotting is under active development.

The standard 1D and 2D plots can be produced through the functions:


Parameters such as the line colors are almost fully customizable.

.. toctree::
  :maxdepth: 1

  plot

1D plot :ref:`plot`

.. toctree::
  :maxdepth: 1

  display

2D plot :ref:`display`

Useful plotting tools
---------------------

Although features such as the legend or colorbar can be easily included
during the plotting procedure, sometimes the best choice (especially for
non-trivial figures) is to add them during a later step.

.. toctree::
  :maxdepth: 1

  zoom
  text

The pyPLUTO module allows for inset zooms through two functions, which, respectively,
zoom 1D and 2D plots.


.. autoclass:: pyPLUTO.NewImage

.. toctree::
   :maxdepth: 1

   create_axes
