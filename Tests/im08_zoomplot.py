import pyPLUTO    as pp
import matplotlib as mpl
import numpy      as np

print(f"Testing the zoom creation... ".ljust(50), end='')

x = np.linspace(0,1,101)
y = np.linspace(1,10,101)
z = np.logspace(0,1,101)

# Check the default options of the inset zoom
I  = pp.Image()
ax = I.create_axes(left = 0.2, right = 0.8, top = 0.85, bottom = 0.05)
I.plot(x,y, ax = ax)
I.plot(x,z, ax = ax)
I.zoom()
pos0    = I.ax[0].get_position().bounds
pos1    = I.ax[1].get_position().bounds
posleft = pos0[0] + 0.6*pos0[2]
posbot  = pos0[1] + 0.6*pos0[3]
width   = 0.2*pos0[2]
height  = 0.15*pos0[3]
line1    = I.ax[1].get_lines()[0]
line2    = I.ax[1].get_lines()[1]
assert len(I.ax) == 2
assert np.isclose(pos1[0],posleft)
assert np.isclose(pos1[1],posbot)
assert np.isclose(pos1[2],width)
assert np.isclose(pos1[3],height)
assert (line1.get_xdata() == x).all()
assert (line1.get_ydata() == y).all()
assert (line2.get_xdata() == x).all()
assert (line2.get_ydata() == z).all()

# Check the custom position (loc) of the inset zoom
I  = pp.Image()
ax = I.create_axes(left = 0.2, right = 0.8, top = 0.85, bottom = 0.05)
I.plot(x,y, ax = ax)
I.zoom(left = 0.2, bottom = 0.1, height = 0.3, width = 0.4)
pos0 = I.ax[0].get_position().bounds
pos1 = I.ax[1].get_position().bounds
posleft = pos0[0] + 0.2*pos0[2]
posbot  = pos0[1] + 0.1*pos0[3]
width   = 0.4*pos0[2]
height  = 0.3*pos0[3]
assert len(I.ax) == 2
assert np.isclose(pos1[0],posleft)
assert np.isclose(pos1[1],posbot)
assert np.isclose(pos1[2],width)
assert np.isclose(pos1[3],height)

# Check the custom position (pos) of the inset zoom
I  = pp.Image()
ax = I.create_axes(left = 0.2, right = 0.8, top = 0.85, bottom = 0.05)
I.plot(x,y, ax = ax)
I.zoom(pos = [0.25,0.6,0.15,0.4])
pos0 = I.ax[0].get_position().bounds
pos1 = I.ax[1].get_position().bounds
posleft = pos0[0] + 0.25*pos0[2]
posbot  = pos0[1] + 0.15*pos0[3]
width   = 0.35*pos0[2]
height  = 0.25*pos0[3]
assert len(I.ax) == 2
assert np.isclose(pos1[0],posleft)
assert np.isclose(pos1[1],posbot)
assert np.isclose(pos1[2],width)
assert np.isclose(pos1[3],height)

# Check axes properties
I  = pp.Image()
ax = I.create_axes(left = 0.2, right = 0.8, top = 0.85, bottom = 0.05)
I.plot(x,y, ax = ax)
I.zoom(title = 'Inset zoom',xtitle = 'x', ytitle = 'y', yticks = [0,0.2,1.0])
x0, y0 = I.ax[1].get_xticks(), I.ax[1].get_yticks()
assert I.ax[1].get_title()  == 'Inset zoom'
assert I.ax[1].get_xlabel() == 'x'
assert I.ax[1].get_ylabel() == 'y'
assert len(x0) == 0
assert (y0  == [0,0.2,1.0]).all()

# Check range properties
I  = pp.Image()
ax = I.create_axes(left = 0.2, right = 0.8, top = 0.85, bottom = 0.05)
I.plot(x,y, ax = ax)
I.zoom(xrange = [0.2,0.5],yrange = [0.3,0.7])
xlim = I.ax[1].get_xlim()
ylim = I.ax[1].get_ylim()
assert np.isclose(xlim[0],0.2)
assert np.isclose(xlim[1],0.5)
assert np.isclose(ylim[0],0.3)
assert np.isclose(ylim[1],0.7)

print("\033[34mPASSED!\033[0m")
