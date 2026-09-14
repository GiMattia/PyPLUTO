"""Test of the range.py file."""

import numpy as np
import pytest

import pyPLUTO as pp
from pyPLUTO.imagefuncs.range import RangeManager

x = np.linspace(0.0, 1.0, 20)
y = np.linspace(1.0, 2.0, 20)


def _manager():
    Image = pp.Image()
    return RangeManager(Image.state), Image


# On a linear scale the range is padded on both sides
def test_range_offset_linear():
    manager, _ = _manager()
    ymin, ymax = manager.range_offset(0.0, 1.0, "linear")
    assert ymin < 0.0
    assert ymax > 1.0


# The margin controls how much padding is added
def test_range_offset_margin():
    manager, _ = _manager()
    small = manager.range_offset(0.0, 1.0, "linear", margin=0.01)
    large = manager.range_offset(0.0, 1.0, "linear", margin=0.5)
    assert large[0] < small[0]
    assert large[1] > small[1]


# A logarithmic scale never pads below zero
def test_range_offset_log():
    manager, _ = _manager()
    ymin, _ = manager.range_offset(1.0, 10.0, "log")
    assert ymin > 0.0


# A negative range on a logarithmic scale warns
def test_range_offset_log_negative():
    manager, _ = _manager()
    with pytest.warns(UserWarning, match="Negative range"):
        manager.range_offset(-1.0, 10.0, "log")


# A zero-width range is still given some padding
def test_range_offset_zero_width():
    manager, _ = _manager()
    ymin, ymax = manager.range_offset(1.0, 1.0, "linear")
    assert ymin < ymax


# The symlog scale is padded like the linear one
def test_range_offset_symlog():
    manager, _ = _manager()
    ymin, ymax = manager.range_offset(0.0, 1.0, "symlog")
    assert ymin < 0.0
    assert ymax > 1.0


# An explicit x-range is applied to the axis
def test_set_xrange():
    _, Image = _manager()
    Image.plot(x, y)
    Image.set_axis(xrange=[0.0, 2.0])
    assert Image.ax[0].get_xlim() == pytest.approx((0.0, 2.0))


# An explicit y-range is applied to the axis
def test_set_yrange():
    _, Image = _manager()
    Image.plot(x, y)
    Image.set_axis(yrange=[0.0, 3.0])
    assert Image.ax[0].get_ylim() == pytest.approx((0.0, 3.0))


# Without an explicit range the data is still fully inside the axis
def test_automatic_range_contains_data():
    _, Image = _manager()
    Image.plot(x, y)
    xmin, xmax = Image.ax[0].get_xlim()
    assert xmin <= x.min()
    assert xmax >= x.max()
