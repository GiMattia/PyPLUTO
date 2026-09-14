"""Test of the gridplot.py file."""

from pathlib import Path

import numpy as np
import numpy.testing as npt
import pytest

import pyPLUTO as pp
from pyPLUTO.imagefuncs.gridplot import _to_cartesian

x1 = np.linspace(1.0, 2.0, 5)
x2 = np.linspace(0.0, np.pi / 2, 4)


# One line is drawn per grid coordinate in each direction
def test_showgrid_line_count():
    Image = pp.Image()
    Image.showgrid(x1=x1, x2=x2)
    assert len(Image.ax[0].get_lines()) == len(x1) + len(x2)


# The everyx and everyy keywords thin out the grid
def test_showgrid_every():
    Image = pp.Image()
    Image.showgrid(x1=x1, x2=x2, everyx=2, everyy=2)
    assert len(Image.ax[0].get_lines()) < len(x1) + len(x2)


# The grid can be taken directly from a loaded dataset
def test_showgrid_from_data(data_dir: Path):
    Data = pp.Load(path=data_dir / "single_file", text=False)
    Image = pp.Image()
    Image.showgrid(data=Data)
    assert len(Image.ax[0].get_lines()) == len(Data.x1r) + len(Data.x2r)


# The color of the grid lines can be chosen
def test_showgrid_color():
    Image = pp.Image()
    Image.showgrid(x1=x1, x2=x2, c="red")
    assert Image.ax[0].get_lines()[0].get_color() == "red"


# The linewidth of the grid lines can be chosen
def test_showgrid_linewidth():
    Image = pp.Image()
    Image.showgrid(x1=x1, x2=x2, lw=2.0)
    assert Image.ax[0].get_lines()[0].get_lw() == 2.0


# Every supported geometry draws one line per grid coordinate
@pytest.mark.parametrize(
    "geom", ["CARTESIAN", "POLAR", "CYLINDRICAL", "SPHERICAL"]
)
def test_showgrid_geometries(geom):
    Image = pp.Image()
    Image.showgrid(x1=x1, x2=x2, geom=geom)
    assert len(Image.ax[0].get_lines()) == len(x1) + len(x2)


# In polar geometry a constant-x1 line is an arc at that radius
def test_showgrid_polar_line_is_an_arc():
    Image = pp.Image()
    Image.showgrid(x1=x1, x2=x2, geom="POLAR")
    line = Image.ax[0].get_lines()[0]
    radius = np.hypot(line.get_xdata(), line.get_ydata())
    npt.assert_allclose(radius, x1[0])


# Missing coordinates are an error
def test_showgrid_without_coordinates():
    Image = pp.Image()
    with pytest.raises(ValueError, match="cannot be None"):
        Image.showgrid()


# An unknown geometry is an error
def test_showgrid_wrong_geometry():
    Image = pp.Image()
    with pytest.raises(ValueError, match="Unsupported geometry"):
        Image.showgrid(x1=x1, x2=x2, geom="WRONG")


# Cartesian coordinates are returned unchanged
def test_to_cartesian_cartesian():
    xx, yy = _to_cartesian(x1, x2, "CARTESIAN")
    npt.assert_array_equal(xx, x1)
    npt.assert_array_equal(yy, x2)


# In polar geometry the coordinates are a radius and an angle
def test_to_cartesian_polar():
    xx, yy = _to_cartesian(np.array([2.0]), np.array([0.0]), "POLAR")
    npt.assert_allclose(xx, [2.0])
    npt.assert_allclose(yy, [0.0], atol=1e-15)


# In spherical geometry the angle is measured from the vertical axis
def test_to_cartesian_spherical():
    xx, yy = _to_cartesian(np.array([2.0]), np.array([0.0]), "SPHERICAL")
    npt.assert_allclose(xx, [0.0], atol=1e-15)
    npt.assert_allclose(yy, [2.0])


# An unknown geometry cannot be converted
def test_to_cartesian_wrong_geometry():
    with pytest.raises(ValueError, match="Unsupported geometry"):
        _to_cartesian(x1, x2, "WRONG")
