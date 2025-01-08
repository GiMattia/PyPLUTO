import pyPLUTO    as pp
import matplotlib as mpl
import numpy      as np

print(f"Testing the axes creation... ".ljust(50), end='')

# Check the default values of the figure created in the __init__
I = pp.Image()
ax = I.create_axes()
nrow, ncol = I.fig.axes[0].get_subplotspec().get_gridspec().get_geometry()
assert ncol == 1
assert nrow == 1

# Change number of rows and columns
I = pp.Image()
ax = I.create_axes(ncol = 2, nrow = 3)
nrow, ncol = I.fig.axes[0].get_subplotspec().get_gridspec().get_geometry()
assert ncol    == 2
assert nrow    == 3
assert len(ax) == 6

# Add suptitle and change tight layout
I = pp.Image()
ax = I.create_axes(ncol = 2, nrow = 3, suptitle = 'this is title', tight = False)
assert I.fig._suptitle.get_text() == 'this is title'
assert I.fig.get_tight_layout()   == False

# Add different borders to the figure
I = pp.Image()
ax = I.create_axes(left = 0.2, right = 0.8, top = 0.85, bottom = 0.05)
assert I.fig.get_tight_layout()   == False
pos = ax.get_position().bounds
assert np.isclose(pos[0],0.2)
assert np.isclose(pos[1],0.05)
assert np.isclose(pos[2],0.6)
assert np.isclose(pos[3],0.8)

# Two columns custom
I = pp.Image()
ax = I.create_axes(ncol = 2, left = 0.15, right = 0.8, wspace = 0.2, wratio = [2,1])
pos = ax[0].get_position().bounds
assert np.isclose(pos[0],0.15)
assert np.isclose(pos[2],0.3)
pos = ax[1].get_position().bounds
assert np.isclose(pos[0],0.65)
assert np.isclose(pos[2],0.15)

# Multiple rows
I = pp.Image()
ax = I.create_axes(ncol = 1, nrow = 3, hspace = [0.2,0.1], hratio = [1,2,1])
pos = ax[0].get_position().bounds
assert np.isclose(pos[1],0.775)
assert np.isclose(pos[3],0.125)
pos = ax[1].get_position().bounds
assert np.isclose(pos[1],0.325)
assert np.isclose(pos[3],0.25)
pos = ax[2].get_position().bounds
assert np.isclose(pos[1],0.1)
assert np.isclose(pos[3],0.125)

# Multiple rows and columns
I = pp.Image()
ax = I.create_axes(ncol = 2, nrow = 3, left = 0.05, bottom = 0.05)
pos = ax[0].get_position().bounds
assert np.isclose(pos[0],0.05)
pos = ax[-1].get_position().bounds
assert np.isclose(pos[1],0.05)

# Suptitle and figsize
I = pp.Image(suptitle = 'This is a title',figsize = (6,7))
assert I.fig._suptitle.get_text() == 'This is a title'
assert I.fig.get_figwidth()  == 6
assert I.fig.get_figheight() == 7
ax = I.create_axes(suptitle = 'This is another title',figsize = (5,8))
assert I.fig._suptitle.get_text() == 'This is another title'
assert I.fig.get_figwidth()  == 5
assert I.fig.get_figheight() == 8

# Multiple create_axes
I = pp.Image()
ax = I.create_axes(left = 0.2, right = 0.5)
ax = I.create_axes(left = 0.6, right = 0.85)
assert len(ax) == 2
pos = ax[0].get_position().bounds
assert np.isclose(pos[0],0.2)
assert np.isclose(pos[2],0.3)
pos = ax[1].get_position().bounds
assert np.isclose(pos[0],0.6)
assert np.isclose(pos[2],0.25)

print(" ---> \033[32mPASSED!\033[0m")
