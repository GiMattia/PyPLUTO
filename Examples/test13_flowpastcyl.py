"""AMR Flow past cylinder test

This test shows how to plot data from the Load class when handling data obtained
from a simulation with AMR.

The data are the ones obtained from the PLUTO test problem
$PLUTO_DIR/Test_Problems/Particles/HD/Viscosity/Flow_Past_Cylinder.

The data is loaded with the Load class into a pload object and the Image class
is created. The display method is used to plot the density, and the oplotbox
method is used to show the AMR levels. The image is then saved and
shown on screen.
"""

# Loading the relevant packages
import numpy as np
import pyPLUTO

# Load the data (4 levels of AMR)
Data = pyPLUTO.Load(
    path="Test_Problems/HD/Viscosity/Flow_Past_Cylinder", level=4
)

# Convert the grid to cartesian
rr, pphh = np.meshgrid(Data.x1r, Data.x2r, indexing="ij")
xx = rr * np.cos(pphh)
yy = rr * np.sin(pphh)

# Initialize the Image class (with black color)
Image = pyPLUTO.Image(withblack=True)

# Show the 2D density
Image.display(
    Data.rho,
    x1=xx,
    x2=yy,
    cpos="right",
    xrange=[-10, 50],
    yrange=[-20, 20],
    aspect="equal",
    cmap="bone",
    clabel=r"$\rho$",
    xtitle="x",
    ytitle="y",
    title="Test 13 - AMR Flow past cylinder test",
)

# Plot the AMR levels (up to 2)
Image.oplotbox(Data.AMRLevel, lrange=[0, 2], geom=Data.geom)

# Save and show the figure
Image.savefig("test13_flowpastcyl.png")
pyPLUTO.show()
