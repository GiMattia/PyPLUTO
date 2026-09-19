"""Test of the range.py file.

RangeManager decides the limits of every plot that does not set them by hand,
so a fault here is a plot that looks fine and shows the wrong window. Nothing
it does raises: the tests compare numbers.

The four cases it works with are the values of `setax`/`setay` per axis: 0 no
limits yet, 1 fixed by the user, 2 limits present and free to grow, 3 being
fixed now. They are held by the manager as `changerange`, `adaptrange` and
`fixrange`; case 1 has no name because it is the one where nothing happens.

The expected limits below are written out by hand from the arithmetic in
`range_offset`, since deriving them from the code would compare it with
itself: a padding of `margin * (ymax - ymin)` on each side, a zero-width
range padded from a tenth of `ymax`, and a logarithmic scale clamped so the
lower limit stays positive.
"""

import warnings

import numpy as np
import pytest

import pyPLUTO as pp
from pyPLUTO.imagefuncs.range import RangeManager

x = np.linspace(0.0, 1.0, 20)
y = np.linspace(1.0, 2.0, 20)

# (ymin, ymax, scale, margin) -> the limits range_offset must return.
#
# linear/symlog/asinh: padding is margin * (ymax - ymin) on each side.
# zero width: the range becomes ymax * 0.1, so padding is margin * that.
# log: the lower limit is the larger of ymin - padding and ymin * 0.5.
# a range above 1e10 on a non-linear scale doubles the padding per decade.
# an unknown scale is returned untouched.
OFFSETS: list[tuple[float, float, str, float, tuple[float, float]]] = [
    (0.0, 1.0, "linear", 0.1, (-0.1, 1.1)),
    (0.0, 1.0, "linear", 0.5, (-0.5, 1.5)),
    (0.0, 1.0, "symlog", 0.1, (-0.1, 1.1)),
    (0.0, 1.0, "asinh", 0.1, (-0.1, 1.1)),
    (1.0, 1.0, "linear", 0.1, (0.99, 1.01)),
    (1.0, 10.0, "log", 0.1, (0.5, 10.9)),
    (0.0, 1e11, "linear", 0.1, (-1e10, 1.1e11)),
    (0.0, 1e11, "symlog", 0.1, (-2.2e11, 3.2e11)),
    (0.0, 1.0, "logit", 0.1, (0.0, 1.0)),
]


def _manager() -> tuple[RangeManager, pp.Image]:
    """Build an image with one axis and a manager reading its state."""
    image = pp.Image(text=False)
    image.create_axes()
    return RangeManager(image.state), image


# ---- Range offset ----
@pytest.mark.parametrize(
    ("ymin", "ymax", "scale", "margin", "expected"), OFFSETS
)
def test_range_offset(
    ymin: float,
    ymax: float,
    scale: str,
    margin: float,
    expected: tuple[float, float],
) -> None:
    """Compare one padded range with the limits written out by hand.

    Exact numbers rather than "wider than the data": padding that is applied
    twice, or to one side only, still passes an inequality and moves every
    automatic plot.
    """
    manager, _ = _manager()
    assert manager.range_offset(ymin, ymax, scale, margin) == pytest.approx(
        expected
    )


def test_range_offset_default_margin() -> None:
    """Check the default margin is the 0.1 the table above assumes.

    Every other expectation here is written for that default, so a change to
    it would leave them silently checking a different function.
    """
    manager, _ = _manager()
    assert manager.range_offset(0.0, 1.0, "linear") == pytest.approx(
        manager.range_offset(0.0, 1.0, "linear", 0.1)
    )


@pytest.mark.parametrize(
    ("constant", "expected"),
    [(1.0, (0.99, 1.01)), (-5.0, (-5.05, -4.95)), (0.0, (-0.1, 0.1))],
)
def test_range_offset_constant_data(
    constant: float, expected: tuple[float, float]
) -> None:
    """Pad a range whose data is a single constant, of either sign.

    Constant data has no range of its own, so the padding comes from the
    value: a tenth of it, in absolute terms. Taking it signed put the limits
    the wrong way round for a negative constant and drew the axis upside
    down, and a constant zero gave no range at all plus a log10(0) warning.
    """
    manager, _ = _manager()

    with warnings.catch_warnings():
        warnings.simplefilter("error", RuntimeWarning)
        limits = manager.range_offset(constant, constant, "linear")

    assert limits == pytest.approx(expected)


def test_range_offset_negative_log_warns() -> None:
    """Check a range crossing zero on a log scale warns and stays positive.

    A logarithmic axis cannot show a negative limit, so the range is folded
    to absolute values. The user is told, because the plot then shows
    something other than what was asked for.
    """
    manager, _ = _manager()
    with pytest.warns(UserWarning, match="Negative range"):
        ymin, ymax = manager.range_offset(-1.0, 10.0, "log")

    assert ymin > 0.0
    assert (ymin, ymax) == pytest.approx((0.5, 11.1))


# ---- X range ----
def test_set_xrange_case_0_sets_limits_and_switches_case() -> None:
    """Set the first limits of an axis and check the case moves on.

    Case 0 is an axis nothing has drawn on yet. Once it has limits the case
    becomes 2, so the next plot widens them instead of replacing them.
    """
    manager, image = _manager()
    manager.set_xrange(image.ax[0], 0, [0.0, 2.0], manager.changerange)

    assert image.ax[0].get_xlim() == pytest.approx((0.0, 2.0))
    assert image.state.setax[0] == manager.adaptrange


def test_set_xrange_case_1_changes_nothing() -> None:
    """Check limits the user fixed are left alone.

    Case 1 is what `set_axis(xrange=...)` leaves behind. A later plot must
    not move the window the user chose.
    """
    manager, image = _manager()
    image.ax[0].set_xlim(0.0, 1.0)

    manager.set_xrange(image.ax[0], 0, [5.0, 6.0], 1)

    assert image.ax[0].get_xlim() == pytest.approx((0.0, 1.0))


def test_set_xrange_case_2_widens_to_hold_both() -> None:
    """Check a second plot widens the axis instead of replacing its limits.

    The union of the two, so both curves stay visible: taking the new limits
    alone would push the first plot out of the window.
    """
    manager, image = _manager()
    image.ax[0].set_xlim(0.0, 1.0)

    manager.set_xrange(image.ax[0], 0, [-1.0, 0.5], manager.adaptrange)

    assert image.ax[0].get_xlim() == pytest.approx((-1.0, 1.0))


def test_set_xrange_case_3_fixes_the_limits() -> None:
    """Set limits by hand and check the axis is then left alone.

    Case 3 is `set_axis(xrange=...)`. It applies the limits and switches to
    case 1, which is what stops the next plot from widening them.
    """
    manager, image = _manager()
    manager.set_xrange(image.ax[0], 0, [3.0, 4.0], manager.fixrange)

    assert image.ax[0].get_xlim() == pytest.approx((3.0, 4.0))
    assert image.state.setax[0] == 1


# ---- Y range ----
def test_set_yrange_case_0_pads_the_data() -> None:
    """Check the first y-limits are the data with a margin around it.

    Unlike the x-axis, the y-limits are computed from the data rather than
    taken as given, so the curve does not touch the frame: 1.0 to 2.0 padded
    by a tenth of the range.
    """
    manager, image = _manager()
    manager.set_yrange(
        image.ax[0], 0, [0.0, 0.0], manager.changerange, data=(x, y)
    )

    assert image.ax[0].get_ylim() == pytest.approx((0.9, 2.1))
    assert image.state.setay[0] == manager.adaptrange


@pytest.mark.parametrize("case", [0, 2])
def test_set_yrange_without_data_raises(case: int) -> None:
    """Ask for computed limits without the data and expect a refusal.

    Both cases that compute the limits need the arrays; without them the
    manager would have nothing to measure, and a silent default would size
    every axis wrongly.
    """
    manager, image = _manager()
    with pytest.raises(ValueError, match="x and y arrays must be provided"):
        manager.set_yrange(image.ax[0], 0, [0.0, 1.0], case)


def test_set_yrange_case_2_widens_to_hold_both() -> None:
    """Check a second plot widens the y-axis rather than replacing it.

    The counterpart of the x-axis test, with the padding applied first: the
    result holds both the previous window and the new padded data.
    """
    manager, image = _manager()
    image.ax[0].set_ylim(0.0, 1.5)

    manager.set_yrange(
        image.ax[0], 0, [0.0, 0.0], manager.adaptrange, data=(x, y)
    )

    assert image.ax[0].get_ylim() == pytest.approx((0.0, 2.1))


def test_set_yrange_case_3_fixes_the_limits() -> None:
    """Set the y-limits by hand and check the axis is then left alone.

    Unlike the computed cases this one takes the limits as given, with no
    padding, and switches to case 1.
    """
    manager, image = _manager()
    manager.set_yrange(image.ax[0], 0, [0.0, 3.0], manager.fixrange)

    assert image.ax[0].get_ylim() == pytest.approx((0.0, 3.0))
    assert image.state.setay[0] == 1


# ---- Through the facade ----
def test_second_plot_widens_the_axis() -> None:
    """Draw twice on one axis and check both curves fit.

    The case machinery end to end: the first plot leaves case 2 behind, so
    the second widens the window rather than cropping to its own data.
    """
    image = pp.Image(text=False)
    image.plot(x, y)
    image.plot(x + 5.0, y)

    # x spans 0 to 1, the second curve 5 to 6.
    xmin, xmax = image.ax[0].get_xlim()
    assert xmin <= 0.0
    assert xmax >= 6.0


def test_fixed_range_survives_a_later_plot() -> None:
    """Fix a range, draw again, and check the window did not move.

    What case 1 is for: a user who set the limits keeps them, however much
    data is drawn afterwards.
    """
    image = pp.Image(text=False)
    image.plot(x, y)
    image.set_axis(xrange=[0.0, 2.0])
    image.plot(x + 5.0, y)

    assert image.ax[0].get_xlim() == pytest.approx((0.0, 2.0))


def test_automatic_range_contains_the_data() -> None:
    """Draw once and check the data is inside the axis.

    The plain case a user sees on every first plot, and the one the padding
    exists for.
    """
    image = pp.Image(text=False)
    image.plot(x, y)

    # x spans 0 to 1.
    xmin, xmax = image.ax[0].get_xlim()
    assert xmin <= 0.0
    assert xmax >= 1.0
