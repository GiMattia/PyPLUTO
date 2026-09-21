"""Test of the plot.py file.

PlotManager draws the 1D lines. The call is short, but three of the things
it does are remembered on the axis rather than done and forgotten, and those
are what the tests are mostly about.

The first is the colour: a line that does not say which colour it wants takes
the next one of the image's palette, and the count that walks it, `nline`, is
per axis, so two axes both start from the first colour.

The second is the range: the limits are widened before the line is drawn, so
a second line on the same axis extends them instead of replacing them, and a
range given by hand is never widened again.

The third is the legend: `legpos` is stored on the axis, so once one line has
asked for a legend every later line on that axis rebuilds it. The rebuild goes
through `LegendManager` with `label` blanked out, which is what makes it
describe the lines that are drawn rather than build its own handles.
"""

from collections.abc import Callable

import numpy as np
import numpy.testing as npt
import pytest
from matplotlib.axes import Axes
from matplotlib.lines import Line2D

import pyPLUTO as pp

x = np.linspace(0.0, 1.0, 11)
y = x**2
z = 10.0 * y

# What a line looks like when nothing but the data is given. The getters are
# matplotlib's own names, since that is where the value ends up.
LINE_DEFAULTS: dict[str, object] = {
    "get_linestyle": "-",
    "get_linewidth": 1.3,
    "get_marker": "",
    "get_markersize": 3.0,
    "get_fillstyle": "full",
}

# One call per keyword, the getter that reads it back, and what it must say.
# The calls are written out rather than built from the keyword name so that
# every one of them is type-checked.
LINE_KEYWORDS: list[tuple[Callable[[pp.Image], None], str, object]] = [
    (lambda image: image.plot(x, y, ls="--"), "get_linestyle", "--"),
    (lambda image: image.plot(x, y, lw=0.5), "get_linewidth", 0.5),
    (lambda image: image.plot(x, y, marker="o"), "get_marker", "o"),
    (lambda image: image.plot(x, y, ms=5.0), "get_markersize", 5.0),
    (lambda image: image.plot(x, y, fillstyle="none"), "get_fillstyle", "none"),
    (lambda image: image.plot(x, y, label="rho"), "get_label", "rho"),
]


def _lines(image: pp.Image, nax: int = 0) -> list[Line2D]:
    """Return the lines drawn on one axis.

    Every test reads them back from matplotlib rather than from the state,
    since the state is not what ends up on the figure.
    """
    assert isinstance(image.ax[nax], Axes)
    return list(image.ax[nax].lines)


# ---- The data that is drawn ----
def test_two_arrays_are_the_x_and_the_y() -> None:
    """Plot one array against the other, and read both back.

    The plain case, and the one everything else is compared against: the
    arrays reach matplotlib untouched.
    """
    image = pp.Image(text=False)
    image.plot(x, y)

    line = _lines(image)[0]
    npt.assert_array_equal(line.get_xdata(), x)
    npt.assert_array_equal(line.get_ydata(), y)


def test_one_array_is_plotted_against_its_index() -> None:
    """Give a single array and check it became the y-axis.

    A lone array is the values, not the positions, so the x-axis is the
    index of each point: this is what makes `I.plot(rho)` a plot of rho.
    """
    image = pp.Image(text=False)
    image.plot(y)

    line = _lines(image)[0]
    npt.assert_array_equal(line.get_xdata(), np.arange(y.size, dtype=float))
    npt.assert_array_equal(line.get_ydata(), y)


def test_lists_are_accepted() -> None:
    """Plot two plain lists rather than arrays.

    The data is converted to float arrays on the way in, so a list of ints
    -- what a user types at the prompt -- is drawn as a float line and not
    refused halfway down in the range code.
    """
    image = pp.Image(text=False)
    image.plot([0, 1, 2], [3, 4, 5])

    line = _lines(image)[0]
    npt.assert_array_equal(line.get_xdata(), [0.0, 1.0, 2.0])
    npt.assert_array_equal(line.get_ydata(), [3.0, 4.0, 5.0])


def test_a_2d_pair_is_one_line_per_column() -> None:
    """Plot two 2D arrays of the same shape.

    matplotlib reads a 2D array as a line per column, which is how several
    lines are drawn in one call; they share the style and the colour, and
    they count as one line for the palette.
    """
    image = pp.Image(text=False)
    xval = np.tile(x, (3, 1)).T

    image.plot(xval, np.column_stack([y, z, y + 1.0]))

    lines = _lines(image)
    assert len(lines) == 3
    assert {line.get_color() for line in lines} == {image.color[0]}
    assert image.nline[0] == 1


def test_a_single_2d_array_is_indexed_by_row() -> None:
    """Give a single 2D array and check the x-axis counts the rows.

    The index has to run over the rows, one per point of each line. Counting
    the elements instead gives an x-axis three times too long, and the plot
    dies in the range code with an IndexError that names neither the array
    nor the call.
    """
    image = pp.Image(text=False)

    image.plot(np.column_stack([y, z, y + 1.0]))

    lines = _lines(image)
    assert len(lines) == 3
    npt.assert_array_equal(lines[0].get_xdata(), np.arange(11, dtype=float))
    npt.assert_array_equal(lines[1].get_ydata(), z)


# ---- The colour of the line ----
def test_the_palette_advances_one_line_at_a_time() -> None:
    """Draw three lines without asking for a colour.

    The palette is walked in order, one step per line, so lines drawn one
    call at a time are told apart without the user choosing anything. The
    colours are the image's own, which are legible with the most common
    vision deficiencies.
    """
    image = pp.Image(text=False)
    for scale in (1.0, 2.0, 3.0):
        image.plot(x, scale * y)

    colours = [line.get_color() for line in _lines(image)]
    assert colours == [image.color[0], image.color[1], image.color[2]]
    assert image.nline[0] == 3


def test_the_palette_is_counted_per_axis() -> None:
    """Draw one line on each of two axes.

    The count is kept per axis, so the first line of every panel is the
    first colour: panels of a figure are read side by side, and a shared
    count would give the same curve a different colour in each.
    """
    image = pp.Image(text=False)
    image.create_axes(ncol=2)
    image.plot(x, y, ax=0)
    image.plot(x, y, ax=1)

    assert _lines(image, 0)[0].get_color() == image.color[0]
    assert _lines(image, 1)[0].get_color() == image.color[0]
    assert image.nline[0] == 1
    assert image.nline[1] == 1


def test_a_chosen_colour_leaves_the_palette_alone() -> None:
    """Draw a red line, then one that does not choose.

    A colour given by hand does not consume a step, so the next automatic
    line still gets the first colour of the palette rather than the second.
    """
    image = pp.Image(text=False)
    image.plot(x, y, c="r")
    image.plot(x, z)

    lines = _lines(image)
    assert lines[0].get_color() == "r"
    assert lines[1].get_color() == image.color[0]
    assert image.nline[0] == 1


def test_a_colour_given_as_none_is_no_colour_at_all() -> None:
    """Pass `c=None` and check the line follows the palette.

    `None` is how a caller forwards "the user did not choose" -- a variable
    that is empty, a GUI field left blank -- so it has to mean the same as
    leaving the keyword out. Read as a colour instead, it reaches matplotlib,
    which draws its own first colour: a line outside the palette, and outside
    the scheme the other lines follow.
    """
    image = pp.Image(text=False)
    image.plot(x, y, c=None)

    assert _lines(image)[0].get_color() == image.color[0]
    assert image.nline[0] == 1


def test_a_colour_given_as_an_rgb_array() -> None:
    """Give the colour as an array of three floats.

    An RGB triple is a colour matplotlib accepts and `c` declares, and an
    array is how one is computed -- out of a colormap, say. It must not be
    weighed for emptiness on the way through, since an array of three has no
    truth value and raises instead of being drawn.
    """
    image = pp.Image(text=False)
    image.plot(x, y, c=np.array([0.1, 0.2, 0.3]))

    colour = np.asarray(_lines(image)[0].get_color(), dtype=float)
    npt.assert_allclose(colour, [0.1, 0.2, 0.3])
    assert image.nline[0] == 0


# ---- The line itself ----
def test_the_default_line() -> None:
    """Draw a line without any styling and read every default back.

    The defaults are the ones in the docstring: a solid line of width 1.3
    and no marker. They are written here by hand so that a change in any of
    them has to be made twice, once in the code and once as a decision.
    """
    image = pp.Image(text=False)
    image.plot(x, y)

    line = _lines(image)[0]
    for getter, expected in LINE_DEFAULTS.items():
        assert getattr(line, getter)() == expected, getter


def test_a_line_without_a_label_stays_out_of_the_legend() -> None:
    """Draw one labelled and one unlabelled line, and legend them.

    The empty label the plot passes is rewritten by matplotlib into one of
    its own, starting with an underscore, which is how it marks an artist
    that legends ignore. That is what keeps a legend to the curves the user
    named rather than one blank entry per line.
    """
    image = pp.Image(text=False)
    image.plot(x, y)
    image.plot(x, z, label="prs", legpos="best")

    assert str(_lines(image)[0].get_label()).startswith("_")
    assert isinstance(image.ax[0], Axes)
    legend = image.ax[0].get_legend()
    assert legend is not None
    assert [text.get_text() for text in legend.get_texts()] == ["prs"]


@pytest.mark.parametrize(("call", "getter", "expected"), LINE_KEYWORDS)
def test_the_line_keywords(
    call: Callable[[pp.Image], None], getter: str, expected: object
) -> None:
    """Set one line keyword and read it back off the line.

    Each of these is forwarded to matplotlib under a name of its own, so a
    failure here means one keyword is dropped or renamed, not that plotting
    is broken.
    """
    image = pp.Image(text=False)
    call(image)

    assert getattr(_lines(image)[0], getter)() == expected


# ---- The ranges ----
def test_the_limits_are_padded_around_the_data() -> None:
    """Draw one line and check the limits leave room around it.

    The y-limits are padded by a tenth of the span so the curve does not
    touch the frame, while the x-limits are the data exactly: a plot is read
    along x and the ends of the interval are the ones asked for.
    """
    image = pp.Image(text=False)
    image.plot(x, y)

    assert isinstance(image.ax[0], Axes)
    npt.assert_allclose(image.ax[0].get_xlim(), (0.0, 1.0))
    npt.assert_allclose(image.ax[0].get_ylim(), (-0.1, 1.1))


def test_the_limits_grow_with_every_line() -> None:
    """Draw a second, taller line on the same axis.

    The limits take in both lines rather than following the last one, which
    is what lets a plot be built up call after call without the first curve
    walking out of the frame.
    """
    image = pp.Image(text=False)
    image.plot(x, y)
    image.plot(x, z)

    assert isinstance(image.ax[0], Axes)
    npt.assert_allclose(image.ax[0].get_ylim(), (-1.0, 11.0))


def test_a_range_given_by_hand_is_kept() -> None:
    """Fix the ranges, then draw a line that does not fit in them.

    A range the user chose is a decision, not a starting point: the second
    line is drawn outside the frame rather than widening it. This is the
    difference between `setax` "fixed" and "free to grow".
    """
    image = pp.Image(text=False)
    image.plot(x, y, xrange=[0.2, 0.4], yrange=[-1.0, 0.0])
    image.plot(x, z)

    assert isinstance(image.ax[0], Axes)
    npt.assert_allclose(image.ax[0].get_xlim(), (0.2, 0.4))
    npt.assert_allclose(image.ax[0].get_ylim(), (-1.0, 0.0))


# ---- The axis ----
def test_the_axis_is_chosen_by_index() -> None:
    """Plot on the second of three axes, by number.

    The index is the one printed on the empty axes, so it is how a plot is
    aimed at a panel without keeping the objects around.
    """
    image = pp.Image(text=False)
    image.create_axes(ncol=3)
    image.plot(x, y, ax=1)

    assert len(_lines(image, 1)) == 1
    assert _lines(image, 0) == []
    assert _lines(image, 2) == []


def test_the_axis_is_chosen_by_object() -> None:
    """Plot on an axis passed as the object itself.

    `create_axes` returns the axes, so passing one back is the other way to
    aim a plot, and it has to land on the same panel as its index.
    """
    image = pp.Image(text=False)
    axes = image.create_axes(ncol=2)
    assert isinstance(axes, list)
    image.plot(x, y, ax=axes[1])

    assert len(_lines(image, 1)) == 1
    assert _lines(image, 0) == []


def test_the_axis_keywords_are_forwarded() -> None:
    """Give a title and axis labels to the plot call.

    The axis is set from the same keywords as the line, so a whole figure
    can be one call; a failure here means the plot keywords and the axis
    keywords have come apart.
    """
    image = pp.Image(text=False)
    image.plot(
        x + 1.0, y, title="a title", xtitle="x", ytitle="y", xscale="log"
    )

    assert isinstance(image.ax[0], Axes)
    assert image.ax[0].get_title() == "a title"
    assert image.ax[0].get_xlabel() == "x"
    assert image.ax[0].get_ylabel() == "y"
    assert image.ax[0].get_xscale() == "log"


def test_the_axis_index_is_hidden() -> None:
    """Check the number create_axes wrote is gone once a line is drawn.

    It is there to tell the user which index to pass, so it goes as soon as
    the panel is used; the axis that was not plotted on keeps its own.
    """
    image = pp.Image(text=False)
    image.create_axes(ncol=2)
    image.plot(x, y, ax=1)

    assert image.ntext[1] == 1


# ---- The legend ----
def test_a_legend_is_created_by_legpos() -> None:
    """Ask for a legend from the plot call itself.

    `legpos` is what turns a label into a legend, so that one call draws the
    line and says what it is.
    """
    image = pp.Image(text=False)
    image.plot(x, y, label="rho", legpos="lower right")

    assert isinstance(image.ax[0], Axes)
    legend = image.ax[0].get_legend()
    assert legend is not None
    assert [text.get_text() for text in legend.get_texts()] == ["rho"]


def test_the_legend_is_made_of_the_drawn_lines() -> None:
    """Check the legend entry carries the colour of its line.

    The legend is asked for the lines already on the axis, with the label
    blanked out on the way, since a label left in place would send it down
    the other branch and build a handle of its own -- black, and describing
    nothing that was drawn.
    """
    image = pp.Image(text=False)
    image.plot(x, y, label="rho", legpos="best")

    assert isinstance(image.ax[0], Axes)
    legend = image.ax[0].get_legend()
    assert legend is not None
    handle = legend.legend_handles[0]
    assert isinstance(handle, Line2D)
    assert handle.get_color() == image.color[0]


def test_the_position_is_remembered_by_the_axis() -> None:
    """Draw a second labelled line without repeating `legpos`.

    Once an axis has a legend every line added to it belongs there, so the
    position is kept and the legend is rebuilt: otherwise the second curve
    would be drawn with a legend that does not mention it.
    """
    image = pp.Image(text=False)
    image.plot(x, y, label="rho", legpos="upper left")
    image.plot(x, z, label="prs")

    assert isinstance(image.ax[0], Axes)
    legend = image.ax[0].get_legend()
    assert legend is not None
    assert [text.get_text() for text in legend.get_texts()] == ["rho", "prs"]
    assert image.legpos[0] == "upper left"


# ---- The figure ----
def test_a_plot_without_a_figure() -> None:
    """Plot on an image whose figure is gone.

    There is nothing to draw on, and saying so is better than the error
    matplotlib would give several calls later, in a function the user never
    called.
    """
    image = pp.Image(text=False)
    image.fig = None

    with pytest.raises(ValueError, match="No figure is present"):
        image.plot(x, y)


def test_the_layout_is_tightened_again() -> None:
    """Draw a line with a long axis label on a tight figure.

    The layout is redone after every plot, since what a plot adds -- a long
    label, a title, a legend -- is what the layout has to make room for. The
    axis box moves to the right to fit the label.
    """
    image = pp.Image(text=False)
    image.plot(x, y)
    assert isinstance(image.ax[0], Axes)
    before = image.ax[0].get_position().x0

    image.plot(x, 1e6 * y, ytitle="a very long y title indeed")

    assert image.ax[0].get_position().x0 > before


def test_a_loose_layout_is_left_alone() -> None:
    """Draw the same line on a figure that asked for no tight layout.

    Without it the axis box is where the figure put it and stays there,
    whatever is drawn: a figure whose panels were placed by hand must not be
    rearranged behind the user's back.
    """
    image = pp.Image(text=False, tight=False)
    image.plot(x, y)
    assert isinstance(image.ax[0], Axes)
    before = image.ax[0].get_position().x0

    image.plot(x, 1e6 * y, ytitle="a very long y title indeed")

    assert image.ax[0].get_position().x0 == before


def test_an_unknown_keyword_warns() -> None:
    """Misspell a keyword and check the plot says which one.

    The keywords are checked in `plot` itself, so the warning names the
    method the user called; the line is still drawn, since a misspelt
    keyword is not a reason to lose the figure.
    """
    image = pp.Image(text=False)

    with pytest.warns(UserWarning, match="Unused kwargs: {'colour'}"):
        image.plot(x, y, colour="r")  # type: ignore[call-overload]

    assert len(_lines(image)) == 1
