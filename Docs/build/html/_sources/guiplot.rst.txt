.. _guiplot:

GUI plot panel
--------------

The third panel of the PyPLUTO GUI is the plot panel, which allows the user to
visualize the loaded data.

  .. image:: ../Figures/gui04_plot.png
     :align: center
     :width: 600px

At the moment the GUI supports only 1D/2D plots of the PLUTO fluid files.
Once the particles will be available in the GUI, the plot panel will be updated
to allow the user to plot also the particle data from the very top left window.
3D plots and volume renderings will be added in the future.

Once the variables are loaded and selected, the user can plot the data by
clicking on the "Plot" button. The "overplot" checkbox allows the user to
plot multiple lines on the same figure in case of 1D plots.

Options: title
--------------

The title of the plot can be set by using the "Title" text box. 

Options: aspect ratio
---------------------

The "Auto-ratio" checkbox allows the user to set the aspect ratio of the plot
automatically. If the checkbox is unchecked, the aspect ratio will be set to 
"equal", meaning that the x- and y-axes will have the same scale. The default
value is "Auto-ratio", which means that the aspect ratio will be set automatically
based on the data.

Options: range
--------------

The (x/y/v) range text boxes allow the user to set the range of the plot.
The user can set the range by typing the desired values in the text boxes.
In case of 1D plots, the user can set the range of the x-axis and the y-axis.
In case of 2D plots, the user can set the range of the x-axis, the y-axis, and the
variable to be plotted (v-axis). The range can also be set automatically by
simply leaving these text boxes empty. The default value is "Auto", which means 
that the range will be set automatically based on the data.

Options: scales
---------------

The x- and y-scales can be set by using the "x-scale" and "y-scale" combo boxes.
Possible options are "linear", "logarithmic", "symlog" and "asinh". The default 
value is "linear", which means that the x- and y-axes will be plotted on a 
linear scale. The last two options require an additional treshold value to be set
in the "tresh" text box. The 2D plot scale can be set by using the "v-scale"
combo box. Possible options are "linear", "logarithmic", "symlog", "2slope", 
"power" and "asinh". The default value is "linear", which means that the
variable will be plotted on a linear scale. Some scales trequire an additional
treshold value to be set in the "tresh" text box.

Options: colormap
-----------------

The colormap can be set by using the "Colormap" combo box. The user can choose
from a list of available colormaps. The default value is "plasma"
which is a perceptually uniform colormap. The user can also select the colormap type
by using the leftmost panel in the cmap section. Then the user can choose the
cesigned colormap from the middle combo box. The colormap can also be reversed
by checking the "Reverse" checkbox.

Options: update plot
--------------------

The "Update plot" button allows the user to update the plot without having to
reload the data. This is useful when the user wants to change the plot settings
or the colormap without having to reload the data. The user can also change the
title, range and scales without having to reload the data. The plot will be
updated automatically when the user clicks on the "Update plot" button.

Options: clear plot section
---------------------------

The "Clear" button will simply clear the plot panel, allowing the user to
start over with a new plot. This is useful when the user wants to plot a new
variable without having to reset all the panels.

Options: reload canvas
----------------------

The "Reload canvas" button allows the user to quickly change the plot settings
by reloading the canvas. This is useful when the user has made changes to the
plot settings or when the user wants to quickly switch between different
plot settings without having to close and reopen the GUI.
