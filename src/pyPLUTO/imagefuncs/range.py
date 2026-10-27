"""RangeManager class.

It decides the limits of every plot that does not set them by hand, and keeps
them in step as more is drawn on the same axis.

Each axis carries a case in `setax`/`setay`, which is what the methods here
switch between: 0 no limits yet, 1 fixed by the user, 2 limits present and
free to grow, 3 being fixed now, 4 the limits are the data exactly.

The last two are asked for by the caller rather than read off the axis: 3 is
a range the user gave, and 4 belongs to what is drawn as an extent rather
than followed as a curve -- a map, a scatter -- where padding would leave a
strip of empty frame. Case 4 still leaves the axis free to grow, so whatever
is drawn on top of a map is not cut off by it.
"""

from __future__ import annotations

import numpy as np
from matplotlib.axes import Axes

from pyPLUTO.imagemixin import ImageMixin
from pyPLUTO.imagestate import ImageState
from pyPLUTO.utils.pperrors import PyPLUTOInternalError
from pyPLUTO.utils.ppwarnings import PPWarn, PyPLUTOBehaviorWarning


class RangeManager(ImageMixin):
    """RangeManager class.

    It provides methods to set the x and y axis limits for a set of axes in a
    plot.

    The x-limits are the ones given, while the y-limits are computed from the
    data and padded, so a curve never touches the frame.
    """

    def __init__(self, state: ImageState) -> None:
        """Initialize the RangeManager with the given state.

        The three cases that do something are named here; case 1, where the
        user has fixed the limits, is the one where nothing happens.
        """
        self.state = state
        self.changerange = 0
        self.adaptrange = 2
        self.fixrange = 3
        self.strictrange = 4

    def set_xrange(
        self,
        ax: Axes,
        nax: int,
        xlim: list[float],
        case: int,
    ) -> None:
        """Set the lower and upper limits of the x-axis of a set of axes.

        Parameters
        ----------
        - ax (not optional): ax
            The selected set of axes.
        - case (not optional): int
            The case in exam (if range is fixed or variable).
        - nax (not optional): int
            The number of the selected set of axes.
        - xlim (not optional): list[float]
            The limits of the x-axis.

        Returns
        -------
        - None

        Examples
        --------
        - Example #1: Set the x-axis limits of the selected set of axes

            >>> _set_xrange(ax, nax, xlim, case)

        """
        # Case 0: the x-axis limits are set automatically (no previous limit)
        if case == self.changerange:
            ax.set_xlim(xlim[0], xlim[1])

            # Case switched to 2 (previous limits are present now)
            self.state.setax[nax] = 2

        # Case 1: limits are already set and they should not be changed
        #         (aka do nothing)

        # Case 2: the x-axis limit are changed automatically
        #         (previous limit present)
        if case == self.adaptrange:
            xmin = min(xlim[0], ax.get_xlim()[0])
            xmax = max(xlim[1], ax.get_xlim()[1])
            ax.set_xlim(xmin, xmax)

        # Case 3: x-axis limits are set manually
        if case == self.fixrange:
            ax.set_xlim(xlim[0], xlim[1])

            # Case switched to 1 (no change unless stated explicitly otherwise)
            self.state.setax[nax] = 1

        # Case 4: the limits are the ones given, exactly, and free to grow.
        # The case on the axis decides between the two, and case 1 (fixed by
        # the user) is left alone here as everywhere else
        if case == self.strictrange:
            if self.state.setax[nax] == self.adaptrange:
                xmin = min(xlim[0], ax.get_xlim()[0])
                xmax = max(xlim[1], ax.get_xlim()[1])
                ax.set_xlim(xmin, xmax)
            elif self.state.setax[nax] == self.changerange:
                ax.set_xlim(xlim[0], xlim[1])
                self.state.setax[nax] = self.adaptrange

        # End of the function

    def set_yrange(
        self,
        ax: Axes,
        nax: int,
        ylim: list[float],
        case: int,
        data: tuple[np.ndarray | None, np.ndarray | None] = (
            None,
            None,
        ),
    ) -> None:
        """Set the lower and upper limits of the y-axis of a set of axes.

        Unlike the x-axis, the y-axis limits are recovered depending on both the
        x-data and the y-data.

        The two computing cases, 0 and 2, need the data and refuse without it;
        case 4 takes the limits it is given instead, which is how a map or a
        scatter asks for its own extent without the padding a curve gets.

        Parameters
        ----------
        - ax (not optional): ax
            The selected set of axes.
        - case (not optional): int
            The case in exam (if range is fixed or variable).
        - data: tuple[np.ndarray | None, np.ndarray | None]
            The x and y data arrays.
        - nax (not optional): int
            The number of the selected set of axes.
        - ylim (not optional): list[float]
            The limits of the y-axis.

        Returns
        -------
        - None

        Examples
        --------
        - Example #1: Set the y-axis limits of the selected set of axes

            >>> _set_yrange(ax, nax, ylim, case)

        """
        x, y = data
        # Case 0: the y-axis limits are set automatically (no previous limit)
        if case == self.changerange:
            if x is None or y is None:
                raise PyPLUTOInternalError(
                    "x and y arrays must be provided if case is 0"
                )
            ymin, ymax = self.find_ylim(ax, nax, x, y)
            ax.set_ylim(ymin, ymax)

            # Switch to case 2 (previous limits are present now)
            self.state.setay[nax] = 2

        # Case 1: limits are already set and they should not be changed
        # (aka do nothing)

        # Case 2: the y-axis limit are changed automatically
        # (previous limit present)
        if case == self.adaptrange:
            if x is None or y is None:
                raise PyPLUTOInternalError(
                    "x and y arrays must be provided if case is 2"
                )
            ymin, ymax = self.find_ylim(ax, nax, x, y)

            # Check if the limits should be changed
            ymin = np.minimum(ymin, ax.get_ylim()[0])
            ymax = np.maximum(ymax, ax.get_ylim()[1])
            ax.set_ylim(ymin, ymax)

        # Case 3: y-axis limits must be set manually
        if case == self.fixrange:
            ax.set_ylim(ylim[0], ylim[1])

            # Case switched to 1 (no change unless stated explicitly otherwise)
            self.state.setay[nax] = 1

        # Case 4: the limits are the ones given, without the padding a curve
        # gets, and free to grow. The data is not needed, since the caller
        # already knows its own extent
        if case == self.strictrange:
            if self.state.setay[nax] == self.adaptrange:
                ymin = min(ylim[0], ax.get_ylim()[0])
                ymax = max(ylim[1], ax.get_ylim()[1])
                ax.set_ylim(ymin, ymax)
            elif self.state.setay[nax] == self.changerange:
                ax.set_ylim(ylim[0], ylim[1])
                self.state.setay[nax] = self.adaptrange

        # End of the function

    def find_ylim(
        self,
        ax: Axes,
        nax: int,
        x: np.ndarray,
        y: np.ndarray,
    ) -> tuple[float, float]:
        """Return the padded y-limits of the data inside the x-limits.

        The x-limits are already set when this is called, so they are the
        window the user sees: a point outside it, past an x-range given by
        hand, does not stretch the y-axis. If no point is inside, all of them
        are taken, so the axis still shows the data rather than nothing.

        Parameters
        ----------
        - ax (not optional): Axes
            The axis whose x-limits are the window.
        - nax (not optional): int
            The index of the axis, for the scale of its y-axis.
        - x (not optional): np.ndarray
            The x data.
        - y (not optional): np.ndarray
            The y data, the same shape as x or one column per line.

        Returns
        -------
        - tuple[float, float]
            The lower and upper y-limits, padded.

        Examples
        --------
        - Example #1: the y-limits of a curve on the first axis

            >>> self.find_ylim(ax, 0, x, y)

        """
        xmin, xmax = sorted(ax.get_xlim())
        inside = np.logical_and(x >= xmin, x <= xmax)
        smally = y[inside] if inside.any() else y
        return self.range_offset(
            smally.min(),
            smally.max(),
            self.state.yscale[nax],
        )

    def range_offset(
        self,
        ymin: float,
        ymax: float,
        scale: str,
        margin: float = 0.1,
    ) -> tuple[float, float]:
        """Return the offsetted data range for the y-axis limits.

        Parameters
        ----------
        - margin (optional): float
            The margin of the data range.
        - scale (not optional): str
            The scale of the y-axis.
        - ymin (not optional): float
            The lower limit of the y-axis.
        - ymax (not optional): float
            The upper limit of the y-axis.

        Returns
        -------
        - tuple[float, float]

        Examples
        --------
        - Example #1: Set the y-axis limits of the selected set of axes

            >>> ymin, ymax = _range_offset(ymin, ymax, scale)

        """
        # Find the data range. Constant data has no range of its own, so the
        # padding is taken from the value itself; absolute, or a negative
        # constant would pad downwards and turn the axis upside down, and
        # falling back to 1.0 keeps a constant zero from giving no range at
        # all.
        data_range = ymax - ymin
        if data_range == 0:
            data_range = abs(ymax) * 0.1 or 1.0

        # Find the padding (with non-inear scale adjustments)
        padding = margin * data_range
        range_maxval = 10
        if np.log10(np.abs(data_range)) > range_maxval and scale != "linear":
            padding *= 2 * np.abs(np.log10(np.abs(data_range)))

        # Set the limits (additional check if the scale is logarithmic)
        if scale in ["linear", "symlog", "asinh"]:
            return (ymin - padding, ymax + padding)
        if scale == "log":
            # Folded to absolute values together: reassigning one before the
            # other lost the original of the first
            if ymin <= 0 or ymax <= 0:
                ymin, ymax = sorted((abs(ymin), abs(ymax)))
                PPWarn.warn(
                    "Negative range for logarithmic scale!",
                    PyPLUTOBehaviorWarning,
                )

            # A log axis cannot show 0: with no positive value to start from,
            # the range starts a decade below its top, or at 0.1 if all is 0
            if ymin == 0:
                ymin = ymax / 10 if ymax > 0 else 0.1
                ymax = max(ymax, 10 * ymin)
            return (max(ymin - padding, ymin * 0.5), ymax + padding)

        return (ymin, ymax)
