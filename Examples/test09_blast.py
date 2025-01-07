"""
MHD Blast test (configuration 9)

This test shows how to plot different quantities with customized legends in two
different subplots refering to initial and final time data.

The package "os" is loaded to create the path to the directory
$PLUTO_DIR/Test_Problems/MHD/Blast, where the MHD Blast test problem is located.

The data is loaded twice into a pload object D and the Image class is created.
The slices method is used to obtain a slice of the desired quantity along the
diagonals of the domain. The plot method and the legend method are then used
to plot an highly informative plot of density and pression with customized
legend labels. The image is then saved and shown on screen.
"""

# Loading the relevant packages
import pyPLUTO as pp
import os
import numpy as np

# Transforming the magnetic field components from polar to cartesian coordinates
def cart_vec(Bx1,Bx2,x1,x2):
    Bx = Bx1*np.sin(x2) + Bx2*np.cos(x2)
    Bz = Bx1*np.cos(x2) - Bx2*np.sin(x2)
    return Bx, Bz

# Creating the path for the data directory
plutodir = os.environ['PLUTO_DIR']
wdir     = plutodir + '/Test_Problems/MHD/Blast'

# Creating the Image, the subplot axes and defining the colors of the lines
I = pp.Image(suptitle = 'Test 09 - MHD Blast test')
I.create_axes(ncol = 2)
col = I.color[:2]

# Loading the initial data into a pload object D
D = pp.Load(0, path = wdir)

# Plotting the data in the first subplot
varM = D.slices(D.rho, diag = True)
varm = D.slices(D.rho, diag = 'min')

I.plot(D.x1*np.sqrt(2), varM,
                        c = col[0],
                        ax = 0,
                        label = r"$\rho$",
                        legpos = 2,
                        legsize = 13)

I.plot(D.x1*np.sqrt(2), varm,
                        c = col[0],
                        ax = 0,
                        ls = '--',
                        yrange = [0.1,200])

varM = D.slices(D.prs, diag = True)
varm = D.slices(D.prs, diag = 'min')

I.plot(D.x1*np.sqrt(2), varM,
                        c = col[1],
                        ax = 0,
                        yscale = 'log',
                        label = r"$p$")

I.plot(D.x1*np.sqrt(2), varm,
                        c = col[1],
                        ax = 0,
                        ls = '--',
                        xtitle = r'$x$',
                        title = "t = 0.0 s")

I.legend(ax = 0, legpos = 1, label = ['M','m'], ls = ['-','--'])

# Overwrite the final data into the pload object D
D = pp.Load(path = wdir)

# Plotting the data in the second subplot
varM = D.slices(D.prs, diag = True)
varm = D.slices(D.prs, diag = 'min')

I.plot(D.x1*np.sqrt(2), varM,
                        c = col[1],
                        ax = 1,
                        yscale = 'log',
                        label = r"$p$")

I.plot(D.x1*np.sqrt(2), varm,
                        c = col[1],
                        ax = 1,
                        ls = '--',
                        xtitle = r'$x$',
                        title = "t = 0.01 s")

varM = D.slices(D.rho, diag = True)
varm = D.slices(D.rho, diag = 'min')

I.plot(D.x1*np.sqrt(2), varM,
                        c = col[0],
                        ax = 1,
                        label = r"$\rho$",
                        legpos = 2,
                        legsize = 13)

I.plot(D.x1*np.sqrt(2), varm,
                        c = col[0],
                        ax = 1,
                        ls = '--',
                        yrange = [0.1,200])

I.legend(ax = 1, legpos = 1, label = ['m','M'], ls = ['--','-'])

# Saving the image and showing the plot
I.savefig('test09_blast.png')
pp.show()
