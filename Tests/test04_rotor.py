"""
MHD Rotor test

This test shows how to compute and plot contour lines of the vector potential
from a test problem in non-cartesian coordinates.

The package "os" is loaded to create the path to the directory
$PLUTO_DIR/Test_problems/MHD/Rotor, where the MHD rotor test problem is located.

The data is loaded into a pload object D and the Image class is created. The
display method is used to plot the density and the magnetic field magnitude. The
contour_lines method is used to compute the contour lines of the vector
potential. The plot method is used to plot the contour lines on the density and
magnetic field magnitude plots. The image is then saved and shown on screen.



"""

import pyPLUTO as pp
import os
import numpy as np
import matplotlib.pyplot as plt
import timeit

# Creating the path for the data directory
plutodir = os.environ['PLUTO_DIR']
wdir     = plutodir+'/Test_Problems/MHD/Rotor'

# Loading the data into a pload object D.
D = pp.Load(path = wdir)

# Creating the Image
I = pp.Image(nwin = 2, suptitle = 'Rotor test MHD', figsize = [11,5],
             suptitlesize = 27)

# Creating the subplots (2 for the different variables)
ax = I.create_axes(ncol = 2)

# Compute the magnetic field magnitude
B2 = np.sqrt(D.Bx1**2 + D.Bx2**2 + D.Bx3**2)

# Plotting the data (colorbars adaptively positioned)
I.display(D.rho, cpos = 'right', aspect = 'equal', x1 = D.x1rc, x2 = D.x2rc,
          ax = I.ax[0], cscale = 'log')
I.display(B2, cpos = 'right', aspect = 'equal', x1 = D.x1rc, x2 = D.x2rc,
          ax = I.ax[1])

#I.ax[0].contour(D.x1c, D.x2c, D.Ax3.T, 
#               levels = np.linspace(D.Ax3.min(),D.Ax3.max(),10), color = 'b')

# Plot the contour lines
lines = D.contour_lines(D.Ax3)
for line in lines:
    I.plot(line[0], line[1], ax = I.ax[0], c = 'b')

lines = D.contour_lines("Ax3", levels = 10, cmap = 'RdYlBu')
for line in lines:
    I.plot(line[0], line[1], ax = I.ax[1], c = line[2])

# Saving the image
I.savefig('test04_rotor.png')
pp.show()
