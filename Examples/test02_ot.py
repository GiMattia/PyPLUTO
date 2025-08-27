"""Classical MHD Orszag-Tang test.

This test shows how to display a 2D quantity from a test problem in a
single subplot.

The data are the ones obtained from the PLUTO test problem
$PLUTO_DIR/Test_Problems/MHD/Orszag_Tang (configuration 2).

In the script the spatial dependence of the density is displayed, with a
colorbar positioned dynamically on the right side of the figure. In
order to properly display the Greek letter rho, the r character is used
before the string and the LaTeX interpreter is activated by setting it
to True. All the keywords necessary to customize the plot are within the
display method. The image is then saved and shown on screen.

"""

# Loading the relevant packages
import pyPLUTO

# Set the relative path to the data folder
data_path = pyPLUTO.find_example("MHD/Orszag_Tang")

# Load data
Data = pyPLUTO.Load(path=data_path)

# Creating the image
Image = pyPLUTO.Image(figsize=[7, 6])

# Plotting the data
Image.display(
    Data.rho,
    x1=Data.x1r,
    x2=Data.x2r,
    xtitle="x",
    ytitle="y",
    title="Test 02 - MHD Orszag-Tang vortex",
    cpos="right",
    cmap="RdBu_r",
    clabel=r"$\rho$",
)

# Saving the image and showing the plot
Image.savefig("test02_ot.png", script_relative=True)
pyPLUTO.show()
