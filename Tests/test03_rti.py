'''
Authors:

        D. Crocco
        G. Mattia
'''

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
ax = I.create_axes(ncol = 4, wratio = [1,1,1,0.2], wspace = [0.005,0.005,0.005])

# Customizing y labels and y ticks labels
ylab = ['y', None, None]
ytcl = ['Default', None, None]

# Loop over the different outputs
for i in [0,1,2]:
    # Plotting the data
    I.display(D.rho[i], x1 = D.x1r, x2 = D.x2r, ax = ax[i], 
              title = r'$\tau = $' + str(round(D.timelist[i],i%2)), cmap = 'inferno', xtitle = 'x',
              ytitle = ylab[i], aspect = 'equal', ytickslabels = ytcl[i], 
              xticks = [-0.4,-0.2,0,0.2,0.4])

# Placing the colorbar
I.colorbar(axs = ax[0], cax = ax[-1])

# Saving the image
pp.savefig('test03_rti.png')
pp.show()
