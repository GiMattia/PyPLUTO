"""MHD jet volume rendering test.

This test shows how to volume-render a 3D quantity from a test problem
with the interactive ray-marching renderer.

The data are obtained from a 3D Cartesian MHD jet propagating along the
z (x3) axis. The rendered field is the velocity magnitude: the beam moves
fast while the ambient medium is nearly static, which gives a high
contrast that isolates the jet beam, its head and the turbulent cocoon
(the density, in contrast, only spans a factor of a few and would render
as a solid block). The opacity transfer function keeps the slow ambient
transparent so the fast beam glows against the background.

The volume is drawn as an RGBA underlay synchronized with a Matplotlib
Axes3D, which keeps ownership of the camera. The render is interactive:
rotating with the mouse updates the volume live (a fast preview while
dragging, full quality on release), and the toolbar Home button resets
both the camera and the rendered volume to the fixed view set through the
elev/azim keywords. The color limits are fixed with vmin/vmax for a
reproducible image.

The renderer follows the active Matplotlib style, so the Image is created
with style="dark_background" to make the beam stand out on a dark
backdrop.

Note that the Image is saved through I.savefig (and not pp.savefig)
since saving a file should be strictly related to a single Image class.
Conversely, the pp.show displays all the figures generated in the script
(here only one).

"""

# Loading the relevant packages
import numpy as np

import pyPLUTO

# Set the relative path to the data folder
data_path = pyPLUTO.find_example("MHD/Jet")

# Load data
Data = pyPLUTO.Load(path=data_path)

# Velocity magnitude: high in the beam, near zero in the ambient medium
speed = np.sqrt(Data.vx1**2 + Data.vx2**2)

# Creating the image (dark background, tall figure for the elongated jet)
Image = pyPLUTO.Image(style="dark_background", figsize=[5, 7])
Image.create_axes(right=0.7, proj="3d")

# Volume-rendering the speed. The grid coordinates (x1, x2, x3) set the
# physical extent; the sigmoid opacity keeps the slow ambient transparent
# so only the fast beam and its head accumulate color. elev/azim fix the
# camera and vmin/vmax fix the color limits for a reproducible figure.
Image.volume(
    speed,
    x1=Data.x1,
    x2=Data.x2,
    x3=Data.x3,
    cmap="inferno",
    vmin=0.0,
    vmax=5.0,
    opacity=("sigmoid", 0.35, 0.10, 1.0),
    opacity_scale=10.0,
    elev=12.0,
    azim=-45.0,
    roll=30,
    resolution=(300, 360),
    samples=160,
)

# Saving the image and showing the plot in the Examples folder
# (i.e., where the file test16_jet.py is located)
Image.savefig("test16_jet.png", script_relative=True)
pyPLUTO.show()
