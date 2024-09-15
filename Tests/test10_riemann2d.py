"""
vtk       0.1  -1   multiple_files
"""

# Loading the relevant packages
import pyPLUTO as pp
import os

# Creating the path for the data directory
plutodir = os.environ['PLUTO_DIR']
wdir     = plutodir + '/Test_Problems/HD/Riemann_2D'

# Loading the data into a pload object D.
D = pp.Load('all', datatype = 'vtk', path = wdir)
I = pp.Image()

#v2 = np.sqrt(D.vx1**2 + D.vx2**2)
I.interactive(D.rho, x1 = D.x1, x2 = D.x2, cpos = 'right', vmin = 0, vmax = 1.0)

I.savegif('test10_riemann2d.gif')
