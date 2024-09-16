'''
CHange pluto.ini analysis to 0.05!!!
'''

import pyPLUTO as pp
import os
import numpy   as np

# Creating the path for the data directory
plutodir = os.environ['PLUTO_DIR']
wdir     = plutodir+'/Test_Problems/RMHD/KH'

# Loading the data into a pload object D.
D = pp.Load(path = wdir)

# Creating the Image and the subplot axes (in order to have two zoom simultaneously)
I = pp.Image(figsize = [10,10])
I.create_axes(ncol = 2, wratio = [1,0.1], wspace = [0.003], right = 0.55)
I.create_axes(nrow = 2, hspace = [0.003], left = 0.67)

# Plotting the data
I.display(D.rho, x1 = D.x1, x2 = D.x2, title = 'Density',
          ax = 0, shading = 'gouraud', xtitle = r'$x$', ytitle = r'$y$')
I.colorbar(axs = 0, cax = 1)

lines = D.find_fieldlines(D.Bx1, D.Bx2, x1 = D.x1, x2 = D.x2, y0 = [0.0,0.1,-0.1,0.2,-0.2], x0 = [0.55,0.0,0.0,0.0,0.0],
                          order = 'RK45', maxstep = 0.01, numsteps = 25000)

for _, line in enumerate(lines):
    I.plot(line[0],line[1],ax = 0, c = 'k')

data = np.genfromtxt(wdir+'/kh.dat', names=True)
analysis = {name: data[name] for name in data.dtype.names}

I.text(r"$\langle v_y^2\rangle$",  ax = 2, x = 0.05)
I.text(r"$v_{y, \mathrm{MAX}}^2$", ax = 3, x = 0.05)


I.plot(analysis['time'], analysis['vy2']  ,ax = 2, c = 'k', yscale = 'log', xtickslabels = None)
I.plot(analysis['time'], analysis['maxvy'],ax = 3, c = 'k', yscale = 'log', xtitle = r'$t$')


# Saving the image
I.savefig('test07_khi.png')
pp.show()
