"""Test of the scatter.py file.

ScatterManager draws points rather than a line, and that one difference
decides most of what it does.

The `c` keyword is the awkward part: it is either the color of the points or
a variable to color them by, told apart by what it holds. Numbers are data,
and bring a colormap, a norm and a colorbar with them; anything else is a
color, or a color per point, and is passed on untouched. When it is missing
the points take the next color of the palette, exactly as a line would.

The limits are the other difference. A line is followed, so its limits are
padded and it never touches the frame; a point is a position, so the limits
are the data exactly. They still grow with what is drawn afterwards, which is
what keeps a scatter from freezing the axis for the plots that follow it.
"""

import warnings
from collections.abc import Callable

import numpy as np
import numpy.testing as npt
import pytest
from matplotlib.axes import Axes
from matplotlib.collections import PathCollection
from matplotlib.colors import (
    LogNorm,
    Normalize,
    SymLogNorm,
    TwoSlopeNorm,
    to_rgb,
)
from matplotlib.markers import MarkerStyle

import pyPLUTO as pp

x = np.linspace(0.0, 1.0, 11)
y = x**2
z = 10.0 * y

# The markers, as the number of vertices of the path matplotlib draws: it is
# the only number that tells one marker from another from the outside.
CIRCLE = 26
CROSS = 4
SQUARE = 5
CARET = 3

# One call per form a marker can take, and the shape it must come out as.
MARKERS: list[tuple[Callable[[pp.Image], PathCollection], int]] = [
    (lambda image: image.scatter(x, y), CIRCLE),
    (lambda image: image.scatter(x, y, marker="x"), CROSS),
    (lambda image: image.scatter(x, y, marker=5), CARET),
    (lambda image: image.scatter(x, y, marker=MarkerStyle("s")), SQUARE),
    (lambda image: image.scatter(x, y, marker=["x", "o"]), CROSS),
    (lambda image: image.scatter(x, y, marker=[]), CIRCLE),
]

# The color scales, and the norm each one has to build. The limits differ
# from scale to scale: a logarithm needs both of them positive, and a
# twoslope needs its center, which is the threshold, to fall between them.
CSCALES: list[tuple[Callable[[pp.Image], PathCollection], type[Normalize]]] = [
    (lambda i: i.scatter(x, z + 1.0, c=z + 1.0, cscale="norm"), Normalize),
    (lambda i: i.scatter(x, z + 1.0, c=z + 1.0, cscale="log"), LogNorm),
    (
        lambda i: i.scatter(x, z, c=z, cscale="symlog", vmin=-1.0, vmax=11.0),
        SymLogNorm,
    ),
    (
        lambda i: i.scatter(x, z, c=z, cscale="twoslope", vmin=-1.0, vmax=11.0),
        TwoSlopeNorm,
    ),
]


def _rgb(colour: str) -> tuple[float, float, float]:
    """Return a color as the three numbers matplotlib stores.

    Every color read back off a collection is an RGBA array, so the names
    the tests are written with have to be resolved the same way to be
    compared with it.
    """
    return to_rgb(colour)


def _offsets(points: PathCollection) -> np.ndarray:
    """Return the coordinates of the points as an array of pairs."""
    return np.asarray(points.get_offsets())


def _face(points: PathCollection, index: int = 0) -> np.ndarray:
    """Return the RGB of one point's face.

    matplotlib gives the colors back as rows of RGBA; the alpha is dropped
    here so that every comparison in the tests is three numbers against
    three numbers.
    """
    return np.asarray(points.get_facecolor())[index][:3]


def _corners(points: PathCollection) -> int:
    """Return how many vertices the marker of a collection is drawn with.

    It is the only number that tells one marker from another from the
    outside: a cross has four, a square five, a circle twenty-six.
    """
    return np.asarray(points.get_paths()[0].vertices).shape[0]


def _points(image: pp.Image, nax: int = 0) -> list[PathCollection]:
    """Return the point collections drawn on one axis.

    A scatter is one collection, so counting them is how a second scatter is
    told from a redrawn first one.
    """
    assert isinstance(image.ax[nax], Axes)
    return [
        artist
        for artist in image.ax[nax].collections
        if isinstance(artist, PathCollection)
    ]


# ---- The points that are drawn ----
def test_the_collection_is_returned() -> None:
    """Check the scatter hands back the collection it drew.

    It is the handle for everything done afterwards -- a colorbar of one's
    own, a second axis -- so a scatter that returns nothing cannot be built
    on.
    """
    image = pp.Image(text=False)
    points = image.scatter(x, y)

    assert isinstance(points, PathCollection)


def test_every_point_is_drawn_where_it_was_given() -> None:
    """Read the coordinates back off the collection.

    The pairs are kept in order and unchanged: a scatter is the plot where
    every point is a datum, so none of them may be moved or dropped.
    """
    image = pp.Image(text=False)
    points = image.scatter(x, y)

    npt.assert_allclose(_offsets(points)[:, 0], x)
    npt.assert_allclose(_offsets(points)[:, 1], y)


def test_lists_are_accepted() -> None:
    """Scatter two plain lists rather than arrays.

    They are converted on the way in, so the coordinates a user types at the
    prompt are drawn like any other.
    """
    image = pp.Image(text=False)
    points = image.scatter([0.0, 1.0], [2.0, 3.0])

    assert _offsets(points).shape == (2, 2)


def test_the_size_and_the_opacity() -> None:
    """Set the two keywords that change how a point looks, not where it is.

    `ms` is the area of the marker and `alpha` its opacity; both go straight
    to matplotlib, so a failure means one of them is dropped on the way.
    """
    image = pp.Image(text=False)
    points = image.scatter(x, y, ms=50, alpha=0.5)

    npt.assert_allclose(points.get_sizes(), 50)
    assert points.get_alpha() == 0.5


# ---- The color of the points ----
def test_the_palette_is_walked_as_it_is_for_a_line() -> None:
    """Scatter twice without choosing a color.

    Points and lines share one count per axis, so a scatter drawn next to a
    plot is a different color and the two can be told apart. Left to
    matplotlib instead, the points come out in its own first color, outside
    the palette and outside the scheme every other curve follows.
    """
    image = pp.Image(text=False)
    image.scatter(x, y)
    image.scatter(x, y + 1.0)

    first, second = _points(image)
    npt.assert_allclose(_face(first), _rgb(image.color[0]))
    npt.assert_allclose(_face(second), _rgb(image.color[1]))
    assert image.nline[0] == 2


def test_a_chosen_color_leaves_the_palette_alone() -> None:
    """Scatter in a named color, then scatter without choosing.

    A color given by hand is not a step of the palette, so the next
    automatic scatter still starts from its first color.
    """
    image = pp.Image(text=False)
    image.scatter(x, y, c="silver")
    image.scatter(x, y + 1.0)

    first, second = _points(image)
    npt.assert_allclose(_face(first), _rgb("silver"))
    npt.assert_allclose(_face(second), _rgb(image.color[0]))
    assert image.nline[0] == 1


def test_a_color_for_every_point() -> None:
    """Give one color name per point.

    A list of names is a list of colors, not a variable: weighed as data it
    is handed to `nanmin`, which cannot compare strings and gives up on a
    plot that matplotlib would have drawn.
    """
    image = pp.Image(text=False)
    colours = ["r"] * 6 + ["b"] * 5

    points = image.scatter(x, y, c=colours)

    npt.assert_allclose(_face(points, 0), _rgb("r"))
    npt.assert_allclose(_face(points, -1), _rgb("b"))
    assert points.get_cmap() is not None
    assert image.nline[0] == 0


def test_a_variable_colors_the_points() -> None:
    """Color the points by a third array.

    This is the scatter with a meaning of its own: the variable brings a
    colormap and a norm, and the limits of the norm are the extremes of the
    data, so the colors span the whole map.
    """
    image = pp.Image(text=False)

    points = image.scatter(x, y, c=z, cmap="hot")

    assert points.get_cmap().name == "hot"
    limits = (float(np.min(z)), float(np.max(z)))
    assert points.get_clim() == pytest.approx(limits)
    assert image.nline[0] == 0


def test_the_limits_of_the_colors_are_chosen() -> None:
    """Give `vmin` and `vmax` by hand.

    Fixed color limits are what makes two figures comparable, so they must
    win over the extremes of the data, which differ from file to file.
    """
    image = pp.Image(text=False)

    points = image.scatter(x, y, c=z, vmin=-1.0, vmax=20.0)

    npt.assert_allclose(points.get_clim(), (-1.0, 20.0))
    npt.assert_allclose(image.vlims[0][:2], (-1.0, 20.0))


@pytest.mark.parametrize(("call", "norm"), CSCALES)
def test_the_color_scale(
    call: Callable[[pp.Image], PathCollection], norm: type[Normalize]
) -> None:
    """Ask for each color scale and check the norm that was built.

    The scale is the arithmetic between the data and the colormap, so the
    wrong norm is a figure that looks right and reads wrong.
    """
    image = pp.Image(text=False)

    points = call(image)

    assert isinstance(points.norm, norm)


def test_the_threshold_of_the_composite_scales() -> None:
    """Check the threshold kept on the axis for the scales that need one.

    `symlog` and `twoslope` need a point where the arithmetic changes; it
    defaults to a hundredth of the largest limit, and it is stored with the
    color limits so a colorbar drawn later uses the same one.
    """
    image = pp.Image(text=False)

    image.scatter(x, y, c=z, vmin=-4.0, vmax=8.0, cscale="symlog")

    npt.assert_allclose(image.vlims[0], (-4.0, 8.0, 0.08))


def test_no_colorbar_unless_one_is_asked_for() -> None:
    """Scatter a variable without `cpos`, then with it.

    The colorbar is what a colored scatter is read with, but it takes room
    from the figure, so it is drawn only when a side is named.
    """
    image = pp.Image(text=False)
    image.scatter(x, y, c=z)
    assert image.fig is not None
    assert len(image.fig.axes) == 1

    image.scatter(x, y + 1.0, c=z, cpos="right")

    assert len(image.fig.axes) == 2


# ---- The markers ----
@pytest.mark.parametrize(("call", "vertices"), MARKERS)
def test_the_marker_shapes(
    call: Callable[[pp.Image], PathCollection], vertices: int
) -> None:
    """Ask for a marker in each of the forms accepted, and count its corners.

    A marker is a name, one of the integers matplotlib keeps for the carets,
    a style object, or a list of any of those -- the form the other plots
    use, where there is one per line and a scatter takes the first. An empty
    list is nothing chosen, so the default circle is drawn.
    """
    image = pp.Image(text=False)

    points = call(image)

    assert _corners(points) == vertices


def test_an_unfilled_marker_says_nothing() -> None:
    """Draw the points as crosses and listen for warnings.

    A cross has no inside to fill, so an edge color -- which the scatter
    used to send for every marker -- makes matplotlib warn that it is
    ignoring it. Nothing is wrong with the figure, and nothing should be
    said about it.
    """
    image = pp.Image(text=False)

    with warnings.catch_warnings():
        warnings.simplefilter("error")
        image.scatter(x, y, marker="x")

    assert len(_points(image)) == 1


def test_the_edge_color_is_forwarded() -> None:
    """Ask for an edge of a different color around every point.

    It is how a light marker is kept visible on a light background, so the
    keyword has to reach matplotlib rather than be overruled by the default.
    """
    image = pp.Image(text=False)

    points = image.scatter(x, y, edgecolors="k")

    edge = np.asarray(points.get_edgecolor())[0][:3]
    npt.assert_allclose(edge, _rgb("k"))


def test_something_that_is_not_a_marker() -> None:
    """Pass a number that names no marker at all.

    Nothing can be drawn from it, so the default circle is drawn instead of
    the figure being lost. The checkers refuse the call in the first place;
    this is what happens to the one that gets past them.
    """
    image = pp.Image(text=False)

    points = image.scatter(x, y, marker=1.5)  # type: ignore[call-overload]  # ty: ignore[invalid-argument-type]

    assert _corners(points) == CIRCLE


# ---- The limits ----
def test_the_limits_are_the_data_exactly() -> None:
    """Scatter once and read the limits back.

    A point is a position and not a curve to be followed, so the frame is
    the data: no padding on either axis, unlike a line.
    """
    image = pp.Image(text=False)
    image.scatter(x, y)

    assert isinstance(image.ax[0], Axes)
    npt.assert_allclose(image.ax[0].get_xlim(), (0.0, 1.0))
    npt.assert_allclose(image.ax[0].get_ylim(), (0.0, 1.0))


def test_the_limits_grow_with_the_second_scatter() -> None:
    """Scatter a second, taller set of points on the same axis.

    Without this the axis is frozen by whatever was drawn first and the
    second scatter is outside the frame: drawn, counted, and invisible.
    """
    image = pp.Image(text=False)
    image.scatter(x, y)
    image.scatter(x, z)

    assert isinstance(image.ax[0], Axes)
    npt.assert_allclose(image.ax[0].get_ylim(), (0.0, 10.0))


def test_a_line_drawn_over_a_scatter_is_not_clipped() -> None:
    """Scatter, then plot a line that leaves the scattered range.

    The axis must not be fixed by the scatter, since points and lines are
    drawn together all the time -- particles over a fluid, a fit over its
    data -- and whichever came first would otherwise decide what is seen.
    """
    image = pp.Image(text=False)
    image.scatter(x, y)
    image.plot(x, z)

    assert isinstance(image.ax[0], Axes)
    assert image.ax[0].get_ylim()[1] >= float(np.max(z))


def test_a_range_given_by_hand_is_kept() -> None:
    """Fix the ranges, then scatter points that fall outside them.

    A range the user chose is a decision: the second scatter is drawn
    outside the frame rather than widening it.
    """
    image = pp.Image(text=False)
    image.scatter(x, y, xrange=[0.2, 0.4], yrange=[0.0, 3.0])
    image.scatter(x, z)

    assert isinstance(image.ax[0], Axes)
    npt.assert_allclose(image.ax[0].get_xlim(), (0.2, 0.4))
    npt.assert_allclose(image.ax[0].get_ylim(), (0.0, 3.0))


def test_a_logarithmic_axis() -> None:
    """Scatter on a logarithmic x-axis.

    The scale is set before the limits are computed, so the limits are the
    ones of a log axis and not of a linear one rescaled afterwards.
    """
    image = pp.Image(text=False)
    image.scatter(x + 1.0, y, xscale="log")

    assert isinstance(image.ax[0], Axes)
    assert image.ax[0].get_xscale() == "log"


# ---- The axis ----
def test_the_axis_keywords_are_forwarded() -> None:
    """Give the titles to the scatter call.

    The axis is set from the same keywords as the points, so one call is a
    whole figure.
    """
    image = pp.Image(text=False)
    image.scatter(x, y, title="points", xtitle="xx", ytitle="yy")

    assert isinstance(image.ax[0], Axes)
    assert image.ax[0].get_title() == "points"
    assert image.ax[0].get_xlabel() == "xx"
    assert image.ax[0].get_ylabel() == "yy"


def test_the_axis_is_chosen_by_index() -> None:
    """Scatter on the second of two axes.

    The index is how a panel is aimed at without keeping the objects around,
    and nothing must land on the other one.
    """
    image = pp.Image(text=False)
    image.create_axes(ncol=2)
    image.scatter(x, y, ax=1)

    assert len(_points(image, 1)) == 1
    assert _points(image, 0) == []
    assert image.ntext[1] == 1


# ---- The legend ----
def test_a_legend_is_created_by_legpos() -> None:
    """Ask for a legend from the scatter call.

    The entry describes the points that were drawn, so the label and the
    position given here are enough to say what they are.
    """
    image = pp.Image(text=False)
    image.scatter(x, y, label="particles", legpos="lower right")

    assert isinstance(image.ax[0], Axes)
    legend = image.ax[0].get_legend()
    assert legend is not None
    assert [text.get_text() for text in legend.get_texts()] == ["particles"]


def test_the_position_is_remembered_by_the_axis() -> None:
    """Scatter a second labelled set without repeating `legpos`.

    Once an axis has a legend everything added to it belongs there, so the
    legend is rebuilt with both entries rather than left describing half of
    what is drawn.
    """
    image = pp.Image(text=False)
    image.scatter(x, y, label="one", legpos="upper left")
    image.scatter(x, z, label="two")

    assert isinstance(image.ax[0], Axes)
    legend = image.ax[0].get_legend()
    assert legend is not None
    texts = [text.get_text() for text in legend.get_texts()]
    assert texts == ["one", "two"]


# ---- The figure ----
def test_a_scatter_without_a_figure() -> None:
    """Scatter on an image whose figure is gone.

    There is nothing to draw on, and saying so is better than the error
    matplotlib would give further down, in a call the user never made.
    """
    image = pp.Image(text=False)
    image.fig = None

    with pytest.raises(ValueError, match="No figure is present"):
        image.scatter(x, y)


def test_the_layout_is_tightened_again() -> None:
    """Scatter with a long axis label on a tight figure.

    The layout is redone after every scatter, since what it adds -- a label,
    a colorbar -- is what the layout has to make room for.
    """
    image = pp.Image(text=False)
    image.scatter(x, y)
    assert isinstance(image.ax[0], Axes)
    before = image.ax[0].get_position().x0

    image.scatter(x, 1e6 * y, ytitle="a very long y title indeed")

    assert image.ax[0].get_position().x0 > before


def test_a_loose_layout_is_left_alone() -> None:
    """Scatter the same points on a figure that asked for no tight layout.

    The axis box is where the figure put it and stays there, whatever is
    drawn on it.
    """
    image = pp.Image(text=False, tight=False)
    image.scatter(x, y)
    assert isinstance(image.ax[0], Axes)
    before = image.ax[0].get_position().x0

    image.scatter(x, 1e6 * y, ytitle="a very long y title indeed")

    assert image.ax[0].get_position().x0 == before


def test_an_unknown_keyword_warns() -> None:
    """Misspell a keyword and check the scatter says which one.

    The warning names the method the user called, and the points are drawn
    anyway: a misspelt keyword is not a reason to lose the figure.
    """
    image = pp.Image(text=False)

    with pytest.warns(UserWarning, match="Unused kwargs: {'colour'}"):
        image.scatter(x, y, colour="r")  # type: ignore[call-overload]

    assert len(_points(image)) == 1
