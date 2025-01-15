"""
Particles LP Riemann 2D test

This test shows how to plot data from the Load class and the LoadPart class
simultaneously and how to produce a scatter plot on a omplex axes grid.

The data are the ones obtained from the PLUTO test problem
$PLUTO_DIR/Test_Problems/Particles/LP/Riemann_2D (configuration 1).

The data is loaded with the Load class and the LoadPart class into two pload
objects and the Image class is created. The display method is used to plot the
density and the scatter method is used to plot the loaded particles at the final
time of the simulation. Two color bars are then created in order to show the
particles identity and the fluid velocity values. The image is then saved and
shown on screen.
"""

# Loading the relevant packages
import numpy as np
import pyPLUTO as pp

# Loading the data and the particle data into two pload objects
Df = pp.Load(path="Test_Problems/Particles/LP/Riemann_2D")
Dp = pp.LoadPart(path="Test_Problems/Particles/LP/Riemann_2D", nfile_lp=0)

# Creating the image and the axes
I = pp.Image(figsize=[9.5, 8])
I.create_axes(right=0.8)
I.create_axes(nrow=2, left=0.81, right=0.85, hspace=0.01)

# Plotting the data
pcm = I.display(Df.rho, x1=Df.x1, x2=Df.x2, ax=0, aspect="equal")
indx = np.argsort(Dp.vx1**2 + Dp.vx2**2 + Dp.vx3**2)

# Plot the fluid colorbar
I.colorbar(pcm, cax=1, clabel=r"$\rho$")

# Plot the particles
pcm = I.scatter(
    Dp.x1[indx[::20]],
    Dp.x2[indx[::20]],
    ax=0,
    c=Dp.id[indx[::20]],
    cmap="Greys_r",
    title="Test 12 - LP Riemann 2D test",
    titlesize=23,
    ms=20,
    vmin=0,
    xtitle="x",
    ytitle="y",
)

# Plot the particles colorbar
I.colorbar(pcm, cax=2, clabel="id")

# Saving the image and showing the plot
I.savefig("test12_riemannlp.png")
pp.show()
