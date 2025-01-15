"""
Classical MHD Rayleigh-Taylor instability test

This test shows how to display a 2D quantity from a test problem at different
times in different subplots.

The data are the ones obtained from the PLUTO test problem
$PLUTO_DIR/Test_Problems/MHD/Rayleigh_Taylor (configuration 1).

In the script the spatial dependence of the density is displayed at three
different times in three different subplots. Here the subplots are created
through the create_axes method, which allows to create a grid of subplots with a
given number of columns and a given width ratio between the subplots. The
colorbar is placed in the last subplot through the colorbar method. The y labels
and y ticks labels are customized in order to show the flexibility of PyPLUTO in
terms of plot customization. The image is then saved and shown on screen.

The title of the subplots is set to the time of the simulation, which is stored
in the timelist attribute of the pload object D. In order to display a fixed
number of decimal digits, the f-string formatting is used.

IMPORTANT: During the setup of the test, in the pluto.ini file the simulation
time at which a .dbl output file is printed should be changed in

dbl      7.5   -1   single_file

in the static grid output section.
"""

# Loading the relevant packages
import pyPLUTO as pp

# Loading the data into a pload object D
D = pp.Load([0, 1, 2], path="Test_Problems/MHD/Rayleigh_Taylor")

# Creating the image
I = pp.Image(
    figsize=[13, 7.6],
    suptitle="Test 03 - MHD Rayleigh-Taylor instability",
    suptitlesize=22,
)

# Creating the subplots (3 for the temporal evolution and 1 for the colorbar)
I.create_axes(ncol=4, wratio=[1, 1, 1, 0.2], wspace=[0.005, 0.005, 0.005], top=0.88)

# Customizing y labels and y ticks labels
ylab = ["y", None, None]
ytcl = [True, None, None]

# Loop over the different outputs
for i in [0, 1, 2]:
    # Plotting the data
    I.display(
        D.rho[i],
        x1=D.x1r,
        x2=D.x2r,
        ax=i,
        cmap="inferno",
        title=rf"$\tau = ${D.timelist[i]:.1f}",
        xtitle="x",
        ytitle=ylab[i],
        aspect="equal",
        ytickslabels=ytcl[i],
        xticks=[-0.4, -0.2, 0, 0.2, 0.4],
    )

# Placing the colorbar
I.colorbar(axs=0, cax=-1, clabel=r"$\rho$")

# Saving the image and showing the plots
I.savefig("test03_rti.png")
pp.show()
