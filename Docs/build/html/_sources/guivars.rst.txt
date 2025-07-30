.. _guivars:

GUI vars panel
--------------

The second panel of the PyPLUTO GUI is the variables panel, which allows the 
user to select and manipulate the loaded variables.

  .. image:: ../Figures/gui03_vars.png
     :align: center
     :width: 600px

The user can select the variable to be plotted by choosing from the loaded
variables. Note that custom variables are not available yet, but they will
be implemented in the future. 

Option: transpose
-----------------

The transpose button allows the user to transpose the selected variable.
Although this is not a strictly essential, it will enhance the visualization
of the data, especially for 2D plots involving different codes.

Option: axes
------------

The x- and y-axes (in case of 2D plots) can also be selected here. The user
can choose the x- and y-axes from the loaded variables, allowing for a
flexible visualization of the data. This is particularly useful when the user
wants to plot variables from a non-cartesian geometry, such as spherical
or cylindrical coordinates.
The naming convention is the same as in the Load class, where the "p" or "c" 
suffixes indicate polar or cartesian mesh transformation, respectively.

Option: slices
--------------

In presence of 3D data, or in case the user wants to visualize a 1D slice of 2D
data, the user can select the desired slice by choosing from the available
slices. The slices are automatically generated based on the loaded data. 