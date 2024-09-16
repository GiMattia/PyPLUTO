import pyPLUTO as pp
import numpy as np
import os

# Creating the path for the data directory
plutodir = os.environ['PLUTO_DIR']
wdir     = plutodir + '/Test_Problems/MHD/Jet'

D = pp.Load(path = wdir)

I = pp.Image()

B2 = ((D.Bx1**2 + D.Bx2**2 + D.Bx3**2)/D.rho)**0.5
I.display((D.rho/D.rho.max())[:,0,:], x1 = D.x1, x2 = D.x3, aspect = 'equal',
 xrange = [-D.x1.max(), D.x1.max()], cpos = 'right', cscale = 'log', vmin = 0.001)
I.display((B2/B2.max())[:,0,:], x1 = -D.x1, x2 = D.x3, aspect = 'equal', cscale = 'log', vmin = 0.001)

lines = D.find_fieldlines(D.Bx1[:,0,:], D.Bx3[:,0,:], x1 = D.x1, x2 = D.x3, x0 = [1,3,5], y0 = [30.0,30.0,30.0],
                          order = 'RK45', maxstep = 0.1, numsteps = 25000)

I.plot(lines[0][0],lines[0][1], c = 'k')
I.plot(lines[1][0],lines[1][1], c = 'k')
I.plot(lines[2][0],lines[2][1], c = 'k')

lines = D.find_fieldlines(-D.Bx1[::-1,0,:], D.Bx3[::-1,0,:], x1 = -D.x1[::-1], x2 = D.x3, x0 = [-1,-3,-5], y0 = [30.0,30.0,30.0],
                          order = 'RK45', maxstep = 0.1, numsteps = 25000)

I.plot(lines[0][0],lines[0][1], c = 'k')
I.plot(lines[1][0],lines[1][1], c = 'k')
I.plot(lines[2][0],lines[2][1], c = 'k')

I.savefig("test13_jet.png")
pp.show()
