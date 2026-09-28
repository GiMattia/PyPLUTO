"""Test of the streamplot.py file.

StreamplotManager draws the streamlines of a 2D vector field, through
matplotlib's streamplot. Like a map, the two components are indexed as
`var[x, y]`, the PLUTO order, and are transposed on the way out, so the
orientation is checked on uniform fields over a rectangular grid: a field
pointing along x has to give lines that only move in x, which a transposition
turns into lines that only move in y.

The lines take the color `c` if given, otherwise the next color of the
palette, as a curve does; a colormap or a colorbar colors them instead by the
magnitude of the field. The limits `vmin` and `vmax` also hide the lines
where the magnitude falls outside them, which is how a figure leaves the
regions of a negligible field empty. None of this may reach the arrays the
user passed: the hidden cells are a mask on views, never written into them.
"""

import warnings

import numpy as np
import numpy.testing as npt
import pytest
from matplotlib.axes import Axes
from matplotlib.collections import LineCollection
from matplotlib.colors import to_hex
from matplotlib.patches import FancyArrowPatch, Rectangle

import pyPLUTO as pp

# Two uniform fields on a rectangular 6 x 4 grid, one along +x and one along
# +y, so that a line running along the wrong axis cannot pass.
along_x = (np.ones((6, 4)), np.zeros((6, 4)))
along_y = (np.zeros((6, 4)), np.ones((6, 4)))

# A rotating vector field on a square grid, whose magnitude is the distance
# from the center: from about 0.07 near it to sqrt(2) in the corners.
x = np.linspace(-1, 1, 20)
y = np.linspace(-1, 1, 20)
x2d, y2d = np.meshgrid(x, y, indexing="ij")
vx, vy = -y2d, x2d


def _vertices(lines: LineCollection) -> np.ndarray:
    """Return every vertex of the drawn lines, one (x, y) pair per row."""
    segments = [np.asarray(segment) for segment in lines.get_segments()]
    assert len(segments) >= 1
    return np.concatenate(segments)


def _motion(lines: LineCollection) -> np.ndarray:
    """Return how far the lines travel along x and along y, in total."""
    steps = [
        np.diff(np.asarray(segment), axis=0) for segment in lines.get_segments()
    ]
    return np.abs(np.concatenate(steps)).sum(axis=0)


def _color(lines: LineCollection) -> str:
    """Return the color of the first line, as a hex string."""
    return to_hex(np.asarray(lines.get_color())[0])


# ---- The lines that are drawn ----
def test_streamplot_returns_linecollection() -> None:
    """Check the streamplot hands back the collection of its lines.

    It is what a colorbar is built from, so a streamplot that returns
    nothing cannot be given one of its own.
    """
    image = pp.Image(text=False)
    lines = image.streamplot(vx, vy, x1=x, x2=y)

    assert isinstance(lines, LineCollection)


def test_streamplot_draws_on_axis() -> None:
    """Check the lines end up on the current axis.

    A collection that is returned but never added to the axis is a figure
    that stays empty.
    """
    image = pp.Image(text=False)
    image.streamplot(vx, vy, x1=x, x2=y)

    assert isinstance(image.ax[0], Axes)
    assert len(image.ax[0].collections) > 0


def test_the_components_are_indexed_x_first() -> None:
    """Draw a field along x, then one along y, and see where the lines go.

    `var1` is the component along x and `var2` the one along y, both indexed
    as `var[x, y]`. A field along x moves its lines in x only, and one along
    y in y only; swapping the components or the axes turns one into the
    other, a figure that looks plausible and is wrong everywhere.
    """
    horizontal = pp.Image(text=False).streamplot(*along_x)
    vertical = pp.Image(text=False).streamplot(*along_y)

    dx, dy = _motion(horizontal)
    assert dx > 0.0
    assert dy == pytest.approx(0.0)
    dx, dy = _motion(vertical)
    assert dx == pytest.approx(0.0)
    assert dy > 0.0


def test_without_coordinates_the_lines_are_drawn_on_the_indices() -> None:
    """Draw a field and nothing else, then read where the lines lie.

    The coordinates are then the cell numbers, one point per cell, so every
    line stays between 0 and 5 along x and between 0 and 3 along y for a
    6 x 4 field.
    """
    lines = pp.Image(text=False).streamplot(*along_y)

    vertices = _vertices(lines)
    assert vertices[:, 0].min() >= 0.0
    assert vertices[:, 0].max() <= 5.0
    assert vertices[:, 1].min() >= 0.0
    assert vertices[:, 1].max() == pytest.approx(3.0)


def test_a_transposed_field_draws_the_same_lines() -> None:
    """Draw the transposed components declared as transposed.

    `transpose` says the components are given as `var[y, x]`, so the lines
    have to move exactly as before. The default coordinates used to be
    built before the transposition, from the wrong shape, so any rectangular
    field raised a ValueError from matplotlib.
    """
    straight = pp.Image(text=False).streamplot(*along_x)
    turned = pp.Image(text=False).streamplot(
        along_x[0].T, along_x[1].T, transpose=True
    )

    npt.assert_allclose(_motion(turned), _motion(straight))


def test_lists_are_accepted() -> None:
    """Give the components as nested lists instead of arrays.

    They are converted on the way in; the first row used to be read with an
    array index, which a list refuses with a TypeError.
    """
    lines = pp.Image(text=False).streamplot(
        along_x[0].tolist(), along_x[1].tolist()
    )

    assert _motion(lines)[0] > 0.0


def test_components_of_different_shapes_are_refused() -> None:
    """Give two components that do not describe the same grid.

    The error is raised before anything is drawn, rather than letting
    matplotlib fail on a shape the user never wrote.
    """
    image = pp.Image(text=False)

    with pytest.raises(ValueError, match="shapes of the variables"):
        image.streamplot(vx, vy[:, :10])


def test_the_components_are_left_untouched() -> None:
    """Draw with limits that hide part of the field, then read the input.

    The hidden cells are a mask on views of the components, so the arrays
    the user passed keep every value and gain no mask. Writing NaN into them
    would silently corrupt the data for whatever comes next.
    """
    first, second = vx.copy(), vy.copy()

    pp.Image(text=False).streamplot(first, second, x1=x, x2=y, vmin=0.5)

    assert not np.ma.isMaskedArray(first)
    assert not np.ma.isMaskedArray(second)
    npt.assert_array_equal(first, vx)
    npt.assert_array_equal(second, vy)


# ---- Which lines are drawn ----
def test_streamplot_density() -> None:
    """Draw the same field sparse and dense.

    A higher density packs the lines closer, so more of them are drawn.
    """
    sparse = pp.Image(text=False).streamplot(vx, vy, x1=x, x2=y, density=0.4)
    dense = pp.Image(text=False).streamplot(vx, vy, x1=x, x2=y, density=2.0)

    assert len(dense.get_segments()) > len(sparse.get_segments())


def test_the_field_above_vmax_is_left_empty() -> None:
    """Draw the rotating field with a top limit of 0.5.

    Its magnitude is the distance from the center, so every line has to
    stay inside that radius; without the limit they reach past 1.3.
    """
    lines = pp.Image(text=False).streamplot(vx, vy, x1=x, x2=y, vmax=0.5)

    radius = np.hypot(*_vertices(lines).T)
    assert radius.max() < 0.5


def test_the_field_below_vmin_is_left_empty() -> None:
    """Draw the rotating field with a bottom limit of 0.5.

    Every line has to stay outside that radius, which is how the regions of
    a negligible field are left empty in a figure.
    """
    lines = pp.Image(text=False).streamplot(vx, vy, x1=x, x2=y, vmin=0.5)

    radius = np.hypot(*_vertices(lines).T)
    assert radius.min() > 0.5


# ---- The colors ----
def test_the_default_colors_follow_the_palette() -> None:
    """Draw twice on one axis without a color.

    Each streamplot takes the next color of the palette, as a curve does,
    rather than the blue matplotlib would pick on its own.
    """
    image = pp.Image(text=False)
    first = image.streamplot(vx, vy, x1=x, x2=y)
    second = image.streamplot(vx, vy, x1=x, x2=y)

    assert _color(first) == image.color[0]
    assert _color(second) == image.color[1]


def test_the_palette_wraps_around() -> None:
    """Draw one streamplot more than the palette has colors.

    The last one starts the palette again instead of running past its end.
    The small field and the loose layout only keep the many draws quick.
    """
    image = pp.Image(text=False, tight=False)
    for _ in image.color:
        image.streamplot(*along_x)

    lines = image.streamplot(*along_x)

    assert _color(lines) == image.color[0]


def test_streamplot_color() -> None:
    """Give a color and check it is the one applied."""
    image = pp.Image(text=False)
    lines = image.streamplot(vx, vy, x1=x, x2=y, c="red")

    npt.assert_allclose(np.asarray(lines.get_color())[0], [1.0, 0.0, 0.0, 1.0])


def test_a_color_wins_over_a_colormap() -> None:
    """Give both a color and a colormap.

    Only one of the two can apply: the color is used and the user is told
    the colormap was dropped. The warning used to look for `colors` instead
    of `c`, so it never fired.
    """
    image = pp.Image(text=False)

    with pytest.warns(UserWarning, match="Both c and cmap are defined"):
        lines = image.streamplot(vx, vy, x1=x, x2=y, c="red", cmap="magma")

    assert _color(lines) == "#ff0000"


def test_a_colormap_colors_by_the_magnitude() -> None:
    """Give a colormap and read the values the lines are colored by.

    They are the magnitude of the field along each line, so they stay
    within the range of the field itself. The colormap used to be passed to
    matplotlib with nothing to map, and did nothing.
    """
    lines = pp.Image(text=False).streamplot(vx, vy, x1=x, x2=y, cmap="magma")

    values = np.asarray(lines.get_array())
    magnitude = np.hypot(vx, vy)
    assert lines.get_cmap().name == "magma"
    assert values.size > 0
    assert values.min() >= magnitude.min() - 1e-12
    assert values.max() <= magnitude.max()


def test_a_colorbar_colors_by_the_magnitude() -> None:
    """Ask for a colorbar and nothing else about the colors.

    The colorbar shows the magnitude of the field, so the lines are colored
    by it: a bar next to single-colored lines would describe nothing on the
    plot, which is what it used to do.
    """
    image = pp.Image(text=False)
    lines = image.streamplot(vx, vy, x1=x, x2=y, cpos="right")

    assert image.fig is not None
    assert len(image.fig.axes) == 2
    assert np.asarray(lines.get_array()).size > 0


def test_colors_is_an_unknown_keyword() -> None:
    """Pass the old `colors` keyword and check it is reported.

    `colors` was deprecated and accepted without effect: read only as a
    presence test, never applied. It is now removed, and like any unknown
    keyword it warns by name while the lines are drawn anyway.
    """
    image = pp.Image(text=False)

    with pytest.warns(UserWarning, match="Unused kwargs: {'colors'}"):
        lines = image.streamplot(vx, vy, colors="red")  # type: ignore[call-overload]

    assert isinstance(lines, LineCollection)


# ---- The style of the lines ----
def test_the_default_linewidth() -> None:
    """Check the width of the lines when none is asked for.

    It is 1.3, as for contour lines, and as the docstring always said.
    """
    lines = pp.Image(text=False).streamplot(vx, vy, x1=x, x2=y)

    npt.assert_allclose(lines.get_linewidth(), 1.3)


def test_the_opacity_reaches_lines_and_arrows() -> None:
    """Draw with an opacity next to a patch that was already there.

    matplotlib's streamplot takes no opacity, and draws its arrows as
    separate patches on the axis, so each is set after drawing. Only the
    arrows of this call change: the patch drawn before keeps its own.
    """
    image = pp.Image(text=False)
    image.create_axes()
    assert isinstance(image.ax[0], Axes)
    before = image.ax[0].add_patch(Rectangle((0.0, 0.0), 0.1, 0.1))

    lines = image.streamplot(vx, vy, x1=x, x2=y, alpha=0.4)

    arrows = [patch for patch in image.ax[0].patches if patch is not before]
    assert lines.get_alpha() == pytest.approx(0.4)
    assert len(arrows) > 0
    assert all(isinstance(arrow, FancyArrowPatch) for arrow in arrows)
    assert all(arrow.get_alpha() == pytest.approx(0.4) for arrow in arrows)
    assert before.get_alpha() is None


# ---- The axis ----
def test_streamplot_axis_range() -> None:
    """Check the axis spans the given coordinates, from -1 to 1."""
    image = pp.Image(text=False)
    image.streamplot(vx, vy, x1=x, x2=y)

    assert isinstance(image.ax[0], Axes)
    assert image.ax[0].get_xlim() == pytest.approx((-1.0, 1.0))


def test_streamplot_title() -> None:
    """Check the title keyword reaches the axis."""
    image = pp.Image(text=False)
    image.streamplot(vx, vy, x1=x, x2=y, title="stream")

    assert isinstance(image.ax[0], Axes)
    assert image.ax[0].get_title() == "stream"


def test_streamplot_labels() -> None:
    """Check the axis labels reach the axis."""
    image = pp.Image(text=False)
    image.streamplot(vx, vy, x1=x, x2=y, xtitle="xx", ytitle="yy")

    assert isinstance(image.ax[0], Axes)
    assert image.ax[0].get_xlabel() == "xx"
    assert image.ax[0].get_ylabel() == "yy"


def test_streamplot_on_second_axis() -> None:
    """Send the lines to the second axis of a two-panel figure.

    They land there, and the first axis is left empty.
    """
    image = pp.Image(text=False)
    image.create_axes(ncol=2)
    image.streamplot(vx, vy, x1=x, x2=y, ax=1)

    assert isinstance(image.ax[0], Axes)
    assert isinstance(image.ax[1], Axes)
    assert len(image.ax[1].collections) > 0
    assert len(image.ax[0].collections) == 0


# ---- The figure ----
def test_a_streamplot_without_a_figure() -> None:
    """Draw on an image whose figure is gone.

    There is nothing to draw on, and saying so is better than the error
    matplotlib would give further down, in a call the user never made.
    """
    image = pp.Image(text=False)
    image.fig = None

    with pytest.raises(ValueError, match="No figure is present"):
        image.streamplot(vx, vy)


def test_the_layout_is_tightened_again() -> None:
    """Draw with a long axis label on a tight figure.

    The layout is redone after every streamplot, since what it adds -- a
    label, a colorbar -- is what the layout has to make room for.
    """
    image = pp.Image(text=False)
    image.streamplot(vx, vy, x1=x, x2=y)
    assert isinstance(image.ax[0], Axes)
    before = image.ax[0].get_position().x0

    image.streamplot(
        vx * 1e6, vy * 1e6, x1=x, x2=y, ytitle="a very long y title indeed"
    )

    assert image.ax[0].get_position().x0 > before


def test_a_loose_layout_is_left_alone() -> None:
    """Draw the same lines on a figure that asked for no tight layout.

    The axis box is where the figure put it and stays there, whatever is
    drawn on it.
    """
    image = pp.Image(text=False, tight=False)
    image.streamplot(vx, vy, x1=x, x2=y)
    assert isinstance(image.ax[0], Axes)
    before = image.ax[0].get_position().x0

    image.streamplot(
        vx * 1e6, vy * 1e6, x1=x, x2=y, ytitle="a very long y title indeed"
    )

    assert image.ax[0].get_position().x0 == before


def test_a_streamplot_says_nothing_of_its_own() -> None:
    """Draw the ordinary way, colorbar included, and listen for warnings.

    Nothing about plain streamlines is worth a warning, and one that appears
    here comes from matplotlib rather than from us.
    """
    image = pp.Image(text=False)

    with warnings.catch_warnings():
        warnings.simplefilter("error")
        lines = image.streamplot(vx, vy, x1=x, x2=y, cpos="right")

    assert isinstance(lines, LineCollection)
