'''
A one-dimensional Riemann problem where density, pressure and velocity of a ideal gas 
are given at the left and at the right end of the dominion.

The plot shows the profiles of the three quantities at the time t = 0.2.

Authors:

        D. Crocco
        G. Mattia
'''

import pyPLUTO as pp
import os

# Creating the path for the data directory
plutodir = os.environ['PLUTO_DIR']
wdir     = plutodir+'/Test_Problems/HD/Sod'

# Loading the data into a pload object D.
D = pp.Load(path = wdir, text = False)

# Creating the Image
I = pp.Image(figsize = [7,5])

# Plotting the data
I.plot(D.x1, D.rho, label = r'$\rho$', title = 'Sod shock tube test',
    xtitle = '$x$', xrange = [0.0,1.0], yrange = [-0.05,1.05], legpos = 0)
I.plot(D.x1, D.prs, label = r'$p$')
I.plot(D.x1, D.vx1, label = r'$v_x$')

# Saving the image
pp.savefig('test01_sod.png')
pp.show()
