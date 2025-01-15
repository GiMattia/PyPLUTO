"""
Classical MHD Orszag-Tang test

This test shows how to display a 2D quantity from a test problem in a single
subplot.

The data are the ones obtained from the PLUTO test problem
$PLUTO_DIR/Test_Problems/MHD/Orszag_Tang (configuration 2).

In the script the spatial dependence of the density is displayed, with a
colorbar positioned dinamically on the right side of the figure.
In order to properly display the greek letter rho, the r character is used
before the string and the LaTeX interpreter is activated by setting it to True.
All the keywords necessary to customize the plot are iwithin the display method.
The image is then saved and shown on screen.
"""

# Loading the relevant packages
import pyPLUTO as pp

# Loading the data into a pload object D
D = pp.Load(path="Test_Problems/MHD/Orszag_Tang")

# Creating the image
I = pp.Image(figsize=[7, 6])

# Plotting the data
I.display(
    D.rho,
    x1=D.x1r,
    x2=D.x2r,
    xtitle="x",
    ytitle="y",
    title="Test 02 - MHD Orszag-Tang vortex",
    cpos="right",
    cmap="RdBu_r",
    clabel=r"$\rho$",
)

var2 = 5 * 6

# Saving the image and showing the plot
I.savefig("test02_ot.png")
pp.show()
