import warnings

import numpy as np
from matplotlib.axes import Axes
from numpy.typing import NDArray

from .delegator import delegator
from .imagestate import ImageState


@delegator("state")
class RangeManager:

    def __init__(self, state: ImageState):
        """Initialize the RangeManager with the given state."""
        self.state = state

    def set_xrange(
        self, ax: Axes, nax: int, xlim: list[float], case: int
    ) -> None:
        """Sets the lower and upper limits of the x-axis of a set of
        axes (if not stated otherwise later).

        Returns
        -------
        - None

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

        Notes
        -----
        - The chance to set only one limit dinamically will be implemented
        in future code releases

        ----

        Examples
        --------
        - Example #1: Set the x-axis limits of the selected set of axes

            >>> _set_xrange(ax, nax, xlim, case)

        """
        # Case 0: the x-axis limits are set automatically (no previous limit)
        if case == 0:
            ax.set_xlim(xlim[0], xlim[1])

            # Case switched to 2 (previous limits are present now)
            self.state.setax[nax] = 2

        # Case 1: limits are already set and they should not be changed
        #         (aka do nothing)

        # Case 2: the x-axis limit are changed automatically
        #         (previous limit present)
        if case == 2:
            xmin = min(xlim[0], ax.get_xlim()[0])
            xmax = max(xlim[1], ax.get_xlim()[1])
            ax.set_xlim(xmin, xmax)

        # Case 3: x-axis limits are set manually
        if case == 3:
            ax.set_xlim(xlim[0], xlim[1])

            # Case switched to 1 (no change unless stated explicitly otherwise)
            self.state.setax[nax] = 1

        # End of the function

    def set_yrange(
        self,
        ax: Axes,
        nax: int,
        ylim: list[float],
        case: int,
        x: NDArray[np.float64] | None = None,
        y: NDArray[np.float64] | None = None,
    ) -> None:
        """Sets the lower and upper limits of the y-axis of a set of
        axes (if not stated otherwise later). Unlike the x-axis, the
        y-axis limits are recovered depending on both the x-data and the
        y-data.

        Returns
        -------
        - None

        Parameters
        ----------
        - ax (not optional): ax
            The selected set of axes.
        - case (not optional): int
            The case in exam (if range is fixed or variable).
        - nax (not optional): int
            The number of the selected set of axes.
        - x: np.ndarray
            The x-array (to limit the y-range automatically).
        - y: np.ndarray
            The y-array (to limit the y-range automatically).
        - ylim (not optional): list[float]
            The limits of the y-axis.

        Notes
        -----
        - The chance to set only one limit dinamically will be implemented
        in future code releases

        ----

        Examples
        --------
        - Example #1: Set the y-axis limits of the selected set of axes

            >>> _set_yrange(ax, nax, ylim, case)

        """
        # Case 0: the y-axis limits are set automatically (no previous limit)
        if case == 0:
            if x is None or y is None:
                raise ValueError("x and y arrays must be provided if case is 0")

            # Find the limits of the x-axis
            yrange = np.where(np.logical_and(x >= x.min(), x <= x.max()))
            smally = y[yrange]

            # Extend slightly the range
            ymin, ymax = self.range_offset(
                smally.min(), smally.max(), self.state.yscale[nax]
            )
            # ymin   = smally.min() - 0.02*np.abs(smally.min())
            # ymax   = smally.max() + 0.02*np.abs(smally.max())
            ax.set_ylim(ymin, ymax)

            # Switch to case 2 (previous limits are present now)
            self.state.setay[nax] = 2

        # Case 1: limits are already set and they should not be changed
        # (aka do nothing)

        # Case 2: the y-axis limit are changed automatically
        # (previous limit present)
        if case == 2:

            if x is None or y is None:
                raise ValueError("x and y arrays must be provided if case is 2")

            # Find the limits of the x-axis
            yrange = np.where(np.logical_and(x >= x.min(), x <= x.max()))
            smally = y[yrange]

            # Extend slightly the range (not perfect method)
            ymin, ymax = self.range_offset(
                smally.min(), smally.max(), self.state.yscale[nax]
            )
            # ymin   = smally.min() - 0.02*np.abs(smally.min())
            # ymax   = smally.max() + 0.02*np.abs(smally.max())

            # Check if the limits should be changed
            ymin = np.minimum(ymin, ax.get_ylim()[0])
            ymax = np.maximum(ymax, ax.get_ylim()[1])
            ax.set_ylim(ymin, ymax)

        # Case 3: y-axis limits must be set manually
        if case == 3:
            ax.set_ylim(ylim[0], ylim[1])

            # Case switched to 1 (no change unless stated explicitly otherwise)
            self.state.setay[nax] = 1

        # End of the function

    def range_offset(
        self, ymin: float, ymax: float, scale: str, margin: float = 0.1
    ) -> tuple[float, float]:
        """Returns the offsetted data range for the y-axis limits.

        Returns
        -------
        - ymin: float
            The lower limit of the y-axis.
        - ymax: float
            The upper limit of the y-axis.

        Parameters
        ----------
        - ymin (not optional): float
            The lower limit of the y-axis.
        - ymax (not optional): float
            The upper limit of the y-axis.
        - scale (not optional): str
            The scale of the y-axis.
        - margin (optional): float
            The margin of the data range.

        Notes
        -----
        - The chance to set only one limit dinamically will be implemented
        in future code releases

        ----

        Examples
        --------
        - Example #1: Set the y-axis limits of the selected set of axes

            >>> ymin, ymax = _range_offset(ymin, ymax, scale)

        """
        # Find the data range
        data_range = ymax - ymin
        if data_range == 0:
            data_range = ymax * 0.1

        # Find the padding (with non-inear scale adjustments)
        padding = margin * data_range
        if np.log10(np.abs(data_range)) > 10 and scale != "linear":
            padding *= 2 * np.abs(np.log10(np.abs(data_range)))
            print(padding)

        # Set the limits (additional check if the scale is logarithmic)
        if scale in ["linear", "symlog", "asinh"]:
            return (ymin - padding, ymax + padding)
        if scale == "log":
            if ymin <= 0 or ymax <= 0:
                ymin = min(np.abs(ymin), np.abs(ymax))
                ymax = max(np.abs(ymin), np.abs(ymax))
                warnings.warn(
                    "Negative range for logarithmic scale!", UserWarning
                )
            return (max(ymin - padding, ymin * 0.5), ymax + padding)

        return (ymin, ymax)
