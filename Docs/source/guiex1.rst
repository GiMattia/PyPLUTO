.. _guiex1:

GUI Example 1: Sod
==================

.. raw:: html

    <div style="text-align: center;">
      <video width="700" autoplay loop muted playsinline controls>
        <source src="_static/pluto_sod_gui.mp4" type="video/mp4">
        Your browser does not support the video tag.
      </video>
    </div>

Phase 1 (sod): Loading the data
-------------------------------

The first step in using the PyPLUTO GUI is to load the data files. The user can
load the data files by clicking on the "Select File" button. A window will open,
allowing the user to select the desired file by clicking on it. Once the data are
loaded, the user can quickly change the loaded variables or output time by using
the "Reload folder" button.

Phase 2 (sod): Selecting the variable
-------------------------------------

The second step is to select the variable to be plotted. The user can select the
variable by choosing from the loaded variables. The user can also slice the
variables by selecting the desired slice. The x- and the y-axes (in case of 2D plots)
can also be selected here.

Phase 3 (sod): Plotting the data
--------------------------------

The final step is to plot the data. In case of 1D plots, the user can plot 
multiple lines on the same figure by checking the "overplot" box. The title,
range, and scales are highly customizable, as well as the colormap (for 2D plots).
All these features can be changed and updated without the need to reload the
data by clicking on the "Update plot" button. The user can also further customize
the plot due to the matplotlib customization bar.

