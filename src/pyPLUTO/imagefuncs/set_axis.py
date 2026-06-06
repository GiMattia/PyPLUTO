"""Module to manage the axis of the image."""

from __future__ import annotations

import warnings
from collections.abc import Iterable
from typing import Unpack

import matplotlib.pyplot as plt
from matplotlib.axes import Axes
from matplotlib.ticker import (
    AutoMinorLocator,
    FixedFormatter,
    NullFormatter,
    NullLocator,
)

from pyPLUTO.imagefuncs.imagetools import ImageToolsManager
from pyPLUTO.imagefuncs.range import RangeManager
from pyPLUTO.imagekwargs import (
    CheckRangeKwargs,
    MinorTicksKwargs,
    SetAxisKwargs,
    SetScalesKwargs,
    SetTitleKwargs,
    ShareAxesKwargs,
)
from pyPLUTO.imagemixin import ImageMixin
from pyPLUTO.imagestate import ImageState
from pyPLUTO.utils.inspector import track_kwargs


class AxisManager(ImageMixin):
    """Manage the axis of the image.

    It allows to customize the axis of the image, such as the range, scale and
    aspect.
    """

    def __init__(self, state: ImageState) -> None:
        """Initialize the AxisManager with the given state."""
        self.state = state
        self.ImageToolsManager = ImageToolsManager(state)
        self.RangeManager = RangeManager(state)

    @track_kwargs
    def set_axis(
        self,
        ax: Axes | list[Axes] | int | None,
        _check: bool = True,
        **kwargs: Unpack[SetAxisKwargs],
    ) -> None:
        """Customize a single subplot axis.

        Properties such as the range, scale and aspect of each subplot should be
        customized here.

        Parameters
        ----------
        - alpha: float, default 1.0
            Sets the opacity of the plot, where 1.0 is fully opaque and 0.0 is
            fully transparent.
        - aspect: 'auto' | 'equal' | float, default 'auto'
            Sets the aspect ratio of the plot. The 'auto' keyword is the
            default option. The 'equal' keyword sets the same scaling for x and
            y. A float fixes the ratio between the y-scale and the x-scale (1.0
            is the same as 'equal').
        - ax: ax object, default None
            The axis to customize. If None the current axis will be selected.
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
        - grid: bool | string, default False
            Enables/disables the grid on the plot. If True it enables both axes
            grids. If 'x' or 'y' it enables only the x- or y-axis grid.
        - hratio: [float], default [1.0]
            Ratio between the rows of the plot. The default is that every plot
            row has the same height.
        - hspace: [float], default []
            The space between plot rows (in figure units). If not enough or too
            many spaces are considered, the program will remove the excess and
            fill the lacks with [0.1].
        - labelsize: float, default fontsize
            Sets the labels fontsize (which is the same for both labels). The
            default value corresponds to the value of the keyword 'fontsize'.
        - left: float, default varies
            The left limit of the axis / axes set. For the figure layout it is
            the space from the left border to the plot (default 0.125); for an
            inset zoom it is the left position of the inset (default 0.6).
        - minorticks: str, default None
            If not None enables the minor ticks on the plot (for both grid
            axes).
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
        - sharex: Matplotlib axis, default False
            Enables/disables the sharing of the x-axis between the subplots.
        - sharey: Matplotlib axis, default False
            Enables/disables the sharing of the y-axis between the subplots.
        - suptitle: str, default None
            Creates a figure title over all the subplots.
        - ticksdir: {'in', 'out'}, default 'in'
            Sets the ticks direction. The default option is 'in'.
        - tickssize: float | bool, default True
            Sets the ticks fontsize (which is the same for both grid axes). The
            default value corresponds to the value of the keyword 'fontsize'.
        - tight: bool, default True
            Enables/disables tight layout options for the figure. In case of a
            highly customized plot (e.g. ratios or space between rows and
            columns) the option is set by default to False since that option
            would not be available for standard matplotlib functions.
        - title: str, default None
            Places the title of the plot on top of it.
        - titlepad: float, default 8.0
            Sets the distance between the title and the top of the plot.
        - titlesize: float, default fontsize
            Sets the title fontsize. The default value corresponds to the value
            of the keyword 'fontsize'.
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
        - xlabelpad: float, default 4.0
            The padding between the x-axis label and the axis.
        - xrange: [float, float], default 'Default'
            Sets the range in the x-direction. If not defined, the range is
            computed automatically from the x-array.
        - xscale: {'linear','log'}, default 'linear'
            If enabled (and different from 'Default'), sets automatically the
            scale on the x-axis. Data in log scale should be used with the
            keyword 'log', while data in linear scale should be used with the
            keyword 'linear'.
        - xticks: list[float] | None | bool, default True
            If enabled (and different from True), sets manually ticks on the
            x-axis. In order to completely remove the ticks the keyword should
            be used with None.
        - xtickslabels: list[str] | None | bool, default True
            If enabled (and different from True), sets manually the ticks
            labels on the x-axis. In order to completely remove the ticks the
            keyword should be used with None. Note that fixed tickslabels
            should always correspond to fixed ticks.
        - xtitle: str, default None
            Sets and places the label of the x-axis.
        - xtresh: float
            The threshold parameter for the x-axis symlog/asinh scale.
        - ylabelpad: float, default 4.0
            The padding between the y-axis label and the axis.
        - yrange: [float, float], default 'Default'
            Sets the range in the y-direction. If not defined, the range is
            computed automatically from the y-array.
        - yscale: {'linear','log'}, default 'linear'
            If enabled (and different from 'Default'), sets automatically the
            scale on the y-axis. Data in log scale should be used with the
            keyword 'log', while data in linear scale should be used with the
            keyword 'linear'.
        - yticks: list[float] | None | bool, default True
            If enabled (and different from True), sets manually ticks on the
            y-axis. In order to completely remove the ticks the keyword should
            be used with None.
        - ytickslabels: list[str] | None | bool, default True
            If enabled (and different from True), sets manually the ticks
            labels on the y-axis. In order to completely remove the ticks the
            keyword should be used with None. Note that fixed tickslabels
            should always correspond to fixed ticks.
        - ytitle: str, default None
            Sets and places the label of the y-axis.
        - ytresh: float
            The threshold parameter for the y-axis symlog/asinh scale.

        Returns
        -------
        - None

        Examples
        --------
        - Example #1: create an axis and set title and labels on both axes

            >>> import pyPLUTO as pp
            >>> I = pp.Image()
            >>> ax = I.create_axes()
            >>> I.set_axis(
            ...     title="Title",
            ...     titlesize=30.0,
            ...     xtitle="x-axis",
            ...     ytitle="y-axis",
            ... )

        - Example #2: create an axis, remove the ticks for the x-axis and
            set manually the ticks for the y-axis

            >>> import pyPLUTO as pp
            >>> I = pp.Image()
            >>> ax = I.create_axes()
            >>> I.set_axis(
            ...     ax,
            ...     xticks=None,
            ...     yrange=[-1.0, 1.0],
            ...     yticks=[-0.8, -0.6, -0.4, -0.2, 0, 0.2, 0.4, 0.6, 0.8],
            ... )

        - Example #3: create two axes and invert the direction of the ticks in
            the first one

            >>> import pyPLUTO as pp
            >>> I = pp.Image()
            >>> ax = I.create_axes(right=0.7)
            >>> ax = I.create_axes(left=0.8)
            >>> I.set_axis(ax=ax[0], ticksdir="out")

        - Example #4: create a 2x2 grid with axes labels and customed ticks

            >>> import pyPLUTO as pp
            >>> I = pp.Image()
            >>> ax = I.create_axes(ncol=2, nrow=2)
            >>> for i in [0, 1, 2, 3]:
            ...     I.set_axis(
            ...         ax=ax[i],
            ...         xtitle="x-axis",
            ...         ytitle="y-title",
            ...         xticks=[0.25, 0.5, 0.75],
            ...         yticks=[0.25, 0.5, 0.75],
            ...         xtickslabels=["1/4", "1/2", "3/4"],
            ...     )

        """
        # Take last axis if not specified
        kwargs["ncol"] = 1
        kwargs["nrow"] = 1
        ax, nax = self.ImageToolsManager.assign_ax(ax, _check=False, **kwargs)

        if ax is None:
            raise ValueError("No axis can be set!")

        # Set fontsize
        self.state.fontsize = kwargs.get("fontsize", self.state.fontsize)
        plt.rcParams.update({"font.size": self.state.fontsize})

        # Set aspect ratio
        if kwargs.get("aspect", True) is not True:
            self.state.ax[nax].set_aspect(kwargs["aspect"])

        # Set xrange and yrange
        self.check_range(ax, nax, _check=False, **kwargs)

        # Set title and axes labels
        self.set_titles(ax, _check=False, **kwargs)

        # Share axis if needed
        self.share_axes(ax, _check=False, **kwargs)

        # Set ticks size
        if kwargs.get("tickssize", True) is not True:
            ax.tick_params(axis="x", labelsize=kwargs["tickssize"])
            ax.tick_params(axis="y", labelsize=kwargs["tickssize"])
        else:
            ax.tick_params(axis="both", labelsize=self.state.fontsize)

        # Set ticks direction
        if kwargs.get("ticksdir") or self.state.tickspar[nax] == 0:
            tckd = kwargs.get("ticksdir", "in")
            ax.tick_params(
                axis="both",
                which="major",
                direction=tckd,
                right="off",
                top="off",
            )
            ax.tick_params(
                which="minor", direction=tckd, right="off", top="off"
            )

        # Set minor ticks
        self.check_minorticks(ax, nax, _check=False, **kwargs)

        # Set parameter that fixes the minorticks and ticksdir
        self.state.tickspar[nax] = 1

        # Scales and alpha
        self.set_scales(ax, nax, _check=False, **kwargs)

        if kwargs.get("alpha"):
            ax.set_alpha(kwargs["alpha"])

        # Set ticks and tickslabels
        xtc = kwargs.get("xticks", True)
        ytc = kwargs.get("yticks", True)
        xtl = kwargs.get("xtickslabels", True)
        ytl = kwargs.get("ytickslabels", True)
        minor = kwargs.get("minorticks", "on")
        if xtc is not True or xtl is not True:
            self.set_ticks(ax, xtc, xtl, "x", minor=minor)
        if ytc is not True or ytl is not True:
            self.set_ticks(ax, ytc, ytl, "y", minor=minor)

        # Sets grid on the axis
        grid = kwargs.get("grid", False)
        if grid is True or grid == "both":
            ax.grid(True)
        elif grid in ("x", "y"):
            ax.grid(True, axis=grid)

        # Reinforces the tight_layout if needed
        if self.state.tight is not False and self.state.fig is not None:
            self.state.fig.tight_layout()

        # End of the function

    def set_ticks(
        self,
        ax: Axes,
        tc: str | list[float] | bool | None,
        tl: str | list[str] | bool | None,
        typeaxis: str,
        minor: str | int | None = "on",
    ) -> None:
        """Setsthe ticks and ticks labels on the x-/y-axis of a selected axis.

        Parameters
        ----------
        - ax: ax
            the selected set of axes
        - tc: list[float]
            the ticks of the x-axis
        - tl: list[float]
            the ticks labels of the x-axis
        - typeaxis: str
            the type of axis (x or y)

        Returns
        -------
        - None

        Examples
        --------
        - Example #1: set ticks and ticks labels on the x-axis

            >>> _set_ticks(ax, [0, 1, 2, 3], ["0", "1", "2", "3"], "x")

        - Example #2: set ticks and ticks labels on the y-axis (no ticks)

            >>> _set_ticks(ax, None, None, "y")

        - Example #3: set ticks and ticks labels on the x-axis (no ticks labels)

            >>> _set_ticks(ax, [0, 1, 2, 3], None, "x")

        """
        set_ticks = {"x": ax.set_xticks, "y": ax.set_yticks}
        set_label = {"x": ax.set_xticklabels, "y": ax.set_yticklabels}

        # Ticks are None
        if tc is None:
            set_ticks[typeaxis]([])
            set_label[typeaxis]([])

            # If tickslabels are not None raise a warning
            if tl is not None and tl is not True:
                warn = (
                    "Warning, tickslabels are defined with no"
                    "ticks!! (function setax)"
                )
                warnings.warn(warn, UserWarning, stacklevel=2)

        # Ticks are not None and tickslabels are custom
        elif tl is not True:
            # Ticks are not None, then are set
            if tc is not True:
                set_ticks[typeaxis](tc)

            # Ticks are Default with custom tickslabels, a warning is raised
            elif tl is not None:
                warn = (
                    "Warning, tickslabels should be fixed only"
                    "when ticks are fixed (function setax)"
                )
                warnings.warn(warn, UserWarning, stacklevel=2)

            # Ticks are set custom, then tickslabels are set
            # Use formatters directly: set_xticklabels is reset by log scale
            axis = getattr(ax, f"{typeaxis}axis")
            if tl is None:
                if tc is True:
                    axis.set_major_formatter(NullFormatter())
                    axis.set_minor_formatter(NullFormatter())
                else:
                    set_label[typeaxis]([])
            elif isinstance(tl, str):
                axis.set_major_formatter(FixedFormatter([tl]))
                axis.set_minor_formatter(NullFormatter())
                scale = getattr(ax, f"get_{typeaxis}scale")()
                if minor == "off" or scale != "linear":
                    axis.set_minor_locator(NullLocator())
                else:
                    axis.set_minor_locator(AutoMinorLocator(5))
            elif isinstance(tl, Iterable):
                axis.set_major_formatter(FixedFormatter(list(tl)))
                axis.set_minor_formatter(NullFormatter())
                scale = getattr(ax, f"get_{typeaxis}scale")()
                if minor == "off" or scale != "linear":
                    axis.set_minor_locator(NullLocator())
                else:
                    axis.set_minor_locator(AutoMinorLocator(5))
            else:
                raise TypeError(f"Invalid tick labels: {tl!r}")

        # Ticks are custom, tickslabels are default
        elif tc is not True:
            set_ticks[typeaxis](tc)

        # End of the function

    @track_kwargs
    def set_titles(
        self, ax: Axes, _check: bool = True, **kwargs: Unpack[SetTitleKwargs]
    ) -> None:
        """Set the title or axis labels of the plot.

        Parameters
        ----------
        - ax: ax
            the selected set of axes
        - labelsize: float, default fontsize
            Sets the labels fontsize (which is the same for both labels). The
            default value corresponds to the value of the keyword 'fontsize'.
        - title: str, default None
            Places the title of the plot on top of it.
        - titlepad: float, default 8.0
            Sets the distance between the title and the top of the plot.
        - titlesize: float, default fontsize
            Sets the title fontsize. The default value corresponds to the value
            of the keyword 'fontsize'.
        - xlabelpad: float, default 4.0
            The padding between the x-axis label and the axis.
        - xtitle: str, default None
            Sets and places the label of the x-axis.
        - ylabelpad: float, default 4.0
            The padding between the y-axis label and the axis.
        - ytitle: str, default None
            Sets and places the label of the y-axis.

        Returns
        -------
        - None

        """
        if isinstance(kwargs.get("title"), str):
            ax.set_title(
                str(kwargs.get("title")),
                fontsize=kwargs.get("titlesize", self.state.fontsize),
                pad=kwargs.get("titlepad", 8.0),
            )
        if isinstance(kwargs.get("xtitle"), str):
            ax.set_xlabel(
                str(kwargs.get("xtitle")),
                fontsize=kwargs.get("labelsize", self.state.fontsize),
                labelpad=kwargs.get("xlabelpad", 4.0),
            )
        if isinstance(kwargs.get("ytitle"), str):
            ax.set_ylabel(
                str(kwargs.get("ytitle")),
                fontsize=kwargs.get("labelsize", self.state.fontsize),
                labelpad=kwargs.get("ylabelpad", 4.0),
            )

    @track_kwargs
    def set_scales(
        self,
        ax: Axes,
        nax: int,
        _check: bool = True,
        **kwargs: Unpack[SetScalesKwargs],
    ) -> None:
        """Set the scales of the x- and y-axis of a selected axis.

        Parameters
        ----------
        - ax: ax
            the selected set of axes
        - nax: int
            the index of the selected axis
        - xscale: {'linear','log'}, default 'linear'
            If enabled (and different from 'Default'), sets automatically the
            scale on the x-axis. Data in log scale should be used with the
            keyword 'log', while data in linear scale should be used with the
            keyword 'linear'.
        - xtresh: float
            The threshold parameter for the x-axis symlog/asinh scale.
        - yscale: {'linear','log'}, default 'linear'
            If enabled (and different from 'Default'), sets automatically the
            scale on the y-axis. Data in log scale should be used with the
            keyword 'log', while data in linear scale should be used with the
            keyword 'linear'.
        - ytresh: float
            The threshold parameter for the y-axis symlog/asinh scale.

        Returns
        -------
        - None

        """
        spar = {"asinh": "linear_width", "symlog": "linthresh"}

        if kwargs.get("xscale", True) is not True:
            xscale = kwargs["xscale"]
            xscale_param = spar.get(xscale)
            xscale_kwargs = (
                {str(xscale_param): kwargs.get("xtresh")}
                if "xtresh" in kwargs
                else {}
            )
            ax.set_xscale(xscale, **xscale_kwargs)
            self.state.xscale[nax] = xscale

        if kwargs.get("yscale", True) is not True:
            yscale = kwargs["yscale"]
            yscale_param = spar.get(yscale)
            yscale_kwargs = (
                {str(yscale_param): kwargs.get("ytresh")}
                if "ytresh" in kwargs
                else {}
            )
            ax.set_yscale(yscale, **yscale_kwargs)
            self.state.yscale[nax] = yscale

    @track_kwargs
    def check_range(
        self,
        ax: Axes,
        nax: int,
        _check: bool = True,
        **kwargs: Unpack[CheckRangeKwargs],
    ) -> None:
        """Check and set the range of the x- and y-axis of a selected axis.

        Parameters
        ----------
        - ax: ax
            the selected set of axes
        - nax: int
            the index of the selected axis
        - xrange: [float, float], default 'Default'
            Sets the range in the x-direction. If not defined, the range is
            computed automatically from the x-array.
        - yrange: [float, float], default 'Default'
            Sets the range in the y-direction. If not defined, the range is
            computed automatically from the y-array.

        Returns
        -------
        - None

        """
        if kwargs.get("xrange") is not None:
            self.RangeManager.set_xrange(ax, nax, kwargs["xrange"], 3)
        if kwargs.get("yrange") is not None:
            self.RangeManager.set_yrange(ax, nax, kwargs["yrange"], 3)

    @track_kwargs
    def share_axes(
        self, ax: Axes, _check: bool = True, **kwargs: Unpack[ShareAxesKwargs]
    ) -> None:
        """Share the x- and y-axis of a selected axis.

        Parameters
        ----------
        - ax: ax
            the selected set of axes
        - sharex: bool | str | Matplotlib axis, default False
            Enables/disables the sharing of the x-axis between the subplots.
        - sharey: bool | str | Matplotlib axis, default False
            Enables/disables the sharing of the y-axis between the subplots.

        Returns
        -------
        - None

        """
        if kwargs.get("sharex", False) is not False:
            ax.sharex(kwargs["sharex"])
        if kwargs.get("sharey", False) is not False:
            ax.sharey(kwargs["sharey"])

    @track_kwargs
    def check_minorticks(
        self,
        ax: Axes,
        nax: int,
        _check: bool = True,
        **kwargs: Unpack[MinorTicksKwargs],
    ) -> None:
        """Check and set the minor ticks of the x- and y-axes.

        Parameters
        ----------
        - ax: ax
            the selected set of axes
        - minorticks: str, default None
            If not None enables the minor ticks on the plot (for both grid
            axes).
        - nax: int
            the index of the selected axis

        Returns
        -------
        - None

        """
        if kwargs.get("minorticks") or self.state.tickspar[nax] == 0:
            mintks = kwargs.get("minorticks", "on")
            if mintks != "off":
                ax.minorticks_on()
            else:
                ax.minorticks_off()
