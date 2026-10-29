"""Test of the ticks.py file.

TicksManager sets the ticks of an axis and their labels, for set_axis and for
the colorbar alike. Labels are written only on known ticks: the ones given in
the same call or, on an axis of the figure, the ones kept from an earlier
call. The rule is tested here through set_axis, since what the user writes is
`xticks=` and `xtickslabels=`, with every sequence of calls in the SEQUENCES
table. The colorbar, which keeps nothing, is tested in test_colorbar.py, and
the ticks applied again after a scale in test_set_axis.py.
"""

import warnings
from typing import Any

import numpy as np
import pytest
from matplotlib.axes import Axes
from matplotlib.ticker import NullLocator

import pyPLUTO as pp
from pyPLUTO.utils.pperrors import PyPLUTOOptionError
from pyPLUTO.utils.ppwarnings import (
    PyPLUTOConflictWarning,
    PyPLUTOOptionWarning,
)

# The labels matplotlib writes on an untouched axis, and the same ticks empty
AUTOMATIC = "automatic"
HIDDEN = "hidden"

ABC = ["a", "b", "c"]
TICKS = [0.1, 0.5, 0.9]

# The labels 1.5, 2 and 3e4, written as matplotlib writes a value
NUMBERS = [
    r"$\mathdefault{1.5}$",
    r"$\mathdefault{2}$",
    r"$\mathdefault{3 \times 10^{4}}$",
]

# Each sequence of set_axis calls on the x-axis: the labels then shown, the
# ticks and labels kept in the state, and the warning raised, if any.
SEQUENCES = [
    pytest.param(
        [{"xticks": TICKS, "xtickslabels": ABC}],
        {0.1: "a", 0.5: "b", 0.9: "c"},
        (TICKS, ABC),
        None,
        id="ticks-and-labels",
    ),
    pytest.param(
        [{"xticks": [0.5], "xtickslabels": "half"}],
        {0.5: "half"},
        ([0.5], ["half"]),
        None,
        id="one-string-label",
    ),
    pytest.param(
        [{"xticks": TICKS, "xtickslabels": [1.5, 2, 3e4]}],
        {0.1: NUMBERS[0], 0.5: NUMBERS[1], 0.9: NUMBERS[2]},
        (TICKS, NUMBERS),
        None,
        id="numbers-as-labels",
    ),
    pytest.param(
        [{"xticks": [0.25, 0.75]}],
        {0.25: "0.25", 0.75: "0.75"},
        ([0.25, 0.75], True),
        None,
        id="ticks-alone",
    ),
    pytest.param(
        [{"xticks": None}],
        {},
        (None, True),
        None,
        id="ticks-removed",
    ),
    pytest.param(
        [{"xticks": TICKS}, {"xtickslabels": ABC}],
        {0.1: "a", 0.5: "b", 0.9: "c"},
        (TICKS, ABC),
        None,
        id="labels-on-earlier-ticks",
    ),
    pytest.param(
        [{"xticks": TICKS, "xtickslabels": ABC}, {"xticks": [0.25, 0.75]}],
        {0.25: "0.25", 0.75: "0.75"},
        ([0.25, 0.75], True),
        None,
        id="new-ticks-forget-the-labels",
    ),
    pytest.param(
        [{"xtickslabels": ABC}],
        AUTOMATIC,
        (True, True),
        PyPLUTOConflictWarning,
        id="labels-without-ticks",
    ),
    pytest.param(
        [{"xticks": [0.25, 0.75], "xtickslabels": ABC}],
        {0.25: "0.25", 0.75: "0.75"},
        ([0.25, 0.75], True),
        PyPLUTOOptionWarning,
        id="labels-of-the-wrong-count",
    ),
    pytest.param(
        [{"xticks": TICKS, "xtickslabels": ABC}, {"xtickslabels": ["x", "y"]}],
        {0.1: "a", 0.5: "b", 0.9: "c"},
        (TICKS, ABC),
        PyPLUTOOptionWarning,
        id="ignored-labels-leave-the-kept-ones",
    ),
    pytest.param(
        [{"xtickslabels": None}],
        HIDDEN,
        (True, None),
        None,
        id="labels-removed",
    ),
    pytest.param(
        [{"xtickslabels": None}, {"xtickslabels": ABC}],
        HIDDEN,
        (True, None),
        PyPLUTOConflictWarning,
        id="ignored-labels-leave-them-removed",
    ),
    pytest.param(
        [{"xticks": TICKS}, {"xtickslabels": None}],
        {0.1: "", 0.5: "", 0.9: ""},
        (TICKS, None),
        None,
        id="labels-removed-from-earlier-ticks",
    ),
]


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


@pytest.mark.parametrize(("calls", "shown", "kept", "category"), SEQUENCES)
def test_a_sequence_of_calls(
    calls: list[dict[str, Any]],
    shown: dict[float, str] | str,
    kept: tuple[Any, Any],
    category: type[Warning] | None,
) -> None:
    """Make a sequence of set_axis calls of SEQUENCES on a fresh axis.

    The labels shown, the ticks and labels the state keeps and the warnings
    raised must be the ones of the table. A failure means the rule of known
    ticks is broken: labels written where no ticks are known, labels of
    earlier ticks left on new ones, ignored labels that still changed what
    is kept, or a warning missing or unexpected.
    """
    # Read before the image under test, which reuses the same figure
    if shown == AUTOMATIC:
        shown = _shown(_axis()[0])
    elif shown == HIDDEN:
        shown = dict.fromkeys(_shown(_axis()[0]), "")
    image, _ = _axis()

    with warnings.catch_warnings(record=True) as raised:
        warnings.simplefilter("always")
        for call in calls:
            image.set_axis(**call)

    assert _shown(image) == shown
    assert image.ticks[0]["x"] == kept
    assert [w.category for w in raised] == ([category] if category else [])


def test_labels_of_the_wrong_kind_are_refused() -> None:
    """Give a number as the labels of fixed ticks.

    A string or a sequence of them is what can be written on an axis, so a
    number raises PyPLUTOOptionError and nothing is kept. A failure means a
    formatter was built from something meaningless.
    """
    image, _ = _axis()
    wrong: Any = 42

    with pytest.raises(PyPLUTOOptionError, match="Invalid tick labels"):
        image.set_axis(xticks=[0.5], xtickslabels=wrong)

    assert image.ticks[0]["x"] == (True, True)


def test_fixed_ticks_of_a_log_scale_are_all_labeled() -> None:
    """Fix ticks off the powers of ten on a log scale, without labels.

    matplotlib alone labels only the powers of ten of a wide log axis, so
    2, 5 and 20 would show nothing; every fixed tick must carry its label.
    A failure means the automatic labels were left to the default rule.
    """
    image = pp.Image(text=False)
    data = np.geomspace(1.0, 1000.0, 4)

    image.plot(data, data, xscale="log", xticks=[2, 5, 20, 100])

    assert len(_shown(image)) == 4
    assert all(_shown(image).values())


def test_minor_ticks_come_back_with_the_automatic_labels() -> None:
    """Fix labels on a log scale, then fix the ticks alone.

    Fixed labels switch off the minor ticks of a log scale; once the new
    ticks forget the labels, the minor ticks of the scale are back. A
    failure means the axis stayed as the forgotten labels left it.
    """
    image, ax = _axis()
    image.set_axis(xscale="log", xticks=[1, 10], xtickslabels=["a", "b"])
    assert isinstance(ax.xaxis.get_minor_locator(), NullLocator)

    image.set_axis(xticks=[1, 100])

    assert not isinstance(ax.xaxis.get_minor_locator(), NullLocator)


def test_axes_sharing_x_keep_the_same_ticks() -> None:
    """Fix ticks and labels on one of two axes sharing x, then scale the other.

    Shared axes share their ticks, so a scale given to either resets both;
    every axis sharing them keeps the ticks set, so the labels come back
    whichever axis gets the scale. A failure means only the axis named in
    the call kept them, and the labels were lost on both.
    """
    image = pp.Image(text=False)
    image.create_axes(ncol=2, sharex=True)
    data = np.array([64.0, 128.0, 256.0, 512.0, 1024.0])
    image.plot(data, data, ax=0, xticks=[128.0, 512.0], xtickslabels=["a", "b"])

    image.plot(data, data, ax=1, xscale="log")

    assert image.ticks[1]["x"] == ([128.0, 512.0], ["a", "b"])
    assert list(_shown(image, 0).values()) == ["a", "b"]
    assert list(_shown(image, 1).values()) == ["a", "b"]
