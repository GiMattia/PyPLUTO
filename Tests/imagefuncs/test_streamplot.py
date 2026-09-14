"""Test of the streamplot.py file."""

import numpy as np
import numpy.testing as npt
import pytest
from matplotlib.collections import LineCollection

import pyPLUTO as pp

# A simple rotating vector field on a square grid
x = np.linspace(-1, 1, 20)
y = np.linspace(-1, 1, 20)
x2d, y2d = np.meshgrid(x, y, indexing="ij")
vx, vy = -y2d, x2d


# A streamplot returns the collection of streamlines
def test_streamplot_returns_linecollection():
    Image = pp.Image()
    lines = Image.streamplot(vx, vy, x1=x, x2=y)
    assert isinstance(lines, LineCollection)


# The streamlines are drawn on the current axis
def test_streamplot_draws_on_axis():
    Image = pp.Image()
    Image.streamplot(vx, vy, x1=x, x2=y)
    assert len(Image.ax[0].collections) > 0


# The axis range follows the given coordinates
def test_streamplot_axis_range():
    Image = pp.Image()
    Image.streamplot(vx, vy, x1=x, x2=y)
    assert Image.ax[0].get_xlim() == pytest.approx((-1.0, 1.0))


# The title keyword is forwarded to the axis
def test_streamplot_title():
    Image = pp.Image()
    Image.streamplot(vx, vy, x1=x, x2=y, title="stream")
    assert Image.ax[0].get_title() == "stream"


# The axis labels are forwarded as well
def test_streamplot_labels():
    Image = pp.Image()
    Image.streamplot(vx, vy, x1=x, x2=y, xtitle="xx", ytitle="yy")
    assert Image.ax[0].get_xlabel() == "xx"
    assert Image.ax[0].get_ylabel() == "yy"


# A higher density really does draw more streamline segments
def test_streamplot_density():
    sparse = pp.Image().streamplot(vx, vy, x1=x, x2=y, density=0.4)
    dense = pp.Image().streamplot(vx, vy, x1=x, x2=y, density=2.0)
    assert len(dense.get_segments()) > len(sparse.get_segments())


# An explicit color is applied to the streamlines
def test_streamplot_color():
    Image = pp.Image()
    lines = Image.streamplot(vx, vy, x1=x, x2=y, c="red")
    npt.assert_allclose(lines.get_color()[0], [1.0, 0.0, 0.0, 1.0])


# The plot can be sent to a chosen axis of a multi-panel figure
def test_streamplot_on_second_axis():
    Image = pp.Image()
    Image.create_axes(ncol=2)
    Image.streamplot(vx, vy, x1=x, x2=y, ax=1)
    assert len(Image.ax[1].collections) > 0
