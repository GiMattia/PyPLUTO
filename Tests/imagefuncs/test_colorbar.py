"""Test of the colorbar.py file.

ColorbarManager draws the colorbar of a collection: the one it is given, or
the last one on the axis that is colored by data -- a map, contour lines,
points or streamlines colored by a variable. Lines drawn in a single color
carry no scale and are skipped, which is what lets black contours over a map
leave the colorbar to the map.

The bar is cut from one side of the axis, `cpad` inches away, or placed in a
given axis. Contour lines get a continuous bar on their scale, as a map does,
rather than matplotlib's one block per level. The ticks follow the rules of
`xticks` and `xtickslabels` -- True automatic, None removed, a list fixed --
through the same `set_ticks`.

Where the colorbar lands is only settled once the figure is drawn, since the
new axis is positioned by a locator at draw time, so the placement tests draw
the canvas before reading any box.
"""

import inspect
import warnings
from collections.abc import Callable

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

# A bowl-shaped variable from 0 at the center to 2 in the corners.
x = np.linspace(-1, 1, 20)
x2d, y2d = np.meshgrid(x, x, indexing="ij")
var = x2d**2 + y2d**2


def _image() -> pp.Image:
    """Return an image holding one map of the bowl."""
    image = pp.Image(text=False)
    image.display(var, x1=x, x2=x)
    return image


def _box(axis: Axes) -> Bbox:
    """Return where an axis is drawn, in pixels, after drawing the figure."""
    figure = axis.get_figure()
    assert figure is not None
    figure.canvas.draw()
    return axis.get_window_extent()


def _steps(cbar: Colorbar) -> int:
    """Return how many colors the bar is painted with."""
    assert cbar.solids is not None
    return np.asarray(cbar.solids.get_array()).size


# ---- The documentation ----
def test_colorbar_documents_its_real_default() -> None:
    """Compare the documented default of `cpos` with the one the code uses.

    `kwargs.get("cpos", "right")` is what runs, while the docstring said
    "default None", so a user read that no colorbar would be placed and got
    one on the right.
    """
    documented = inspect.getdoc(ColorbarManager.colorbar) or ""
    entry = next(
        line for line in documented.splitlines() if line.startswith("- cpos:")
    )

    assert "default 'right'" in entry


# ---- Where the colorbar goes ----
@pytest.mark.parametrize(
    ("cpos", "orientation"),
    [
        ("right", "vertical"),
        ("left", "vertical"),
        ("top", "horizontal"),
        ("bottom", "horizontal"),
    ],
)
def test_colorbar_positions(cpos: str, orientation: str) -> None:
    """Ask for each side and check where the bar is drawn.

    The bar lies wholly on that side of the axis, and runs along it:
    upright beside the axis, lying down above or below it.
    """
    image = _image()
    cbar = image.colorbar(cpos=cpos)

    assert isinstance(image.ax[0], Axes)
    axis, bar = _box(image.ax[0]), _box(cbar.ax)
    side = {
        "right": bar.x0 >= axis.x1,
        "left": bar.x1 <= axis.x0,
        "top": bar.y0 >= axis.y1,
        "bottom": bar.y1 <= axis.y0,
    }
    assert side[cpos]
    assert cbar.orientation == orientation


def test_colorbar_default_position() -> None:
    """Ask for a colorbar with no side and check it is on the right."""
    image = _image()
    cbar = image.colorbar()

    assert isinstance(image.ax[0], Axes)
    assert _box(cbar.ax).x0 >= _box(image.ax[0]).x1


def test_the_gap_is_in_inches() -> None:
    """Draw with two paddings and measure the gap in pixels.

    `cpad` is the space between the axis and the bar in inches, so at 100
    dots per inch 0.07 leaves 7 pixels and 0.5 leaves 50.
    """
    for cpad, pixels in ((0.07, 7.0), (0.5, 50.0)):
        image = pp.Image(text=False, tight=False)
        image.display(var)
        assert image.fig is not None
        image.fig.set_dpi(100)
        cbar = image.colorbar(cpad=cpad)

        assert isinstance(image.ax[0], Axes)
        gap = _box(cbar.ax).x0 - _box(image.ax[0]).x1
        assert gap == pytest.approx(pixels, abs=0.5)


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

    with pytest.warns(UserWarning, match="pcm will be used"):
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

    with pytest.raises(ValueError, match="No collection colored by data"):
        image.colorbar()


def test_a_collection_drawn_nowhere() -> None:
    """Give a collection that was never added to an axis.

    Its axis is where the bar would be placed, so without one there is
    nowhere to put it.
    """
    image = pp.Image(text=False)

    with pytest.raises(TypeError, match="Expected an Axes instance"):
        image.colorbar(pcm=QuadMesh(np.zeros((2, 2, 2))))


def test_a_second_colorbar() -> None:
    """Ask for a colorbar twice on the same map.

    After the first, matplotlib holds the colorbar axis as its current one,
    which is not an axis of the image; reading it as one raised a
    ValueError. The second call finds the map's axis again.
    """
    image = _image()
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

    assert _steps(cbar) == 256
    assert cbar.cmap.name == "magma"
    assert cbar.norm.vmin == pytest.approx(lines.norm.vmin)
    assert cbar.norm.vmax == pytest.approx(lines.norm.vmax)


# ---- The ticks and the label ----
def test_colorbar_label() -> None:
    """Check the label is written along the bar."""
    image = _image()
    cbar = image.colorbar(cpos="right", clabel="rho")

    assert cbar.ax.get_ylabel() == "rho"


def test_colorbar_ticks() -> None:
    """Fix the ticks and read them back."""
    image = _image()
    cbar = image.colorbar(cpos="right", cticks=[0.0, 1.0, 2.0])

    npt.assert_allclose(cbar.ax.get_yticks(), [0.0, 1.0, 2.0])


def test_no_ticks() -> None:
    """Remove the ticks with None, as for xticks.

    None used to mean automatic, so a bar without ticks could only be asked
    for with an empty list. Neither major nor minor ticks are left.
    """
    image = _image()
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
    _box(cbar.ax)

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
    _box(cbar.ax)

    labels = [label.get_text() for label in cbar.ax.get_yticklabels()]
    assert labels == [
        r"$\mathdefault{5\times10^{-1}}$",
        r"$\mathdefault{10^{0}}$",
    ]


def test_ticks_and_labels_from_an_array() -> None:
    """Fix the ticks with an array and label them.

    The labels used to be applied through `cticks or ...`, which an array
    refuses: its truth value is ambiguous.
    """
    image = _image()
    cbar = image.colorbar(
        cticks=np.array([0.5, 1.0]),  # pyright: ignore[reportArgumentType]  # ty: ignore[invalid-argument-type]
        ctickslabels=["a", "b"],
    )
    _box(cbar.ax)

    npt.assert_allclose(cbar.ax.get_yticks(), [0.5, 1.0])
    assert [t.get_text() for t in cbar.ax.get_yticklabels()] == ["a", "b"]


def test_labels_on_a_horizontal_bar() -> None:
    """Label the ticks of a bar placed on top, which runs along x."""
    image = _image()
    cbar = image.colorbar(
        cpos="top", cticks=[0.5, 1.0], ctickslabels=["a", "b"]
    )
    _box(cbar.ax)

    assert [t.get_text() for t in cbar.ax.get_xticklabels()] == ["a", "b"]


def test_no_labels() -> None:
    """Remove the labels with None and keep the ticks, as for xtickslabels."""
    image = _image()
    cbar = image.colorbar(ctickslabels=None)
    _box(cbar.ax)

    assert len(cbar.ax.get_yticks()) > 0
    assert {t.get_text() for t in cbar.ax.get_yticklabels()} == {""}


def test_labels_on_automatic_ticks() -> None:
    """Label the ticks of a bar without choosing them.

    The labels go on the ticks matplotlib picks for the range of the bar,
    which is set when the bar is drawn, so the ticks are pinned there once
    and nothing warns. A bar keeps no case: nothing is drawn on it later.
    """
    image = _image()

    with warnings.catch_warnings(record=True) as raised:
        warnings.simplefilter("always")
        cbar = image.colorbar(ctickslabels=["a", "b", "c"])
    _box(cbar.ax)

    assert [str(w.message) for w in raised] == []
    labels = [t.get_text() for t in cbar.ax.get_yticklabels()]
    assert labels[:3] == ["a", "b", "c"]


def test_labels_without_ticks_warn() -> None:
    """Give labels while removing the ticks.

    There is nothing to put them on, and the user is told so rather than
    seeing them disappear.
    """
    image = _image()

    with pytest.warns(UserWarning, match="tickslabels are defined with no"):
        cbar = image.colorbar(cticks=None, ctickslabels=["a"])

    assert list(cbar.ax.get_yticks()) == []


def test_the_extensions() -> None:
    """Ask for extensions at both ends, rectangular rather than triangular."""
    image = _image()
    cbar = image.colorbar(extend="both", extendrect=True)

    assert cbar.extend == "both"
    assert cbar.extendrect is True


# ---- Finding the axis ----
def test_find_ax_from_collection() -> None:
    """Check a collection gives the axis it was drawn on."""
    image = pp.Image(text=False)
    mesh = image.display(var)
    manager = ColorbarManager(image.state)

    assert manager._find_ax(pcm=mesh) is image.ax[0]


def test_find_ax_default() -> None:
    """Check that without a collection the current image axis is taken."""
    image = _image()
    manager = ColorbarManager(image.state)

    assert manager._find_ax() is image.ax[0]


def test_find_ax_by_index() -> None:
    """Check an axis can be selected by its index."""
    image = pp.Image(text=False)
    image.create_axes(ncol=2)
    manager = ColorbarManager(image.state)

    assert manager._find_ax(axs=1) is image.ax[1]


# ---- The figure ----
def test_check_must_be_a_flag() -> None:
    """Pass a non-boolean `_check` and check it is refused."""
    image = _image()

    with pytest.raises(TypeError, match="_check must be a boolean"):
        image.colorbar(_check="yes")  # pyright: ignore[reportArgumentType]  # ty: ignore[invalid-argument-type]


def test_a_colorbar_without_a_figure() -> None:
    """Ask for a colorbar on an image whose figure is gone."""
    image = pp.Image(text=False)
    image.fig = None

    with pytest.raises(ValueError, match="No figure is present"):
        image.colorbar()


LONG_LABEL = "a very long colorbar label indeed " * 2


def _label_right_edge(cbar: Colorbar) -> float:
    """Return how far right the label of a vertical bar reaches, in pixels."""
    _box(cbar.ax)
    return cbar.ax.yaxis.label.get_window_extent().x1


def test_the_layout_is_tightened_again() -> None:
    """Add a colorbar with a long label to a tight figure.

    The layout is redone after the bar is placed, since its label is what
    the layout has to make room for: the label ends inside the figure.
    """
    image = _image()
    cbar = image.colorbar(clabel=LONG_LABEL)

    assert image.fig is not None
    assert _label_right_edge(cbar) <= image.fig.bbox.width


def test_a_loose_layout_is_left_alone() -> None:
    """Add the same colorbar to a figure that asked for no tight layout.

    Nothing makes room for the label, so it runs past the edge of the
    figure: the layout is the user's, as asked.
    """
    image = pp.Image(text=False, tight=False)
    image.display(var)
    cbar = image.colorbar(clabel=LONG_LABEL)

    assert image.fig is not None
    assert _label_right_edge(cbar) > image.fig.bbox.width


def test_a_colorbar_says_nothing_of_its_own() -> None:
    """Draw the ordinary way and listen for warnings.

    Nothing about a plain colorbar is worth a warning, and one that appears
    here comes from matplotlib rather than from us.
    """
    image = _image()

    with warnings.catch_warnings():
        warnings.simplefilter("error")
        cbar = image.colorbar(clabel="rho", cticks=[0.5, 1.0])

    assert isinstance(cbar, Colorbar)
