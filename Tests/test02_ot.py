"""
Classical MHD Orszag-Tang test (configuration 2).

This test shows how to display a 2D quantity from a test problem in a single
subplot.

The package "os" is loaded to create the path to the directory
$PLUTO_DIR/Test_Problems/MHD/Orszag_Tang, where the the test problem is located
(see section 0.3 of the userguide to run the shock-tube problem).

In the script the spatial dependence of the density is displayed, with a
colorbar positioned dinamically on the right side of the figure.
In order to properly display the greek letter rho, the r character is used
before the string and the LaTeX interpreter is activated by setting it to True.
All the keywords necessary to customize the plot are iwithin the display method.
The image is then saved and shown on screen.
"""

# Loading the relevant packages
import pyPLUTO as pp
import os

# Creating the path for the data directory
plutodir = os.environ['PLUTO_DIR']
wdir     = plutodir + '/Test_Problems/MHD/Orszag_Tang'

# Loading the data into a pload object D
D = pp.Load(path = wdir)

# Creating the image
I = pp.Image(figsize = [7,6])

# Plotting the data
I.display(D.rho, x1 = D.x1r, x2 = D.x2r,
                             xtitle = 'x',
                             ytitle = 'y',
                             title = 'Test 02 - MHD Orszag-Tang vortex',
                             cpos = 'right',
                             cmap = 'RdBu_r',
                             clabel = r'$\rho$')

# Saving the image and showing the plot
I.savefig('test02_ot.png')
pp.show()
