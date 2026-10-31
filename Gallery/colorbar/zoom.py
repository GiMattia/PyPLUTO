"""
The colorbar of a zoom
======================

An inset made by ``zoom`` can have a colorbar of its own, given with
``cpos``. The parent stays the last considered axis, so a ``colorbar()``
asked for after the zoom describes the parent's map.
"""

import numpy as np

import pyPLUTO

# A bowl on a square grid: 0 at the center, 2 in the corners
x1 = np.linspace(-1.0, 1.0, 64)
x2 = np.linspace(-1.0, 1.0, 64)
bowl = x1[:, None] ** 2 + x2[None, :] ** 2

Image = pyPLUTO.Image(figsize=[11, 5])
Image.create_axes(ncol=2)

# An inset with a colorbar of its own
Image.display(
    bowl,
    x1=x1,
    x2=x2,
    ax=0,
    title="zoom(cpos='right')",
    xtitle="x",
    ytitle="y",
)
Image.zoom(ax=0, xrange=[-0.3, 0.3], yrange=[-0.3, 0.3], cpos="right")

# A colorbar after the zoom goes to the parent
Image.display(
    bowl,
    x1=x1,
    x2=x2,
    ax=1,
    title="zoom, then colorbar()",
    xtitle="x",
    ytitle="y",
)
Image.zoom(ax=1, xrange=[-0.3, 0.3], yrange=[-0.3, 0.3])
Image.colorbar(clabel=r"$\rho$")
