"""
Classical MHD Field loop test (configuration 5).

This test shows how to compute streamlines and field lines of the magnetic field
in a display with two subplots.

The package "os" is loaded to create the path to the directory
$PLUTO_DIR/Test_Problems/MHD/Field_Loop, where the MHD rotor test problem is
located.

The data is loaded into a pload object D and the Image class is created. The
display method is used to plot the x and y components of the magnetic field. The
find_fieldlines method is used to compute the field lines of the magnetic field.
The streamplot method is used to plot the streamlines of the magnetic field in
the first display, while the plot method is used to plot the field lines
previously computed. The image is then saved and shown on screen.
"""

# Loading the relevant packages
import pyPLUTO as pp
import os
import numpy as np

# Creating the path for the data directory
plutodir = os.environ['PLUTO_DIR']
wdir     = plutodir + '/Test_Problems/MHD/Field_Loop'

# Loading the data into a pload object D
D = pp.Load(path = wdir)

# Creating the image
I  = pp.Image(figsize = [13,5], suptitle = 'Test 05 - MHD Field loop test')

# Creating the subplots
ax = I.create_axes(ncol = 2, top = 0.91)

# Integrate the field line
lines = D.find_fieldlines(D.Bx1, D.Bx2,
                                 x1 = D.x1,
                                 x2 = D.x2,
                                 x0 = [0.1,0.2,0.3],
                                 y0 = [0.0,0.0,0.0],
                                 order = 'RK45',
                                 maxstep = 0.1,
                                 numsteps = 25000)

# Plotting the data
I.display(1000*D.Bx1, x1 = D.x1, x2 = D.x2,
                                 ax = 0,
                                 cmap = 'RdBu_r',
                                 aspect = 'equal',
                                 xrange = [-0.5,0.5],
                                 cpos = 'right',
                                 vmin = -1,
                                 vmax = 1,
                                 shading = 'gouraud',
                                 title = r'$B_x$',
                                 xtitle = 'x',
                                 ytitle = 'y')

I.display(1000*D.Bx2, x1 = D.x1, x2 = D.x2,
                                 ax = 1,
                                 cmap = 'RdBu_r',
                                 aspect = 'equal',
                                 xrange = [-0.5,0.5],
                                 cpos = 'right',
                                 vmin = -1,
                                 vmax = 1,
                                 shading = 'gouraud',
                                 title = r'$B_y$',
                                 xtitle = 'x')

# Plot the field lines in two different ways
I.streamplot(D.Bx1, D.Bx2, x1 = D.x1, x2 = D.x2,
                                      ax = 0,
                                      vmin = 1.e-4,
                                      c = 'k')

I.plot(lines[0][0], lines[0][1], ax = 1, c = 'k')
I.plot(lines[1][0], lines[1][1], ax = 1, c = 'k')
I.plot(lines[2][0], lines[2][1], ax = 1, c = 'k')

# Saving the image and showing the plots
I.savefig('test05_fieldloop.png')
pp.show()
