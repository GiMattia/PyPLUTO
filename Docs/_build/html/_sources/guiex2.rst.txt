.. _guiex2:

GUI Example 2: OT vortex
========================

.. raw:: html

    <div style="text-align: center;">
      <video width="700" autoplay loop muted playsinline controls>
        <source src="_static/pluto_ot_gui.mp4" type="video/mp4">
        Your browser does not support the video tag.
      </video>
    </div>

Phase 1 (ot): Loading the data
-------------------------------

The first step in using the PyPLUTO GUI is to load the data files. The user can
load the data files by clicking on the "Select File" button. A window will open,
allowing the user to select the desired file by clicking on it. Once the data are
loaded, the user can quickly change the loaded variables or output time by using
the "Reload folder" button.

Phase 2 (ot): Selecting the variable
-------------------------------------

The second step is to select the variable to be plotted. The user can select the
variable by choosing from the loaded variables. The user can also slice the
variables by selecting the desired slice. The x- and the y-axes (in case of 2D plots)
can also be selected here.

Phase 3 (ot): Plotting the data
--------------------------------

The final step is to plot the data. In case of 2D plot, the user can choose an 
appropriate colormap and customize the plot title, range, and scales. All these
features can be changed and updated without the need to reload the data by clicking
on the "Update plot" button. The user can also further customize the plot due to
the matplotlib customization bar.