'''
Rotor test.

Authors:

        D. Crocco
        G. Mattia
'''

import pyPLUTO as pp
import os

# Creating the path for the data directory
plutodir = os.environ['PLUTO_DIR']
wdir     = plutodir+'/Test_Problems/MHD/Rotor'

# Loading the data into a pload object D.
D = pp.Load(path = wdir)

# Creating the Image
I = pp.Image()

# Creating the subplots (3 for the temporal evolution and 1 for the colorbar)
ax = I.create_axes(ncol = 2)

I.display(D.rho, cpos = 'right', aspect = 'equal', x1 = D.x1rc, x2 = D.x2rc, ax = I.ax[0], cscale = 'log')
I.display(D.prs, cpos = 'right', aspect = 'equal', x1 = D.x1rc, x2 = D.x2rc, ax = I.ax[1], cscale = 'log')

#T  = pp.Tools(D)

#lines = T.contour(D.Ax3)

# Saving the image
pp.savefig('test04_rotor.png')
pp.show()
