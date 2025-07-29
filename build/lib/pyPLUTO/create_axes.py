import copy
import warnings
from itertools import islice
from typing import Any

import matplotlib.pyplot as plt
import numpy as np
from matplotlib.axes import Axes

from .delegator import delegator
from .imagestate import ImageState
from .inspector import track_kwargs

defaults = {
    "left": 0.125,
    "right": 0.9,
    "top": 0.9,
    "bottom": 0.1,
    "hspace": [],
    "wspace": [],
    "hratio": [1.0],
    "wratio": [1.0],
}


@delegator("state")
class CreateAxesManager:
    """Class to manage the creation of axes in the image.

    This class provides methods to create axes in the image class. It allows
    for customization of the axes' position, spacing, projection, and other
    properties."""

    exposed_methods = ("create_axes",)

    def __init__(self, state: ImageState) -> None:
        """Initialization of the CreateAxesManager class."""
        self.state = state

    @track_kwargs(extra_keys=set(defaults.keys()))
    def create_axes(
        self, ncol: int = 1, nrow: int = 1, check: bool = True, **kwargs: Any
    ) -> Axes | list[Axes]:
        """Creation of a set of axes using add_subplot from the matplotlib
        library.

        If additional parameters (like the figure limits or the spacing)
        are given, the plots are located using set_position.
        The spacing and the ratio between the plots can be given by hand.
        In case only few custom options are given, the code computes the rest
        (but gives a small warning); in case no custom option is given, the axes
        are located through the standard methods of matplotlib.

        If more axes are created in the figure, the list of all axes is
        returned, otherwise the single axis is returned.

        Returns
        -------
        - The list of axes (if more axes are in the figure) or the axis
        (if only one axis is present)

        Parameters
        ----------
        - bottom: float, default 0.1
            The space from the bottom border to the last row of plots.
        - figsize: [float, float], default [6*sqrt(ncol),5*sqrt(nrow)]
            Sets the figure size. The default value is computed from the number
            of rows and columns.
        - fontsize: float, default 17.0
            Sets the fontsize for all the axes.
        - hratio: [float], default [1.0]
            Ratio between the rows of the plot. The default is that every plot
            row has the same height.
        - hspace: [float], default []
            The space between plot rows (in figure units). If not enough or
            too many spaces are considered, the program will remove the excess
            and fill the lacks with [0.1].
        - left: float, default 0.125
            The space from the left border to the leftmost column of plots.
        - ncol: int, default 1
            The number of columns of subplots.
        - nrow: int, default 1
            The number of rows of subplots.
        - proj: str, default None
            Custom projection for the plot (e.g. 3D). Recommended only if
            needed.
            WARNING: pyPLUTO does not support 3D plotting for now, only 3D axes.
            The 3D plot feature will be available in future releases.
        - right: float, default 0.9
            The space from the right border to the rightmost column of plots.
        - sharex: bool | str | Matplotlib axis, default False
            Enables/disables the sharing of the x-axis between the subplots.
        - sharey: bool | str | Matplotlib axis, default False
            Enables/disables the sharing of the y-axis between the subplots.
        - suptitle: str, default None
            Creates a figure title over all the subplots.
        - tight: bool, default True
            Enables/disables tight layout options for the figure. In case of a
            highly customized plot (e.g. ratios or space between rows and
            columns) the option is set by default to False since that option
            would not be available for standard matplotlib functions.
        - top: float, default 0.9
            The space from the top border to the first row of plots.
        - wratio: [float], default [1.0]
            Ratio between the columns of the plot. The default is that every
            plot column has the same width.
        - wspace: [float], default []
            The space between plot columns (in figure units). If not enough or
            too many spaces are considered, the program will remove the excess
            and fill the lacks with [0.1].

        ----

        Examples
        --------
        - Example #1: create a simple grid of 2 columns and 2 rows on a new
          figure

            >>> import pyPLUTO as pp
            >>> I = pp.Image()
            >>> ax = I.create_axes(ncol=2, nrow=2)

        - Example #2: create a grid of 2 columns with the first one having half
          the width of the second one

            >>> import pyPLUTO as pp
            >>> I = pp.Image()
            >>> ax = I.create_axes(ncol=2, wratio=[0.5, 1])

        - Example #3: create a grid of 2 rows with a lot of blank space between
          them

            >>> import pyPLUTO as pp
            >>> I = pp.Image()
            >>> ax = I.create_axes(nrow=2, hspace=[0.5])

        - Example #4: create a 2x2 grid with a fifth image on the right side

            >>> import pyPLUTO as pp
            >>> I = pp.Image()
            >>> ax = I.create_axes(ncol=2, nrow=2, right=0.7)
            >>> ax = I.create_axes(left=0.75)

        """
        kwargs.pop("check", check)

        # Change fontsize if requested
        if "fontsize" in kwargs:
            plt.rcParams.update({"font.size": kwargs["fontsize"]})

        custom_plot = bool(defaults.keys() & kwargs.keys())

        if custom_plot:
            kwargs["tight"] = False
            filtered_kwargs = {
                key: kwargs.get(key, value) for key, value in defaults.items()
            }
            wplot, hplot = self._set_custom_axes(filtered_kwargs, nrow, ncol)
        else:
            wplot, hplot = None, None

        # Set figure size
        if self.state.fig is None:
            raise ValueError(
                "You need to create a figure before creating axes."
            )

        if figsize := kwargs.get("figsize"):
            self.state.fig.set_size_inches(*figsize)
            self.state.figsize = figsize
        elif not (custom_plot or self.state.set_size):
            self.state.fig.set_size_inches(6 * np.sqrt(ncol), 5 * np.sqrt(nrow))

        # Set the projection if requested
        proj = kwargs.get("proj")

        # Set sharex and sharey
        sharex = kwargs.get("sharex")
        sharey = kwargs.get("sharey")

        for i in range(ncol * nrow):
            # Interpret True as: share with the first axis
            if sharex is True:
                sharex_ref = self.state.ax[0] if i > 0 else None
            elif isinstance(sharex, int):
                sharex_ref = self.state.ax[sharex]
            else:
                sharex_ref = sharex  # None or an Axes reference

            # Same for sharey
            if sharey is True:
                sharey_ref = self.state.ax[0] if i > 0 else None
            elif isinstance(sharey, int):
                sharey_ref = self.state.ax[sharey]
            else:
                sharey_ref = sharey

            self.add_ax(
                axis := self.state.fig.add_subplot(
                    nrow + self.state.nrow0,
                    ncol + self.state.ncol0,
                    i + 1,
                    projection=proj,
                    sharex=sharex_ref,
                    sharey=sharey_ref,
                ),
                len(self.state.ax),
            )
            self.state.ax.append(axis)

            # Compute row and column
            row = int(i / ncol)
            col = int(i % ncol)

            # Set position if custom axes
            if wplot is not None and hplot is not None:
                self.state.ax[-1].set_position(
                    pos=(
                        wplot[col][0],
                        hplot[row][0],
                        wplot[col][1],
                        hplot[row][1],
                    )
                )

        # Updates rows and columns
        self.state.nrow0 = self.state.nrow0 + nrow
        self.state.ncol0 = self.state.ncol0 + ncol

        # Set figure title if requested
        if "suptitle" in kwargs:
            self.state.fig.suptitle(kwargs["suptitle"])

        # Tight layout (depending on the subplot creation)
        self.state.tight = kwargs.get("tight", self.state.tight)
        self.state.fig.set_layout_engine(
            None if not self.state.tight else "tight"
        )

        ret_ax = self.state.ax[0] if len(self.state.ax) == 1 else self.state.ax

        return ret_ax

    def _set_custom_axes(
        self, custom: dict[str, Any], nrow: int, ncol: int
    ) -> tuple[list[list[float]], list[list[float]]]:
        """Sets the axes position and spacing according to the custom
        parameters.

        Returns
        -------
        - wplot: list[list[float]]
            List of the left and right position of the axes.
        - hplot: list[list[float]]
            List of the top and bottom position of the axes.

        Parameters
        ----------
        - custom: dict[str, Any]
            Dictionary with the custom parameters for the axes.
        - nrow: int
            Number of rows in the axes.
        - ncol: int
            Number of columns in the axes.

        """
        hspace, hratio = self._check_rowcol(
            custom["hratio"], custom["hspace"], nrow, "rows"
        )
        wspace, wratio = self._check_rowcol(
            custom["wratio"], custom["wspace"], ncol, "cols"
        )

        hsize = custom["top"] - custom["bottom"] - sum(hspace)
        wsize = custom["right"] - custom["left"] - sum(wspace)
        htot, wtot = sum(hratio), sum(wratio)
        ll, tt = custom["left"], custom["top"]
        hplot, wplot = [], []

        # Computes left, right of every ax
        for i in islice(range(ncol), ncol - 1):
            rr = wsize * wratio[i] / wtot
            wplot.append([ll, rr])
            ll += rr + wspace[i]

        # Computes top, bottom of every ax
        for i in islice(range(nrow), nrow - 1):
            bb = tt - hsize * hratio[i] / htot
            hplot.append([bb, tt - bb])
            tt = bb - hspace[i]

        # Append the last items without extra space
        rr = wsize * wratio[ncol - 1] / wtot
        wplot.append([ll, rr])

        bb = tt - hsize * hratio[nrow - 1] / htot
        hplot.append([bb, tt - bb])
        return wplot, hplot

    def _check_rowcol(
        self,
        ratio: list[float],
        space: float | list[float | int],
        length: int,
        func: str,
    ) -> tuple[list[float | int], list[float | int]]:
        """Checks the width and spacing of the plots on a single row or
        column.

        Returns
        -------
        - space: list[float]
            the space between the rows or columns
        - ratio: list[float]
            the ratio of the rows or columns

        Parameters
        ----------
        - ratio: list[float]
            the ratio of the rows or columns
        - space: list[float]
            the space between the rows or columns
        - length: int
            the number of rows or columns in the single row or column
        - func: str
            the function to check (rows or cols)

        ----

        Examples
        --------
        - Example #1: ratio and space are given correctly (rows)

            >>> _check_rowcol([1, 2, 3], [0.1, 0.2], 3, "rows")

        - Example #2: ratio and space are given incorrectly (rows) (warning)

            >>> _check_rowcol([], 0.1, 3, "rows")

        - Example #3: ratio and space are given correctly (cols)

            >>> _check_rowcol([1, 2, 3], [0.1, 0.2], 3, "cols")

        """
        rat = {"rows": "hratio", "cols": "wratio"}
        spc = {"rows": "hspace", "cols": "wspace"}

        # Check if space is a list
        newspace = space if isinstance(space, list) else [space]
        space = space if isinstance(space, list) else newspace * (length - 1)

        # Fill the lists with the default values
        ratio = ratio + [1.0] * (length - len(ratio))
        space = space + [0.1] * (length - len(space) - 1)

        # Check if the lists have the correct length
        if len(ratio) != length:
            warn = f"WARNING! {rat[func]} has wrong length!"
            warnings.warn(warn, UserWarning)
        if len(space) + 1 != length:
            warn = f"WARNING! {spc[func]} has wrong length!"
            warnings.warn(warn, UserWarning)

        # End of the function. Return the lists
        return space[: length - 1], ratio[:length]

    def add_ax(self, ax: Axes, i: int) -> None:
        """Adds the axhes properties to the class info variables. The
        corresponding axis is appended to the list of axes.

        Returns
        -------
        - None

        Parameters
        ----------
        - ax (not optional): ax
            The axis to be added.
        - i (not optional): int
            The index of the axis in the list.

        ----

        Examples
        --------
        - Example #1: Add the axis to the class info variables

            >>> _add_ax(ax, i)

        """
        ax_pars = {
            #      "ax": ax,
            "legpos": None,
            "legpar": [self.state.fontsize, 1, 2, 0.8, 0.8],
            "nline": 0,
            "ntext": None,
            "setax": 0,
            "setay": 0,
            "shade": "auto",
            "tickspar": 0,
            "xscale": "linear",
            "yscale": "linear",
            "vlims": [],
        }

        # Append the axis to the list of axes
        for attr, default in ax_pars.items():
            getattr(self, attr).append(copy.copy(default))

        # Position the axis index in the middle of the axis
        ax.annotate(str(i), (0.47, 0.47), xycoords="axes fraction")
