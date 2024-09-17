'''
MHD Jet test (configuration 1)

This test shows...

The package "os" is loaded to create the path to the directory
$PLUTO_DIR/Test_Problems/MHD/Jet, where the MHD Jet test problem is located.

The data is loaded into a pload object D and the Image class is created. The...
'''

# Loading the relevant packages
import pyPLUTO as pp
import numpy as np
import os

# Creating the path for the data directory
plutodir = os.environ['PLUTO_DIR']
wdir     = plutodir + '/Test_Problems/MHD/Jet'

# Loading the data into a pload object D
D = pp.Load(path = wdir)

# Creating the image
I = pp.Image()

# Plotting the data
B2 = ((D.Bx1**2 + D.Bx2**2 + D.Bx3**2)/D.rho)**0.5
I.display((D.rho/D.rho.max())[:,0,:], x1 = D.x1, 
                                      x2 = D.x3, 
                                      aspect = 'equal',
                                      xrange = [-D.x1.max(), D.x1.max()], 
                                      cpos = 'right', 
                                      cscale = 'log', 
                                      vmin = 0.001)
I.display((B2/B2.max())[:,0,:], x1 = -D.x1, 
                                x2 = D.x3, 
                                aspect = 'equal', 
                                cscale = 'log', 
                                vmin = 0.001)

lines = D.find_fieldlines(D.Bx1[:,0,:], D.Bx3[:,0,:], x1 = D.x1, 
                                                      x2 = D.x3, 
                                                      x0 = [1,3,5], 
                                                      y0 = [30.0,30.0,30.0],
                                                      order = 'RK45', 
                                                      maxstep = 0.1, 
                                                      numsteps = 25000)

I.plot(lines[0][0],lines[0][1], c = 'k')
I.plot(lines[1][0],lines[1][1], c = 'k')
I.plot(lines[2][0],lines[2][1], c = 'k')

lines = D.find_fieldlines(-D.Bx1[::-1,0,:], D.Bx3[::-1,0,:], 
                                            x1 = -D.x1[::-1], 
                                            x2 = D.x3, 
                                            x0 = [-1,-3,-5], 
                                            y0 = [30.0,30.0,30.0],
                                            order = 'RK45', 
                                            maxstep = 0.1, 
                                            numsteps = 25000)

I.plot(lines[0][0],lines[0][1], c = 'k')
I.plot(lines[1][0],lines[1][1], c = 'k')
I.plot(lines[2][0],lines[2][1], c = 'k')

# Saving the image and showing the plots
I.savefig("test13_jet.png")
pp.show()
