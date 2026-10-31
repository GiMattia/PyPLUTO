"""
The four sides
==============

``cpos`` puts the colorbar on any side of the map, with its ticks and label
on the outer side. ``cpad`` is the space past the tick labels and titles the
map draws there, so the bar never covers them.
"""

import numpy as np

import pyPLUTO

# A bowl on a square grid: 0 at the center, 2 in the corners
x1 = np.linspace(-1.0, 1.0, 64)
x2 = np.linspace(-1.0, 1.0, 64)
bowl = x1[:, None] ** 2 + x2[None, :] ** 2

Image = pyPLUTO.Image(figsize=[11, 10])
Image.create_axes(ncol=2, nrow=2)

# One map per side, each with its colorbar
for nax, side in enumerate(["right", "left", "top", "bottom"]):
    Image.display(
        bowl, x1=x1, x2=x2, ax=nax, title=side, xtitle="x", ytitle="y"
    )
    Image.colorbar(axs=nax, cpos=side, clabel=r"$\rho$")
