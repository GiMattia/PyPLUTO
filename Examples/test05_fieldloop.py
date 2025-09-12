"""Classical MHD Field loop test.

This test shows how to compute streamlines and field lines of the
magnetic field in a display with two subplots.

The data are the ones obtained from the PLUTO test problem
$PLUTO_DIR/Test_Problems/MHD/Field_Loop (configuration 5).

The data is loaded into a pload object D and the Image class is created.
The display method is used to plot the x and y components of the
magnetic field. The find_fieldlines method is used to compute the field
lines of the magnetic field. The streamplot method is used to plot the
streamlines of the magnetic field in the first display, while the plot
method is used to plot the field lines previously computed. The image is
then saved and shown on screen.

IMPORTANT: During the setup of the test, in the pluto.ini file, the simulation
time at which a .vtk output file is printed should be changed in

dbl     -1.0   -1   single_file
vtk      2.0   -1   single_file

"""

# Loading the relevant packages
import pyPLUTO

# Set the relative path to the data folder
data_path = pyPLUTO.find_example("MHD/Field_Loop")

# Load data
Data = pyPLUTO.Load(path=data_path)

# Creating the image
Image = pyPLUTO.Image(figsize=[13, 5], suptitle="Test 05 - MHD Field loop test")

# Creating the subplots
ax = Image.create_axes(ncol=2, top=0.91)

# Integrate the field line
lines = Data.find_fieldlines(
    Data.Bx1,
    Data.Bx2,
    x1=Data.x1,
    x2=Data.x2,
    x0=[0.1, 0.2, 0.3],
    y0=[0.0, 0.0, 0.0],
    order="RK45",
    maxstep=0.1,
    numsteps=25000,
)

# Plotting the data
Image.display(
    1000 * Data.Bx1,
    x1=Data.x1,
    x2=Data.x2,
    ax=0,
    cmap="RdBu_r",
    aspect="equal",
    xrange=[-0.5, 0.5],
    cpos="right",
    vmin=-1.5,
    vmax=1.5,
    shading="gouraud",
    title=r"$B_x$ (+ streamplot)",
    xtitle="x",
    ytitle="y",
)

Image.display(
    1000 * Data.Bx2,
    x1=Data.x1,
    x2=Data.x2,
    ax=1,
    cmap="RdBu_r",
    aspect="equal",
    xrange=[-0.5, 0.5],
    cpos="right",
    vmin=-1.5,
    vmax=1.5,
    shading="gouraud",
    title=r"$B_y$ (+ find$\_$fieldlines)",
    xtitle="x",
)

# Plot the field lines in two different ways
Image.streamplot(
    Data.Bx1, Data.Bx2, x1=Data.x1, x2=Data.x2, ax=0, lw=1.5, vmin=1.0e-4, c="k"
)

Image.plot(lines[0][0], lines[0][1], ax=1, c="k", lw=1.5)
Image.plot(lines[1][0], lines[1][1], ax=1, c="k", lw=1.5)
Image.plot(lines[2][0], lines[2][1], ax=1, c="k", lw=1.5)

# Saving the image and showing the plots
Image.savefig("test05_fieldloop.png", script_relative=True)
pyPLUTO.show()
