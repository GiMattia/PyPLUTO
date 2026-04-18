"""Test of the display.py file."""

from typing import cast

import numpy as np
import numpy.testing as npt
import numpy.typing as nptp
from matplotlib.collections import QuadMesh

import pyPLUTO as pp

x = np.linspace(-1, 1, 101)
y = np.linspace(-1, 1, 101)
xr = np.linspace(-1.01, 1.01, 102)
yr = np.linspace(-1.01, 1.01, 102)

x2d, y2d = np.meshgrid(x, y, indexing="ij")
x2dr, y2dr = np.meshgrid(xr, yr)
var = 1 / ((x2d**2 + y2d**2) / 2 + 1)


def test_simple_display() -> None:
    """Ensure that the display functionalities work correctly."""
    image = pp.Image(withblack=True)
    image.display(var, cpos="right", cmap="magma", x1=x, x2=y)

    pcm = image.ax[0].collections[0]
    assert isinstance(pcm, QuadMesh)

    ccd = cast(nptp.NDArray[np.float64], pcm.get_coordinates())
    xc = ccd[:, :, 0]
    arr = np.asarray(pcm.get_array())

    npt.assert_array_equal(arr, var)
    npt.assert_allclose(xc, x2dr, atol=1.0e-13)
