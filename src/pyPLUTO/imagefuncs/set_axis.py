"""Module to manage the axis of the image."""

from __future__ import annotations

from typing import Unpack

import matplotlib.pyplot as plt
from matplotlib.axes import Axes
from matplotlib.axis import Axis
from matplotlib.colors import to_rgba
from matplotlib.legend import Legend

from pyPLUTO.imagefuncs.create_axes import CreateAxesManager
from pyPLUTO.imagefuncs.imagetools import ImageToolsManager
from pyPLUTO.imagefuncs.range import RangeManager
from pyPLUTO.imagefuncs.ticks import TicksManager
from pyPLUTO.imagekwargs import (
    CheckRangeKwargs,
    CreateAxesKwargs,
    MinorTicksKwargs,
    SetAxisKwargs,
    SetScalesKwargs,
    SetTitleKwargs,
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
        self.CreateAxesManager = CreateAxesManager(state)
        self.ImageToolsManager = ImageToolsManager(state)
        self.RangeManager = RangeManager(state)
        self.TicksManager = TicksManager(state)

    @track_kwargs
    def set_axis(
        self,
        ax: Axes | list[Axes] | int | None = None,
        _check: bool = True,
        **kwargs: Unpack[SetAxisKwargs],
    ) -> None:
        """Customize a single subplot axis.

        Properties such as the range, scale and aspect of each subplot should be
        customized here.

        Parameters
        ----------
        - aspect: 'auto' | 'equal' | float, default 'auto'
            Sets the aspect ratio of the plot. The 'auto' keyword is the
            default option. The 'equal' keyword sets the same scaling for x and
            y. A float fixes the ratio between the y-scale and the x-scale (1.0
            is the same as 'equal').
        - ax: ax object, default None
            The axis to customize. If None the current axis will be selected.
        - axalpha: float, default None
            Sets the opacity of the whole panel, where 1.0 is fully opaque and
            0.0 is fully transparent: background, spines, ticks, labels,
            title, grid, legend and everything drawn on it, own alpha
            included. It is kept for the axis, so what is drawn there later
            takes it too, unless given its own alpha.
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
        - sharex: bool | int | 'all' | 'row' | 'col' | Axes, default None
            Shares the x-axis: True or 'all' with the first axis (in
            create_axes, the first of those it makes), an index with that
            axis of the image, an Axes with that axis. 'row' and 'col' share
            within each row or column of the axes a create_axes call makes,
            and are refused for axes that already exist.
        - sharexaxes: bool | int | 'all' | 'row' | 'col' | Axes, default None
            Deprecated, use sharex.
        - sharey: bool | int | 'all' | 'row' | 'col' | Axes, default None
            Shares the y-axis, as sharex does.
        - shareyaxes: bool | int | 'all' | 'row' | 'col' | Axes, default None
            Deprecated, use sharey.
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
        - xtickslabels: str | list[str] | list[float] | None | bool, default True
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
        - ytickslabels: str | list[str] | list[float] | None | bool, default True
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
        ax, nax = self.ImageToolsManager.assign_ax(ax, _check=False, **kwargs)

        # Set fontsize
        self.state.fontsize = kwargs.get("fontsize", self.state.fontsize)
        plt.rcParams.update({"font.size": self.state.fontsize})

        # Set aspect ratio
        if "aspect" in kwargs and kwargs["aspect"] is not True:
            self.state.ax[nax].set_aspect(kwargs["aspect"])

        # Set xrange and yrange
        self.check_range(ax, nax, _check=False, **kwargs)

        # Set title and axes labels
        self.set_titles(ax, _check=False, **kwargs)

        # Share axis if needed
        self.share_axes(ax, nax, _check=False, **kwargs)

        # Set ticks size
        if "tickssize" in kwargs and kwargs["tickssize"] is not True:
            ax.tick_params(axis="x", labelsize=kwargs["tickssize"])
            ax.tick_params(axis="y", labelsize=kwargs["tickssize"])
        else:
            ax.tick_params(axis="both", labelsize=self.state.fontsize)

        # Set ticks direction, with ticks on all four sides: the far ones were
        # set with the string "off", which matplotlib read as True, and that
        # four-sided look is the one kept (decided 2026-09-29)
        if kwargs.get("ticksdir") or self.state.tickspar[nax] == 0:
            tckd = kwargs.get("ticksdir", "in")
            ax.tick_params(
                axis="both",
                which="major",
                direction=tckd,
                right=True,
                top=True,
            )
            ax.tick_params(
                which="minor",
                direction=tckd,
                right=True,
                top=True,
            )

        # Scales, which put back their own minor ticks
        self.set_scales(ax, nax, _check=False, **kwargs)

        # Set minor ticks, again after a scale
        xscaled = kwargs.get("xscale", True) is not True
        scaled = xscaled or kwargs.get("yscale", True) is not True
        self.check_minorticks(ax, nax, scaled, _check=False, **kwargs)

        # Set parameter that fixes the minorticks and ticksdir
        self.state.tickspar[nax] = 1

        # Opacity of the whole panel
        if (axalpha := kwargs.get("axalpha")) is not None:
            self.set_axalpha(ax, nax, axalpha)

        # Set ticks and tickslabels
        xtc = kwargs.get("xticks", True)
        ytc = kwargs.get("yticks", True)
        xtl = kwargs.get("xtickslabels", True)
        ytl = kwargs.get("ytickslabels", True)
        xminor = self.state.minorticks[nax]["x"]
        yminor = self.state.minorticks[nax]["y"]
        kept = self.state.ticks[nax]
        # A scale puts back its default ticks, so the kept ones are applied again
        if xtc is not True or xtl is not True:
            self.TicksManager.set_ticks(ax, xtc, xtl, "x", xminor, nax)
        elif kwargs.get("xscale", True) is not True:
            self.TicksManager.apply_ticks(ax, *kept["x"], "x", xminor)
        if ytc is not True or ytl is not True:
            self.TicksManager.set_ticks(ax, ytc, ytl, "y", yminor, nax)
        elif kwargs.get("yscale", True) is not True:
            self.TicksManager.apply_ticks(ax, *kept["y"], "y", yminor)

        # Sets grid on the axis
        grid = kwargs.get("grid", False)
        if grid is True or grid == "both":
            ax.grid(True)
        elif grid in ("x", "y"):
            ax.grid(True, axis=grid)

        # Reinforces the tight_layout if needed
        self.state.tight = kwargs.get("tight", self.state.tight)
        if self.state.tight is not False and self.state.fig is not None:
            self.state.fig.tight_layout()

        # End of the function

    @track_kwargs
    def set_titles(
        self,
        ax: Axes,
        _check: bool = True,
        **kwargs: Unpack[SetTitleKwargs],
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

        if "xscale" in kwargs and kwargs["xscale"] is not True:
            xscale = kwargs["xscale"]
            xscale_param = spar.get(xscale)
            xscale_kwargs = (
                {str(xscale_param): kwargs.get("xtresh")}
                if "xtresh" in kwargs
                else {}
            )
            ax.set_xscale(xscale, **xscale_kwargs)
            self.state.xscale[nax] = xscale

        if "yscale" in kwargs and kwargs["yscale"] is not True:
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
        if "xrange" in kwargs and kwargs["xrange"] is not None:
            self.RangeManager.set_xrange(ax, nax, kwargs["xrange"], 3)
        if "yrange" in kwargs and kwargs["yrange"] is not None:
            self.RangeManager.set_yrange(ax, nax, kwargs["yrange"], 3)

    @track_kwargs
    def share_axes(
        self,
        ax: Axes,
        nax: int,
        _check: bool = True,
        **kwargs: Unpack[CreateAxesKwargs],
    ) -> None:
        """Share the x- and y-axis of an axis that already exists.

        The values are the ones create_axes takes, resolved by the same
        find_share_target with no grid: True or 'all' share with the first
        axis of the image, an index or an Axes with that axis, and 'row' and
        'col' are refused, since the axis may come from any create_axes call.
        An axis already joined to its target is left alone, as when a
        drawing method has just created it with the same keyword.

        Parameters
        ----------
        - ax (not optional): Axes
            The axis that shares.
        - nax (not optional): int
            The index of the axis in the image.
        - sharex: bool | int | 'all' | Axes, default None
            The axis to share the x-axis with.
        - sharey: bool | int | 'all' | Axes, default None
            The axis to share the y-axis with.

        Returns
        -------
        - None

        Examples
        --------
        - Example #1: share the x-axis of the second axis with the first

            >>> self.share_axes(ax, 1, sharex=0)

        """
        self.CreateAxesManager.warn_old_share(kwargs)
        sharex = kwargs.get("sharex", kwargs.get("sharexaxes"))
        sharey = kwargs.get("sharey", kwargs.get("shareyaxes"))
        pairs = (
            (sharex, ax.sharex, ax.get_shared_x_axes()),
            (sharey, ax.sharey, ax.get_shared_y_axes()),
        )
        for share, join, shared in pairs:
            target = self.CreateAxesManager.find_share_target(nax, share)
            if target is not None and not shared.joined(ax, target):
                join(target)

    def set_axalpha(self, ax: Axes, nax: int, axalpha: float) -> None:
        """Fade everything on a panel, and record it for what comes later.

        The opacity reaches the background, the spines, the ticks, the tick
        labels, the grid, the titles, the axis labels and every artist
        already on the axis, its own alpha included; it is stored per axis,
        so the drawing methods give it to what they add afterwards. Inset
        axes are children of the panel but axes of their own, and are left
        to their own axalpha; a colorbar is a separate axis and is never
        reached.

        Parameters
        ----------
        - ax (not optional): Axes
            The axis to fade.
        - nax (not optional): int
            The index of the axis in the image.
        - axalpha (not optional): float
            The opacity, where 1.0 is fully opaque and 0.0 fully transparent.

        Returns
        -------
        - None

        Examples
        --------
        - Example #1: fade the first axis to a third

            >>> self.set_axalpha(ax, 0, 0.3)

        """
        self.state.axalpha[nax] = axalpha

        # Ticks, tick labels and grid through tick_params, which also holds
        # for the ticks matplotlib creates later; the axis labels and the
        # offset text belong to the axis too
        for axis in (ax.xaxis, ax.yaxis):
            tick = axis.get_major_ticks(numticks=1)[0]
            axis.set_tick_params(
                which="both",
                color=to_rgba(tick.tick1line.get_color(), axalpha),
                labelcolor=to_rgba(tick.label1.get_color(), axalpha),
                grid_alpha=axalpha,
            )
            axis.label.set_alpha(axalpha)
            axis.get_offset_text().set_alpha(axalpha)

        # Everything else on the panel: background, spines, titles, labels,
        # lines, maps, texts, and every part of a legend
        for artist in ax.get_children():
            if isinstance(artist, (Axis, Axes)):
                continue
            parts = artist.findobj() if isinstance(artist, Legend) else [artist]
            for part in parts:
                part.set_alpha(axalpha)

    @track_kwargs
    def check_minorticks(
        self,
        ax: Axes,
        nax: int,
        scaled: bool = False,
        _check: bool = True,
        **kwargs: Unpack[MinorTicksKwargs],
    ) -> None:
        """Check and set the minor ticks of the x- and y-axes.

        The value given is kept per axis and direction, also for the axes
        sharing that direction, and stays until another is given. It is
        applied when given, on the first call for the axis, and after a
        scale, which puts back the minor ticks of its own.

        Parameters
        ----------
        - ax: ax
            the selected set of axes
        - minorticks: str, default 'on'
            'off' removes the minor ticks on both axes, any other value
            shows them.
        - nax: int
            the index of the selected axis
        - scaled: bool, default False
            Whether a scale was just given.

        Returns
        -------
        - None

        """
        # Shared axes share their minor ticks, so every one of them keeps them
        if "minorticks" in kwargs:
            for typeaxis in ("x", "y"):
                for i in self.TicksManager.shared(ax, typeaxis):
                    self.state.minorticks[i][typeaxis] = kwargs["minorticks"]
        elif not scaled and self.state.tickspar[nax] != 0:
            return
        for typeaxis, minor in self.state.minorticks[nax].items():
            axis = getattr(ax, f"{typeaxis}axis")
            if minor != "off":
                axis.minorticks_on()
            else:
                axis.minorticks_off()
