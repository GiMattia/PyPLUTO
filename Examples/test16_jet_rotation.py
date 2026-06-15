"""Rotating MHD jet volume rendering (360-degree turntable frames).

This script renders a single, fully developed output of the 3D MHD jet from a
full turn of azimuthal angles: 360 frames, one per degree, with a fixed
elevation and roll. The frames show all sides of the jet without any time
evolution. Each frame is saved as a PNG in ``test16_jet_rotation_frames``;
assembling them into a video (e.g. with ffmpeg) is left to the user.

"""

# Loading the relevant packages
from pathlib import Path

import numpy as np

import pyPLUTO

# ---- turntable settings ----
NFRAMES = 720  # number of frames over the full 360 degrees (1 per degree)
ELEV = 12.0  # fixed elevation angle (deg)
ROLL = 30.0  # fixed roll angle (deg)
DPI = 300  # resolution of each saved PNG

# Folder holding the time-series data (data.NNNN.dbl, grid.out, dbl.out)
data_dir = Path(__file__).resolve().parent / "test16_jet_frames"

# Output folder for the rendered frames (kept separate from the data)
movie_dir = Path(__file__).resolve().parent / "test16_jet_rotation_frames"
movie_dir.mkdir(exist_ok=True)

# Use the last (fully developed) output; the data stays fixed across frames
Data = pyPLUTO.Load(path=data_dir, nout="last", text=False)
speed = np.sqrt(Data.vx1**2 + Data.vx2**2)

# Create the image and the volume once; only the camera changes per frame
Image = pyPLUTO.Image(style="dark_background", figsize=[8, 10])
Image.create_axes(right=0.7, proj="3d")
vol = Image.volume(
    speed,
    x1=Data.x1,
    x2=Data.x2,
    x3=Data.x3,
    cmap="inferno",
    vmin=0.0,
    vmax=5.0,
    opacity=("sigmoid", 0.35, 0.10, 1.0),
    opacity_scale=10.0,
    elev=ELEV,
    azim=0.0,
    roll=ROLL,
    resolution=(450, 560),
    samples=160,
    interactive=False,
)

# Remove the 3D axes entirely (box, panes, ticks, labels) for a clean volume
vol.ax3d.set_axis_off()

# One frame per azimuthal angle over a full turn; the data stays fixed
for i, azim in enumerate(np.linspace(0.0, 720.0, NFRAMES, endpoint=False)):
    vol.ax3d.view_init(elev=ELEV, azim=azim, roll=ROLL)
    vol.render(final=True, force=True)
    vol.fig.savefig(movie_dir / f"frame_{i:04d}.png", dpi=DPI)
    print(f"frame {i + 1:4d}/{NFRAMES}  azim {azim:5.1f}")

print(f"\nDone. {NFRAMES} frames written to {movie_dir}")
