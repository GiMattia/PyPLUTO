.. _imageclass:

Plotting
========

.. toctree::
   :hidden:

   image
   animate
   colorbar
   contour
   create_axes
   display
   interactive
   legend
   oplotbox
   plot
   savefig
   scatter
   set_axis
   streamplot
   text
   zoom

The loaded data should be visualized in a complete yet efficient way.
The :ref:`Image <image>` class is a quick tool in order to obtain simple plots
suitable for scientific articles.

For the sake of simplicity, every Image class corresponds to one single figure.
The reason behind such choice is that an Image including multiple figures would
not be efficient in order to effectively remember where all the potential
subplots are located.

|

----


Subplots creation and customization
-----------------------------------

The first step of the plotting procedure is to create a list of axes
(where each element of the axes list corresponds to a subplot).
Two functions are built in order to give a good compromise between simplicity
and customization:

The :ref:`create_axes <create_axes>` method creates a simple figure and set of
axes, given a specific number of rows and columns. The subplots are
automatically spaced evenly and the ratio between the different subplots sizes
is 1. The aspect of the single subplots is automatically determined from the
image size.

The :ref:`create_axes <create_axes>` method allows for a better customization,
since both the size ratios of the plots and the horizontal and vertical spacing
are customizable. Moreover, this function is designed to be called multiple
times for the same figure (e.g. in case of plots which span over a different
number of columns).

Once the figure and the axes are created, they are customizable through the
:ref:`set_axis  <set_axis>` method.

Parameters as the axes range or scale should be defined here. However, in case
of simple plots all the parameters in this function can be defined in the
specific plotting functions.

|

----

The plotting procedure
----------------------

At the moment only 1D and 2D plots are available, for both fluid and particles.

.. note::
   Full 3D plotting is under active development.

The standard 1D and 2D fluid plots can be produced through the functions
:ref:`plot <plot>` and :ref:`display <display>`.
Both functions are highly customizable and call the :ref:`set_axis  <set_axis>`
method.
The particles can be plotted through the :ref:`scatter <scatter>` method, which
is also very customizable due to the call to the :ref:`set_axis  <set_axis>`
method.

|

----

Field and contour lines
-----------------------

The :ref:`Image <image>` class contains a :ref:`contour <contour>` and a
:ref:`streamplot <streamplot>` methods, which can be used for a quick
visualization of contour and field lines. Such methods are based on the contour
and streamplot maptlotlib methods. Note that field and contour lines can be also
produced in the Load class for a more accurate computation. Nonetheless, these
methods require a limited computational time, favoring a quick visualization in
absence of complex structures.

|

----

Interactive plots
-----------------

A quick interactive visualization is possible due to the
:ref:`interactive <interactive>` methods, which is available for both 1D and 2D
fluid output files.

.. note::
   In the future a better customization will be possible (e.g. displays with
   fieldlines through callable functions).

Figures plotted interactively can be visualized through the entire temporal
evolution, with a high parameters customization provided by the
:ref:`plot <plot>` and :ref:`display <display>` methods (called be the
:ref:`interactive <interactive>` method).
Interactive plots can be saved through the :ref:`animate <animate>` method,
which can create or save a video, showing the output with a selected temporal
interval. If no file name is provided, the :ref:`animate <animate>` will
show a video.

|

----

Useful plotting tools
---------------------

Although features such as the :ref:`legend <legend>` or
:ref:`colorbar <colorbar>` can be easily included during the plotting procedure,
sometimes the best choice (especially for non-trivial figures) is to add them
during a later step. However, multiple legends and colorbars are possible
within the same figure.

The PyPLUTO module allows for easy inset zooms through the :ref:`zoom <zoom>`
for both 1D and 2D plots with the same level of customization of the functions
:ref:`plot <plot>` and :ref:`display <display>`.
Note that, for the zoom of 2D variables, an additional customization level is
possible; in fact, the zoom of a different quantities can be easily plotted
in order to see two variables of a selected region at the same time with minimum
effort.

Image figures can be saved through the :ref:`savefig <savefig>` method, which is
a simple wrapper of the matplotlib savefig method.

Text can be written within a figure through the :ref:`text <text>` method.
Depending on the user's choice, the text can be placed in different font size,
color and position (relative to the figure, axes points or fraction).

|

----

AMR blocks
----------

AMR blocks can be visualized through the :ref:`oplotbox <oplotbox>` method,
although, due to the ongoing upgrades to the AMR in gPLUTO and its output, such
method may change in the future.

|

----

.. This is a comment to prevent the document from ending with a transition.
