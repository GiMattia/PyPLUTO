import numpy as np
import numpy.testing as npt
import pytest

import pyPLUTO as pp

x = np.linspace(0, 1, 101)
y = np.linspace(1, 10, 101)
z = np.logspace(0, 1, 101)


# Check the default options of the inset zoom
def test_default_zoom():
    Image = pp.Image()
    ax = Image.create_axes(left=0.2, right=0.8, top=0.85, bottom=0.05)
    Image.plot(x, y, ax=ax)
    Image.plot(x, z, ax=ax)
    Image.zoom()
    pos0 = Image.ax[0].get_position().bounds
    pos1 = Image.ax[1].get_position().bounds
    posleft = pos0[0] + 0.6 * pos0[2]
    posbot = pos0[1] + 0.6 * pos0[3]
    width = 0.15 * pos0[2]
    height = 0.15 * pos0[3]
    line1 = Image.ax[1].get_lines()[0]
    line2 = Image.ax[1].get_lines()[1]
    assert len(Image.ax) == 2
    assert np.isclose(pos1[0], posleft)
    assert np.isclose(pos1[1], posbot)
    assert np.isclose(pos1[2], width)
    assert np.isclose(pos1[3], height)
    npt.assert_array_equal(line1.get_xdata(), x)
    npt.assert_array_equal(line1.get_ydata(), y)
    npt.assert_array_equal(line2.get_xdata(), x)
    npt.assert_array_equal(line2.get_ydata(), z)


# Check the custom position (loc) of the inset zoom
def test_custom_loc():
    Image = pp.Image()
    ax = Image.create_axes(left=0.2, right=0.8, top=0.85, bottom=0.05)
    Image.plot(x, y, ax=ax)
    Image.zoom(left=0.2, bottom=0.1, height=0.3, width=0.4)
    pos0 = Image.ax[0].get_position().bounds
    pos1 = Image.ax[1].get_position().bounds
    posleft = pos0[0] + 0.2 * pos0[2]
    posbot = pos0[1] + 0.1 * pos0[3]
    width = 0.4 * pos0[2]
    height = 0.3 * pos0[3]
    assert len(Image.ax) == 2
    assert np.isclose(pos1[0], posleft)
    assert np.isclose(pos1[1], posbot)
    assert np.isclose(pos1[2], width)
    assert np.isclose(pos1[3], height)


# Check the custom position (pos) of the inset zoom
def test_cutom_pos():
    Image = pp.Image()
    ax = Image.create_axes(left=0.2, right=0.8, top=0.85, bottom=0.05)
    Image.plot(x, y, ax=ax)
    Image.zoom(pos=[0.25, 0.6, 0.15, 0.4])
    pos0 = Image.ax[0].get_position().bounds
    pos1 = Image.ax[1].get_position().bounds
    posleft = pos0[0] + 0.25 * pos0[2]
    posbot = pos0[1] + 0.15 * pos0[3]
    width = 0.35 * pos0[2]
    height = 0.25 * pos0[3]
    assert len(Image.ax) == 2
    assert np.isclose(pos1[0], posleft)
    assert np.isclose(pos1[1], posbot)
    assert np.isclose(pos1[2], width)
    assert np.isclose(pos1[3], height)


# Check axes properties
def test_axes_properties():
    Image = pp.Image()
    ax = Image.create_axes(left=0.2, right=0.8, top=0.85, bottom=0.05)
    Image.plot(x, y, ax=ax)
    Image.zoom(title="Inset zoom", xtitle="x", ytitle="y", yticks=[0, 0.2, 1.0])
    x0, y0 = Image.ax[1].get_xticks(), Image.ax[1].get_yticks()
    assert Image.ax[1].get_title() == "Inset zoom"
    assert Image.ax[1].get_xlabel() == "x"
    assert Image.ax[1].get_ylabel() == "y"
    assert len(x0) == 0
    npt.assert_array_equal(y0, [0, 0.2, 1.0])


# Check range properties
def test_range():
    Image = pp.Image()
    ax = Image.create_axes(left=0.2, right=0.8, top=0.85, bottom=0.05)
    Image.plot(x, y, ax=ax)
    Image.zoom(xrange=[0.2, 0.5], yrange=[0.3, 0.7])
    xlim = Image.ax[1].get_xlim()
    ylim = Image.ax[1].get_ylim()
    assert np.isclose(xlim[0], 0.2)
    assert np.isclose(xlim[1], 0.5)
    assert np.isclose(ylim[0], 0.3)
    assert np.isclose(ylim[1], 0.7)


# A zoom on a colormap redraws the same data inside the inset
def test_zoom_on_display():
    """LONG TEST: CHECK"""
    coord = np.linspace(-1.0, 1.0, 20)
    x2d, y2d = np.meshgrid(coord, coord, indexing="ij")
    var = x2d**2 + y2d**2

    Image = pp.Image()
    Image.display(var, x1=coord, x2=coord)
    axins = Image.zoom(
        xrange=[-0.5, 0.5], yrange=[-0.5, 0.5], pos=[0.6, 0.9, 0.6, 0.9]
    )

    assert len(axins.collections) == 1
    assert axins.get_xlim() == pytest.approx((-0.5, 0.5))
    assert axins.get_ylim() == pytest.approx((-0.5, 0.5))


# The inset keeps the colormap of the plot it zooms into
def test_zoom_on_display_keeps_cmap():
    coord = np.linspace(-1.0, 1.0, 20)
    x2d, y2d = np.meshgrid(coord, coord, indexing="ij")

    Image = pp.Image()
    Image.display(x2d**2 + y2d**2, x1=coord, x2=coord, cmap="magma")
    axins = Image.zoom(xrange=[-0.5, 0.5], yrange=[-0.5, 0.5])

    assert axins.collections[0].get_cmap().name == "magma"


# A zoom of an empty axis gives an empty inset rather than an error
def test_zoom_on_empty_axis():
    Image = pp.Image()
    Image.create_axes()
    axins = Image.zoom(xrange=[0.0, 1.0], yrange=[0.0, 1.0])
    assert axins.get_lines() == []
    assert list(axins.collections) == []
