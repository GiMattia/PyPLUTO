GUI
===

A simplified GUI has been implemented to allow for a quick visualization of the
output files. The GUI is based on the PyPLUTO module and is designed to be
simple and user-friendly. The GUI is divided into twhree main sections: the
loading section the setting section and the plotting section.

  .. image:: ../Figures/gui01_start.png
     :align: center
     :width: 600px

|

----

Installation
------------

The GUI is directly installed with the PyPLUTO package, so no additional
installation is required. However, it is recommended to install the package in
an editable mode, so that any changes made to the source code are immediately
reflected in the GUI. This can be done by using `pip` or `pipenv` as
described in the :ref:`install` section of the documentation.

To run the GUI, simply execute the following command in the terminal:

.. code-block:: console

   $ pypluto-gui

This will open the PyPLUTO GUI, where you can load your data files, select the
variables to be plotted, and visualize the data.

Load the data with the GUI
--------------------------

The loading section is used to load the data files. The user can load the data
files by clicking on the "Select File" button. A window will open, allowing
the user to select the desired file by clicking on it. Once the data are loaded,
the user can quickly change the loaded variables or output time by using the
"Reload folder" button.
Note that the variables can be specified also while selecting the file, while
the output file number will be determine by the clicked file.
The "preferred format" combo box allows the user to visualize only the selected
formats while searching the file.
A "Clear" button will simply clear the loading panel.
Further information can be found in the
:ref:`guiload` section of the documentation.

.. toctree::
   :hidden:

   guiload
   guivars
   guiplot

|

----

Selecting the variable with the GUI
-----------------------------------

The setting section is used to select the variable to be plotted. The user can
select the variable by choosing from the loaded variables. The user can also
slice the variables by selecting the desired slice.
The x- and the y-axes (in case of 2D plots) can also be selected here.
Further information can be found in the
:ref:`guivars` section of the documentation.

|

----

Plotting the data with the GUI
------------------------------

The plotting section is used to plot the data. The user can plot the data by
clicking on the "Plot" button. The title, range and scales are highly
customizable, as well as the colormap (for 2D plots).
All these features can be changed and updated without the need to reload the
data by clicking on the "Update plot" button.
Multiple lines can be plotted on the same figure by checking the "overplot"
box.
The user can also further customize the plot due to the matplotlib customization
bar.

|

----

.. This is a comment to prevent the document from ending with a transition.
