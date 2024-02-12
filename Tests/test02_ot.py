'''
Authors:

        D. Crocco
        G. Mattia
'''

import pyPLUTO as pp
import os

# Creating the path for the data directory
plutodir = os.environ['PLUTO_DIR']
wdir     = plutodir+'/Test_Problems/MHD/Orszag_Tang'

# Loading the data into a pload object D.
D = pp.Load(path = wdir, datatype = 'vtk')

# Creating the Image
I = pp.Image(figsize = [7,6])

# Plotting the data
I.display(D.rho, x1 = D.x1r, x2 = D.x2r, title = r'Density $\rho$ [Orszag Tang test]',
    xtitle = 'x', ytitle = 'y', cpos = 'right', cmap = 'RdBu_r')

# Saving the image
pp.savefig('test02_ot.png')
pp.show()
