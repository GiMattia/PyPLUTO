'''
Authors:

        D. Crocco
        G. Mattia
'''

import pyPLUTO as pp
import os

# Creating the path for the data directory
plutodir = os.environ['PLUTO_DIR']
wdir     = plutodir+'/Test_Problems/MHD/Blast'

# Loading the data into a pload object D.
D = pp.Load(path = wdir)

# Creating the Image and the subplot axes (in order to have two zoom simultaneously)
I = pp.Image()
ax = I.create_axes()
I.set_axis(xrange = [D.x1.min(),D.x1.max()], yrange = [D.x2.min(),D.x2.max()])

q = [
    (slice(0, D.nx1//2), slice(0, D.nx2//2)),   # Bottom-left
    (slice(0, D.nx1//2), slice(D.nx2//2, D.nx2)), # Top-left
    (slice(D.nx1//2, D.nx1), slice(0, D.nx2//2)), # Bottom-right
    (slice(D.nx1//2, D.nx1), slice(D.nx2//2, D.nx2))# Top-right
]



# Plotting the data
I.display(D.vx1[q[0]], x1 = D.x1r[q[0][0]], x2 = D.x2r[q[0][1]])
I.display(D.vx2[q[1]], x1 = D.x1r[q[1][0]], x2 = D.x2r[q[1][1]])
I.display(D.Bx1[q[2]], x1 = D.x1r[q[2][0]], x2 = D.x2r[q[2][1]])
I.display(D.Bx2[q[3]], x1 = D.x1r[q[3][0]], x2 = D.x2r[q[3][1]])

# Saving the image
I.savefig('test07_blast.png')
pp.show()
