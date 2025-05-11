import numpy as np
import numpy.testing as npt
import pyPLUTO as pp

x = np.linspace(-1, 1, 101)
y = np.linspace(-1, 1, 101)
xr = np.linspace(-1.01, 1.01, 102)
yr = np.linspace(-1.01, 1.01, 102)

x2d, y2d = np.meshgrid(x, y, indexing="ij")
x2dr, y2dr = np.meshgrid(xr, yr)
var = 1 / ((x2d**2 + y2d**2) / 2 + 1)


# Simple plot
def test_simple_display():
    Image = pp.Image(withblack=True)
    Image.display(var, cpos="right", cmap="magma", x1=x, x2=y)
    pcm = Image.ax[0].collections[0]
    ccd = pcm.get_coordinates()
    xc, _ = ccd[:, :, 0], ccd[:, :, 1]
    pcm = pcm.get_array()
    npt.assert_array_equal(pcm, var)
    npt.assert_allclose(xc, x2dr, atol=1.0e-13)


"""
line = I.ax[0].get_lines()[0]
assert (line.get_xdata() == np.linspace(0,len(y)-1,len(y))).all()
assert (line.get_ydata() == y).all()
assert line.get_color()  == '#000000'
assert line.get_lw()     == 1.3
assert line.get_ls()     == '-'

# Simple plot with x-values
I = pp.Image()
I.plot(x,y)
line = I.ax[0].get_lines()[0]
assert (line.get_xdata() == x).all()
assert (line.get_ydata() == y).all()

# Title and labels
I = pp.Image()
I.plot(x,y, title = 'this is a title', xtitle = 'x', ytitle = 'y')
assert I.ax[0].get_title() == 'this is a title'
assert I.ax[0].get_xlabel() == 'x'
assert I.ax[0].get_ylabel() == 'y'

# x range
I = pp.Image()
I.plot(x,y, title = 'this is a title', xrange = [0.2,0.4])
xlim = I.ax[0].get_xlim()
assert np.isclose(xlim[0],0.2)
assert np.isclose(xlim[1],0.4)

# x range and y range
I = pp.Image()
I.plot(x,y, title = 'this is a title', xrange = [0.2,0.4], yrange = [-1,0])
xlim = I.ax[0].get_xlim()
assert np.isclose(xlim[0],0.2)
assert np.isclose(xlim[1],0.4)
ylim = I.ax[0].get_ylim()
assert np.isclose(ylim[0],-1)
assert np.isclose(ylim[1],0)

# plot from create_axes
I = pp.Image()
ax = I.create_axes(ncol = 1, nrow = 3, hspace = [0.2,0.1], hratio = [1,2,1])
I.plot(x,y, ax = ax[1])
line = ax[1].get_lines()[0]
assert (line.get_xdata() == x).all()
assert (line.get_ydata() == y).all()

# different line parameters
I = pp.Image()
I.plot(x,y, ls = '--', lw = 0.5, c = 'r')
line = I.ax[0].get_lines()[0]
assert line.get_color() == 'r'
assert line.get_ls()    == '--'
assert line.get_lw()    == 0.5

# different marker parameters
I = pp.Image()
I.plot(x,y, marker = 'o', ms = 5.0)
line = I.ax[0].get_lines()[0]
assert line.get_marker() == 'o'
assert line.get_ms()     == 5.0

# multiple lines
I = pp.Image()
I.plot(x,y)
I.plot(x,z)
line = I.ax[0].get_lines()[0]
assert (line.get_xdata() == x).all()
assert (line.get_ydata() == y).all()
line = I.ax[0].get_lines()[1]
assert (line.get_xdata() == x).all()
assert (line.get_ydata() == z).all()

# legend
I = pp.Image()
I.plot(x,y, label = 'rho', legpos = 0, legcols = 2)
I.plot(x,z, label = 'rho')
assert I.ax[0].get_legend()._ncols == 2

"""
