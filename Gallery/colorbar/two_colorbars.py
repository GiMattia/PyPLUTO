"""
Two colorbars and the space around them
=======================================

A map can have more than one colorbar: each is cut from its side, and the
map shrinks for all of them. ``cpad`` sets the space between a bar and the
map, in inches.
"""

import numpy as np

import pyPLUTO

# A bowl on a square grid: 0 at the center, 2 in the corners
x1 = np.linspace(-1.0, 1.0, 64)
x2 = np.linspace(-1.0, 1.0, 64)
bowl = x1[:, None] ** 2 + x2[None, :] ** 2

Image = pyPLUTO.Image(figsize=[11, 5])
Image.create_axes(ncol=2)

# A colorbar on each side of the same map
Image.display(
    bowl, x1=x1, x2=x2, ax=0, title="two colorbars", xtitle="x", ytitle="y"
)
Image.colorbar(axs=0, cpos="left", clabel="left")
Image.colorbar(axs=0, cpos="right", clabel="right")

# A wider space between the map and its colorbar
Image.display(
    bowl, x1=x1, x2=x2, ax=1, title="cpad=0.4", xtitle="x", ytitle="y"
)
Image.colorbar(axs=1, cpad=0.4, clabel=r"$\rho$")
