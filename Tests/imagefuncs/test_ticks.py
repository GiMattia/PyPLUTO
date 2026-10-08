"""Test of the ticks.py file.

TicksManager sets the ticks of an axis and their labels, for set_axis and for
the colorbar alike. Most of what it does is reached through those two and is
tested there, in test_set_axis.py and test_colorbar.py, since what the user
writes is `xticks=` or `cticks=`, not a call to this manager. What is tested
here is the manager called directly.
"""

import warnings

import numpy as np
import pytest
from matplotlib.axes import Axes
from matplotlib.ticker import FixedLocator

import pyPLUTO as pp

x = np.linspace(0.0, 100.0, 11)


def _axis() -> tuple[pp.Image, Axes]:
    """Build a quiet image with one axis to work on.

    create_axes hands back a single axis or a list, so the narrowing is
    done here once rather than in every test below.
    """
    image = pp.Image(text=False)
    axis = image.create_axes()
    assert isinstance(axis, Axes)
    return image, axis


def _shown(image: pp.Image, nax: int = 0) -> dict[float, str]:
    """Draw the figure and return the x ticks seen, with their labels.

    The labels are read from a drawn canvas, since that is when matplotlib
    writes them, and only the ticks inside the limits are kept: those are
    the ones the user sees.
    """
    assert image.fig is not None
    image.fig.canvas.draw()
    ax = image.ax[nax]
    assert isinstance(ax, Axes)
    lo, hi = ax.get_xlim()
    return {
        float(tick.get_loc()): tick.label1.get_text()
        for tick in ax.xaxis.get_major_ticks()
        if lo <= tick.get_loc() <= hi
    }


def test_set_ticks_does_nothing_when_both_are_automatic() -> None:
    """Call set_ticks with both the ticks and the labels left automatic.

    set_axis never makes this call -- it only calls the manager when one of
    the two is given -- but the method is public, and asking it to change
    nothing must leave matplotlib's own ticks in place.
    """
    image, ax = _axis()
    before = list(ax.get_xticks())

    image.TicksManager.set_ticks(ax, True, True, "x")

    assert list(ax.get_xticks()) == before


# ---- Case 2: labels on automatic ticks ----
def test_labels_on_automatic_ticks_are_pinned_without_warnings() -> None:
    """Give labels while the ticks are left automatic.

    The labels go on the ticks matplotlib chooses for the current limits,
    and those ticks are pinned, so the labels cannot drift onto other
    positions; the axis is in case 2. Nothing warns: neither us, since
    this is now a supported call, nor matplotlib, whose complaint was a
    fixed formatter on ticks that were not fixed.
    """
    image, ax = _axis()

    with warnings.catch_warnings(record=True) as raised:
        warnings.simplefilter("always")
        image.set_axis(xtickslabels=["a", "b", "c", "d", "e", "f"])

    assert [str(w.message) for w in raised] == []
    assert isinstance(ax.xaxis.get_major_locator(), FixedLocator)
    assert list(_shown(image).values()) == ["a", "b", "c", "d", "e", "f"]
    assert image.setxticks[0] == 2


def test_labels_given_to_plot_go_on_the_ticks_of_the_data() -> None:
    """Plot data from 0 to 100 with labels on automatic ticks.

    set_axis runs before the ranges are set, when the axis still spans 0 to
    1; the plot pins the ticks again once the data is in, so the labels go
    on 0, 20, ..., 100 rather than on ticks of the empty axis.
    """
    image = pp.Image(text=False)

    with warnings.catch_warnings(record=True) as raised:
        warnings.simplefilter("always")
        image.plot(x, x, xtickslabels=["a", "b", "c", "d", "e", "f"])

    assert [str(w.message) for w in raised] == []
    assert _shown(image) == {
        0.0: "a",
        20.0: "b",
        40.0: "c",
        60.0: "d",
        80.0: "e",
        100.0: "f",
    }


def test_the_ticks_follow_a_wider_range() -> None:
    """Draw a second line that widens the range of a labelled axis.

    The labels stay in case 2, so they are pinned again on the automatic
    ticks of the new limits, as the range itself grows with every line.
    """
    image = pp.Image(text=False)
    image.plot(x, x, xtickslabels=["a", "b", "c"])

    image.plot(4.0 * x, x)

    assert list(_shown(image))[:3] == [0.0, 100.0, 200.0]
    assert list(_shown(image).values())[:3] == ["a", "b", "c"]


def test_labels_on_automatic_ticks_of_a_contour() -> None:
    """Draw a contour on a fresh axis with labels on automatic ticks.

    contour sets no range of its own and lets matplotlib choose the limits,
    so the ticks are pinned once the contour is drawn, on those limits.
    """
    image = pp.Image(text=False)
    xx, yy = np.meshgrid(x, x, indexing="ij")

    image.contour(xx * yy, x1=x, x2=x, xtickslabels=["a", "b", "c"])

    assert list(_shown(image))[:3] == [0.0, 20.0, 40.0]


def test_labels_of_the_wrong_kind_on_automatic_ticks_are_refused() -> None:
    """Give a number as the labels of automatic ticks.

    The same check as for fixed ticks: a string or a sequence of them is
    what can be written on an axis, and the axis is left as it was.
    """
    image, _ = _axis()

    with pytest.raises(TypeError, match="Invalid tick labels"):
        image.set_axis(xtickslabels=42)  # pyright: ignore[reportArgumentType] # ty: ignore[invalid-argument-type]

    assert image.setxticks[0] == 0


# ---- Moving between the cases ----
def test_labels_alone_go_on_ticks_already_fixed() -> None:
    """Fix the ticks, then give the labels in a second call.

    The axis is in case 1, so the labels belong to the ticks the user
    chose, and there is nothing to warn about or to pin.
    """
    image, _ = _axis()
    image.set_axis(xticks=[0.1, 0.5, 0.9])

    with warnings.catch_warnings(record=True) as raised:
        warnings.simplefilter("always")
        image.set_axis(xtickslabels=["a", "b", "c"])

    assert [str(w.message) for w in raised] == []
    assert _shown(image) == {0.1: "a", 0.5: "b", 0.9: "c"}
    assert image.setxticks[0] == 1


def test_fixed_ticks_replace_labels_on_automatic_ones() -> None:
    """Pin labels on automatic ticks, then fix the ticks alone.

    The fixed ticks win, as a range given by hand does, and the labels the
    pin wrote are gone: the formatter it replaced is put back, so the new
    ticks show their values.
    """
    image, _ = _axis()
    image.set_axis(xtickslabels=["a", "b", "c"])

    image.set_axis(xticks=[0.25, 0.75])

    assert _shown(image) == {0.25: "0.25", 0.75: "0.75"}
    assert image.setxticks[0] == 1
    assert image.xtickspin[0] is None


def test_removing_the_labels_frees_the_ticks() -> None:
    """Pin labels on automatic ticks, then remove the labels.

    The ticks were pinned only to carry the labels, so without them they
    are automatic again -- the locator the pin replaced is put back -- and
    nothing is written on them.
    """
    image, ax = _axis()
    image.set_axis(xtickslabels=["a", "b", "c"])

    image.set_axis(xtickslabels=None)

    assert not isinstance(ax.xaxis.get_major_locator(), FixedLocator)
    assert set(_shown(image).values()) == {""}
    assert image.setxticks[0] == 0
    assert image.xtickspin[0] is None
