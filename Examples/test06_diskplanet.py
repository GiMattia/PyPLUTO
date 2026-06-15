"""HD disk-planet test.

This test shows how to plot different 2D quantities from a test problem
in the same plot with two zooms.

The data are the ones obtained from the PLUTO test problem directory
$PLUTO_DIR/Test_Problems/HD/Disk_Planet (configuration 6).

Physical units are read automatically from the pluto.log file:
  - unit length   = 7.779e+13 cm  (~5.2 AU)
  - unit velocity = 2.085e+05 cm/s  (~2.09 km/s)
  - unit density  = 4.249e-09 g/cm³
  - unit time     = 3.732e+08 s  (~11.83 yr)

The data is loaded into a pload object D and the Image class is created.
The create_axes method is used here to make easier to associate the
zooms with the main plot. The display method is used to plot the density
(converted to g/cm³) in the main plot, while the zoom method is used to
create the two zooms.  The image is then saved and shown on screen.

Note that the second zoom requires the keyword ax to be passed to the
zoom method, in order to associate the zoom with main plot. The zoom
method is called twice, once for each zoom region. If no keyword ax was
passed, the second zoom would be associated as a zoom of the first zoom.
The second zoom is also plotted with a different variable with respect
to the main plot, to show the flexibility of the zoom method in plotting
different quantities in the same region.

"""

# Loading the relevant packages
import numpy as np

import pyPLUTO

# Set the relative path to the data folder
data_path = pyPLUTO.find_example("HD/Disk_Planet")

# Load data and attach physical units to density (auto-detected from pluto.log)
Data = pyPLUTO.Load(path=data_path, units="rho")

# Physical unit scales from the log
rho0 = float(Data.unit_base["UNIT_DENSITY"])  # g/cm³
l0 = float(Data.unit_base["UNIT_LENGTH"])  # cm
v0 = float(Data.unit_base["UNIT_VELOCITY"])  # cm/s

AU_cm = 1.495979e13  # 1 AU in cm
l0_au = l0 / AU_cm  # unit length in AU
v0_kms = v0 / 1e5  # unit velocity in km/s

# Creating the image and the subplot axes (to have two zoom simultaneously)
Image = pyPLUTO.Image(nwin=6, style="dark_background")
ax = Image.create_axes()

# Compute the disk Keplerian rotation speed (code units)
omega = 2.0 * np.pi / np.sqrt(Data.x1)

# Coordinates in AU and velocity perturbation in km/s
x1_au = Data.x1rc * l0_au
x2_au = Data.x2rc * l0_au
dv_kms = (Data.vx2 - omega[:, None]) * v0_kms

# Derived plot ranges and ticks in AU
zoom_x = [0.9 * l0_au, 1.1 * l0_au]
zoom_y = [-0.1 * l0_au, 0.1 * l0_au]

# Plotting the data (density in physical units g/cm³)
Image.display(
    np.asarray(Data.rho),
    x1=x1_au,
    x2=x2_au,
    cscale="log",
    cpos="right",
    clabel=r"$\rho$ [g cm$^{-3}$]",
    title="Test 06 - HD Disk planet test",
    vmin=0.1 * rho0,
    xtitle="x [AU]",
    ytitle="y [AU]",
    xticks=[-10, -5, 0, 5, 10],
    yticks=[-10, -5, 0, 5, 10],
    xrange=[-13, 13],
    yrange=[-13, 13],
)

# Zooming the planet region
Image.zoom(xrange=zoom_x, yrange=zoom_y, pos=[0.74, 0.95, 0.7, 0.9])
Image.zoom(
    var=dv_kms,
    xrange=zoom_x,
    yrange=zoom_y,
    pos=[0.07, 0.27, 0.67, 0.9],
    cpos="bottom",
    cmap="berlin",
    cscale="linear",
    vmin=-2,
    vmax=2,
    ax=0,
    title=r"  $(v_\phi - \Omega R)$ [km s$^{-1}$]",
    titlesize=13,
    cticks=[-2, 0, 2],
)

# Saving the image and showing the plots
Image.savefig("test06_diskplanet.png", script_relative=True)
# pyPLUTO.show()
