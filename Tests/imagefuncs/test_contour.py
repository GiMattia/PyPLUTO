"""Test of the contour.py file."""

import numpy as np
import pytest
from matplotlib.contour import QuadContourSet

import pyPLUTO as pp

# A simple bowl-shaped function, whose contours are circles
x = np.linspace(-1, 1, 30)
y = np.linspace(-1, 1, 30)
x2d, y2d = np.meshgrid(x, y, indexing="ij")
var = x2d**2 + y2d**2


# A contour plot returns the set of contour lines
def test_contour_returns_contourset():
    Image = pp.Image()
    lines = Image.contour(var, x1=x, x2=y)
    assert isinstance(lines, QuadContourSet)


# The contours are drawn on the current axis
def test_contour_draws_on_axis():
    Image = pp.Image()
    Image.contour(var, x1=x, x2=y)
    assert len(Image.ax[0].collections) > 0


# The requested levels are the ones that get drawn
def test_contour_explicit_levels():
    Image = pp.Image()
    lines = Image.contour(var, x1=x, x2=y, levels=[0.25, 0.5, 0.75])
    assert list(lines.levels) == [0.25, 0.5, 0.75]


# The number of levels is a hint: asking for more really gives more
def test_contour_number_of_levels():
    few = pp.Image().contour(var, x1=x, x2=y, levels=3)
    many = pp.Image().contour(var, x1=x, x2=y, levels=20)
    assert len(many.levels) > len(few.levels)


# The levels are increasing and stay inside the data range
def test_contour_levels_are_ordered():
    lines = pp.Image().contour(var, x1=x, x2=y, levels=8)
    assert list(lines.levels) == sorted(lines.levels)
    assert lines.levels[0] <= var.min()
    assert lines.levels[-1] >= var.max()


# The title keyword is forwarded to the axis
def test_contour_title():
    Image = pp.Image()
    Image.contour(var, x1=x, x2=y, title="bowl")
    assert Image.ax[0].get_title() == "bowl"


# The axis labels are forwarded as well
def test_contour_labels():
    Image = pp.Image()
    Image.contour(var, x1=x, x2=y, xtitle="xx", ytitle="yy")
    assert Image.ax[0].get_xlabel() == "xx"
    assert Image.ax[0].get_ylabel() == "yy"


# The axis range follows the given coordinates
def test_contour_axis_range():
    Image = pp.Image()
    Image.contour(var, x1=x, x2=y)
    assert Image.ax[0].get_xlim() == pytest.approx((-1.0, 1.0))


# A colormap can be chosen
def test_contour_cmap():
    Image = pp.Image()
    lines = Image.contour(var, x1=x, x2=y, cmap="magma")
    assert lines.get_cmap().name == "magma"


# The plot can be sent to a chosen axis of a multi-panel figure
def test_contour_on_second_axis():
    Image = pp.Image()
    Image.create_axes(ncol=2)
    Image.contour(var, x1=x, x2=y, ax=1)
    assert len(Image.ax[1].collections) > 0
