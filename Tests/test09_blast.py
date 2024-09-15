"""

"""

import pyPLUTO as pp
import os
import numpy as np

def cart_vec(Bx1,Bx2,x1,x2):
    Bx = Bx1*np.sin(x2) + Bx2*np.cos(x2)
    Bz = Bx1*np.cos(x2) - Bx2*np.sin(x2)
    return Bx,Bz


# Creating the path for the data directory
plutodir = os.environ['PLUTO_DIR']
wdir     = plutodir+'/Test_Problems/MHD/Blast'

I = pp.Image()
I.create_axes(ncol = 2)
col = I.color[:2]

D = pp.Load(0, path = wdir)

varM = D.slices(D.rho, diag = True)
varm = D.slices(D.rho, diag = 'min')
I.plot(D.x1*np.sqrt(2),varM, c = col[0], ax = 0, label = r"$\rho$", legpos = 2, legsize = 13)
I.plot(D.x1*np.sqrt(2),varm, c = col[0], ax = 0, ls = '--', yrange = [0.1,200])

varM = D.slices(D.prs, diag = True)
varm = D.slices(D.prs, diag = 'min')
I.plot(D.x1*np.sqrt(2),varM, c = col[1], ax = 0, yscale = 'log', label = r"$p$")
I.plot(D.x1*np.sqrt(2),varm, c = col[1], ax = 0, ls = '--', xtitle = r'$x$', title = "t = 0.0 s")

I.legend(legpos = 1, label = ['M','m'], ls = ['-','--'], ax = 0)

D = pp.Load(path = wdir)

varM = D.slices(D.prs, diag = True)
varm = D.slices(D.prs, diag = 'min')
I.plot(D.x1*np.sqrt(2),varM, c = col[1], ax = 1, yscale = 'log', label = r"$p$")
I.plot(D.x1*np.sqrt(2),varm, c = col[1], ax = 1, ls = '--', xtitle = r'$x$', title = "t = 0.01 s")

varM = D.slices(D.rho, diag = True)
varm = D.slices(D.rho, diag = 'min')
I.plot(D.x1*np.sqrt(2),varM, c = col[0], ax = 1, label = r"$\rho$", legpos = 2, legsize = 13)
I.plot(D.x1*np.sqrt(2),varm, c = col[0], ax = 1, ls = '--', yrange = [0.1,200])

I.legend(legpos = 1, label = ['m','M'], ls = ['--','-'], ax = 1)

I.savefig('test09_blast.png')
pp.show()
