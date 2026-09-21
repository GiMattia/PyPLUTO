"""Test of the set_axis.py file.

AxisManager is what every plotting call ends with: the axis it drew on is
handed here to be given its range, its titles, its ticks, its scales and its
grid. So these tests read the result off matplotlib rather than off the
state -- what the user sees is the axis, not the record of it.

The tick machinery is the part worth knowing. `xticks` and `xtickslabels`
each accept three kinds of value, and the meaning is not the same: True
means "leave matplotlib's own", None means "remove them", and a list means
"use these". The combinations are what most of this file covers, including
the two that make no sense and warn -- labels without ticks, and labels on
ticks left automatic.

Labels are set through the axis formatters rather than `set_xticklabels`,
because a log scale resets the latter; the tests therefore read the labels
back after the scale is set, which is where that distinction shows.
"""

import inspect
import warnings
from typing import Literal

import numpy.testing as npt
import pytest
from matplotlib.axes import Axes

import pyPLUTO as pp
from pyPLUTO.imagefuncs.set_axis import AxisManager


def _axis() -> tuple[pp.Image, Axes]:
    """Build a quiet image with one axis to work on.

    create_axes hands back a single axis or a list, so the narrowing is
    done here once rather than in every test below.
    """
    image = pp.Image(text=False)
    axis = image.create_axes()
    assert isinstance(axis, Axes)
    return image, axis


# ---- Defaults ----
def test_the_defaults_change_nothing() -> None:
    """Call set_axis with no keywords and check the axis is untouched.

    Every keyword is optional, and a call without any is what the plotting
    methods make for themselves: it must leave matplotlib's own defaults in
    place rather than imposing a range, a title or a scale.
    """
    image, ax = _axis()
    image.set_axis()

    assert ax.get_aspect() == "auto"
    assert ax.get_xlim() == pytest.approx((0.0, 1.0))
    assert ax.get_ylim() == pytest.approx((0.0, 1.0))
    assert ax.get_title() == ""
    assert ax.get_xlabel() == ""
    assert ax.get_ylabel() == ""
    assert ax.get_xscale() == "linear"
    assert ax.get_yscale() == "linear"
    assert ax.get_alpha() is None


def test_the_aspect_and_the_fontsize() -> None:
    """Set the aspect ratio twice, by name and by number, and the fontsize.

    'equal' means one unit of x is one unit of y, which matplotlib reports
    as the ratio 1.0; a number is that ratio directly. The fontsize is
    recorded on the state, which everything drawn afterwards reads.
    """
    image, ax = _axis()

    image.set_axis(aspect="equal", fontsize=20)
    assert ax.get_aspect() == pytest.approx(1.0)
    assert image.fontsize == 20

    image.set_axis(aspect=2.0)
    assert ax.get_aspect() == pytest.approx(2.0)


def test_the_ranges_are_fixed() -> None:
    """Give both ranges and check the axis holds exactly them.

    Ranges given here are fixed rather than adapted, so a later plot widens
    nothing: that is what makes `set_axis(xrange=...)` the way to pin a
    window.
    """
    image, ax = _axis()
    image.set_axis(xrange=[-1, 1], yrange=[1, 10])

    assert ax.get_xlim() == pytest.approx((-1.0, 1.0))
    assert ax.get_ylim() == pytest.approx((1.0, 10.0))


def test_the_titles() -> None:
    """Set the three titles and read them back.

    The plot title and the two axis labels, which are the only text
    set_axis writes.
    """
    image, ax = _axis()
    image.set_axis(title="this is a title", xtitle="x", ytitle="y")

    assert ax.get_title() == "this is a title"
    assert ax.get_xlabel() == "x"
    assert ax.get_ylabel() == "y"


# ---- Ticks ----
def test_the_ticks_are_set_or_removed() -> None:
    """Give ticks on one axis and remove them on the other, then swap.

    A list places the ticks, None removes them entirely. Swapping the two
    checks that neither axis is being written by the other's branch.
    """
    image, ax = _axis()

    image.set_axis(xticks=[0, 0.5, 1], yticks=None)
    npt.assert_array_equal(ax.get_xticks(), [0, 0.5, 1])
    assert len(ax.get_yticks()) == 0

    image.set_axis(xticks=None, yticks=[0, 0.2, 1.0])
    assert len(ax.get_xticks()) == 0
    npt.assert_array_equal(ax.get_yticks(), [0, 0.2, 1.0])


def test_the_tick_labels_are_set_or_blanked() -> None:
    """Label one axis and blank the other, then swap.

    Labels are placed through the formatter, so they survive the scale
    being changed afterwards; blanking leaves the ticks themselves in place.
    """
    image, ax = _axis()
    labels = ["a", "b", "c"]

    image.set_axis(
        xticks=[0, 0.5, 1],
        yticks=[0, 0.5, 1],
        xtickslabels=None,
        ytickslabels=labels,
    )
    assert [t.get_text() for t in ax.get_xticklabels()] == ["", "", ""]
    assert [t.get_text() for t in ax.get_yticklabels()] == labels

    image.set_axis(
        xticks=[0, 0.5, 1],
        yticks=[0, 0.5, 1],
        xtickslabels=labels,
        ytickslabels=None,
    )
    assert [t.get_text() for t in ax.get_xticklabels()] == labels
    assert [t.get_text() for t in ax.get_yticklabels()] == ["", "", ""]


def test_one_label_for_every_tick() -> None:
    """Give a single string as the labels and check it is used.

    A lone string labels the first tick and leaves the rest formatted by
    nothing, which is how a single annotated value is drawn.

    `SetAxisKwargs` declares `list[str] | bool | None`, so the checkers
    refuse the call the code supports; that gap is an open bug with its own
    test in test_with_issues.py.
    """
    image, ax = _axis()
    image.set_axis(xticks=[0, 0.5, 1], xtickslabels="only")  # pyright: ignore[reportArgumentType] # ty: ignore[invalid-argument-type]

    assert ax.get_xticklabels()[0].get_text() == "only"


def test_labels_are_blanked_when_the_ticks_are_automatic() -> None:
    """Blank the labels while leaving the ticks to matplotlib.

    The ticks stay where matplotlib put them and lose their text, which is
    how an axis is stripped without choosing its ticks by hand.
    """
    image, ax = _axis()
    image.set_axis(xtickslabels=None)

    assert all(not t.get_text() for t in ax.get_xticklabels())


def test_labels_without_ticks_warn() -> None:
    """Remove the ticks and give labels for them in the same call.

    The labels have nothing to sit on, so they are dropped; without the
    warning the axis would simply come back bare with no explanation.
    """
    image, _ = _axis()

    with pytest.warns(UserWarning, match="tickslabels are defined with no"):
        image.set_axis(xticks=None, xtickslabels=["a", "b"])


def test_labels_on_automatic_ticks_warn() -> None:
    """Give labels while the ticks are left automatic.

    Matplotlib chooses the ticks, so a fixed list of labels would be
    attached to positions the user did not choose and would move with the
    data; the manager says so.

    The labels are then applied anyway, which makes matplotlib warn in turn
    about a FixedFormatter without a FixedLocator. That second warning is
    an open bug with its own test in test_with_issues.py; it is recorded
    here so this test does not depend on it either way.
    """
    image, _ = _axis()

    with warnings.catch_warnings(record=True) as raised:
        warnings.simplefilter("always")
        image.set_axis(xtickslabels=["a", "b"])

    messages = [str(w.message) for w in raised]
    assert any("should be fixed only" in message for message in messages)


def test_labels_of_the_wrong_kind_are_refused() -> None:
    """Give a number as the tick labels.

    A string or a sequence of them is what can be written on an axis;
    anything else is a mistake worth naming, rather than a formatter built
    from something meaningless.
    """
    image, _ = _axis()

    with pytest.raises(TypeError, match="Invalid tick labels"):
        image.set_axis(xticks=[0, 1], xtickslabels=42)  # pyright: ignore[reportArgumentType] # ty: ignore[invalid-argument-type]


@pytest.mark.parametrize("minor", ["on", "off"])
def test_the_minor_ticks_follow_the_keyword(minor: str) -> None:
    """Switch the minor ticks on and off, and count them.

    They are subdivisions between the labelled ticks, so 'off' must leave
    none at all while 'on' leaves several.
    """
    image, ax = _axis()
    image.set_axis(minorticks=minor)

    count = len(ax.get_xticks(minor=True))
    assert (count > 0) is (minor == "on")


def test_a_single_label_without_minor_ticks() -> None:
    """Give one label and switch the minor ticks off in the same call.

    The single-label path places its own minor locator, so it has to honour
    the keyword too; otherwise minor ticks would come back on an axis that
    asked for none.
    """
    image, ax = _axis()
    image.set_axis(
        xticks=[0, 0.5, 1],
        xtickslabels="only",  # ty: ignore[invalid-argument-type] # pyright: ignore[reportArgumentType]
        minorticks="off",
    )

    assert len(ax.get_xticks(minor=True)) == 0


def test_set_ticks_does_nothing_when_both_are_automatic() -> None:
    """Call set_ticks with both the ticks and the labels left automatic.

    set_axis never makes this call -- it only calls the helper when one of
    the two is given -- but the helper is public, and asking it to change
    nothing must leave matplotlib's own ticks in place.
    """
    image, ax = _axis()
    before = list(ax.get_xticks())

    image.AxisManager.set_ticks(ax, True, True, "x")

    assert list(ax.get_xticks()) == before


def test_the_minor_ticks_are_dropped_on_a_log_scale() -> None:
    """Label the ticks on a log axis and check no minor ticks are left.

    Minor ticks on a log scale are placed by decade, so the even spacing
    they get here would be wrong; the manager removes them instead.
    """
    image, ax = _axis()
    image.set_axis(
        xscale="log", xticks=[1, 10, 100], xtickslabels=["1", "10", "100"]
    )

    assert len(ax.get_xticks(minor=True)) == 0


# ---- Scales, grid and size ----
def test_the_scales() -> None:
    """Set both axes to a logarithmic scale.

    The scale is recorded on the state as well, since the range machinery
    pads a logarithmic axis differently from a linear one.
    """
    image, ax = _axis()
    image.set_axis(xscale="log", yscale="log")

    assert ax.get_xscale() == "log"
    assert ax.get_yscale() == "log"
    assert image.xscale[0] == "log"
    assert image.yscale[0] == "log"


def test_a_scale_with_a_threshold() -> None:
    """Set a symlog scale and give it the width of its linear part.

    Below the threshold a symlog axis is linear, which is what lets it
    cross zero; the number is passed to matplotlib under a name that
    differs per scale, so it is worth pinning.
    """
    image, ax = _axis()
    image.set_axis(xscale="symlog", xtresh=0.01)

    assert ax.get_xscale() == "symlog"
    transform = ax.xaxis.get_transform()
    assert getattr(transform, "linthresh", None) == pytest.approx(0.01)


@pytest.mark.parametrize(
    ("grid", "xvisible", "yvisible"),
    [
        (True, True, True),
        ("both", True, True),
        ("x", True, False),
        ("y", False, True),
    ],
)
def test_the_grid(
    grid: bool | Literal["x", "y", "both"], xvisible: bool, yvisible: bool
) -> None:
    """Switch the grid on, for both directions or for one.

    'x' draws the vertical lines that mark the x ticks and leaves the
    horizontal ones alone, which is how one direction is emphasised.
    """
    image, ax = _axis()
    image.set_axis(grid=grid)

    assert ax.xaxis.get_gridlines()[0].get_visible() is xvisible
    assert ax.yaxis.get_gridlines()[0].get_visible() is yvisible


@pytest.mark.parametrize("tight", [True, False])
def test_the_layout_is_reinforced_only_when_asked(tight: bool) -> None:
    """Set the layout flag and check it is recorded and acted on.

    set_axis lays the figure out again after changing the axis, since new
    titles and ticks need the room; with the flag off it leaves the
    positions exactly as they are, which is what a hand-placed layout needs.
    """
    image, ax = _axis()
    image.set_axis(tight=tight, title="a title", xtitle="x")

    assert image.tight is tight
    if tight:
        assert ax.get_position().x0 < 0.125
    else:
        assert ax.get_position().x0 == pytest.approx(0.125)


def test_the_tick_label_size() -> None:
    """Give the ticks a size of their own and read it back.

    Separate from the fontsize, so the numbers along the axes can be made
    smaller than the labels without touching anything else.
    """
    image, ax = _axis()
    image.set_axis(tickssize=7)

    assert ax.get_xticklabels()[0].get_fontsize() == 7


@pytest.mark.parametrize(("direction", "marker"), [("in", 2), ("out", 3)])
def test_the_tick_direction(direction: str, marker: int) -> None:
    """Point the ticks each way and check matplotlib was told.

    pyPLUTO draws them inwards while matplotlib's own default is outwards,
    so the keyword matters in both directions. It is read off the tick's
    marker, which is how matplotlib says which way it points: 2 inwards and
    3 outwards, written out by hand here.
    """
    image, ax = _axis()
    image.set_axis(ticksdir=direction)

    assert ax.xaxis.get_major_ticks()[0].tick1line.get_marker() == marker


# ---- Sharing ----
@pytest.mark.parametrize("keyword", ["sharex", "sharey"])
def test_share_axes_documents_what_it_accepts(keyword: str) -> None:
    """Compare the documented type of `sharex` with the one it really takes.

    The value goes straight to `ax.sharex()`, which takes an axis, and
    `SetAxisKwargs` declares exactly that. The docstring promised
    `bool | str | Matplotlib axis` with a default of False, so `sharex=True`
    raised a TypeError from inside matplotlib. Sharing between all the
    subplots of a figure is `sharexaxes`, read by create_axes.
    """
    documented = inspect.getdoc(AxisManager.share_axes) or ""
    entry = next(
        line
        for line in documented.splitlines()
        if line.startswith(f"- {keyword}:")
    )

    assert "bool" not in entry
    assert "default False" not in entry


@pytest.mark.parametrize("keyword", ["sharex", "sharey"])
def test_an_axis_can_be_shared_with_another(keyword: str) -> None:
    """Tie one axis to another after both were created.

    What `sharexaxes` does at creation, done afterwards for two axes that
    already exist: panning one then moves the other.
    """
    image = pp.Image(text=False)
    axes = image.create_axes(ncol=2)
    assert isinstance(axes, list)

    if keyword == "sharex":
        image.set_axis(ax=axes[1], sharex=axes[0])
        shared = axes[0].get_shared_x_axes()
    else:
        image.set_axis(ax=axes[1], sharey=axes[0])
        shared = axes[0].get_shared_y_axes()

    assert shared.joined(axes[0], axes[1])
