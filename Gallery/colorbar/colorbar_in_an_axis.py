"""
A colorbar in an axis of its own
================================

``cax`` places the colorbar in an axis of the figure instead of cutting one
from the map: here a thin third column holds the bar shared by two maps on
the same scale.
"""

import numpy as np

import pyPLUTO

# A bowl on a square grid: 0 at the center, 2 in the corners
x1 = np.linspace(-1.0, 1.0, 64)
x2 = np.linspace(-1.0, 1.0, 64)
bowl = x1[:, None] ** 2 + x2[None, :] ** 2

Image = pyPLUTO.Image(figsize=[12, 5])
Image.create_axes(
    ncol=3, wratio=[1.0, 1.0, 0.06], wspace=[0.12, 0.04], bottom=0.15
)

# Two maps on the same scale, so that one colorbar describes both
Image.display(
    bowl,
    x1=x1,
    x2=x2,
    ax=0,
    vmin=0.0,
    vmax=2.0,
    title="bowl",
    xtitle="x",
    ytitle="y",
)
Image.display(
    2.0 - bowl,
    x1=x1,
    x2=x2,
    ax=1,
    vmin=0.0,
    vmax=2.0,
    title="2 - bowl",
    xtitle="x",
)

# The bar of the second map, in the third axis
Image.colorbar(axs=1, cax=2, clabel=r"$\rho$")
