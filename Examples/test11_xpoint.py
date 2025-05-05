"""Particles CR Xpoint test

This test shows how to plot data from the Load class and the LoadPart class
simultaneously and how to produce a scatter plot.

The data are the ones obtained from the PLUTO test problem
$PLUTO_DIR/Test_Problems/Particles/CR/Xpoint (configuration 1).

The data is loaded with the Load class and the LoadPart class into two pload
 objects, and the Image class is created. The contour method is used to plot the
contour lines of the electromagnetic vector potential. The scatter method is
used to plot the single particles at the end of the simulation time. The
spectrum and plot method are then used to show the velocity spectra of the
particles at the beginning and at the end of the simulation. The image is then
saved and shown on screen.
"""

import matplotlib.pyplot as plt
import numpy as np
import pyPLUTO

# --- Load fluid and particle data ---
Data = pyPLUTO.Load(path="Test_Problems/Particles/CR/Xpoint")
Dp_f = pyPLUTO.LoadPart(
    path="Test_Problems/Particles/CR/Xpoint", datatype="vtk"
)
Dp_i = pyPLUTO.LoadPart(
    0, path="Test_Problems/Particles/CR/Xpoint", datatype="vtk"
)


# --- Compute Lorentz factor and sort ---
def compute_gamma(dp):
    return np.sqrt(1 + dp.vx1**2 + dp.vx2**2 + dp.vx3**2)


gl_final = compute_gamma(Dp_f)
indx_final = np.argsort(gl_final)

# --- Create the figure ---
Image = pyPLUTO.Image(figsize=[7, 7], fontsize=20)

# --- Plot contour of Ax3 ---
Image.contour(
    Data.Ax3,
    x1=Data.x1 / 1000,
    x2=Data.x2 / 1000,
    levels=20,
    aspect="equal",
    c="silver",
)

# --- Plot particle positions ---
Image.scatter(
    Dp_f.x1[indx_final] / 1000,
    Dp_f.x2[indx_final] / 1000,
    cpos="right",
    vmin=0,
    vmax=40,
    c=gl_final[indx_final],
    cmap=plt.get_cmap("YlOrRd", 8),
    ms=10,
    title="Test 11 - Particles CR Xpoint test",
    xrange=[-3.5, 3.5],
    yrange=[-3.5, 3.5],
    xticks=[-3, -2, -1, 0, 1, 2, 3],
    yticks=[-3, -2, -1, 0, 1, 2, 3],
    xtitle=r"$x\;(\times10^3)$",
    ytitle=r"$y\;(\times10^3)$",
    clabel=r"$\Gamma$",
)

# --- Create inset axes for spectra ---
Image.create_axes(left=0.35, right=0.7, bottom=0.23, top=0.4)

# --- Plot particle spectra ---
for Dp, label in [(Dp_i, "t = 0"), (Dp_f, "t = 100")]:
    gl = compute_gamma(Dp)
    hist, bins = Dp.spectrum(gl, density=False)

    Image.plot(
        bins,
        hist,
        ax=1,
        xscale="log",
        yscale="log",
        xrange=[1, 50],
        yrange=[1, 1.0e8],
        label=label,
        fontsize=13,
    )

# --- Customize the second plot ---
Image.legend(ax=1, legpos=0, legsize=10, legalpha=0.25)
Image.ax[1].patch.set_alpha(0.75)

# --- Save and show ---
Image.savefig("test11_xpoint.png")
pyPLUTO.show()
