'''
'''

# Loading the relevant packages
import pyPLUTO as pp
import numpy as np
import os

# Creating the path for the data directory
plutodir = os.environ['PLUTO_DIR']
wdir     = plutodir + '/Test_Problems/MHD/FARGO/Spherical_Disk'

# Loading the data into a pload object D
D = pp.Load(path = wdir, datatype = 'vtk')

# Creating the image
I = pp.Image()



# Saving the image and showing the plot
I.savefig("test14_sphericaldisk.png")
pp.show()
