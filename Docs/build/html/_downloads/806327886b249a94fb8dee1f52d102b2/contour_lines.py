"""
The colorbar of contour lines
=============================

Contour lines get a continuous colorbar on their color scale, as a map does.
With ``fillmap=False`` the colorbar is matplotlib's own instead, with a line
at each level.
"""

import numpy as np

import pyPLUTO

# A bowl on a square grid: 0 at the center, 2 in the corners
x1 = np.linspace(-1.0, 1.0, 64)
x2 = np.linspace(-1.0, 1.0, 64)
bowl = x1[:, None] ** 2 + x2[None, :] ** 2

Image = pyPLUTO.Image(figsize=[11, 5])
Image.create_axes(ncol=2)

# The default: a continuous colorbar
Image.contour(
    bowl,
    x1=x1,
    x2=x2,
    ax=0,
    levels=8,
    title="fillmap=True",
    xtitle="x",
    ytitle="y",
)
Image.colorbar(axs=0, clabel=r"$\rho$")

# A line at each level
Image.contour(
    bowl,
    x1=x1,
    x2=x2,
    ax=1,
    levels=8,
    title="fillmap=False",
    xtitle="x",
    ytitle="y",
)
Image.colorbar(axs=1, clabel=r"$\rho$", fillmap=False)
