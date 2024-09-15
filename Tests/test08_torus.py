"""

"""

import pyPLUTO as pp
import os
import numpy as np

def cart_vec(Bx1,Bx2,x1,x2):
    Bx = Bx1*np.sin(x2) + Bx2*np.cos(x2)
    Bz = Bx1*np.cos(x2) - Bx2*np.sin(x2)
    return Bx,Bz


# Creating the path for the data directory
plutodir = os.environ['PLUTO_DIR']
wdir     = plutodir+'/Test_Problems/MHD/Torus'

# Loading the data into a pload object D.
D = pp.Load(path = wdir)

# Creating the Image
I = pp.Image(nwin = 2)

# Creating the subplots (2 for the different variables)
ax = I.create_axes(ncol = 2)

# Compute the magnetic field magnitude
B2 = np.sqrt(D.Bx1**2 + D.Bx2**2 + D.Bx3**2)

# Plotting the data (colorbars adaptively positioned)
I.display(D.rho, cpos = 'right', aspect = 'equal', x1 = D.x1p, x2 = D.x2p,
          ax = I.ax[0], cscale = 'log', title = 'Density',# shading = 'gouraud',
          xtitle = 'x', ytitle = 'y', xrange = [0,14], yrange =[-7,7])
I.display(D.prs, cpos = 'right', aspect = 'equal', x1 = D.x1p, x2 = D.x2p,
          ax = I.ax[1], cscale = 'log', title = 'Pressure', #shading = 'gouraud',
          xtitle = 'x', ytitle = 'y', xrange = [0,14], yrange =[-7,7])

Bx, Bz = cart_vec(D.Bx1,D.Bx2,D.x1,D.x2)
xc, yc, Bx, Bz =  D.reshape_cartesian(Bx, Bz)

I.streamplot(Bx, Bz, x1 =xc, x2 = yc, ax = 0, c = 'r', lw = 0.7, vmin = 1.e-5, density = 5)

#lines = D.find_fieldlines(Bx.T, Bz.T, x1 = yc, x2 = xc, x0 = [3.75,4,4.25], y0 = [0,0,0], maxstep = 0.07)

#I.plot(lines[0][0],lines[0][1],ax = 1, c = 'r')
#I.plot(lines[1][0],lines[1][1],ax = 1, c = 'r')
#I.plot(lines[2][0],lines[2][1],ax = 1, c = 'r')
# Saving the image
I.savefig('test08_torus.png')
pp.show()
