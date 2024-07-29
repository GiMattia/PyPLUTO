"""
Classical MHD Rayleigh-Taylor instability test.

This test shows how to display a 2D quantity from a test problem at different 
times in different subplots.

The package "os" is loaded to create the path to the directory 
$PLUTO_DIR/Test_problems/MHD/Rayleigh_Taylor, where the the test problem is
located.

In the script the spatial dependence of the density is displayed at three
different times in three different subplots. Here the subplots are created 
through the create_axes method, which allows to create a grid of subplots with a
given number of columns and a given width ratio between the subplots. The 
colorbar is placed in the last subplot through the colorbar method. The y labels
and y ticks labels are customized in order to show the flexibility of PyPLUTO in
terms of plot customization. The image is then saved and shown on screen.

The title of the subplots is set to the time of the simulation, which is stored
in the timelist attribute of the pload object D. In order to display a fixed 
number of decimal digits, the f-string formatting is used (see line 38).
"""

# Loading the relevant packages
import pyPLUTO as pp
import os

# Creating the path for the data directory
plutodir = os.environ['PLUTO_DIR']
wdir     = plutodir+'/Test_Problems/MHD/Rayleigh_Taylor'

# Loading the data into a pload object D.
D = pp.Load([0,1,2], path = wdir)

# Creating the Image
I = pp.Image(figsize = [10.2,6])

# Creating the subplots (3 for the temporal evolution and 1 for the colorbar)
I.create_axes(ncol = 4, wratio = [1,1,1,0.2], wspace = [0.005,0.005,0.005])

# Customizing y labels and y ticks labels
ylab = ['y',       None, None]
ytcl = ['Default', None, None]

# Loop over the different outputs
for i in [0,1,2]:
    # Plotting the data
    I.display(D.rho[i], x1 = D.x1r, x2 = D.x2r, ax = I.ax[i], cmap = 'inferno',
              title = rf'$\tau = ${D.timelist[i]:.1f}', xtitle = 'x',
              ytitle = ylab[i], aspect = 'equal', ytickslabels = ytcl[i],
              xticks = [-0.4,-0.2,0,0.2,0.4])

# Placing the colorbar
I.colorbar(axs = I.ax[0], cax = I.ax[-1])

# Saving the image
I.savefig('test03_rti.png')
pp.show()
