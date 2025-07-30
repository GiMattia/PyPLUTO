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
