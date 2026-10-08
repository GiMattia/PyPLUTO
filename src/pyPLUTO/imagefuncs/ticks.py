"""TicksManager class.

It sets the ticks and the ticks labels of an axis, for xticks/xtickslabels
and yticks/ytickslabels through set_axis, and for cticks/ctickslabels on a
colorbar. Both keywords take the same three kinds of value: True leaves them
automatic, None removes them and a list fixes them.

Each axis carries a case in `setxticks`/`setyticks`, as it does for the
ranges: 0 automatic ticks, 1 fixed by the user (a list, or None), 2 ticks
present and free to change, 3 being fixed now.

Case 2 is labels given on automatic ticks. The labels are written on the
ticks matplotlib would choose for the current limits, and those ticks are
pinned, so they do not move under the labels; every drawing method calls
update_ticks once its ranges are set, which pins them again for the new
limits. What the pin replaced, the automatic locator and formatter, is kept
in `xtickspin`/`ytickspin`, to find the ticks of new limits and to give the
axis back when the labels go. A colorbar keeps no case: its range is set
when it is drawn, so its ticks are pinned once.
"""

from __future__ import annotations

import warnings
from collections.abc import Iterable

from matplotlib.axes import Axes
from matplotlib.ticker import (
    AutoMinorLocator,
    FixedFormatter,
    FixedLocator,
    LogFormatterSciNotation,
    NullFormatter,
    NullLocator,
)

from pyPLUTO.imagemixin import ImageMixin
from pyPLUTO.imagestate import ImageState, TicksPin


class TicksManager(ImageMixin):
    """TicksManager class.

    It provides the methods that set the ticks of an axis and their labels,
    shared by set_axis and colorbar so that the same values mean the same
    thing on both.
    """

    def __init__(self, state: ImageState) -> None:
        """Initialize the TicksManager with the given state.

        The cases that do something are named here; case 1, where the user
        has fixed the ticks, is the one that later draws leave alone.
        """
        self.state = state
        self.autoticks = 0
        self.freeticks = 2
        self.fixticks = 3

    def set_ticks(
        self,
        ax: Axes,
        tc: str | list[float] | bool | None,
        tl: str | list[str] | bool | None,
        typeaxis: str,
        minor: str | int | None = "on",
        nax: int | None = None,
    ) -> None:
        """Set the ticks and the ticks labels on the x- or y-axis of an axis.

        True leaves the ticks or the labels as they are, None removes them
        and a list fixes them. Ticks given are fixed now (case 3, then 1),
        and ticks removed take their labels with them, with a warning if
        labels were given too. Labels given alone go on the ticks the user
        fixed (case 1), or else on automatic ticks, which are pinned to the
        current limits (case 2). The labels themselves are set by
        set_tickslabels. The same rules serve xticks/xtickslabels here and
        cticks/ctickslabels on a colorbar.

        Parameters
        ----------
        - ax (not optional): Axes
            The axis whose ticks are set.
        - minor: str | int | None, default 'on'
            'off' leaves no minor ticks next to fixed labels.
        - nax: int | None, default None
            The index of the axis, whose case is read and updated. None for
            a colorbar, which keeps no case.
        - tc (not optional): list[float] | bool | None
            The ticks: True as they are, None removed, a list fixed.
        - tl (not optional): str | list[str] | bool | None
            The ticks labels: True as they are, None removed, a list fixed.
        - typeaxis (not optional): str
            The axis of the ticks, 'x' or 'y'.

        Returns
        -------
        - None

        Examples
        --------
        - Example #1: set ticks and ticks labels on the x-axis

            >>> self.set_ticks(ax, [0, 1, 2, 3], ["0", "1", "2", "3"], "x")

        - Example #2: remove the ticks of the y-axis

            >>> self.set_ticks(ax, None, True, "y")

        - Example #3: labels on the automatic ticks of the first axis

            >>> self.set_ticks(ax, True, ["a", "b", "c"], "x", nax=0)

        """
        axis = getattr(ax, f"{typeaxis}axis")
        cases = getattr(self.state, f"set{typeaxis}ticks")
        pins = getattr(self.state, f"{typeaxis}tickspin")
        case = self.autoticks if nax is None else cases[nax]
        pin = None if nax is None else pins[nax]

        # Case 3: the ticks are given, so they are fixed now and the axis is
        # switched to case 1; labels pinned before give their formatter back
        if tc is not True:
            if pin is not None:
                axis.set_major_formatter(pin[2])
            self.fix_ticks(ax, tc, tl, typeaxis, minor)
            if nax is not None:
                cases[nax], pins[nax] = 1, None
            return

        # From here the ticks are not asked for, so the case decides
        if tl is True:
            return

        # Case 1: the labels go on the ticks the user fixed
        if case == 1:
            ticks = list(axis.get_majorticklocs())
            self.set_tickslabels(ax, ticks, tl, typeaxis, minor)

        # No labels: the ticks are automatic again, with nothing written
        elif tl is None:
            if pin is not None:
                axis.set_major_locator(pin[1])
            self.set_tickslabels(ax, True, None, typeaxis, minor)
            if nax is not None:
                cases[nax], pins[nax] = self.autoticks, None

        # Case 2: the labels go on automatic ticks, pinned to the limits
        else:
            labels = self.find_labels(tl)
            new = self.pin_ticks(ax, labels, typeaxis, pin)
            ticks = list(axis.get_majorticklocs())
            self.set_tickslabels(ax, ticks, labels, typeaxis, minor)
            if nax is not None:
                cases[nax], pins[nax] = self.freeticks, new

        # End of the function

    def fix_ticks(
        self,
        ax: Axes,
        tc: str | list[float] | bool | None,
        tl: str | list[str] | bool | None,
        typeaxis: str,
        minor: str | int | None = "on",
    ) -> None:
        """Fix the ticks of an axis, or remove them, with their labels.

        Ticks removed take the minor ones with them, since a log scale places
        its own at every multiple of each decade with no major to follow;
        labels given with them are reported. Fixed ticks take the labels
        given, or keep automatic ones, which a log scale is told to write on
        every tick rather than on its powers of ten only.

        Parameters
        ----------
        - ax (not optional): Axes
            The axis whose ticks are fixed.
        - minor: str | int | None, default 'on'
            'off' leaves no minor ticks next to fixed labels.
        - tc (not optional): str | list[float] | bool | None
            The ticks: None removed, a list fixed.
        - tl (not optional): str | list[str] | bool | None
            The ticks labels: True automatic, None removed, a list fixed.
        - typeaxis (not optional): str
            The axis of the ticks, 'x' or 'y'.

        Returns
        -------
        - None

        Examples
        --------
        - Example #1: fixed ticks on the x-axis, without labels

            >>> self.fix_ticks(ax, [0, 1, 2, 3], None, "x")

        """
        axis = getattr(ax, f"{typeaxis}axis")
        set_ticks = getattr(ax, f"set_{typeaxis}ticks")

        # Ticks are None: so are the labels and the minor ticks
        if tc is None:
            set_ticks([])
            getattr(ax, f"set_{typeaxis}ticklabels")([])
            axis.set_minor_locator(NullLocator())

            # If tickslabels are not None raise a warning
            if tl is not None and tl is not True:
                warn = (
                    "Warning, tickslabels are defined with no"
                    "ticks!! (function setax)"
                )
                warnings.warn(warn, UserWarning, stacklevel=3)
            return

        set_ticks(tc)

        # Custom tickslabels, or else the decades of a log scale are told to
        # label every tick given, in the same notation
        if tl is not True:
            self.set_tickslabels(ax, tc, tl, typeaxis, minor)
        elif getattr(ax, f"get_{typeaxis}scale")() == "log":
            every = (float("inf"), float("inf"))
            formatter = LogFormatterSciNotation(
                labelOnlyBase=False, minor_thresholds=every
            )
            axis.set_major_formatter(formatter)

    def pin_ticks(
        self,
        ax: Axes,
        labels: list[str],
        typeaxis: str,
        pin: TicksPin | None,
    ) -> TicksPin:
        """Pin the automatic ticks of the current limits, under the labels.

        The ticks are the ones the automatic locator gives for the limits,
        kept to those inside them, so the first label goes on the first tick
        that is seen. The locator and the formatter are the axis's own unless
        a pin already replaced them; a change of scale puts new ones on the
        axis, and those are taken instead of the ones kept.

        Parameters
        ----------
        - ax (not optional): Axes
            The axis whose ticks are pinned.
        - labels (not optional): list[str]
            The labels, one per tick.
        - pin (not optional): TicksPin | None
            What a previous pin kept, or None if the ticks are automatic.
        - typeaxis (not optional): str
            The axis of the ticks, 'x' or 'y'.

        Returns
        -------
        - TicksPin
            The labels, with the automatic locator and formatter.

        Examples
        --------
        - Example #1: pin the x ticks of a first axis under three labels

            >>> self.pin_ticks(ax, ["a", "b", "c"], "x", None)

        """
        axis = getattr(ax, f"{typeaxis}axis")
        locator = axis.get_major_locator()
        formatter = axis.get_major_formatter()
        if pin is not None and isinstance(locator, FixedLocator):
            _, locator, formatter = pin

        # The ticks inside the limits, give or take the rounding of a float
        lo, hi = sorted(getattr(ax, f"get_{typeaxis}lim")())
        tol = 1e-10 * (hi - lo)
        ticks = [
            tick
            for tick in locator.tick_values(lo, hi)
            if lo - tol <= tick <= hi + tol
        ]
        getattr(ax, f"set_{typeaxis}ticks")(ticks)
        axis.set_major_formatter(FixedFormatter(labels))
        return labels, locator, formatter

    def update_ticks(self, ax: Axes, nax: int) -> None:
        """Pin again the ticks under labels, for the limits of now.

        Called by every drawing method once its ranges are set. An axis in
        case 2 gets the automatic ticks of its new limits, with its labels
        on them; every other case is left alone.

        Parameters
        ----------
        - ax (not optional): Axes
            The axis just drawn on.
        - nax (not optional): int
            The index of the axis.

        Returns
        -------
        - None

        Examples
        --------
        - Example #1: after the ranges of the first axis are set

            >>> self.update_ticks(ax, 0)

        """
        for typeaxis in ("x", "y"):
            case = getattr(self.state, f"set{typeaxis}ticks")[nax]
            pins = getattr(self.state, f"{typeaxis}tickspin")
            if case == self.freeticks and (pin := pins[nax]) is not None:
                pins[nax] = self.pin_ticks(ax, pin[0], typeaxis, pin)

    def find_labels(self, tl: str | list[str] | bool) -> list[str]:
        """Return the ticks labels as a list, one label per tick.

        A string is a single label, a sequence one label per tick; anything
        else is a mistake worth naming, rather than a formatter built from
        something meaningless.

        Parameters
        ----------
        - tl (not optional): str | list[str] | bool
            The ticks labels as given.

        Returns
        -------
        - list[str]
            The labels.

        Examples
        --------
        - Example #1: a single label

            >>> self.find_labels("only")
            ['only']

        """
        if not isinstance(tl, str | Iterable):
            raise TypeError(f"Invalid tick labels: {tl!r}")
        return [tl] if isinstance(tl, str) else list(tl)

    def set_tickslabels(
        self,
        ax: Axes,
        tc: str | list[float] | bool | None,
        tl: str | list[str] | bool | None,
        typeaxis: str,
        minor: str | int | None = "on",
    ) -> None:
        """Set the ticks labels of an axis whose ticks are already set.

        The labels go through the formatters of the axis rather than through
        set_xticklabels, which a logarithmic scale resets. None removes them,
        keeping the ticks; a string is a single label, a list one label per
        tick. Fixed labels leave the minor ticks unlabelled, and switch them
        off unless the scale is linear and minor is not 'off'.

        Parameters
        ----------
        - ax (not optional): Axes
            The axis whose ticks labels are set.
        - minor: str | int | None, default 'on'
            'off' leaves no minor ticks next to fixed labels.
        - tc (not optional): list[float] | bool | None
            The ticks, as set_ticks received them: True if automatic.
        - tl (not optional): str | list[str] | bool | None
            The ticks labels: None removed, a string or a list fixed.
        - typeaxis (not optional): str
            The axis of the ticks, 'x' or 'y'.

        Returns
        -------
        - None

        Examples
        --------
        - Example #1: label the fixed ticks of the x-axis

            >>> self.set_tickslabels(ax, [0, 1], ["a", "b"], "x")

        """
        axis = getattr(ax, f"{typeaxis}axis")

        # No labels: on automatic ticks the formatters are emptied, which
        # survives a change of scale; on fixed ones the labels are cleared
        if tl is None:
            if tc is True:
                axis.set_major_formatter(NullFormatter())
                axis.set_minor_formatter(NullFormatter())
            else:
                getattr(ax, f"set_{typeaxis}ticklabels")([])
            return

        # A string is one label, a list one label per tick
        axis.set_major_formatter(FixedFormatter(self.find_labels(tl)))
        axis.set_minor_formatter(NullFormatter())
        scale = getattr(ax, f"get_{typeaxis}scale")()
        if minor == "off" or scale != "linear":
            axis.set_minor_locator(NullLocator())
        else:
            axis.set_minor_locator(AutoMinorLocator(5))
