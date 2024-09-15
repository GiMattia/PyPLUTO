import pyPLUTO as pp
import numpy as np
import os

# Creating the path for the data directory
plutodir = os.environ['PLUTO_DIR']
wdir     = plutodir + '/Test_Problems/MHD/FARGO/Spherical_Disk'

D = pp.Load(path = wdir, datatype = 'vtk')

I = pp.Image()




I.savefig("test14_sphericaldisk.png")
pp.show()
