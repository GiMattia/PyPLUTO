"""
Extensions of a colorbar
========================

When the color scale is narrower than the data, ``extend`` adds a pointed
end to the colorbar for the values beyond its limits: on both ends, or only
on the ``'min'`` or the ``'max'`` one. With ``extendrect=True`` the ends are
rectangular.
"""

import numpy as np

import pyPLUTO

# A bowl on a square grid: 0 at the center, 2 in the corners
x1 = np.linspace(-1.0, 1.0, 64)
x2 = np.linspace(-1.0, 1.0, 64)
bowl = x1[:, None] ** 2 + x2[None, :] ** 2

Image = pyPLUTO.Image(figsize=[16, 5])
Image.create_axes(ncol=3)

# The scale covers 0.5 to 1.5, so the center and the corners lie beyond it
cases = [("both", False), ("max", False), ("both", True)]
for nax, (extend, rect) in enumerate(cases):
    title = f"extend='{extend}'" + (", extendrect" if rect else "")
    Image.display(
        bowl,
        x1=x1,
        x2=x2,
        ax=nax,
        vmin=0.5,
        vmax=1.5,
        title=title,
        xtitle="x",
        ytitle="y",
    )
    Image.colorbar(axs=nax, extend=extend, extendrect=rect, clabel=r"$\rho$")
