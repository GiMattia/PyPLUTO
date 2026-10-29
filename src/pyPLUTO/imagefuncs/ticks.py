"""TicksManager class.

It sets the ticks and the ticks labels of an axis, for xticks/xtickslabels
and yticks/ytickslabels through set_axis, and for cticks/ctickslabels on a
colorbar. Both keywords take the same three kinds of value: True leaves them
automatic, None removes them and a list fixes them.

Labels are written only on ticks that are known: the ticks given in the same
call or, on an axis of the figure, the ticks given in an earlier call, which
the state keeps in ticks together with their labels. Labels given where no
ticks are known, or in a number different from the ticks, are ignored with a
warning. Removing the labels (None) needs no ticks. What the state keeps is
applied again by set_axis when a scale is set, since matplotlib then puts
back the default ticks of the scale.
"""

from __future__ import annotations

from collections.abc import Iterable

from matplotlib.axes import Axes
from matplotlib.ticker import (
    AutoMinorLocator,
    FixedFormatter,
    LogFormatterSciNotation,
    NullFormatter,
    NullLocator,
    ScalarFormatter,
)

from pyPLUTO.imagemixin import ImageMixin
from pyPLUTO.imagestate import ImageState
from pyPLUTO.utils.pperrors import PyPLUTOOptionError
from pyPLUTO.utils.ppwarnings import (
    PPWarn,
    PyPLUTOConflictWarning,
    PyPLUTOOptionWarning,
)


class TicksManager(ImageMixin):
    """TicksManager class.

    It provides the methods that set the ticks of an axis and their labels,
    shared by set_axis and colorbar so that the same values mean the same
    thing on both.
    """

    def __init__(self, state: ImageState) -> None:
        """Initialize the TicksManager with the given state."""
        self.state = state

    def set_ticks(
        self,
        ax: Axes,
        tc: list[float] | bool | None,
        tl: str | list[str] | list[float] | bool | None,
        typeaxis: str,
        minor: str | int | None = "on",
        nax: int | None = None,
    ) -> None:
        """Set the ticks and the ticks labels on the x- or y-axis of an axis.

        True leaves the ticks or the labels as they are, None removes them
        and a list fixes them. Ticks given are fixed, with the labels given
        in the same call or with automatic ones: labels of an earlier call
        belonged to the earlier ticks. Labels given alone go on the ticks of
        an earlier call; with none, they are ignored with a warning and what
        is kept stays. Labels removed need no ticks. On an axis of the figure
        what is set is kept in the state, for the axis and for those sharing
        its ticks, to be applied again after a scale.

        Parameters
        ----------
        - ax (not optional): Axes
            The axis whose ticks are set.
        - minor: str | int | None, default 'on'
            'off' leaves no minor ticks next to fixed labels.
        - nax: int | None, default None
            The index of the axis, whose kept ticks are read and updated.
            None for a colorbar, which keeps nothing.
        - tc (not optional): list[float] | bool | None
            The ticks: True as they are, None removed, a list fixed.
        - tl (not optional): str | list[str] | list[float] | bool | None
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

        - Example #3: labels on the ticks fixed earlier on the first axis

            >>> self.set_ticks(ax, True, ["a", "b", "c"], "x", nax=0)

        """
        # Neither ticks nor labels given: nothing to do
        if tc is True and tl is True:
            return

        # Labels alone go on the kept ticks; if ignored, what is kept stays
        alone = tc is True
        if alone and nax is not None:
            tc = self.state.ticks[nax][typeaxis][0]
        labels = self.check_labels(tc, tl)
        if alone and labels is True:
            return

        self.apply_ticks(ax, tc, labels, typeaxis, minor)

        # Shared axes share their ticks, so every one of them keeps them
        if nax is not None:
            for i in self.shared(ax, typeaxis):
                self.state.ticks[i][typeaxis] = (tc, labels)

    def shared(self, ax: Axes, typeaxis: str) -> list[int]:
        """Return the indices of the axes sharing the x- or y-axis of an axis.

        Axes sharing a direction share its ticks and minor ticks, so what is
        kept for one of them is kept for all. The axis itself is included.

        Parameters
        ----------
        - ax (not optional): Axes
            The axis whose shared axes are looked for.
        - typeaxis (not optional): str
            The shared direction, 'x' or 'y'.

        Returns
        -------
        - list[int]
            The indices of the axes, the axis itself included.

        Examples
        --------
        - Example #1: two axes sharing x, the first given

            >>> self.shared(self.state.ax[0], "x")
            [0, 1]

        """
        siblings = getattr(ax, f"get_shared_{typeaxis}_axes")().get_siblings(ax)
        return [i for i, other in enumerate(self.state.ax) if other in siblings]

    def check_labels(
        self,
        tc: list[float] | bool | None,
        tl: str | list[str] | list[float] | bool | None,
    ) -> list[str] | bool | None:
        """Return the labels as a list if they can go on the ticks, or True.

        Labels written need ticks to go on, one label each: with no ticks,
        automatic or removed, or with a different number of them, they are
        ignored with a warning, and True leaves the labels automatic. A
        string is a single label, a sequence one label per tick; a number
        is written as matplotlib writes a value, in the font of the ticks.
        True and None are returned as they are, since they write nothing.

        Parameters
        ----------
        - tc (not optional): list[float] | bool | None
            The ticks the labels would go on.
        - tl (not optional): str | list[str] | list[float] | bool | None
            The labels given.

        Returns
        -------
        - list[str] | bool | None
            The labels as a list, True if they are ignored, or None.

        Raises
        ------
        - PyPLUTOOptionError
            If the labels are neither a string nor a sequence.

        Examples
        --------
        - Example #1: a single label on a single tick

            >>> self.check_labels([0], "only")
            ['only']

        - Example #2: three labels for two ticks are ignored

            >>> self.check_labels([0, 1], ["a", "b", "c"])
            True

        """
        if tl is True or tl is None:
            return tl
        if isinstance(tc, bool) or tc is None:
            warn = "Ticks labels given without ticks are ignored: give the "
            warn += "ticks they go on in the same call or in an earlier one."
            PPWarn.warn(warn, PyPLUTOConflictWarning)
            return True
        if not isinstance(tl, str | Iterable):
            raise PyPLUTOOptionError(f"Invalid tick labels: {tl!r}")
        labels = [tl] if isinstance(tl, str) else list(tl)
        if len(labels) != len(tc):
            warn = f"{len(labels)} ticks labels for {len(tc)} ticks: the "
            warn += "labels are ignored."
            PPWarn.warn(warn, PyPLUTOOptionWarning)
            return True

        # Numbers are written as matplotlib writes a value
        number = ScalarFormatter(useMathText=True)
        return [
            label
            if isinstance(label, str)
            else r"$\mathdefault{" + number.format_data(label) + "}$"
            for label in labels
        ]

    def apply_ticks(
        self,
        ax: Axes,
        tc: list[float] | bool | None,
        tl: list[str] | bool | None,
        typeaxis: str,
        minor: str | int | None = "on",
    ) -> None:
        """Apply ticks and labels, already checked, to the x- or y-axis.

        Ticks removed take the minor ones and the labels with them, since a
        log scale places its own minor ticks at every multiple of each decade
        with no major to follow. Labels go through the formatters of the
        axis: None empties them, on automatic and fixed ticks alike, and a
        list fixes them, leaving the minor ticks unlabeled and switching them
        off unless the scale is linear and minor is not 'off'. Fixed ticks
        with automatic labels get the formatter matplotlib gives the scale,
        writing on every tick of a non-linear scale rather than on its powers
        of ten only, and the minor ticks of the scale unless minor is 'off'.

        Parameters
        ----------
        - ax (not optional): Axes
            The axis whose ticks are applied.
        - minor: str | int | None, default 'on'
            'off' leaves no minor ticks next to fixed labels.
        - tc (not optional): list[float] | bool | None
            The ticks: True as they are, None removed, a list fixed.
        - tl (not optional): list[str] | bool | None
            The ticks labels: True as they are, None removed, a list fixed.
        - typeaxis (not optional): str
            The axis of the ticks, 'x' or 'y'.

        Returns
        -------
        - None

        Examples
        --------
        - Example #1: fixed ticks with their labels on the x-axis

            >>> self.apply_ticks(ax, [0, 1], ["a", "b"], "x")

        - Example #2: the ticks kept for the first axis, after a scale

            >>> self.apply_ticks(ax, *self.state.ticks[0]["x"], "x")

        """
        axis = getattr(ax, f"{typeaxis}axis")
        set_ticks = getattr(ax, f"set_{typeaxis}ticks")
        scale = getattr(ax, f"get_{typeaxis}scale")()

        # No ticks: no labels and no minor ticks either
        if tc is None:
            set_ticks([])
            axis.set_minor_locator(NullLocator())
            return

        if tc is not True:
            set_ticks(tc)

        # Labels removed
        if tl is None:
            axis.set_major_formatter(NullFormatter())
            axis.set_minor_formatter(NullFormatter())

        # Labels fixed, one per tick, with the minor ticks unlabeled
        elif isinstance(tl, list):
            axis.set_major_formatter(FixedFormatter(tl))
            axis.set_minor_formatter(NullFormatter())
            if minor == "off" or scale != "linear":
                axis.set_minor_locator(NullLocator())
            else:
                axis.set_minor_locator(AutoMinorLocator(5))

        # Automatic labels on fixed ticks: matplotlib's, on every tick
        elif tc is not True:
            formatter = ScalarFormatter()
            if scale != "linear":
                every = (float("inf"), float("inf"))
                formatter = LogFormatterSciNotation(
                    labelOnlyBase=False, minor_thresholds=every
                )
            axis.set_major_formatter(formatter)
            if minor != "off":
                axis.minorticks_on()
