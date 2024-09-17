import pyPLUTO as pp
import os
import numpy as np
import matplotlib.pyplot as plt

# Creating the path for the data directory
plutodir = os.environ['PLUTO_DIR']
wdir     = plutodir + '/Test_Problems/HD/Viscosity/Flow_Past_Cylinder'

D = pp.Load(path = wdir, level = 4)

rr, pphh = np.meshgrid(D.x1r,D.x2r,indexing='ij')
xx = rr*np.cos(pphh)
yy = rr*np.sin(pphh)

I = pp.Image(withblack = True)
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
I.oplotbox(D.AMRLevel,lrange=[0,2],geom=D.geom)

I.savefig('test13_flowpastcylinder.png')
pp.show()
