# Loading the relevant packages
import pyPLUTO as pp
import numpy as np
import os
import matplotlib.pyplot as plt

# Creating the path for the data directory
plutodir = os.environ['PLUTO_DIR']
wdir     = plutodir + '/Test_Problems/Particles/CR/Xpoint'

Df = pp.Load(path = wdir)
Dp = pp.LoadPart(path = wdir)
gl = (1 + Dp.vx1**2 + Dp.vx2**2 + Dp.vx3**2)**0.5

indx = np.argsort(gl)

#print(f"Particles found: {len(indx)}/{Dp.npart}")
I = pp.Image(figsize = [7,7], fontsize = 20)

I.contour(Df.Ax3, x1 = Df.x1, x2 = Df.x2, levels = 20, aspect = 'equal')
I.scatter(Dp.x1[indx], Dp.x2[indx], cpos = 'right',vmin = 0, vmax = 40,
          xrange = [-3500,3500], yrange = [-3500,3500],
          cmap = plt.get_cmap('YlOrRd',8), c = gl[indx], ms = 10)

ax = I.create_axes(left = 0.35, right = 0.7, bottom = 0.2, top = 0.4)

Dp = pp.LoadPart(0, path = wdir)
gl = (1 + Dp.vx1**2 + Dp.vx2**2 + Dp.vx3**2)**0.5
hist, bins = Dp.spectrum(gl, density = False)
I.plot(bins, hist, ax = 1, yscale = 'log', xscale = 'log', xrange = [1,50], yrange = [1,1.e8], label = "t = 0", fontsize = 15)
Dp = pp.LoadPart(100, path = wdir)
gl = (1 + Dp.vx1**2 + Dp.vx2**2 + Dp.vx3**2)**0.5
hist, bins = Dp.spectrum(gl, density = False)
I.plot(bins, hist, ax = 1, yscale = 'log', xscale = 'log', xrange = [1,50], yrange = [1,1.e8], label = "t = 100", legpos = 0, legsize = 13, legalpha = 0.25)
I.ax[1].patch.set_alpha(0.75)

I.savefig('test11_xpoint.png')
pp.show()
