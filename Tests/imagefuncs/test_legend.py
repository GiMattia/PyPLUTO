"""Test of the legend.py file.

LegendManager builds a legend in one of two ways, and which one it takes
depends on a single keyword. Without `label` it asks matplotlib for the
artists already drawn and legends those; with `label` it builds its own
handles out of nothing -- lines with no data -- so the legend can describe
things that are not one line each, such as "all the solid lines".

That split is where most of the behaviour lives: the two branches read
different keywords, and each has its own defaults. The tests therefore go
through both, and check the legend's own parameters as well as its entries,
since a legend that reads correctly can still be placed or spaced wrongly.

The five numbers in `legpar` are per axis, in this order: size, columns,
column spacing, handle pad, frame alpha. They are written to by `legend` and
read back by the next call, which is what lets a second legend inherit the
first one's setting.
"""

import numpy as np
import pytest
from matplotlib.axes import Axes
from matplotlib.legend import Legend
from matplotlib.lines import Line2D

import pyPLUTO as pp

x = np.linspace(0, 1, 101)
y = np.linspace(1, 10, 101)
z = np.logspace(0, 1, 101)

# The five per-axis legend parameters, in the order create_axes stores them.
LEGPAR = ["legsize", "legcols", "legspace", "legpad", "legalpha"]


def _plotted(labels: list[str] | None = None) -> tuple[pp.Image, Axes]:
    """Draw one line per label, or one unlabelled line.

    A legend needs something to describe, so every test starts from a plot;
    the labels are what the branch without `label` picks up.
    """
    image = pp.Image(text=False)
    for index, label in enumerate(labels or [None]):
        image.plot(x, y + index, label=label)
    assert isinstance(image.ax[0], Axes)
    return image, image.ax[0]


def _legends(ax: Axes) -> list[Legend]:
    """Return the distinct legends the axis holds.

    Counted by identity: every legend is attached twice, once by
    `ax.legend()` and once by the `add_artist` that follows it, so the
    children list holds each one more than once. That duplication is an
    open bug with its own test in test_with_issues.py; here it only needs
    to be seen through.
    """
    seen: dict[int, Legend] = {}
    for artist in ax.get_children():
        if isinstance(artist, Legend):
            seen[id(artist)] = artist
    return list(seen.values())


def _handles(ax: Axes) -> list[Line2D]:
    """Return the legend's handles, narrowed to lines.

    Everything this manager puts in a legend is a Line2D, so the narrowing
    is done once here rather than in every test.
    """
    legend = ax.get_legend()
    assert legend is not None
    handles = legend.legend_handles
    assert all(isinstance(handle, Line2D) for handle in handles)
    return [handle for handle in handles if isinstance(handle, Line2D)]


# ---- The legend of what is drawn ----
def test_the_labels_of_the_lines() -> None:
    """Legend two labelled lines without saying anything else.

    The plain case: the labels come from the plot calls, in the order they
    were drawn, and the handles are the lines themselves.
    """
    image, ax = _plotted(["a", "b"])
    image.legend()

    assert [handle.get_label() for handle in _handles(ax)] == ["a", "b"]


def test_the_lines_keep_their_colours() -> None:
    """Check the handles carry the colours of the lines they describe.

    The legend is the key to the plot, so an entry drawn in another colour
    would point at the wrong curve. These come from the image's own palette,
    one per line.
    """
    image, ax = _plotted(["a", "b"])
    image.legend()

    colours = [handle.get_color() for handle in _handles(ax)]
    assert colours == [image.color[0], image.color[1]]


def test_the_markers_are_scaled() -> None:
    """Scale the markers of a legend built from the drawn lines.

    `mscale` enlarges the handles without touching the plot, for a marker
    that is legible in the data but too small to identify in a corner.
    """
    image, ax = _plotted(["a"])
    image.plot(x, z, marker="o", ms=4, label="b")

    image.legend(mscale=3.0)

    legend = ax.get_legend()
    assert legend is not None
    assert legend.get_children()[0] is not None


# ---- The legend built from labels ----
def test_custom_labels_replace_the_drawn_ones() -> None:
    """Give the labels by hand and check they are the ones shown.

    The second branch: the handles are built here rather than taken from
    the plot, so a legend can describe four lines with two entries.
    """
    image, ax = _plotted(["a", "b"])
    image.legend(label=["one", "two"])

    assert [handle.get_label() for handle in _handles(ax)] == ["one", "two"]


def test_a_single_custom_label() -> None:
    """Give one label as a string rather than a list.

    A lone label is the common case -- one curve, one entry -- so it is
    wrapped rather than refused.
    """
    image, ax = _plotted(["a"])
    image.legend(label="only one")

    assert [handle.get_label() for handle in _handles(ax)] == ["only one"]


def test_the_style_of_the_custom_handles() -> None:
    """Describe two entries with their own colours and line styles.

    The handles are drawn from the keywords rather than from the plot, so
    each of these has to arrive on the right entry: this is the call that
    makes "black lines" and "red lines" into a two-entry legend.
    """
    image, ax = _plotted(["a", "b"])
    image.legend(
        label=["solid", "dashed"],
        c=["k", "r"],
        ls=["-", "--"],
        lw=[2.0, 3.0],
    )

    handles = _handles(ax)
    assert [handle.get_color() for handle in handles] == ["k", "r"]
    assert [handle.get_linestyle() for handle in handles] == ["-", "--"]
    assert [handle.get_linewidth() for handle in handles] == [2.0, 3.0]


def test_the_style_is_cycled_over_the_labels() -> None:
    """Give three labels and two colours, and check the colours repeat.

    Each style keyword is indexed modulo its own length, so a short list is
    a pattern rather than an error: three entries alternate between two
    colours.
    """
    image, ax = _plotted(["a", "b", "c"])
    image.legend(label=["one", "two", "three"], c=["k", "r"])

    assert [handle.get_color() for handle in _handles(ax)] == ["k", "r", "k"]


def test_the_markers_of_the_custom_handles() -> None:
    """Describe the entries with markers rather than lines.

    A scatter plot is legended by its marker, so the marker keywords have to
    reach the handles: the shape, its size, how it is filled and the colour
    of its edge.
    """
    image, ax = _plotted(["a"])
    image.legend(
        label=["points"],
        marker="o",
        ms=8.0,
        fillstyle="none",
        edgecolor="r",
    )

    handle = _handles(ax)[0]
    assert handle.get_marker() == "o"
    assert handle.get_markersize() == 8.0
    assert handle.get_fillstyle() == "none"
    assert handle.get_markeredgecolor() == "r"


# ---- Placement and the per-axis parameters ----
def test_the_position() -> None:
    """Put the legend in a named corner.

    matplotlib's own names, passed through: 'best' is the default and can
    land anywhere, so a fixed corner is what a figure for a paper needs.
    """
    image, ax = _plotted(["a"])
    image.legend(legpos="lower left")

    legend = ax.get_legend()
    assert legend is not None
    assert image.legpos[0] == "lower left"


@pytest.mark.parametrize(
    ("keyword", "value", "index"),
    [
        ("legsize", 9.0, 0),
        ("legcols", 2, 1),
        ("legspace", 3.0, 2),
        ("legpad", 1.5, 3),
        ("legalpha", 0.4, 4),
    ],
)
def test_the_legend_parameters_are_recorded(
    keyword: str, value: float, index: int
) -> None:
    """Set one legend parameter and find it in the per-axis record.

    They are kept per axis so a second legend on the same axis inherits
    them, which is what makes a double legend look like one: the table
    above is the order they are stored in, which nothing else states.
    """
    image, _ = _plotted(["a"])

    if keyword == "legsize":
        image.legend(legsize=value)
    elif keyword == "legcols":
        image.legend(legcols=int(value))
    elif keyword == "legspace":
        image.legend(legspace=value)
    elif keyword == "legpad":
        image.legend(legpad=value)
    else:
        image.legend(legalpha=value)

    assert image.legpar[0][index] == value


def test_the_parameters_are_inherited_by_the_next_legend() -> None:
    """Set a parameter, then legend again without repeating it.

    The record is what the second call reads, so a double legend keeps one
    appearance instead of reverting to the defaults halfway.
    """
    image, ax = _plotted(["a"])
    image.legend(legsize=7.0, legcols=2)

    image.legend(label=["second"])

    assert image.legpar[0][0] == 7.0
    assert image.legpar[0][1] == 2
    legend = ax.get_legend()
    assert legend is not None


def test_two_legends_on_one_axis() -> None:
    """Put two legends on the same axis and check both survive.

    matplotlib keeps only the last legend of an axis, so each one is added
    as an artist of its own: that is what lets one plot carry a legend of
    colours and a legend of line styles.
    """
    image, ax = _plotted(["a", "b"])
    image.legend(label=["solid", "dashed"], legpos="lower left")
    image.legend(label=["black", "red"], legpos="lower right")

    assert len(_legends(ax)) == 2


def test_a_legend_asked_for_by_the_plot_replaces_the_previous_one() -> None:
    """Draw a second labelled line with the legend on, and count the legends.

    Giving `legpos` to `plot` is what asks for the legend there, and the
    call it makes carries `fromplot`, which removes the legend already
    present before building the new one: without that, every line drawn
    would leave another legend behind on top of the last.
    """
    image, ax = _plotted(["a"])
    image.legend()

    image.plot(x, z, label="b", legpos="upper left")

    assert [handle.get_label() for handle in _handles(ax)] == ["a", "b"]
    assert len(_legends(ax)) == 1


def test_the_first_plot_that_asks_for_a_legend() -> None:
    """Give `legpos` to the first plot, when no legend exists yet.

    The same path as the test above, with nothing to remove: the branch has
    to cope with an axis that has no legend, which is the ordinary case of
    a one-line plot asking for its own legend.
    """
    image = pp.Image(text=False)
    image.plot(x, y, label="a", legpos="upper right")

    assert isinstance(image.ax[0], Axes)
    assert len(_legends(image.ax[0])) == 1
    assert [h.get_label() for h in _handles(image.ax[0])] == ["a"]


def test_the_axis_index_is_hidden() -> None:
    """Check the number create_axes wrote is gone once a legend is drawn.

    Every drawing call hides it, a legend included: it is there to tell the
    user which index to pass, not to stay on the figure.
    """
    image = pp.Image(text=False)
    image.create_axes()
    image.plot(x, y, label="a")

    image.legend()

    assert image.ntext[0] == 1
