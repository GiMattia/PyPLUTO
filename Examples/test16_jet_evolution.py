"""Evolving MHD jet volume rendering (propagation movie frames).

This script renders one frame per simulation output of the 3D MHD jet with a
fixed camera, so the frames show the jet propagating in time without any
rotation. Each frame is saved as a PNG in ``test16_jet_evolution_frames``;
assembling them into a video (e.g. with ffmpeg) is left to the user.

The volume data is swapped in place each frame (reusing the same figure,
camera and colorbar) and the color limits are kept fixed so the colors do not
flicker as the jet evolves.

"""

# Loading the relevant packages
from pathlib import Path

import numpy as np

import pyPLUTO

# ---- fixed camera + output settings ----
ELEV = 12.0  # elevation angle (deg)
AZIM = -45.0  # azimuthal angle (deg), constant: no rotation
ROLL = 30.0  # roll angle (deg)
DPI = 300  # resolution of each saved PNG

# Folder holding the time-series data (data.NNNN.dbl, grid.out, dbl.out)
data_dir = Path(__file__).resolve().parent / "test16_jet_frames"

# Output folder for the rendered frames (kept separate from the data)
movie_dir = Path(__file__).resolve().parent / "test16_jet_evolution_frames"
movie_dir.mkdir(exist_ok=True)

# Discover the available outputs (data.0000.dbl, data.0001.dbl, ...)
outputs = sorted(int(p.stem.split(".")[1]) for p in data_dir.glob("data.*.dbl"))


def load_speed(nout: int) -> np.ndarray:
    """Load one output and return its (transverse) velocity magnitude."""
    data = pyPLUTO.Load(path=data_dir, nout=nout, text=False)
    return np.sqrt(data.vx1**2 + data.vx2**2)


# Build the image and the volume once, from the first output
Data = pyPLUTO.Load(path=data_dir, nout=outputs[0], text=False)
speed0 = np.sqrt(Data.vx1**2 + Data.vx2**2)
Image = pyPLUTO.Image(style="dark_background", figsize=[8, 10])
Image.create_axes(right=0.7, proj="3d")
vol = Image.volume(
    speed0,
    x1=Data.x1,
    x2=Data.x2,
    x3=Data.x3,
    cmap="inferno",
    vmin=0.0,
    vmax=5.0,
    opacity=("sigmoid", 0.35, 0.10, 1.0),
    opacity_scale=10.0,
    elev=ELEV,
    azim=AZIM,
    roll=ROLL,
    resolution=(450, 560),
    samples=160,
    interactive=False,
)

# The camera is fixed, so the axes do not swing around: keep them on to give
# a physical scale and orientation as the jet evolves.

# One frame per output; the camera stays fixed so only the jet evolves
for i, nout in enumerate(outputs):
    # PyPLUTO (x1, x2, x3) order -> engine (z, y, x) order
    vol.volume = np.ascontiguousarray(load_speed(nout).transpose(2, 1, 0))
    vol.render(final=True, force=True)
    vol.fig.savefig(movie_dir / f"frame_{i:04d}.png", dpi=DPI)
    print(f"frame {i + 1:4d}/{len(outputs)}  out {nout:4d}")

print(f"\nDone. {len(outputs)} frames written to {movie_dir}")
