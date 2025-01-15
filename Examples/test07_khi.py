"""
RMHD Kelvin-Helmholtz instability test

This test shows how to plot a more complex figure with a customized number of
subplots and the insert of text inside the plots.

The data are the ones obtained from the PLUTO test problem
$PLUTO_DIR/Test_Problems/RMHD/KH (configuration 1).

The data is loaded into a pload object D and the Image class is created. The
create_axes method is used to form a collage of plots both elegant and useful.
The display method is used to plot the density in the main plot, while the plot
method, together with the text method, is used to show secondary plots of the
trasversal velocity as function of time. The image is then saved and shown on
screen.

IMPORTANT: For the correct representation of the secondary plots, the analysis
parameter in the pluto.ini should be changed to 0.05.
"""

# Loading the relevant packages
import pyPLUTO as pp

# Loading the data into a pload object D
D = pp.Load(path="Test_Problems/RMHD/KH")

# Creating the image and the subplot axes (to have two secondary plots)
I = pp.Image(
    figsize=[10, 10],
    suptitle="Test 07 - RMHD Kelvin-Helmholtz instability test",
)
I.create_axes(ncol=2, wratio=[1, 0.1], wspace=[0.003], right=0.55)
I.create_axes(nrow=2, hspace=[0.003], left=0.67)

# Plotting the data
I.display(
    D.rho,
    x1=D.x1,
    x2=D.x2,
    title="Density",
    ax=0,
    shading="gouraud",
    xtitle=r"$x$",
    ytitle=r"$y$",
)

I.colorbar(axs=0, cax=1)

# Find and plot the field lines
lines = D.find_fieldlines(
    D.Bx1,
    D.Bx2,
    x1=D.x1,
    x2=D.x2,
    y0=[0.0, 0.1, -0.1, 0.2, -0.2],
    x0=[0.55, 0.0, 0.0, 0.0, 0.0],
    order="RK45",
    maxstep=0.01,
    numsteps=25000,
)

for _, line in enumerate(lines):
    I.plot(line[0], line[1], ax=0, c="k")

# Open the kh.dat file and store the variables
analysis = D.read_file("kh.dat")

# Add text in the axes
I.text(r"$\langle v_y^2\rangle$", ax=2, x=0.05)
I.text(r"$v_{y, MAX}^2$", ax=3, x=0.05)

# Plot the velocity from the kh.dat file.
I.plot(
    analysis["time"],
    analysis["vy2"],
    ax=2,
    c="k",
    yscale="log",
    xtickslabels=None,
)
I.plot(
    analysis["time"],
    analysis["maxvy"],
    ax=3,
    c="k",
    yscale="log",
    xtitle=r"$t$",
)

# Saving the image and showing the plots
I.savefig("test07_khi.png")
pp.show()
