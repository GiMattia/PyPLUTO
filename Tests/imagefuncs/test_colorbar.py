"""Test of the colorbar.py file.

ColorbarManager draws the colorbar of a collection: the one it is given, or
the last one on the axis that is colored by data -- a map, contour lines,
points or streamlines colored by a variable. Lines drawn in a single color
carry no scale and are skipped, which is what lets black contours over a map
leave the colorbar to the map.

The bar is cut from one side of the axis, `cpad` inches past the tick labels
and titles the axis draws there, with its own ticks and label on the outer
side; a second bar on the same axis is cut from the same divider, so the two
never overlap. It can also be placed in a given axis, never the one it
describes. Contour lines get a continuous bar on their scale, as a map does,
unless `fillmap` is False. The ticks follow the rules of `xticks` and
`xtickslabels` -- True automatic, None removed, a list fixed -- through the
same `set_ticks`.

Where the colorbar lands is only settled once the figure is drawn, since the
new axis is positioned by a locator at draw time, so the placement tests draw
the canvas before reading any box.
"""

import inspect
import warnings
from collections.abc import Callable
from typing import Any

import numpy as np
import numpy.testing as npt
import pytest
from matplotlib.axes import Axes
from matplotlib.cm import ScalarMappable
from matplotlib.collections import QuadMesh
from matplotlib.colorbar import Colorbar
from matplotlib.transforms import Bbox

import pyPLUTO as pp
from pyPLUTO.imagefuncs.colorbar import ColorbarManager
from pyPLUTO.utils.pperrors import (
    PyPLUTOAxisError,
    PyPLUTODataError,
    PyPLUTOInternalError,
    PyPLUTOOptionError,
)
from pyPLUTO.utils.ppwarnings import PyPLUTOConflictWarning

# A bowl-shaped variable from 0 at the center to 2 in the corners.
x = np.linspace(-1, 1, 20)
x2d, y2d = np.meshgrid(x, x, indexing="ij")
var = x2d**2 + y2d**2

# Every side a bar can take, with the orientation it gets there.
SIDES = [
    pytest.param("right", "vertical", id="right"),
    pytest.param("left", "vertical", id="left"),
    pytest.param("top", "horizontal", id="top"),
    pytest.param("bottom", "horizontal", id="bottom"),
]


def bowl_image() -> pp.Image:
    """Return an image holding one map of the bowl."""
    image = pp.Image(text=False)
    image.display(var, x1=x, x2=x)
    return image


def titled_image() -> pp.Image:
    """Return a map with tick labels, axis titles and a panel title."""
    image = pp.Image(text=False)
    image.display(var, x1=x, x2=x, xtitle="x", ytitle="y", title="bowl")
    return image


def box(axis: Axes) -> Bbox:
    """Return where an axis is drawn, in pixels, after drawing the figure."""
    figure = axis.get_figure()
    assert figure is not None
    figure.canvas.draw()
    return axis.get_window_extent()


def steps(cbar: Colorbar) -> int:
    """Return how many colors the bar is painted with."""
    assert cbar.solids is not None
    return np.asarray(cbar.solids.get_array()).size


def drawn_texts(axis: Axes) -> list[Bbox]:
    """Return where every visible text of an axis is drawn, in pixels.

    The tick labels, the axis titles and the panel title: what a bar placed
    next to the axis must not cover.
    """
    box(axis)
    texts = [
        *axis.get_xticklabels(),
        *axis.get_yticklabels(),
        axis.xaxis.label,
        axis.yaxis.label,
        axis.title,
    ]
    return [t.get_window_extent() for t in texts if t.get_text()]


# ---- Where the colorbar goes ----
def test_the_default_side_is_the_documented_one() -> None:
    """Draw a bar with no side and read the side the docstring promises.

    Both must be the right: the code runs `kwargs.get("cpos", "right")`,
    while the docstring said "default None", so a user read that no
    colorbar would be placed and got one on the right.
    """
    documented = inspect.getdoc(ColorbarManager.colorbar) or ""
    entry = next(
        line for line in documented.splitlines() if line.startswith("- cpos:")
    )
    image = bowl_image()
    cbar = image.colorbar()

    assert isinstance(image.ax[0], Axes)
    assert "default 'right'" in entry
    assert box(cbar.ax).x0 >= box(image.ax[0]).x1


@pytest.mark.parametrize(("cpos", "orientation"), SIDES)
def test_colorbar_positions(cpos: str, orientation: str) -> None:
    """Ask for each side and check where the bar is drawn.

    The bar lies wholly on that side of the axis, and runs along it:
    upright beside the axis, lying down above or below it. Its ticks and
    label are on the outer side, away from the axis; matplotlib puts them
    on the right or at the bottom whatever the side, so on the left and on
    top they faced the axis.
    """
    image = bowl_image()
    cbar = image.colorbar(cpos=cpos)

    assert isinstance(image.ax[0], Axes)
    axis, bar = box(image.ax[0]), box(cbar.ax)
    side = {
        "right": bar.x0 >= axis.x1,
        "left": bar.x1 <= axis.x0,
        "top": bar.y0 >= axis.y1,
        "bottom": bar.y1 <= axis.y0,
    }
    assert side[cpos]
    assert cbar.orientation == orientation
    along = cbar.ax.yaxis if orientation == "vertical" else cbar.ax.xaxis
    assert along.get_ticks_position() == cpos
    assert along.get_label_position() == cpos


@pytest.mark.parametrize(("cpos", "orientation"), SIDES)
def test_the_bar_covers_nothing_the_axis_draws(
    cpos: str, orientation: str
) -> None:
    """Put a bar on each side of a map with every title, and look for overlaps.

    The gap is measured from what the axis draws on that side -- its tick
    labels, its axis title, on top the panel title -- not from its frame,
    which those lie outside of. Measured from the frame, the bar covered the
    y tick labels on the left, the x title below and the title on top.
    """
    image = titled_image()
    assert isinstance(image.ax[0], Axes)
    cbar = image.colorbar(cpos=cpos)

    bar = box(cbar.ax)
    assert cbar.orientation == orientation
    assert not [t for t in drawn_texts(image.ax[0]) if t.overlaps(bar)]


@pytest.mark.parametrize(
    ("cpad", "pixels"),
    [pytest.param(0.07, 7.0, id="default"), pytest.param(0.5, 50.0, id="wide")],
)
def test_the_gap_is_in_inches(cpad: float, pixels: float) -> None:
    """Draw with a padding and measure the gap in pixels.

    `cpad` is the space between the axis and the bar in inches, so at 100
    dots per inch 0.07 leaves 7 pixels and 0.5 leaves 50. Nothing is drawn
    on the right of a map, so the gap is `cpad` alone: the last x tick
    label, which overhangs the corner, does not count, since it does not
    face the bar.
    """
    image = pp.Image(text=False, tight=False)
    image.display(var)
    assert image.fig is not None
    image.fig.set_dpi(100)
    cbar = image.colorbar(cpad=cpad)

    assert isinstance(image.ax[0], Axes)
    gap = box(cbar.ax).x0 - box(image.ax[0]).x1
    assert gap == pytest.approx(pixels, abs=0.5)


def test_two_bars_on_one_map() -> None:
    """Put a bar on each side of the same map.

    Both are cut from the same divider, so each knows of the other: the map
    shrinks for both and nothing overlaps. A new divider per bar placed the
    second one without knowing of the first, and the left bar landed on the
    y tick labels.
    """
    image = titled_image()
    assert isinstance(image.ax[0], Axes)
    left = image.colorbar(cpos="left")
    right = image.colorbar(cpos="right")

    bars = [box(left.ax), box(right.ax)]
    texts = drawn_texts(image.ax[0])
    assert not [t for t in texts for b in bars if t.overlaps(b)]
    assert (
        bars[0].x1 <= box(image.ax[0]).x0 <= box(image.ax[0]).x1 <= bars[1].x0
    )


def test_a_side_that_does_not_exist() -> None:
    """Misspell the side, and get the four sides named.

    The value used to reach matplotlib, whose message speaks of a
    "position" the user never wrote.
    """
    image = bowl_image()

    with pytest.raises(PyPLUTOOptionError, match="'left', 'right', 'top'"):
        image.colorbar(cpos="rigth")


def test_a_colorbar_in_a_given_axis() -> None:
    """Put the bar of the first panel into the second, by index.

    No new axis is cut: the second panel becomes the colorbar.
    """
    image = pp.Image(text=False)
    image.create_axes(ncol=2)
    image.display(var, ax=0)
    assert image.fig is not None
    naxes = len(image.fig.axes)

    cbar = image.colorbar(axs=0, cax=1)

    assert cbar.ax is image.ax[1]
    assert len(image.fig.axes) == naxes


def test_a_given_axis_takes_the_side_of_its_ticks() -> None:
    """Put the bar in a given axis, on the left of the panel it describes.

    With cax, cpos still says where the bar stands, so its ticks and label
    go on the outer side as for a bar cut from the axis.
    """
    image = pp.Image(text=False)
    image.create_axes(ncol=2)
    image.display(var, ax=1)

    cbar = image.colorbar(axs=1, cax=0, cpos="left")

    assert cbar.ax.yaxis.get_ticks_position() == "left"
    assert cbar.ax.yaxis.get_label_position() == "left"


def test_the_axis_described_is_not_a_place_for_the_bar() -> None:
    """Give as cax the axis whose map the bar describes.

    The bar was drawn inside the panel, over the map, without a word. It
    is refused, and the panel is left as it was.
    """
    image = pp.Image(text=False)
    image.create_axes(ncol=2)
    mesh = image.display(var, ax=0)

    with pytest.raises(PyPLUTOAxisError, match="cax is the axis"):
        image.colorbar(axs=0, cax=0)

    assert isinstance(image.ax[0], Axes)
    assert list(image.ax[0].collections) == [mesh]


# ---- What the colorbar describes ----
def test_the_colorbar_is_returned() -> None:
    """Check the call hands back the colorbar, built on the map.

    It is what a user adjusts afterwards -- its label, its ticks -- as every
    drawing method returns what it drew.
    """
    image = pp.Image(text=False)
    mesh = image.display(var)

    cbar = image.colorbar()

    assert isinstance(cbar, Colorbar)
    assert cbar.mappable is mesh


def test_colorbar_from_collection() -> None:
    """Give the collection explicitly and check it is the one described."""
    image = pp.Image(text=False)
    mesh = image.display(var)

    cbar = image.colorbar(pcm=mesh, cpos="right")

    assert cbar.mappable is mesh


def test_a_collection_wins_over_an_axis() -> None:
    """Give both a collection and an axis.

    The collection already knows its axis, so it is used, and the user is
    told the axis was not.
    """
    image = pp.Image(text=False)
    mesh = image.display(var)

    with pytest.warns(PyPLUTOConflictWarning, match="pcm will be used"):
        cbar = image.colorbar(pcm=mesh, axs=0)

    assert cbar.mappable is mesh


@pytest.mark.parametrize(
    "draw",
    [
        lambda image: image.contour(var),
        lambda image: image.streamplot(-y2d, x2d, cmap="magma"),
        lambda image: image.scatter(x, x, c=x),
    ],
    ids=["contour", "streamplot", "scatter"],
)
def test_any_collection_colored_by_data(
    draw: Callable[[pp.Image], ScalarMappable],
) -> None:
    """Draw something that is not a map and ask for its colorbar.

    Only a map was accepted before: the first collection had to be a
    QuadMesh, and anything else raised "First collection is not a QuadMesh".
    """
    image = pp.Image(text=False)
    drawn = draw(image)

    cbar = image.colorbar()

    assert cbar.norm.vmin == pytest.approx(drawn.norm.vmin)
    assert cbar.norm.vmax == pytest.approx(drawn.norm.vmax)


def test_the_last_collection_colored_by_data() -> None:
    """Draw contour lines, then a map on top, and ask for a colorbar.

    It describes the map: the last thing colored by data, rather than the
    first collection of the axis, which is where the lines are.
    """
    image = pp.Image(text=False)
    image.contour(var * 10.0)
    mesh = image.display(var)

    cbar = image.colorbar()

    assert cbar.mappable is mesh


@pytest.mark.parametrize(
    "overlay",
    [
        lambda image: image.contour(var * 10.0, c="k"),
        lambda image: image.scatter(x, x),
        lambda image: image.streamplot(-y2d, x2d, x1=x, x2=x, c="k"),
    ],
    ids=["black-contours", "plain-points", "plain-streamlines"],
)
def test_single_colored_lines_are_skipped(
    overlay: Callable[[pp.Image], object],
) -> None:
    """Draw a map, then something in one color over it.

    A single color carries no scale, so the colorbar still describes the
    map. Contour lines are the case that needs care: they keep their levels
    even when drawn in black, and would otherwise take the colorbar over.
    """
    image = pp.Image(text=False)
    mesh = image.display(var)
    overlay(image)

    cbar = image.colorbar()

    assert cbar.mappable is mesh


def test_an_axis_with_nothing_to_describe() -> None:
    """Ask for a colorbar on an empty axis.

    There is no scale to draw, and saying so is better than the IndexError
    that came out of reading a first collection that does not exist.
    """
    image = pp.Image(text=False)
    image.create_axes()

    with pytest.raises(PyPLUTODataError, match="No collection colored by data"):
        image.colorbar()


def test_a_collection_drawn_nowhere() -> None:
    """Give a collection that was never added to an axis.

    Its axis is where the bar would be placed, so without one there is
    nowhere to put it.
    """
    image = pp.Image(text=False)

    with pytest.raises(PyPLUTOInternalError, match="Expected an Axes instance"):
        image.colorbar(pcm=QuadMesh(np.zeros((2, 2, 2))))


def test_a_second_colorbar() -> None:
    """Ask for a colorbar twice on the same map.

    After the first, matplotlib holds the colorbar axis as its current one,
    which is not an axis of the image; reading it as one raised a
    ValueError. The second call finds the map's axis again.
    """
    image = bowl_image()
    image.colorbar()

    cbar = image.colorbar(cpos="left")

    assert cbar.mappable is image.ax[0].collections[0]


def test_contour_lines_get_a_continuous_bar() -> None:
    """Draw six levels and count the colors of their colorbar.

    matplotlib paints one block per level band; the bar is built instead
    from the scale of the lines, so it is as continuous as a map's -- every
    color of the colormap -- and spans the same limits.
    """
    image = pp.Image(text=False)
    lines = image.contour(var, levels=6, cmap="magma")

    cbar = image.colorbar()

    assert steps(cbar) == 256
    assert cbar.cmap.name == "magma"
    assert cbar.norm.vmin == pytest.approx(lines.norm.vmin)
    assert cbar.norm.vmax == pytest.approx(lines.norm.vmax)


def test_fillmap_off_gives_the_bar_of_the_lines() -> None:
    """Draw contour lines and ask for matplotlib's own bar with fillmap=False.

    The bar then describes the contour set itself, with a line drawn at
    each level, instead of a continuous scale built from it.
    """
    image = pp.Image(text=False)
    lines = image.contour(var, levels=6, cmap="magma")

    cbar = image.colorbar(fillmap=False)

    assert cbar.mappable is lines
    assert len(cbar.lines) == 1
    assert len(cbar.lines[0].get_segments()) == len(list(lines.levels))


# ---- The ticks and the label ----
def test_colorbar_label() -> None:
    """Check the label is written along the bar."""
    image = bowl_image()
    cbar = image.colorbar(cpos="right", clabel="rho")

    assert cbar.ax.get_ylabel() == "rho"


def test_colorbar_ticks() -> None:
    """Fix the ticks and read them back."""
    image = bowl_image()
    cbar = image.colorbar(cpos="right", cticks=[0.0, 1.0, 2.0])

    npt.assert_allclose(cbar.ax.get_yticks(), [0.0, 1.0, 2.0])


def test_no_ticks() -> None:
    """Remove the ticks with None, as for xticks.

    None used to mean automatic, so a bar without ticks could only be asked
    for with an empty list. Neither major nor minor ticks are left.
    """
    image = bowl_image()
    cbar = image.colorbar(cticks=None)

    assert list(cbar.ax.yaxis.get_majorticklocs()) == []
    assert list(cbar.ax.yaxis.get_minorticklocs()) == []


def test_no_ticks_on_a_log_colorbar() -> None:
    """Remove the ticks of a colorbar on a logarithmic scale.

    A log colorbar has minor ticks of its own at every multiple of each
    decade, which removing the major ones used to leave behind: cticks
    goes through the same set_ticks as xticks.
    """
    image = pp.Image(text=False)
    image.display(var + 0.01, cscale="log")
    cbar = image.colorbar(cticks=None)
    box(cbar.ax)

    assert list(cbar.ax.yaxis.get_majorticklocs()) == []
    assert list(cbar.ax.yaxis.get_minorticklocs()) == []


def test_fixed_ticks_on_a_log_colorbar_keep_their_labels() -> None:
    """Fix the ticks of a log colorbar between the decades.

    A log colorbar labels its powers of ten only, so a tick at 0.5 was
    drawn without a label, as on a log axis: cticks goes through the same
    set_ticks as xticks, and gets the same labels.
    """
    image = pp.Image(text=False)
    image.display(var + 0.01, cscale="log")
    cbar = image.colorbar(cticks=[0.5, 1.0])
    box(cbar.ax)

    labels = [label.get_text() for label in cbar.ax.get_yticklabels()]
    assert labels == [
        r"$\mathdefault{5\times10^{-1}}$",
        r"$\mathdefault{10^{0}}$",
    ]


def test_ticks_and_labels_from_an_array() -> None:
    """Fix the ticks with an array and label them.

    The labels used to be applied through `cticks or ...`, which an array
    refuses: its truth value is ambiguous. An array is not among the
    declared types of cticks, hence `Any`.
    """
    image = bowl_image()
    ticks: Any = np.array([0.5, 1.0])
    cbar = image.colorbar(cticks=ticks, ctickslabels=["a", "b"])
    box(cbar.ax)

    npt.assert_allclose(cbar.ax.get_yticks(), [0.5, 1.0])
    assert [t.get_text() for t in cbar.ax.get_yticklabels()] == ["a", "b"]


def test_labels_on_a_horizontal_bar() -> None:
    """Label the ticks of a bar placed on top, which runs along x."""
    image = bowl_image()
    cbar = image.colorbar(
        cpos="top", cticks=[0.5, 1.0], ctickslabels=["a", "b"]
    )
    box(cbar.ax)

    assert [t.get_text() for t in cbar.ax.get_xticklabels()] == ["a", "b"]


def test_no_labels() -> None:
    """Remove the labels with None and keep the ticks, as for xtickslabels."""
    image = bowl_image()
    cbar = image.colorbar(ctickslabels=None)
    box(cbar.ax)

    assert len(cbar.ax.get_yticks()) > 0
    assert {t.get_text() for t in cbar.ax.get_yticklabels()} == {""}


def test_labels_on_automatic_ticks() -> None:
    """Label the ticks of a bar without choosing them.

    A bar keeps no ticks from earlier calls, so labels given without ticks
    have nothing known to go on: they are ignored with a warning and the
    bar keeps matplotlib's own labels. A failure means labels were written
    on ticks nobody chose.
    """
    image = bowl_image()

    with pytest.warns(PyPLUTOConflictWarning, match="without ticks"):
        cbar = image.colorbar(ctickslabels=["a", "b", "c"])
    box(cbar.ax)

    labels = [t.get_text() for t in cbar.ax.get_yticklabels()]
    assert all(labels)
    assert not {"a", "b", "c"} & set(labels)


def test_labels_without_ticks_warn() -> None:
    """Give labels while removing the ticks.

    There is nothing to put them on, and the user is told so rather than
    seeing them disappear.
    """
    image = bowl_image()

    with pytest.warns(PyPLUTOConflictWarning, match="without ticks"):
        cbar = image.colorbar(cticks=None, ctickslabels=["a"])

    assert list(cbar.ax.get_yticks()) == []


def test_the_extensions() -> None:
    """Ask for extensions at both ends, rectangular rather than triangular."""
    image = bowl_image()
    cbar = image.colorbar(extend="both", extendrect=True)

    assert cbar.extend == "both"
    assert cbar.extendrect is True


# ---- Finding the axis and the space around it ----
def test_find_ax_from_collection() -> None:
    """Check a collection gives the axis it was drawn on."""
    image = pp.Image(text=False)
    mesh = image.display(var)
    manager = ColorbarManager(image.state)

    assert manager.find_ax(mesh, None) is image.ax[0]


def test_find_ax_default() -> None:
    """Check that without a collection the last considered axis is taken."""
    image = bowl_image()
    manager = ColorbarManager(image.state)

    assert manager.find_ax(None, None) is image.ax[0]


def test_find_ax_by_index() -> None:
    """Check an axis can be selected by its index."""
    image = pp.Image(text=False)
    image.create_axes(ncol=2)
    manager = ColorbarManager(image.state)

    assert manager.find_ax(None, 1) is image.ax[1]


def test_no_space_where_nothing_is_drawn() -> None:
    """Measure the right of a map, where the axis draws nothing.

    The tick labels of the y axis are on the left, and the last x tick
    label, which overhangs the right corner, does not face that side: a
    bar there needs no room beyond cpad.
    """
    image = titled_image()
    assert isinstance(image.ax[0], Axes)
    manager = ColorbarManager(image.state)
    box(image.ax[0])

    assert manager.side_space(image.ax[0], "right") == 0.0


def test_the_title_takes_space_on_top() -> None:
    """Measure the top of a map with and without a panel title.

    Only the title is drawn above a map, so it is all the space there is:
    without it the top is free, with it the bar must start past it.
    """
    plain, titled = bowl_image(), titled_image()
    assert isinstance(plain.ax[0], Axes)
    assert isinstance(titled.ax[0], Axes)
    box(plain.ax[0])
    box(titled.ax[0])

    assert ColorbarManager(plain.state).side_space(plain.ax[0], "top") == 0.0
    assert ColorbarManager(titled.state).side_space(titled.ax[0], "top") > 0.0


# ---- The figure ----
def test_check_must_be_a_flag() -> None:
    """Pass a non-boolean `_check` and check it is refused.

    The value is deliberately of the wrong type, hence `Any`.
    """
    image = bowl_image()
    wrong: Any = "yes"

    with pytest.raises(PyPLUTOInternalError, match="_check must be a boolean"):
        image.colorbar(_check=wrong)


def test_a_colorbar_without_a_figure() -> None:
    """Ask for a colorbar on an image whose figure is gone."""
    image = pp.Image(text=False)
    image.fig = None

    with pytest.raises(PyPLUTOInternalError, match="No figure is present"):
        image.colorbar()


LONG_LABEL = "a very long colorbar label indeed " * 2


def label_right_edge(cbar: Colorbar) -> float:
    """Return how far right the label of a vertical bar reaches, in pixels."""
    box(cbar.ax)
    return cbar.ax.yaxis.label.get_window_extent().x1


def test_the_layout_is_tightened_again() -> None:
    """Add a colorbar with a long label to a tight figure.

    The layout is redone after the bar is placed, since its label is what
    the layout has to make room for: the label ends inside the figure.
    """
    image = bowl_image()
    cbar = image.colorbar(clabel=LONG_LABEL)

    assert image.fig is not None
    assert label_right_edge(cbar) <= image.fig.bbox.width


def test_a_loose_layout_is_left_alone() -> None:
    """Add the same colorbar to a figure that asked for no tight layout.

    Nothing makes room for the label, so it runs past the edge of the
    figure: the layout is the user's, as asked.
    """
    image = pp.Image(text=False, tight=False)
    image.display(var)
    cbar = image.colorbar(clabel=LONG_LABEL)

    assert image.fig is not None
    assert label_right_edge(cbar) > image.fig.bbox.width


def test_a_colorbar_says_nothing_of_its_own() -> None:
    """Draw the ordinary way and listen for warnings.

    Nothing about a plain colorbar is worth a warning, and one that appears
    here comes from matplotlib rather than from us.
    """
    image = bowl_image()

    with warnings.catch_warnings():
        warnings.simplefilter("error")
        cbar = image.colorbar(clabel="rho", cticks=[0.5, 1.0])

    assert isinstance(cbar, Colorbar)
