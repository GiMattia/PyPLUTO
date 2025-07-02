"""HD disk-planet test.

This test shows how to plot different 2D quantities from a test problem
in the same plot with two zooms.

The data are the ones obtained from the PLUTO test problem directory
$PLUTO_DIR/Test_Problems/HD/Disk_Planet (configuration 6).

The data is loaded into a pload object D and the Image class is created.
The create_axes method is used here to make easier to associate the
zooms with the main plot. The display method is used to plot the density
in the main plot, while the zoom method is used to create the two zooms.
The image is then saved and shown on screen.

Note that the second zoom requires the keyword ax to be passed to the
zoom method, in order to associate the zoom with main plot. The zoom
method is called twice, once for each zoom region. If no keyword ax was
passed, the second zoom would be associated as a zoom of the first zoom.
The second zoom is also plotted with a different variable with respect
to the main plot, to show the flexibility of the zoom method in plotting
different quantities in the same region.

"""

# Loading the relevant packages
import numpy as np
import pyPLUTO

# Loading the data into a pload object D
Data = pyPLUTO.Load(path="Test_Problems/HD/Disk_Planet")

# Creating the image and the subplot axes (to have two zoom simultaneously)
Image = pyPLUTO.Image()
ax = Image.create_axes()

# Compute the disk keplerian rotation speed
omega = 2.0 * np.pi / np.sqrt(Data.x1)

# Plotting the data
Image.display(
    Data.rho,
    x1=Data.x1rc,
    x2=Data.x2rc,
    cscale="log",
    cpos="right",
    clabel=r"$\rho$",
    title="Test 06 - HD Disk planet test",
    vmin=0.1,
    xtitle="x",
    ytitle="y",
    xticks=[-2, -1, 0, 1, 2],
    yticks=[-2, -1, 0, 1, 2],
    xrange=[-2.6, 2.6],
    yrange=[-2.6, 2.6],
)

# Zooming the planet region
Image.zoom(xrange=[0.9, 1.1], yrange=[-0.1, 0.1], pos=[0.74, 0.95, 0.7, 0.9])
Image.zoom(
    var=Data.vx2 - omega[:, np.newaxis],
    xrange=[0.9, 1.1],
    yrange=[-0.1, 0.1],
    pos=[0.07, 0.27, 0.67, 0.9],
    cpos="bottom",
    cmap="RdBu",
    cscale="linear",
    vmin=-1.2,
    vmax=1.2,
    ax=ax,
    title=r"$v_\phi - \Omega R$",
)

# Saving the image and showing the plots
Image.savefig("test06_diskplanet.png")
pyPLUTO.show()
