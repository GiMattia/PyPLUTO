import pyPLUTO    as pp
import matplotlib as mpl
import numpy      as np

print(f"Testing the axes customization... ".ljust(50), end='')

# Check the default values of the set_axes
I = pp.Image()
ax = I.create_axes()
I.set_axis()
assert ax.get_aspect() == 'auto'
xlim = ax.get_xlim()
assert np.isclose(xlim[0],0.0)
assert np.isclose(xlim[1],1.0)
ylim = ax.get_ylim()
assert np.isclose(ylim[0],0.0)
assert np.isclose(ylim[1],1.0)
assert ax.get_title()  == ''
assert ax.get_xlabel() == ''
assert ax.get_ylabel() == ''
assert ax.get_xscale() == 'linear'
assert ax.get_yscale() == 'linear'
assert ax.get_alpha()  == None

# Aspect ratio
I = pp.Image()
ax = I.create_axes()
I.set_axis(aspect = 'equal', fontsize = 20)
assert np.isclose(ax.get_aspect(),1.0)
assert I.fontsize == 20
I.set_axis(aspect = 2.0)
assert np.isclose(ax.get_aspect(),2.0)

# xrange and yrange
I = pp.Image()
ax = I.create_axes()
I.set_axis(xrange = [-1,1], yrange = [1,10])
xlim = ax.get_xlim()
assert np.isclose(xlim[0],-1.0)
assert np.isclose(xlim[1],1.0)
ylim = ax.get_ylim()
assert np.isclose(ylim[0],1.0)
assert np.isclose(ylim[1],10.0)

# labels
I = pp.Image()
ax = I.create_axes()
I.set_axis(title = 'this is a title', xtitle = 'x', ytitle = 'y')
assert ax.get_title() == 'this is a title'
assert ax.get_xlabel() == 'x'
assert ax.get_ylabel() == 'y'

# ticks
I = pp.Image()
ax = I.create_axes()
I.set_axis(xticks = [0,0.5,1], yticks = None)
x, y   = ax.get_xticks(), ax.get_yticks()
assert (x  == [0,0.5,1]).all()
assert len(y) == 0
I.set_axis(xticks = None, yticks = [0,0.2,1.0])
x, y   = ax.get_xticks(), ax.get_yticks()
assert len(x) == 0
assert (y  == [0,0.2,1.0]).all()

# tickslabels
I = pp.Image()
ax = I.create_axes()
yy = ['a','b','c']
I.set_axis(xticks = [0,0.5,1], yticks = [0,0.5,1], xtickslabels = None, ytickslabels = yy)
x, y   = ax.get_xticklabels(), ax.get_yticklabels()
for i in x:
    assert i.get_text() == ''
for i, j in enumerate(y):
    assert j.get_text() == yy[i]
I.set_axis(xticks = [0,0.5,1], yticks = [0,0.5,1], xtickslabels = yy, ytickslabels = None)
x, y   = ax.get_xticklabels(), ax.get_yticklabels()
for i, j in enumerate(x):
    assert j.get_text() == yy[i]
for i in y:
    assert i.get_text() == ''

# scales and alpha
I = pp.Image()
ax = I.create_axes()
I.set_axis(xscale = 'log', yscale = 'log', alpha = 0.5)
assert ax.get_xscale() == 'log'
assert ax.get_yscale() == 'log'
assert np.isclose(ax.get_alpha(),0.5)

print(" ---> \033[32mPASSED!\033[0m")
