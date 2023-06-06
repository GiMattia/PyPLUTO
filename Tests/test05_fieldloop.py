import pyPLUTO as pp
import numpy   as np

D  = pp.Load(0)
I  = pp.Image(figsize = [13,5])
T  = pp.Tools(D)
ax = I.create_axes(ncol = 2)
l  = np.linspace(5e-5,3e-4,9)

I.display(D.Bx1**2 + D.Bx2**2, ax = ax[0], cmap = 'hot_r', aspect = 'equal', x1 = D.x1, x2 = D.x2)
I.display(D.Bx1**2 + D.Bx2**2, ax = ax[1], cmap = 'hot_r', aspect = 'equal', x1 = D.x1, x2 = D.x2)
#ax[0].contour(D.x1,D.x2, D.Ax3.T, levels = l, colors = 'b',linewidths = 1.5)
lines = T.fieldlines(D.Bx1, D.Bx2, ax = ax[1], x1 = D.x1, x2 = D.x2, x0 = [0.15,0.25], y0 = [0.0,0.0], order = 'RK4')
print(len(lines))
#ax[1].streamplot(D.x1, D.x2, D.Bx1.T, D.Bx2.T, color = 'b', density = 1, minlength = 3)
I.plot(lines[0][0],lines[0][1],ax = ax[1], c = 'b')
I.plot(lines[1][0],lines[1][1],ax = ax[1], c = 'b')
pp.show()
