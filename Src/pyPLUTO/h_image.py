from matplotlib.axes import Axes
from numpy.typing import NDArray
import numpy as np
import warnings
from typing import Any


def _add_ax(self, ax: Axes, i: int) -> None:
    """
    Adds the axes properties to the class info variables.
    The corresponding axis is appended to the list of axes.

    Returns
    -------

    - None

    Parameters
    ----------

    - ax (not optional): ax
        The axis to be added.
    - i (not optional): int
        The index of the axis in the list.

    Notes
    -----

    - None

    ----

    Examples
    ========

    - Example #1: Add the axis to the class info variables

        >>> _add_ax(ax, i)

    """

    # Append the axis to the list of axes
    self.ax.append(ax)

    # Append the axis properties to the class info variables
    self.nline.append(0)
    self.ntext.append(None)
    self.setax.append(0)
    self.setay.append(0)
    self.xscale.append("linear")
    self.yscale.append("linear")
    self.legpos.append(None)
    self.legpar.append([self.fontsize, 1, 2, 0.8, 0.8])
    self.vlims.append([])
    self.tickspar.append(0)
    self.shade.append("auto")

    # Position the axis index in the middle of the axis
    self.ax[i].annotate(str(i), (0.47, 0.47), xycoords="axes fraction")

    # End of the function
    return None


def _hide_text(self, nax: int, txts: str | None) -> None:
    """
    Hides the text placed when an axis is created (the axis index).

    Returns
    -------

    - None

    Parameters
    ----------

    - nax (not optional): int
        The number of the selected set of axes.
    - txts (not optional): str | None
        The text of the selected set of axes.

    Notes
    -----

    - None

    ----

    Examples
    ========

    - Example #1: Hide the text of the selected set of axes

        >>> _hide_text(nax, txts)

    """

    # Check if the text has already been removed
    if self.ntext[nax] is None:
        [txt.set_visible(False) for txt in txts]

        # Set the text as removed
        self.ntext[nax] = 1

    # End of the function
    return None


def _set_xrange(self, ax: Axes, nax: int, xlim: list[float], case: int) -> None:
    """
    Sets the lower and upper limits of the x-axis of a set of axes (if
    not stated otherwise later).

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
    ========

    - Example #1: Set the x-axis limits of the selected set of axes

        >>> _set_xrange(ax, nax, xlim, case)

    """

    # Case 0: the x-axis limits are set automatically (no previous limit)
    if case == 0:
        ax.set_xlim(xlim[0], xlim[1])

        # Case switched to 2 (previous limits are present now)
        self.setax[nax] = 2

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
        self.setax[nax] = 1

    # End of the function
    return None


def _set_yrange(
    self,
    ax: Axes,
    nax: int,
    ylim: list[float],
    case: int,
    x: NDArray | None = None,
    y: NDArray | None = None,
) -> None:
    """
    Sets the lower and upper limits of the y-axis of a set of axes (if
    not stated otherwise later).
    Unlike the x-axis, the y-axis limits are recovered depending on both
    the x-data and the y-data.

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
    ========

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
        ymin, ymax = self._range_offset(smally.min(), smally.max(), self.yscale[nax])
        # ymin   = smally.min() - 0.02*np.abs(smally.min())
        # ymax   = smally.max() + 0.02*np.abs(smally.max())
        ax.set_ylim(ymin, ymax)

        # Switch to case 2 (previous limits are present now)
        self.setay[nax] = 2

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
        ymin, ymax = self._range_offset(smally.min(), smally.max(), self.yscale[nax])
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
        self.setay[nax] = 1

    # End of the function
    return None


def _range_offset(
    self, ymin: float, ymax: float, scale: str, margin: float = 0.1
) -> tuple[float, float]:
    """
    Returns the offsetted data range for the y-axis limits.

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
    ========

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
    elif scale == "log":
        if ymin <= 0 or ymax <= 0:
            ymin = min(np.abs(ymin), np.abs(ymax))
            ymax = max(np.abs(ymin), np.abs(ymax))
            warnings.warn("Negative range for logarithmic scale!", UserWarning)
        return (max(ymin - padding, ymin * 0.5), ymax + padding)
    else:
        return (ymin, ymax)


def _assign_ax(self, ax: Axes | list[Axes] | None, **kwargs: Any) -> tuple[Axes, int]:
    """
    Sets the axes of the figure where the plot/feature should go.
    If no axis is present, an axis is created. If the axis is present
    but no axis is seletced, the last axis is selected.

    Returns
    -------

    - ax: ax | list[ax] | int | None
        The selected set of axes.
    - nax: int
        The number of the selected set of axes.

    Parameters
    ----------

    - ax (not optional): ax | int | list[ax] | None
        The selected set of axes.
    - **kwargs: Any
        The keyword arguments to be passed to the create_axes function
        (not written here since is not public method).

    Notes
    -----

    - None

    ----

    Examples
    ========

    - Example #1: Set the axes of the figure

        >>> _assign_ax(ax, **kwargs)

    - Example #2: Set the axes of the figure (no axis selected)

        >>> _assign_ax(None, **kwargs)

    - Example #3: Set the axes of the figure (axis is a list)

        >>> _assign_ax([ax], **kwargs)

    """

    # Check if the axis is None and no axis is present (and create one)
    if ax is None and len(self.ax) == 0:
        ax = self.create_axes(ncol=1, nrow=1, check=False, **kwargs)

    # Check if the axis is None and an axis is present (and select the last one,
    # the current axis if it belongs to the one saved in the figure or the last
    # one saved
    elif ax is None and len(self.ax) > 0:
        ax = self.fig.gca() if self.fig.gca() in self.ax else self.ax[-1]

    # Check if the axis is a list and select the first element
    elif isinstance(ax, list):
        ax = ax[0]

    # Check if the axis is an int, and select the corresponding axis from
    # the list of axes
    elif isinstance(ax, int):
        ax = self.ax[ax]

    # If none of the previous cases is satisfied assert that ax is an axis
    elif not isinstance(ax, Axes):
        raise ValueError("The provided axis is not valid.")

    # Get the figure associated to the axes
    fig = ax.get_figure()

    # Check if the figure is the same as the one in the class
    if fig != self.fig:
        text = "The provided axis does not belong to the expected figure."
        raise ValueError(text)

    # Find the number of the axes and return it
    nax = self.ax.index(ax)

    # Return the axis and its index
    return ax, nax
