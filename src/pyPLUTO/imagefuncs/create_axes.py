"""Module to create axes in the image class."""

from __future__ import annotations

import copy
import warnings
from itertools import islice
from typing import Any, Unpack

import matplotlib.pyplot as plt
import numpy as np
from matplotlib.axes import Axes

from pyPLUTO.imagekwargs import CreateAxesKwargs
from pyPLUTO.imagemixin import ImageMixin
from pyPLUTO.imagestate import ImageState
from pyPLUTO.utils.inspector import track_kwargs

defaults: dict[str, Any] = {
    "left": 0.125,
    "right": 0.9,
    "top": 0.9,
    "bottom": 0.1,
    "hspace": [],
    "wspace": [],
    "hratio": [1.0],
    "wratio": [1.0],
}


class CreateAxesManager(ImageMixin):
    """Class to manage the creation of axes in the image.

    This class provides methods to create axes in the image class. It allows
    for customization of the axes' position, spacing, projection, and other
    properties.
    """

    def __init__(self, state: ImageState) -> None:
        """Initialize the CreateAxesManager class."""
        self.state: ImageState = state

    @track_kwargs(extra_keys=set(defaults.keys()))
    def create_axes(
        self,
        _check: bool = True,
        **kwargs: Unpack[CreateAxesKwargs],
    ) -> Axes | list[Axes]:
        """Creation of a set of axes using add_subplot from matplotlib.

        If additional parameters (like the figure limits or the spacing)
        are given, the plots are located using set_position.
        The spacing and the ratio between the plots can be given by hand.
        In case only few custom options are given, the code computes the rest
        (but gives a small warning); in case no custom option is given, the axes
        are located through the standard methods of matplotlib.

        If more axes are created in the figure, the list of all axes is
        returned, otherwise the single axis is returned.

        Parameters
        ----------
        - bottom: float, default varies
            The bottom limit of the axis / axes set. For the figure layout it
            is the space from the bottom border to the plot (default 0.1); for
            an inset zoom it is the bottom position of the inset (default 0.6 +
            height).
        - figsize: list[float], default varies
            Sets the figure size. The default is [6*sqrt(ncol), 5*sqrt(nrow)],
            computed from the number of rows and columns (or [8,5] for a single
            plot).
        - fontsize: float, default 17.0
            Sets the fontsize for all the axis components.
        - hratio: [float], default [1.0]
            Ratio between the rows of the plot. The default is that every plot
            row has the same height.
        - hspace: [float], default []
            The space between plot rows (in figure units). If not enough or too
            many spaces are considered, the program will remove the excess and
            fill the lacks with [0.1].
        - left: float, default varies
            The left limit of the axis / axes set. For the figure layout it is
            the space from the left border to the plot (default 0.125); for an
            inset zoom it is the left position of the inset (default 0.6).
        - ncol: int, default 1
            The number of columns of subplots.
        - nrow: int, default 1
            The number of rows of subplots.
        - proj: str, default None
            Custom projection for the plot (e.g. 3D). Recommended only if
            needed. WARNING: pyPLUTO does not support 3D plotting for now, only
            3D axes. The 3D plot feature will be available in future releases.
        - right: float, default varies
            The right limit of the axis / axes set. For the figure layout it is
            the space from the right border to the plot (default 0.9); for an
            inset zoom it is the right position of the inset (default left +
            0.15).
        - sharexaxes: bool | int | 'all' | 'row' | 'col' | Axes, default False
            Shares the x-axis between the subplots: True or 'all' with the
            first of them, 'row' and 'col' within each row or column, an
            index with that axis of the image, an Axes with that axis.
        - shareyaxes: bool | int | 'all' | 'row' | 'col' | Axes, default False
            Shares the y-axis between the subplots, as sharexaxes does.
        - suptitle: str, default None
            Creates a figure title over all the subplots.
        - tight: bool, default True
            Enables/disables tight layout options for the figure. In case of a
            highly customized plot (e.g. ratios or space between rows and
            columns) the option is set by default to False since that option
            would not be available for standard matplotlib functions.
        - top: float, default varies
            The top limit of the axis / axes set. For the figure layout it is
            the space from the top border to the plot (default 0.9); for an
            inset zoom it is the top position of the inset (default bottom +
            height).
        - wratio: [float], default [1.0]
            Ratio between the columns of the plot. The default is that every
            plot column has the same width.
        - wspace: [float], default []
            The space between plot columns (in figure units). If not enough or
            too many spaces are considered, the program will remove the excess
            and fill the lacks with [0.1].

        Returns
        -------
        - Axes | list[Axes]

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
        # Change fontsize if requested, in matplotlib and in the state, which
        # the legend, the text box and the labels read theirs from
        if "fontsize" in kwargs:
            plt.rcParams.update({"font.size": kwargs["fontsize"]})
            self.state.fontsize = kwargs["fontsize"]

        nrow = kwargs.get("nrow", 1)
        ncol = kwargs.get("ncol", 1)

        custom_plot = bool(defaults.keys() & kwargs.keys())

        # A layout placed by hand cannot also be a tight one: the layout wins
        if custom_plot:
            filtered_kwargs = {
                key: kwargs.get(key, value) for key, value in defaults.items()
            }
            wplot, hplot = self.set_custom_axes(
                filtered_kwargs, nrow, ncol, kwargs.get("tight")
            )
            kwargs["tight"] = False
        else:
            wplot, hplot = None, None

        # Set figure size
        if self.state.fig is None:
            raise ValueError(
                "You need to create a figure before creating axes.",
            )

        # A size given is marked as chosen, so later calls keep it rather
        # than computing one from their rows and columns
        if figsize := kwargs.get("figsize"):
            self.state.fig.set_size_inches(figsize[0], figsize[1])
            self.state.figsize = figsize
            self.state.set_size = True
        elif not (custom_plot or self.state.set_size):
            self.state.fig.set_size_inches(6 * np.sqrt(ncol), 5 * np.sqrt(nrow))

        # Set the projection if requested
        proj = kwargs.get("proj")

        new: list[Axes] = []
        for i in range(ncol * nrow):
            self.add_ax(
                axis := self.state.fig.add_subplot(
                    nrow + self.state.nrow0,
                    ncol + self.state.ncol0,
                    i + 1,
                    projection=proj,
                ),
                len(self.state.ax),
            )
            self.state.ax.append(axis)
            new.append(axis)

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
                    ),
                )

        # The axes share once they all exist, so an index, a row or a column
        # can point at any of them, made in this call or before it
        sharex = kwargs.get("sharexaxes")
        sharey = kwargs.get("shareyaxes")
        for i, axis in enumerate(new):
            for share, join in ((sharex, axis.sharex), (sharey, axis.sharey)):
                target = self.find_share_target(i, share, new, ncol)
                if target is not None and target is not axis:
                    join(target)

        # Updates rows and columns
        self.state.nrow0 = self.state.nrow0 + nrow
        self.state.ncol0 = self.state.ncol0 + ncol

        # Set figure title if requested
        if (suptitle := kwargs.get("suptitle")) is not None:
            self.state.fig.suptitle(suptitle)

        # Tight layout (depending on the subplot creation)
        self.state.tight = kwargs.get("tight", self.state.tight)
        self.state.fig.set_layout_engine(
            None if not self.state.tight else "tight",
        )

        ret_ax = self.state.ax[0] if len(self.state.ax) == 1 else self.state.ax

        # if not isinstance(ret_ax, list | Axes):
        #    raise TypeError("The returned axis is neither a list nor an Axes.")

        return ret_ax

    def set_custom_axes(
        self,
        custom: dict[str, Any],
        nrow: int,
        ncol: int,
        tight: bool | None = None,
    ) -> tuple[list[list[float]], list[list[float]]]:
        """Compute the position of every axis of a layout placed by hand.

        The borders, spaces and ratios given -- or their defaults -- fix the
        left side and width of every column and the bottom and height of
        every row, in figure units. Such a layout cannot also be tight,
        since a tight layout moves the axes: create_axes switches it off,
        and a tight asked for with the layout is refused with a warning.

        Parameters
        ----------
        - custom (not optional): dict[str, Any]
            The layout keywords with their defaults: left, right, top,
            bottom, hspace, wspace, hratio, wratio.
        - ncol (not optional): int
            The number of columns.
        - nrow (not optional): int
            The number of rows.
        - tight: bool | None, default None
            The tight keyword given with the layout, if any.

        Returns
        -------
        - tuple[list[list[float]], list[list[float]]]
            The [left, width] of every column and [bottom, height] of every
            row.

        Examples
        --------
        - Example #1: two columns with a wider left border

            >>> self.set_custom_axes(dict(defaults, left=0.2), 1, 2)

        """
        if tight is True:
            warn = "A custom layout cannot be tight: tight is set to False."
            warnings.warn(warn, UserWarning, stacklevel=3)

        hspace, hratio = self._check_rowcol(
            custom["hratio"],
            custom["hspace"],
            nrow,
            "rows",
        )
        wspace, wratio = self._check_rowcol(
            custom["wratio"],
            custom["wspace"],
            ncol,
            "cols",
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
        """Check the width and spacing of the plots on a single row or column.

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

        Returns
        -------
        - tuple[list[float], list[float]]

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
            warnings.warn(warn, UserWarning, stacklevel=2)
        if len(space) + 1 != length:
            warn = f"WARNING! {spc[func]} has wrong length!"
            warnings.warn(warn, UserWarning, stacklevel=2)

        # End of the function. Return the lists
        return space[: length - 1], ratio[:length]

    def add_ax(self, ax: Axes, i: int) -> None:
        """Add the axhes properties to the class info variables.

        The corresponding axis is appended to the list of axes.

        Parameters
        ----------
        - ax (not optional): ax
            The axis to be added.
        - i (not optional): int
            The index of the axis in the list.

        Returns
        -------
        - None

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
            "setxticks": 0,
            "setyticks": 0,
            "shade": "auto",
            "tickspar": 0,
            "xscale": "linear",
            "xtickspin": None,
            "yscale": "linear",
            "ytickspin": None,
            "vlims": [],
        }

        # Append the axis to the list of axes
        for attr, default in ax_pars.items():
            getattr(self.state, attr).append(copy.copy(default))

        # Position the axis index in the middle of the axis
        ax.annotate(str(i), (0.47, 0.47), xycoords="axes fraction")

    def find_share_target(
        self,
        i: int,
        share: bool | int | str | Axes | None,
        new: list[Axes],
        ncol: int,
    ) -> Axes | None:
        """Find the axis a new axis shares its x- or y-axis with.

        The axes of one create_axes call are laid out row by row, so the
        i-th of them sits in row i // ncol and column i % ncol. True or
        'all' share with the first of them, 'row' and 'col' with the first
        of the same row or column, as in matplotlib's subplots; an index
        points at any axis of the image, made in this call or before it,
        and an Axes is itself the target. False and None share nothing, and
        are tested first: False is an int, and would be read as the index 0.

        Parameters
        ----------
        - i (not optional): int
            The position of the axis among the new ones.
        - ncol (not optional): int
            The number of columns of the new axes.
        - new (not optional): list[Axes]
            The axes this create_axes call made, in order.
        - share (not optional): bool | int | str | Axes | None
            The sharing asked for, sharexaxes or shareyaxes.

        Returns
        -------
        - Axes | None
            The axis to share with, or None to share nothing.

        Examples
        --------
        - Example #1: the third axis of a two-column grid, sharing by column

            >>> self.find_share_target(2, "col", new, 2)  # new[0]

        """
        if share is None or share is False:
            return None
        if share is True or share == "all":
            return new[0]
        if share == "row":
            return new[i // ncol * ncol]
        if share == "col":
            return new[i % ncol]
        if isinstance(share, str):
            text = f"Unknown sharing {share!r}: use True, 'row', 'col', "
            text += "an axis index or an Axes."
            raise ValueError(text)
        if isinstance(share, int):
            return self.state.ax[share]
        return share
