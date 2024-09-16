import pyPLUTO as pp
import numpy as np
import os

# Creating the path for the data directory
plutodir = os.environ['PLUTO_DIR']
wdir     = plutodir + '/Test_Problems/Particles/LP/Riemann_2D'

Df = pp.Load(path = wdir)
Dp = pp.LoadPart(path = wdir)
I = pp.Image(figsize= [9,8])
I.create_axes(right = 0.85)
I.create_axes(nrow = 2, left = 0.86, hspace = 0.01)

pcm = I.display(Df.rho, x1 = Df.x1, x2 = Df.x2, ax = 0, aspect = 'equal')
indx = np.argsort(Dp.vx1**2 + Dp.vx2**2 + Dp.vx3**2)

I.colorbar(pcm, cax = 1)
print(Dp.id[indx[::20]].min(),Dp.id[indx[::20]].max())
pcm = I.scatter(Dp.x1[indx[::20]], Dp.x2[indx[::20]], c = Dp.id[indx[::20]], cmap = 'Greys_r', ms = 10, ax = 0, vmin = 0)
I.colorbar(pcm, cax = 2)

pp.savefig('test12_riemannlp.png')
pp.show()
