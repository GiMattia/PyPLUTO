"""
MHD Torus test (configuration 4)

This test shows how to plot two quantities in two different subplots, together
with the plotting of streamlines in one of them and the plotting of the field
lines in the other one.

The package "os" is loaded to create the path to the directory
$PLUTO_DIR/Test_Problems/MHD/Torus, where the MHD torus test problem is located.

The data is loaded into a pload object D and the Image class is created. The
create_axes method is used to create two plots for the two variables. The
display method is used to plot the density and the pressure in the two subplots,
while the streamplot method and the find_fieldlines method are used to compute
and then plot streamlines and fieldlines of the magnetic field. Note that the
magnetic field components needs to be converted from spherical into cartesian
through the cartesian_vector method before converting them on the cartesian
mesh grid. The image is then saved and shown on screen.
"""

# Loading the relevant packages
import pyPLUTO as pp
import os
import numpy as np

# Transforming the magnetic field components from polar to cartesian coordinates
def cart_vec(Bx1,Bx2,x1,x2):
    Bx = Bx1*np.sin(x2) + Bx2*np.cos(x2)
    Bz = Bx1*np.cos(x2) - Bx2*np.sin(x2)
    return Bx, Bz

# Creating the path for the data directory
plutodir = os.environ['PLUTO_DIR']
wdir     = plutodir + '/Test_Problems/MHD/Torus'

# Loading the data into a pload object D
D = pp.Load(path = wdir)

# Creating the image
I = pp.Image(nwin = 2, figsize = [11,5], suptitle = 'Test 08 - MHD Torus test')

# Creating the subplots (2 for the different variables)
ax = I.create_axes(ncol = 2, top = 0.91)

# Compute the magnetic field magnitude
B2 = np.sqrt(D.Bx1**2 + D.Bx2**2 + D.Bx3**2)

# Plotting the data (colorbars adaptively positioned)
I.display(D.rho, x1 = D.x1p, x2 = D.x2p,
                             cpos = 'right',
                             aspect = 'equal',
                             ax = 0,
                             cscale = 'log',
                             title = 'Density',
                             shading = 'gouraud',
                             xtitle = 'x',
                             ytitle = 'y',
                             xrange = [0,14],
                             yrange =[-7,7])

I.display(D.prs, x1 = D.x1p, x2 = D.x2p,
                             cpos = 'right',
                             aspect = 'equal',
                             ax = 1,
                             cscale = 'log',
                             title = 'Pressure',
                             shading = 'gouraud',
                             xtitle = 'x',
                             xrange = [0,14],
                             yrange =[-7,7])

# Convert the magnetic field into cartesian components and cartesian geid
Bx, Bz = D.cartesian_vector('B')
xc, yc, Bx, Bz =  D.reshape_cartesian(Bx, Bz, nx1 = 500)

# Plot the magnetic field lines in two different ways
I.streamplot(Bx, Bz, x1 = xc, x2 = yc,
                              ax = 0,
                              c = 'gray',
                              lw = 0.7,
                              vmin = 1.e-5,
                              density = 5)

lines = D.find_fieldlines(Bx, Bz, x1 = xc, x2 = yc,
                          x0 = [3.75,4,4.25], y0 = [0,0,0], maxstep = 0.07)

I.plot(lines[0][0], lines[0][1], ax = 1, c = 'gray')
I.plot(lines[1][0], lines[1][1], ax = 1, c = 'gray')
I.plot(lines[2][0], lines[2][1], ax = 1, c = 'gray')

# Saving the image and showing the plots
I.savefig('test08_torus.png')
pp.show()
