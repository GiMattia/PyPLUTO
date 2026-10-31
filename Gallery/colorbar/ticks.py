"""
Ticks of a colorbar
===================

The ticks of a colorbar follow the rules of ``xticks``: ``cticks`` fixes
them, ``ctickslabels`` names them, and ``None`` removes them. On a
logarithmic scale every fixed tick gets its label, not only the powers of
ten.
"""

import numpy as np

import pyPLUTO

# A bowl on a square grid: 0.01 at the center, 2.01 in the corners
x1 = np.linspace(-1.0, 1.0, 64)
x2 = np.linspace(-1.0, 1.0, 64)
bowl = x1[:, None] ** 2 + x2[None, :] ** 2 + 0.01

Image = pyPLUTO.Image(figsize=[16, 5])
Image.create_axes(ncol=3)

# Fixed ticks on a logarithmic scale, each labeled
Image.display(
    bowl,
    x1=x1,
    x2=x2,
    ax=0,
    cscale="log",
    title="cticks",
    xtitle="x",
    ytitle="y",
)
Image.colorbar(axs=0, cticks=[0.05, 0.1, 0.5, 1.0])

# Fixed ticks with names of their own
Image.display(
    bowl, x1=x1, x2=x2, ax=1, cscale="log", title="ctickslabels", xtitle="x"
)
Image.colorbar(
    axs=1, cticks=[0.05, 0.5, 2.0], ctickslabels=["low", "mid", "high"]
)

# No ticks at all
Image.display(
    bowl, x1=x1, x2=x2, ax=2, cscale="log", title="cticks=None", xtitle="x"
)
Image.colorbar(axs=2, cticks=None)
