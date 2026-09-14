"""Test of the scatter.py file."""

import numpy as np
import numpy.testing as npt
import pytest
from matplotlib.collections import PathCollection

import pyPLUTO as pp

x = np.linspace(0, 1, 20)
y = np.linspace(1, 2, 20)


# A scatter plot returns the collection of points
def test_scatter_returns_pathcollection():
    Image = pp.Image()
    points = Image.scatter(x, y)
    assert isinstance(points, PathCollection)


# Every point of the input is drawn
def test_scatter_point_positions():
    Image = pp.Image()
    points = Image.scatter(x, y)
    npt.assert_allclose(points.get_offsets()[:, 0], x)
    npt.assert_allclose(points.get_offsets()[:, 1], y)


# Lists are accepted as well as arrays
def test_scatter_accepts_lists():
    Image = pp.Image()
    points = Image.scatter([0.0, 1.0], [2.0, 3.0])
    assert points.get_offsets().shape == (2, 2)


# The marker size keyword is forwarded
def test_scatter_marker_size():
    Image = pp.Image()
    points = Image.scatter(x, y, ms=50)
    npt.assert_allclose(points.get_sizes(), 50)


# The opacity keyword is forwarded
def test_scatter_alpha():
    Image = pp.Image()
    points = Image.scatter(x, y, alpha=0.5)
    assert points.get_alpha() == 0.5


# The title keyword is forwarded to the axis
def test_scatter_title():
    Image = pp.Image()
    Image.scatter(x, y, title="points")
    assert Image.ax[0].get_title() == "points"


# The axis labels are forwarded as well
def test_scatter_labels():
    Image = pp.Image()
    Image.scatter(x, y, xtitle="xx", ytitle="yy")
    assert Image.ax[0].get_xlabel() == "xx"
    assert Image.ax[0].get_ylabel() == "yy"


# Explicit ranges are respected
def test_scatter_ranges():
    Image = pp.Image()
    Image.scatter(x, y, xrange=[0.0, 2.0], yrange=[0.0, 3.0])
    assert Image.ax[0].get_xlim() == pytest.approx((0.0, 2.0))
    assert Image.ax[0].get_ylim() == pytest.approx((0.0, 3.0))


# A logarithmic scale can be requested
def test_scatter_log_scale():
    Image = pp.Image()
    Image.scatter(x + 1.0, y, xscale="log")
    assert Image.ax[0].get_xscale() == "log"


# The plot can be sent to a chosen axis of a multi-panel figure
def test_scatter_on_second_axis():
    Image = pp.Image()
    Image.create_axes(ncol=2)
    Image.scatter(x, y, ax=1)
    assert len(Image.ax[1].collections) > 0
