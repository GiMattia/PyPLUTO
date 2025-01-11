"""
HD shock tube test

This test shows how to plot different 1D quantities from a test problem in the
same plot.

The data are the ones obtained from the PLUTO test problem
$PLUTO_DIR/Test_Problems/HD/Sod (configuration 1).

In this script the quatities plotted are density, pressure and velocity
(component x) in different colors. The relevant keywords to customize the plot
(e.g. the labels or the legend position) are scattered through the different
line plotting methods in order to show the flexibility of PyPLUTO in terms of
plot cusotmization. A legend is placed (legpos 0 means that the location is
chosen automatically) in order to differenciate the lines. The image is then
saved and shown on screen.

Note that the Image is saved through I.savefig (and not pp.savefig) since saving
a file should be strictly related to a single Image class. Conversely, the
pp.show displays all the figures generated in the script (here only one).
"""

# Loading the relevant packages
import pyPLUTO as pp

# Creating the path for the data directory
wdir = '../Examples/Test_Problems/HD/Sod'

# Loading the data into a pload object D
D = pp.Load(path = wdir)

# Creating the image
I = pp.Image(figsize = [7,5])

# Plotting the data
I.plot(D.x1, D.rho, label = r'$\rho$',
                    title = 'Test 01 - HD Sod shock tube',
                    xtitle = 'x',
                    xrange = [0.0,1.0],
                    yrange = [-0.05,1.05],
                    legpos = 0)

I.plot(D.x1, D.prs, label = r'$p$')
I.plot(D.x1, D.vx1, label = r'$v_x$')

# Saving the image and showing the plot
I.savefig('test01_sod.png')
pp.show()
