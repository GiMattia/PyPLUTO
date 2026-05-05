"""MHD Torus test.

This test shows how to plot two quantities in two different subplots,
together with the plotting of streamlines in one of them and the
plotting of the field lines in the other one.

The data are the ones obtained from the PLUTO test problem
$PLUTO_DIR/Test_Problems/MHD/Torus (configuration 4).

The data is loaded into a pload object D and the Image class is created.
The create_axes method is used to create two plots for the two
variables. The display method is used to plot the density and the
pressure in the two subplots, while the streamplot method and the
find_fieldlines method are used to compute and then plot streamlines and
fieldlines of the magnetic field. Note that the magnetic field
components need to be converted from spherical into cartesian through
the cartesian_vector method before converting them on the cartesian mesh
grid. The image is then saved and shown on screen.

"""

# Loading the relevant packages
import timeit

import numpy as np

import pyPLUTO

# Set the relative path to the data folder
data_path = pyPLUTO.find_example("MHD/Torus")

# Load data
Data = pyPLUTO.Load(path=data_path)

# Creating the image
Image = pyPLUTO.Image(
    nwin=8, figsize=[11, 5], suptitle="Test 08 - MHD Torus test"
)

# Creating the subplots (2 for the different variables)
ax = Image.create_axes(ncol=2, top=0.91)

# Compute the magnetic field magnitude
B2 = np.sqrt(Data.Bx1**2 + Data.Bx2**2 + Data.Bx3**2)

# Plotting the data (colorbars adaptively positioned)
Image.display(
    Data.rho,
    x1=Data.x1p,
    x2=Data.x2p,
    cpos="right",
    aspect="equal",
    ax=0,
    cscale="log",
    title=r"Density (+ streamplot)",
    shading="gouraud",
    xtitle="x",
    ytitle="y",
    xrange=[0, 14],
    yrange=[-7, 7],
)

Image.display(
    Data.prs,
    x1=Data.x1p,
    x2=Data.x2p,
    cpos="right",
    aspect="equal",
    ax=1,
    cscale="log",
    title=r"Pressure (+ find$\_$fieldlines)",
    shading="gouraud",
    xtitle="x",
    xrange=[0, 14],
    yrange=[-7, 7],
)

# Convert the magnetic field into cartesian components and cartesian grid
Bx, Bz, *others = Data.cartesian_vector("B")
xc, yc, Bx, Bz = Data.reshape_cartesian(Bx, Bz, nx1=500)

try:
    t0 = timeit.default_timer()
    import rustronomy as rastro

    lines2 = rastro.find_fieldlines(
        Data,
        Bx,
        Bz,
        x1=xc,
        x2=yc,
        x0=[3.75, 4, 4.25],
        y0=[0, 0, 0],
        maxstep=0.07,
        numsteps=25000,
    )
    t_rastro = timeit.default_timer() - t0
    print(f"[test08] rustronomy find_fieldlines: {t_rastro:.6f} s")
except ImportError:
    print("[test08] rustronomy not available.")

t0 = timeit.default_timer()
lines = Data.find_fieldlines(
    Bx, Bz, x1=xc, x2=yc, x0=[3.75, 4, 4.25], y0=[0, 0, 0], maxstep=0.07
)
t_scipy = timeit.default_timer() - t0
print(f"[test08] PyPLUTO    find_fieldlines: {t_scipy:.6f} s")

Image.plot(lines[0][0], lines[0][1], ax=1, c="gray")
Image.plot(lines[1][0], lines[1][1], ax=1, c="gray")
Image.plot(lines[2][0], lines[2][1], ax=1, c="gray")

# Plot the magnetic field lines in two different ways
try:
    Image.plot(lines2[0][0], lines2[0][1], ax=0, c="gray")
    Image.plot(lines2[1][0], lines2[1][1], ax=0, c="gray")
    Image.plot(lines2[2][0], lines2[2][1], ax=0, c="gray")
except NotImplementedError:
    Image.streamplot(
        Bx, Bz, x1=xc, x2=yc, ax=0, c="gray", lw=0.7, vmin=1.0e-5, density=5
    )

# Saving the image and showing the plots
Image.savefig("test08_torus.png", script_relative=True)
# pyPLUTO.show()
