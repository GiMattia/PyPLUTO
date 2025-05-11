import numpy as np
import numpy.testing as npt
import pyPLUTO as pp

x = np.linspace(0, 1, 101)
y = np.linspace(1, 10, 101)
z = np.logspace(0, 1, 101)


# Simple plot without x-values
def test_plot_noxvalues():
    Image = pp.Image(withblack=True)
    Image.plot(y)
    line = Image.ax[0].get_lines()[0]
    npt.assert_array_equal(line.get_xdata(), np.linspace(0, len(y) - 1, len(y)))
    npt.assert_array_equal(line.get_ydata(), y)
    assert line.get_color() == "#000000"
    assert line.get_lw() == 1.3
    assert line.get_ls() == "-"


# Simple plot with x-values
def test_easyplot():
    Image = pp.Image()
    Image.plot(x, y)
    line = Image.ax[0].get_lines()[0]
    npt.assert_array_equal(line.get_xdata(), x)
    npt.assert_array_equal(line.get_ydata(), y)


# Title and labels
def test_title_labels():
    Image = pp.Image()
    Image.plot(x, y, title="this is a title", xtitle="x", ytitle="y")
    assert Image.ax[0].get_title() == "this is a title"
    assert Image.ax[0].get_xlabel() == "x"
    assert Image.ax[0].get_ylabel() == "y"


# x range
def test_xrange():
    Image = pp.Image()
    Image.plot(x, y, title="this is a title", xrange=[0.2, 0.4])
    xlim = Image.ax[0].get_xlim()
    assert np.isclose(xlim[0], 0.2)
    assert np.isclose(xlim[1], 0.4)


# x range and y range
def test_ranges():
    Image = pp.Image()
    Image.plot(x, y, title="this is a title", xrange=[0.2, 0.4], yrange=[-1, 0])
    xlim = Image.ax[0].get_xlim()
    assert np.isclose(xlim[0], 0.2)
    assert np.isclose(xlim[1], 0.4)
    ylim = Image.ax[0].get_ylim()
    assert np.isclose(ylim[0], -1)
    assert np.isclose(ylim[1], 0)


# plot from create_axes
def test_create_axes():
    Image = pp.Image()
    ax = Image.create_axes(ncol=1, nrow=3, hspace=[0.2, 0.1], hratio=[1, 2, 1])
    Image.plot(x, y, ax=ax[1])
    line = ax[1].get_lines()[0]
    npt.assert_array_equal(line.get_xdata(), x)
    npt.assert_array_equal(line.get_ydata(), y)
    Image.plot(x, 2 * y, ax=2)
    line = ax[2].get_lines()[0]
    npt.assert_array_equal(line.get_xdata(), x)
    npt.assert_array_equal(line.get_ydata(), 2 * y)


# different line parameters
def test_line_parameters():
    Image = pp.Image()
    Image.plot(x, y, ls="--", lw=0.5, c="r")
    line = Image.ax[0].get_lines()[0]
    assert line.get_color() == "r"
    assert line.get_ls() == "--"
    assert line.get_lw() == 0.5


# different marker parameters
def test_markers():
    Image = pp.Image()
    Image.plot(x, y, marker="o", ms=5.0)
    line = Image.ax[0].get_lines()[0]
    assert line.get_marker() == "o"
    assert line.get_ms() == 5.0


# multiple lines
def test_multiple_lines():
    Image = pp.Image()
    Image.plot(x, y)
    Image.plot(x, z)
    line = Image.ax[0].get_lines()[0]
    npt.assert_array_equal(line.get_xdata(), x)
    npt.assert_array_equal(line.get_ydata(), y)
    line = Image.ax[0].get_lines()[1]
    npt.assert_array_equal(line.get_xdata(), x)
    npt.assert_array_equal(line.get_ydata(), z)


# legend
def test_legend():
    Image = pp.Image()
    Image.plot(x, y, label="rho", legpos=0, legcols=2)
    Image.plot(x, z, label="prs")
    assert Image.ax[0].get_legend()._ncols == 2
