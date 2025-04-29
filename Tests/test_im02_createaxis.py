import numpy as np
import pyPLUTO as pp


# Check the default values of the figure created in the __init__
def test_figure_default_init():
    Image = pp.Image()
    Image.create_axes()
    nrow, ncol = Image.fig.axes[0].get_subplotspec().get_gridspec().get_geometry()
    assert ncol == 1
    assert nrow == 1


# Change number of rows and columns
def test_rows_columns():
    Image = pp.Image()
    ax = Image.create_axes(ncol=2, nrow=3)
    nrow, ncol = Image.fig.axes[0].get_subplotspec().get_gridspec().get_geometry()
    assert ncol == 2
    assert nrow == 3
    assert len(ax) == 6


# Add suptitle and change tight layout
def test_suptitle_layout():
    Image = pp.Image()
    Image.create_axes(ncol=2, nrow=3, suptitle="this is title", tight=False)
    assert Image.fig._suptitle.get_text() == "this is title"
    assert Image.fig.get_tight_layout() is False


# Add different borders to the figure
def test_borders():
    Image = pp.Image()
    ax = Image.create_axes(left=0.2, right=0.8, top=0.85, bottom=0.05)
    assert Image.fig.get_tight_layout() is False
    pos = ax.get_position().bounds
    assert np.isclose(pos[0], 0.2)
    assert np.isclose(pos[1], 0.05)
    assert np.isclose(pos[2], 0.6)
    assert np.isclose(pos[3], 0.8)


# Two columns custom
def test_twocolumns():
    Image = pp.Image()
    ax = Image.create_axes(ncol=2, left=0.15, right=0.8, wspace=0.2, wratio=[2, 1])
    pos = ax[0].get_position().bounds
    assert np.isclose(pos[0], 0.15)
    assert np.isclose(pos[2], 0.3)
    pos = ax[1].get_position().bounds
    assert np.isclose(pos[0], 0.65)
    assert np.isclose(pos[2], 0.15)


# Multiple rows
def test_multiple_row():
    Image = pp.Image()
    ax = Image.create_axes(ncol=1, nrow=3, hspace=[0.2, 0.1], hratio=[1, 2, 1])
    pos = ax[0].get_position().bounds
    assert np.isclose(pos[1], 0.775)
    assert np.isclose(pos[3], 0.125)
    pos = ax[1].get_position().bounds
    assert np.isclose(pos[1], 0.325)
    assert np.isclose(pos[3], 0.25)
    pos = ax[2].get_position().bounds
    assert np.isclose(pos[1], 0.1)
    assert np.isclose(pos[3], 0.125)


# Multiple rows and columns
def test_multiple_rowcols():
    Image = pp.Image()
    ax = Image.create_axes(ncol=2, nrow=3, left=0.05, bottom=0.05)
    pos = ax[0].get_position().bounds
    assert np.isclose(pos[0], 0.05)
    pos = ax[-1].get_position().bounds
    assert np.isclose(pos[1], 0.05)


# Suptitle and figsize
def test_size_suptitle():
    Image = pp.Image(suptitle="This is a title", figsize=(6, 7))
    assert Image.fig._suptitle.get_text() == "This is a title"
    assert Image.fig.get_figwidth() == 6
    assert Image.fig.get_figheight() == 7
    Image.create_axes(suptitle="This is another title", figsize=(5, 8))
    assert Image.fig._suptitle.get_text() == "This is another title"
    assert Image.fig.get_figwidth() == 5
    assert Image.fig.get_figheight() == 8


# Multiple create_axes
def test_multiple_created():
    Image = pp.Image()
    ax = Image.create_axes(left=0.2, right=0.5)
    ax = Image.create_axes(left=0.6, right=0.85)
    assert len(ax) == 2
    pos = ax[0].get_position().bounds
    assert np.isclose(pos[0], 0.2)
    assert np.isclose(pos[2], 0.3)
    pos = ax[1].get_position().bounds
    assert np.isclose(pos[0], 0.6)
    assert np.isclose(pos[2], 0.25)
