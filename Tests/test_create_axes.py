"""Test of the create_axes.py file."""

import numpy as np

import pyPLUTO as pp


# Check the default values of the figure created in the __init__
def test_figure_default_init() -> None:
    """Ensure that the figure is initialized with default values."""
    Image = pp.Image()
    Image.create_axes()
    fig = Image.fig
    assert fig is not None
    ax = fig.axes[0]
    assert ax is not None
    spec = ax.get_subplotspec()
    assert spec is not None
    nrow, ncol = spec.get_gridspec().get_geometry()
    assert ncol == 1
    assert nrow == 1


# Change number of rows and columns
def test_rows_columns() -> None:
    """Ensure that the number of rows and columns can be changed."""
    Image = pp.Image()
    newax = Image.create_axes(ncol=2, nrow=3)
    check_col, check_row, check_len = 2, 3, 6
    assert isinstance(newax, list)
    fig = Image.fig
    assert fig is not None
    ax = fig.axes[0]
    assert ax is not None
    spec = ax.get_subplotspec()
    assert spec is not None
    nrow, ncol = spec.get_gridspec().get_geometry()
    assert ncol == check_col
    assert nrow == check_row
    assert len(newax) == check_len


# Add suptitle and change tight layout
def test_suptitle_layout() -> None:
    """Ensure that suptitle and tight layout can be changed."""
    Image = pp.Image()
    Image.create_axes(ncol=2, nrow=3, suptitle="this is title", tight=False)
    fig = Image.fig
    assert fig is not None
    titles = [text.get_text() for text in fig.texts]
    assert "this is title" in titles
    assert fig._suptitle is not None  # type: ignore[attr-defined]  # ty:ignore[unresolved-attribute]

    assert fig.get_tight_layout() is False


# Add different borders to the figure
def test_borders() -> None:
    """Ensure that different borders can be added to the figure."""
    Image = pp.Image()
    Image.create_axes(left=0.2, right=0.8, top=0.85, bottom=0.05)
    fig = Image.fig
    assert fig is not None
    assert fig.get_tight_layout() is False
    ax = fig.axes[0]
    assert ax is not None
    pos = ax.get_position().bounds
    assert np.isclose(pos[0], 0.2)
    assert np.isclose(pos[1], 0.05)
    assert np.isclose(pos[2], 0.6)
    assert np.isclose(pos[3], 0.8)


# Two columns custom
def test_twocolumns() -> None:
    """Ensure that multiple columns can be created with custom parameters."""
    Image = pp.Image()
    ax = Image.create_axes(
        ncol=2, left=0.15, right=0.8, wspace=0.2, wratio=[2, 1]
    )
    assert isinstance(ax, list)
    pos = ax[0].get_position().bounds
    assert np.isclose(pos[0], 0.15)
    assert np.isclose(pos[2], 0.3)
    pos = ax[1].get_position().bounds
    assert np.isclose(pos[0], 0.65)
    assert np.isclose(pos[2], 0.15)


# Multiple rows
def test_multiple_row() -> None:
    """Ensure that multiple rows can be created with custom parameters."""
    Image = pp.Image()
    ax = Image.create_axes(ncol=1, nrow=3, hspace=[0.2, 0.1], hratio=[1, 2, 1])
    assert isinstance(ax, list)
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
def test_multiple_rowcols() -> None:
    """Ensure that multiple rows/columns can be created with custom params."""
    Image = pp.Image()
    ax = Image.create_axes(ncol=2, nrow=3, left=0.05, bottom=0.05)
    assert isinstance(ax, list)
    pos = ax[0].get_position().bounds
    assert np.isclose(pos[0], 0.05)
    pos = ax[-1].get_position().bounds
    assert np.isclose(pos[1], 0.05)


# Suptitle and figsize
def test_size_suptitle() -> None:
    """Ensure that suptitle and figsize can be changed."""
    w1, h1, w2, h2 = 6, 7, 5, 8
    Image = pp.Image(suptitle="This is a title", figsize=[6, 7])
    fig = Image.fig
    assert fig is not None
    assert fig._suptitle.get_text() == "This is a title"  # type: ignore[attr-defined]  # ty:ignore[unresolved-attribute]
    assert fig.get_figwidth() == w1
    assert fig.get_figheight() == h1
    Image.create_axes(suptitle="This is another title", figsize=[5, 8])
    assert fig._suptitle.get_text() == "This is another title"  # type: ignore[attr-defined]  # ty:ignore[unresolved-attribute]
    assert fig.get_figwidth() == w2
    assert fig.get_figheight() == h2


# Multiple create_axes
def test_multiple_created() -> None:
    """Ensure that multiple axes can be created."""
    axesnum = 2
    Image = pp.Image()
    _ = Image.create_axes(left=0.2, right=0.5)
    ax = Image.create_axes(left=0.6, right=0.85)
    assert isinstance(ax, list)
    assert len(ax) == axesnum
    pos = ax[0].get_position().bounds
    assert np.isclose(pos[0], 0.2)
    assert np.isclose(pos[2], 0.3)
    pos = ax[1].get_position().bounds
    assert np.isclose(pos[0], 0.6)
    assert np.isclose(pos[2], 0.25)
