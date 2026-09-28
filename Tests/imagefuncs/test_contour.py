"""Test of the contour.py file.

ContourManager draws the contour lines of a 2D variable, through matplotlib's
contour. Like a map, the variable is indexed as `var[x, y]`, the PLUTO order,
and is transposed on the way out, so most tests use a rectangular array whose
values say where they came from: a transposition cannot pass on it, while a
square test array hides the whole question.

On that array, `var[i, j] = 4 * i + j`, so the contour at level L is the
straight line `4 * x + y = L`. Reading the vertices back and checking that
equation pins the orientation exactly: the transposed variable would put them
on `x + 4 * y = L` instead.

The coordinates `x1` and `x2` are where the values sit, one per cell, so
without them the lines are drawn on the cell indices. The lines are colored
by the colormap through the same color scales as a map, unless a color `c`
replaces it -- matplotlib takes only one of the two, so `c` wins over `cmap`.
"""

import warnings
from collections.abc import Callable

import numpy as np
import numpy.testing as npt
import pytest
from matplotlib.axes import Axes
from matplotlib.colors import LogNorm, Normalize, SymLogNorm, TwoSlopeNorm
from matplotlib.contour import QuadContourSet

import pyPLUTO as pp

# A rectangular variable, so that an accidental transposition cannot pass,
# with values that say where they came from: var[i, j] is 4 * i + j.
var = np.arange(24.0).reshape(6, 4)

# A simple bowl-shaped function, whose contours are circles, on a grid from
# -1 to 1: used where only the levels and the axis matter.
x = np.linspace(-1, 1, 30)
y = np.linspace(-1, 1, 30)
x2d, y2d = np.meshgrid(x, y, indexing="ij")
bowl = x2d**2 + y2d**2

# The color scales and the norm each one has to build.
CSCALES: list[tuple[Callable[[pp.Image], QuadContourSet], type[Normalize]]] = [
    (lambda i: i.contour(var, cscale="norm"), Normalize),
    (lambda i: i.contour(var + 1.0, cscale="log"), LogNorm),
    (
        lambda i: i.contour(var, cscale="symlog", vmin=-4.0, vmax=8.0),
        SymLogNorm,
    ),
    (
        lambda i: i.contour(var, cscale="twoslope", vmin=-4.0, vmax=8.0),
        TwoSlopeNorm,
    ),
]


def _vertices(lines: QuadContourSet) -> np.ndarray:
    """Return every vertex of the drawn lines, one (x, y) pair per row."""
    paths = [np.asarray(path.vertices) for path in lines.get_paths()]
    paths = [vertices for vertices in paths if len(vertices)]
    assert len(paths) >= 1
    return np.concatenate(paths)


def _levels(lines: QuadContourSet) -> np.ndarray:
    """Return the drawn levels as an array, which matplotlib types loosely."""
    return np.asarray(lines.levels)


def _edgecolors(lines: QuadContourSet) -> np.ndarray:
    """Return the color of each level, one RGBA row per level."""
    return np.asarray(lines.get_edgecolor())


# ---- The lines that are drawn ----
def test_contour_returns_contourset() -> None:
    """Check the contour hands back the set of lines it drew.

    It is what a colorbar is built from and what a user reads the levels
    from, so a contour that returns nothing cannot be given either.
    """
    image = pp.Image(text=False)
    lines = image.contour(bowl, x1=x, x2=y)

    assert isinstance(lines, QuadContourSet)


def test_contour_draws_on_axis() -> None:
    """Check the lines end up on the current axis.

    A set of lines that is returned but never added to the axis is a figure
    that stays empty.
    """
    image = pp.Image(text=False)
    image.contour(bowl, x1=x, x2=y)

    assert isinstance(image.ax[0], Axes)
    assert len(image.ax[0].collections) > 0


def test_the_variable_is_indexed_x_first() -> None:
    """Draw one level and check the equation its vertices lie on.

    `var[i, j]` is the value at the i-th x and the j-th y, so the level 10
    is the line `4 * x + y = 10`, running from x = 1.75 at the top to x = 2.5
    at the bottom. A variable drawn the other way round puts the line on
    `x + 4 * y = 10`, a figure that looks plausible and is wrong everywhere.
    """
    image = pp.Image(text=False)
    lines = image.contour(var, levels=[10.0])

    vertices = _vertices(lines)
    npt.assert_allclose(4 * vertices[:, 0] + vertices[:, 1], 10.0)
    npt.assert_allclose(vertices.min(axis=0), (1.75, 0.0))
    npt.assert_allclose(vertices.max(axis=0), (2.5, 3.0))


def test_without_coordinates_the_lines_are_drawn_on_the_indices() -> None:
    """Draw a variable and nothing else, then read the limits.

    The coordinates are then the cell numbers, one point per cell, so the
    axis runs from 0 to one less than the number of cells in each direction:
    0 to 5 along x and 0 to 3 along y for a 6 x 4 variable.
    """
    image = pp.Image(text=False)
    image.contour(var)

    assert isinstance(image.ax[0], Axes)
    npt.assert_allclose(image.ax[0].get_xlim(), (0.0, 5.0))
    npt.assert_allclose(image.ax[0].get_ylim(), (0.0, 3.0))


def test_a_transposed_variable_draws_the_same_lines() -> None:
    """Draw `var.T` declared as transposed and compare with `var`.

    `transpose` says the variable is given as `var[y, x]`, so the lines have
    to be the same ones. The default coordinates used to be built before the
    transposition, from the wrong shape, so any rectangular variable raised
    a TypeError from matplotlib.
    """
    straight = pp.Image(text=False).contour(var, levels=[10.0])
    turned = pp.Image(text=False).contour(var.T, levels=[10.0], transpose=True)

    npt.assert_allclose(
        np.sort(_vertices(turned), axis=0),
        np.sort(_vertices(straight), axis=0),
    )


# ---- The levels ----
def test_contour_explicit_levels() -> None:
    """Give the levels as a list and read them back.

    A list is used as it is, which is how a user draws the one value that
    matters -- a shock front, a density threshold -- and nothing else.
    """
    image = pp.Image(text=False)
    lines = image.contour(bowl, x1=x, x2=y, levels=[0.25, 0.5, 0.75])

    assert list(_levels(lines)) == [0.25, 0.5, 0.75]


def test_contour_number_of_levels() -> None:
    """Ask for few levels, then for many, and compare.

    An integer is a hint to matplotlib, which picks round values near that
    number rather than exactly that many, so only the direction is checked:
    asking for more really gives more.
    """
    few = pp.Image(text=False).contour(bowl, x1=x, x2=y, levels=3)
    many = pp.Image(text=False).contour(bowl, x1=x, x2=y, levels=20)

    assert len(_levels(many)) > len(_levels(few))


def test_contour_levels_are_ordered() -> None:
    """Ask for a number of levels and check what matplotlib chose.

    They are increasing and bracket the data, so every value of the variable
    falls between two drawn levels.
    """
    lines = pp.Image(text=False).contour(bowl, x1=x, x2=y, levels=8)

    levels = _levels(lines)
    assert list(levels) == sorted(levels)
    assert levels[0] <= np.min(bowl)
    assert levels[-1] >= np.max(bowl)


def test_the_default_levels_span_the_color_limits() -> None:
    """Give no levels and check the ten that are drawn.

    They are evenly spaced from `vmin` to `vmax`, both included, so the
    limits of the color scale are also the outermost lines.
    """
    lines = pp.Image(text=False).contour(var, vmin=5.0, vmax=10.0)

    npt.assert_allclose(_levels(lines), np.linspace(5.0, 10.0, 10))


def test_logarithmic_levels_go_by_decades() -> None:
    """Ask for a number of levels on a logarithmic scale.

    The levels follow the color scale, so on a logarithmic one matplotlib
    picks powers of ten, each ten times the previous.
    """
    lines = pp.Image(text=False).contour(var + 1.0, cscale="log", levels=3)

    levels = _levels(lines)
    npt.assert_allclose(levels[1:] / levels[:-1], 10.0)


# ---- The color scale ----
@pytest.mark.parametrize(("call", "norm"), CSCALES)
def test_the_color_scale(
    call: Callable[[pp.Image], QuadContourSet], norm: type[Normalize]
) -> None:
    """Ask for each color scale and check the norm that was built.

    The scale decides which color each level gets, so the wrong norm is a
    set of lines that looks right and reads wrong.
    """
    image = pp.Image(text=False)

    lines = call(image)

    assert isinstance(lines.norm, norm)


def test_the_default_threshold() -> None:
    """Check the threshold of a symmetric logarithmic scale.

    It is a hundredth of the largest limit by default: 0.08 for limits of
    -4 and 8, where the scale turns from linear to logarithmic.
    """
    lines = pp.Image(text=False).contour(
        var, cscale="symlog", vmin=-4.0, vmax=8.0
    )

    assert isinstance(lines.norm, SymLogNorm)
    assert lines.norm.linthresh == pytest.approx(0.08)


# ---- The colors ----
def test_the_default_colormap_is_viridis() -> None:
    """Draw without a color or a colormap.

    The default differs from the plasma of a map on purpose, so lines drawn
    over a display stand out from it.
    """
    lines = pp.Image(text=False).contour(var)

    assert lines.get_cmap().name == "viridis"


def test_contour_cmap() -> None:
    """Choose a colormap and check it is the one applied."""
    image = pp.Image(text=False)
    lines = image.contour(bowl, x1=x, x2=y, cmap="magma")

    assert lines.get_cmap().name == "magma"


def test_a_single_color_paints_every_line() -> None:
    """Give one color and check every level carries it.

    A single color replaces the colormap, which is how contours are drawn in
    black over a map.
    """
    lines = pp.Image(text=False).contour(var, c="k", levels=[5.0, 10.0])

    npt.assert_allclose(_edgecolors(lines), [[0, 0, 0, 1], [0, 0, 0, 1]])


def test_a_list_of_colors_goes_level_by_level() -> None:
    """Give one color per level and check each one is applied in order."""
    lines = pp.Image(text=False).contour(var, c=["r", "b"], levels=[5.0, 10.0])

    npt.assert_allclose(_edgecolors(lines), [[1, 0, 0, 1], [0, 0, 1, 1]])


def test_a_color_wins_over_a_colormap() -> None:
    """Give both a color and a colormap.

    matplotlib accepts only one of the two and used to raise, even though a
    warning was written for exactly this case: it looked for `colors`
    instead of `c`, so it never fired. Now the color is used and the user is
    told the colormap was dropped.
    """
    image = pp.Image(text=False)

    with pytest.warns(UserWarning, match="Both c and cmap are defined"):
        lines = image.contour(var, c="k", cmap="magma", levels=[10.0])

    npt.assert_allclose(_edgecolors(lines), [[0, 0, 0, 1]])


def test_colors_is_an_unknown_keyword() -> None:
    """Pass the old `colors` keyword and check it is reported.

    `colors` was deprecated and accepted without effect: read only as a
    presence test, never applied, so `colors="red"` drew in viridis without
    a word. It is now removed, and like any unknown keyword it warns by name
    while the lines are drawn anyway.
    """
    image = pp.Image(text=False)

    with pytest.warns(UserWarning, match="Unused kwargs: {'colors'}"):
        lines = image.contour(var, colors="red")  # type: ignore[call-overload]

    assert isinstance(lines, QuadContourSet)


# ---- The style of the lines ----
def test_the_default_linewidth() -> None:
    """Check the width of the lines when none is asked for."""
    lines = pp.Image(text=False).contour(var)

    npt.assert_allclose(lines.get_linewidth(), 1.3)


def test_the_opacity_and_width_are_applied() -> None:
    """Give an opacity and a width and read both back from the lines."""
    lines = pp.Image(text=False).contour(var, alpha=0.4, lw=3.0)

    assert lines.get_alpha() == pytest.approx(0.4)
    npt.assert_allclose(lines.get_linewidth(), 3.0)


# ---- The axis ----
def test_contour_title() -> None:
    """Check the title keyword reaches the axis."""
    image = pp.Image(text=False)
    image.contour(bowl, x1=x, x2=y, title="bowl")

    assert isinstance(image.ax[0], Axes)
    assert image.ax[0].get_title() == "bowl"


def test_contour_labels() -> None:
    """Check the axis labels reach the axis."""
    image = pp.Image(text=False)
    image.contour(bowl, x1=x, x2=y, xtitle="xx", ytitle="yy")

    assert isinstance(image.ax[0], Axes)
    assert image.ax[0].get_xlabel() == "xx"
    assert image.ax[0].get_ylabel() == "yy"


def test_contour_axis_range() -> None:
    """Check the axis spans the given coordinates, from -1 to 1."""
    image = pp.Image(text=False)
    image.contour(bowl, x1=x, x2=y)

    assert isinstance(image.ax[0], Axes)
    assert image.ax[0].get_xlim() == pytest.approx((-1.0, 1.0))


def test_contour_on_second_axis() -> None:
    """Send the lines to the second axis of a two-panel figure.

    They land there, and the first axis is left empty.
    """
    image = pp.Image(text=False)
    image.create_axes(ncol=2)
    image.contour(bowl, x1=x, x2=y, ax=1)

    assert isinstance(image.ax[0], Axes)
    assert isinstance(image.ax[1], Axes)
    assert len(image.ax[1].collections) > 0
    assert len(image.ax[0].collections) == 0


def test_no_colorbar_unless_one_is_asked_for() -> None:
    """Draw without `cpos`, then with it.

    A colorbar takes room from the figure, so it is drawn only when a side
    is named.
    """
    image = pp.Image(text=False)
    image.contour(var)
    assert image.fig is not None
    assert len(image.fig.axes) == 1

    image.contour(var, cpos="right")

    assert len(image.fig.axes) == 2


# ---- The figure ----
def test_a_contour_without_a_figure() -> None:
    """Draw on an image whose figure is gone.

    There is nothing to draw on, and saying so is better than the error
    matplotlib would give further down, in a call the user never made.
    """
    image = pp.Image(text=False)
    image.fig = None

    with pytest.raises(ValueError, match="No figure is present"):
        image.contour(var)


def test_the_layout_is_tightened_again() -> None:
    """Draw with a long axis label on a tight figure.

    The layout is redone after every contour, since what it adds -- a
    label, a colorbar -- is what the layout has to make room for.
    """
    image = pp.Image(text=False)
    image.contour(var)
    assert isinstance(image.ax[0], Axes)
    before = image.ax[0].get_position().x0

    image.contour(var * 1e6, ytitle="a very long y title indeed")

    assert image.ax[0].get_position().x0 > before


def test_a_loose_layout_is_left_alone() -> None:
    """Draw the same lines on a figure that asked for no tight layout.

    The axis box is where the figure put it and stays there, whatever is
    drawn on it.
    """
    image = pp.Image(text=False, tight=False)
    image.contour(var)
    assert isinstance(image.ax[0], Axes)
    before = image.ax[0].get_position().x0

    image.contour(var * 1e6, ytitle="a very long y title indeed")

    assert image.ax[0].get_position().x0 == before


def test_a_contour_says_nothing_of_its_own() -> None:
    """Draw the ordinary way, colorbar included, and listen for warnings.

    Nothing about plain contour lines is worth a warning, and one that
    appears here comes from matplotlib rather than from us.
    """
    image = pp.Image(text=False)

    with warnings.catch_warnings():
        warnings.simplefilter("error")
        lines = image.contour(var, cpos="right")

    assert isinstance(lines, QuadContourSet)
