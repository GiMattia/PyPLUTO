"""
Particles CR Xpoint test (configuration 1)

This test shows how to plot data from the Load class and the LoadPart class
simultaneously and how to produce a scatter plot.

The package "os" is loaded to create the path to the directory
$PLUTO_DIR/Test_Problems/Particles/CR/Xpoint, where the Particles CR Xpoint
test problem is located.

The data is loaded with the Load class and the LoadPart class into two pload
objects and the Image class is created. The contour method is used to plot the
contour lines of the electromagnetic vector potential. The scatter method is
used to plot the single particles at the end of the simulation time. The
spectrum and plot method are then used to show the velocity spectra of the
particles at the beginning and at the end of the simulation. The image is then
saved and shown on screen.
"""

# Loading the relevant packages
import pyPLUTO as pp
import numpy as np
import os
import matplotlib.pyplot as plt

# Creating the path for the data directory
plutodir = os.environ['PLUTO_DIR']
wdir     = plutodir + '/Test_Problems/Particles/CR/Xpoint'

# Loading the data and the particle data into two pload objects
Df = pp.Load(path = wdir)
Dp = pp.LoadPart(path = wdir, datatype = "vtk")
gl = (1 + Dp.vx1**2 + Dp.vx2**2 + Dp.vx3**2)**0.5
indx = np.argsort(gl)

# Creating the image
I = pp.Image(figsize = [7,7], fontsize = 20)

# Plotting the data
I.contour(Df.Ax3, x1 = Df.x1/1000, x2 = Df.x2/1000, levels = 20, aspect = 'equal', c = 'silver')
I.scatter(Dp.x1[indx]/1000, Dp.x2[indx]/1000,
                       cpos = 'right',
                       vmin = 0,
                       vmax = 40,
                       title = 'Test 11 - Particles CR Xpoint test',
                       xrange = [-3.5,3.5],
                       yrange = [-3.5,3.5],
                       xticks = [-3,-2,-1,0,1,2,3],
                       yticks = [-3,-2,-1,0,1,2,3],
                       xtitle = r'$x\;(\times10^3)$',
                       ytitle = r'$y\;(\times10^3)$',
                       cmap = plt.get_cmap('YlOrRd',8),
                       clabel = r"$\Gamma$",
                       c = gl[indx],
                       ms = 10)

# Create the second axis
ax = I.create_axes(left = 0.35, right = 0.7, bottom = 0.23, top = 0.4)

# Compute and plot the particle spectrum at the initial time
Dp = pp.LoadPart(0, path = wdir, datatype = "vtk")
gl = (1 + Dp.vx1**2 + Dp.vx2**2 + Dp.vx3**2)**0.5
hist, bins = Dp.spectrum(gl, density = False)
I.plot(bins, hist,
             ax = 1,
             xscale = 'log',
             yscale = 'log',
             xrange = [1,50],
             yrange = [1,1.e8],
             label = "t = 0",
             fontsize = 13)

# Compute and plot the particle spectrum at the final time
Dp = pp.LoadPart(path = wdir, datatype = "vtk")
gl = (1 + Dp.vx1**2 + Dp.vx2**2 + Dp.vx3**2)**0.5
hist, bins = Dp.spectrum(gl, density = False)
I.plot(bins, hist,
             ax = 1,
             xscale = 'log',
             yscale = 'log',
             xrange = [1,50],
             yrange = [1,1.e8],
             label = "t = 100",
             legpos = 0,
             legsize = 10,
             legalpha = 0.25)

# Set a different alpha for the spectrum plot
I.ax[1].patch.set_alpha(0.75)

# Saving the image and showing the plots
I.savefig('test11_xpoint.png')
pp.show()
