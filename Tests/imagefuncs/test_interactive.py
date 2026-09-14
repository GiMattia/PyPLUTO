"""Test of the interactive.py file."""

import numpy as np
import numpy.testing as npt

import pyPLUTO as pp

x = np.linspace(0.0, 1.0, 20)
x2d, y2d = np.meshgrid(x, x, indexing="ij")

# Three frames of a 1D and of a 2D dataset
lines = {i: np.sin(x * (i + 1)) for i in range(3)}
maps = {i: (x2d**2 + y2d**2) * (i + 1) for i in range(3)}


# A 1D interactive plot draws the first frame and builds a slider
def test_interactive_1D():
    Image = pp.Image()
    Image.interactive(x, lines)
    assert Image.InteractiveManager.nsld == 3
    assert len(Image.ax[0].get_lines()) > 0


# A 2D interactive plot draws the first frame as a colormap
def test_interactive_2D():
    Image = pp.Image()
    Image.interactive(maps, x1=x, x2=x)
    assert Image.InteractiveManager.nsld == 3
    assert len(Image.ax[0].collections) > 0


# The number of slider positions matches the number of frames
def test_interactive_slider_length():
    Image = pp.Image()
    Image.interactive(x, {i: np.sin(x * (i + 1)) for i in range(5)})
    assert Image.InteractiveManager.nsld == 5


# The first frame is the one drawn when the plot is created
def test_interactive_draws_first_frame():
    Image = pp.Image()
    Image.interactive(x, lines)
    npt.assert_allclose(Image.ax[0].get_lines()[0].get_ydata(), lines[0])


# Moving the slider replaces the plotted data with that frame
def test_interactive_update_slider():
    Image = pp.Image()
    Image.interactive(x, lines)
    Image.InteractiveManager.update_slider(1)
    npt.assert_allclose(Image.ax[0].get_lines()[0].get_ydata(), lines[1])


# The combined update moves to the requested frame as well
def test_interactive_update_both():
    Image = pp.Image()
    Image.interactive(x, lines)
    Image.InteractiveManager.update_both(2)
    npt.assert_allclose(Image.ax[0].get_lines()[0].get_ydata(), lines[2])


# A title is forwarded to the axis
def test_interactive_title():
    Image = pp.Image()
    Image.interactive(x, lines, title="frames")
    assert Image.ax[0].get_title() == "frames"


# An animation can be written to a GIF file
def test_animate_writes_gif(tmp_path):
    """LONG TEST: CHECK"""
    Image = pp.Image()
    Image.interactive(x, lines)

    out = tmp_path / "movie.gif"
    Image.animate(gifname=str(out), interval=100)

    assert out.exists()
    assert out.stat().st_size > 0
