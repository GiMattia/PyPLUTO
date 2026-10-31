"""
One colorbar
============

A colorbar asked for with ``colorbar()`` after the map, or drawn together
with it by ``display(cpos=...)``: the two give the same bar.
"""

import numpy as np

import pyPLUTO

# A bowl on a square grid: 0 at the center, 2 in the corners
x1 = np.linspace(-1.0, 1.0, 64)
x2 = np.linspace(-1.0, 1.0, 64)
bowl = x1[:, None] ** 2 + x2[None, :] ** 2

Image = pyPLUTO.Image(figsize=[11, 5])
Image.create_axes(ncol=2)

# The map first, then its colorbar
Image.display(
    bowl, x1=x1, x2=x2, ax=0, title="colorbar()", xtitle="x", ytitle="y"
)
Image.colorbar(axs=0, clabel=r"$\rho$")

# The map and its colorbar in one call
Image.display(
    bowl,
    x1=x1,
    x2=x2,
    ax=1,
    cpos="right",
    clabel=r"$\rho$",
    title="display(cpos='right')",
    xtitle="x",
    ytitle="y",
)
