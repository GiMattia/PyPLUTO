'''
Authors:

        D. Crocco
        G. Mattia
'''

import pyPLUTO as pp
import os

# Creating the path for the data directory
plutodir = os.environ['PLUTO_DIR']
wdir     = plutodir+'/Test_Problems/HD/Disk_Planet'

# Loading the data into a pload object D.
D = pp.Load(path = wdir)

# Creating the Image and the subplot axes (in order to have two zoom simultaneously)
I = pp.Image()
ax = I.create_axes()

# Plotting the data
I.display(D.rho, x1 = D.x1rc, x2 = D.x2rc, cscale = 'log', cpos = 'right', title = 'Density', 
          vmin = 0.1)

#Zooming the planet region
I.zoom(xrange = [0.9,1.1], yrange = [-0.1,0.1], pos = [0.74,0.95,0.7,0.9])
I.zoom(var = D.vx2, xrange = [0.9,1.1], yrange = [-0.1,0.1], pos = [0.07,0.27,0.67,0.9],
       cpos = 'bottom', cmap = 'magma', cscale = 'linear', vmin = 5, vmax = 7, ax = ax,
       title = r'$v_\phi$')

# Saving the image
pp.savefig('test06_diskplanet.png')
pp.show()
