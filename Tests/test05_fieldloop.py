import pyPLUTO as pp
import os
import numpy   as np

# Creating the path for the data directory
plutodir = os.environ['PLUTO_DIR']
wdir     = plutodir+'/Test_Problems/MHD/Field_Loop'

# Loading the data into a pload object D.
D = pp.Load(path = wdir)
I  = pp.Image(figsize = [13,5])
ax = I.create_axes(ncol = 2)

norm = np.sqrt(D.Bx1**2 + D.Bx2**2)
# Integrate the field line
lines = D.find_fieldlines(D.Bx1, D.Bx2, x1 = D.x1, x2 = D.x2, x0 = [0.1,0.2,0.3], y0 = [0.0,0.0,0.0],
                          order = 'RK45', maxstep = 0.1, numsteps = 25000)

I.display(1000*D.Bx1, ax = ax[0], cmap = 'RdBu_r', aspect = 'equal', x1 = D.x1, x2 = D.x2, xrange = [-0.5,0.5], cpos = 'right', vmin = -1, vmax = 1, shading = 'gouraud')
I.display(1000*D.Bx2, ax = ax[1], cmap = 'RdBu_r', aspect = 'equal', x1 = D.x1, x2 = D.x2, xrange = [-0.5,0.5], cpos = 'right', vmin = -1, vmax = 1, shading = 'gouraud')

I.streamplot(D.Bx1, D.Bx2,x1 = D.x1,x2 = D.x2, ax = ax[0], vmin = 1.e-4, c = 'k')
I.plot(lines[0][0],lines[0][1],ax = 1, c = 'k')
I.plot(lines[1][0],lines[1][1],ax = 1, c = 'k')
I.plot(lines[2][0],lines[2][1],ax = 1, c = 'k')


I.savefig('test05_fieldloop.png')
pp.show()
