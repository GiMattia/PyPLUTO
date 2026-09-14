"""Test of the colorbar.py file."""

import numpy as np
import numpy.testing as npt
import pytest

import pyPLUTO as pp
from pyPLUTO.imagefuncs.colorbar import ColorbarManager

x = np.linspace(-1, 1, 20)
x2d, y2d = np.meshgrid(x, x, indexing="ij")
var = x2d**2 + y2d**2


def _image():
    Image = pp.Image()
    Image.display(var, x1=x, x2=x)
    return Image


# A colorbar adds a new axis to the figure
@pytest.mark.parametrize("cpos", ["right", "left", "top", "bottom"])
def test_colorbar_positions(cpos):
    Image = _image()
    Image.colorbar(cpos=cpos)
    assert len(Image.fig.axes) == 2


# Without a position the colorbar defaults to the right side
def test_colorbar_default_position():
    Image = _image()
    Image.colorbar()
    assert len(Image.fig.axes) == 2


# The label is written next to the colorbar
def test_colorbar_label():
    Image = _image()
    Image.colorbar(cpos="right", clabel="rho")
    assert Image.fig.axes[-1].get_ylabel() == "rho"


# The requested ticks are the ones drawn on the colorbar
def test_colorbar_ticks():
    Image = _image()
    Image.colorbar(cpos="right", cticks=[0.0, 1.0, 2.0])
    npt.assert_allclose(Image.fig.axes[-1].get_yticks(), [0.0, 1.0, 2.0])


# The colorbar can be built from a given collection
def test_colorbar_from_collection():
    Image = _image()
    Image.colorbar(pcm=Image.ax[0].collections[0], cpos="right")
    assert len(Image.fig.axes) == 2


# The axis of a collection is the one the collection was drawn on
def test_find_ax_from_collection():
    Image = _image()
    manager = ColorbarManager(Image.state)
    assert manager._find_ax(pcm=Image.ax[0].collections[0]) is Image.ax[0]


# Without a collection the last used axis is taken
def test_find_ax_default():
    Image = _image()
    manager = ColorbarManager(Image.state)
    assert manager._find_ax() is Image.ax[0]


# An axis can be selected by its index
def test_find_ax_by_index():
    Image = pp.Image()
    Image.create_axes(ncol=2)
    manager = ColorbarManager(Image.state)
    assert manager._find_ax(axs=1) is Image.ax[1]
