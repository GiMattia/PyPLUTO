import pyPLUTO as pp
import os
import numpy as np
import matplotlib.pyplot as plt

# Creating the path for the data directory
plutodir = os.environ['PLUTO_DIR']
wdir     = plutodir + '/Test_Problems/HD/Viscosity/Flow_Past_Cylinder'

# Load the data (4 levels of AMR)
D = pp.Load(path = wdir, level = 4)

# Convert the grid to cartesian
rr, pphh = np.meshgrid(D.x1r,D.x2r,indexing='ij')
xx = rr*np.cos(pphh)
yy = rr*np.sin(pphh)

# Initialize the Image class (with black color)
I = pp.Image(withblack = True)

# Show the 2D density
I.display(D.rho, x1 = xx, x2 = yy, 
                 cpos = 'right', 
                 xrange = [-10,50], 
                 yrange = [-20,20], 
                 aspect = 'equal', 
                 cmap = 'bone',
                 clabel = r"$\rho$",
                 xtitle = 'x',
                 ytitle = 'y',
                 title = 'Test 13 - AMR Flow past cylinder test')
                 
# Plot the AMR levels (up to 2)
I.oplotbox(D.AMRLevel,lrange=[0,2],geom=D.geom)

# Save and show the figure
I.savefig('test13_flowpastcylinder.png')
pp.show()
