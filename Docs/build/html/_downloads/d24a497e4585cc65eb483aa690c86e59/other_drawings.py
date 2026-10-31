"""
Points and streamlines colored by data
======================================

``scatter`` and ``streamplot`` draw a colorbar with ``cpos`` too, when their
color comes from a variable: the value at each point, or the speed of the
flow.
"""

import numpy as np

import pyPLUTO

# A vortex on a square grid: the flow turns around the center
x1 = np.linspace(-1.0, 1.0, 64)
x2 = np.linspace(-1.0, 1.0, 64)
vx1 = -x2[None, :] + 0.0 * x1[:, None]
vx2 = x1[:, None] + 0.0 * x2[None, :]

# Points along a parabola, colored by their abscissa
xp = np.linspace(-1.0, 1.0, 30)
yp = xp**2

Image = pyPLUTO.Image(figsize=[11, 5])
Image.create_axes(ncol=2)

Image.scatter(
    xp,
    yp,
    c=xp,
    ax=0,
    cpos="right",
    clabel="x",
    title="scatter",
    xtitle="x",
    ytitle="y",
)
Image.streamplot(
    vx1,
    vx2,
    x1=x1,
    x2=x2,
    ax=1,
    cmap="magma",
    cpos="bottom",
    clabel="speed",
    title="streamplot",
    xtitle="x",
    ytitle="y",
)
