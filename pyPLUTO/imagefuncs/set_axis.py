import warnings
from collections.abc import Iterable
from typing import Any

import matplotlib.pyplot as plt
from matplotlib.axes import Axes

from ..imagemixin import ImageMixin
from ..imagestate import ImageState
from ..utils.inspector import track_kwargs
from .imagetools import ImageToolsManager
from .range import RangeManager


class AxisManager(ImageMixin):
    """This class manages the axis of the image. It allows to customize the
    axis of the image, such as the range, scale and aspect."""

    exposed_methods = ("set_axis",)

    def __init__(self, state: ImageState) -> None:
        """Initializes the AxisManager with the given state."""
        self.state = state
        self.ImageToolsManager = ImageToolsManager(state)
        self.RangeManager = RangeManager(state)

    @track_kwargs
    def set_axis(
        self, ax: Axes | None = None, check: bool = True, **kwargs: Any
    ) -> None:
        """Customization of a single subplot axis. Properties such as the
        range, scale and aspect of each subplot should be customized here.

        Returns
        -------
        - None

        Parameters
        ----------
        - alpha: float, default 1.0
            Sets the opacity of the plot, where 1.0 means total opaque and 0.0
            means total transparent.
        - aspect: {'auto', 'equal', float}, default 'auto'
            Sets the aspect ratio of the plot. The 'auto' keyword is the default
            option (most likely the plot will be squared). The 'equal' keyword
            will set the same scaling for x and y. A float will fix the ratio
            between the y-scale and the x-scale (1.0 is the same as 'equal').
        - ax: ax object, default None
            The axis to customize. If None the current axis will be selected.
        - fontsize: float, default 17.0
            Sets the fontsize for all the axis components (only for the current
            axis).
        - grid: bool | string, default False
            Enables/disables the grid on the plot. If True it enables both axes
            grids. If 'x' or 'y' it enables only the x or y axis grid.
        - labelsize: float, default fontsize
            Sets the labels fontsize (which is the same for both labels).
            The default value corresponds to the value of the keyword
            'fontsize'.
        - minorticks: str, default None
            If not None enables the minor ticks on the plot (for both grid
            axes).
        - sharex: Matplotlib axis | False, default False
            Shares the x-axis with another axis.
        - sharey: Matplotlib axis | False, default False
            Shares the y-axis with another axis.
        - ticksdir: {'in', 'out'}, default 'in'
            Sets the ticks direction. The default option is 'in'.
        - tickssize: float | bool, default True
            Sets the ticks fontsize (which is the same for both grid axes).
            The default value corresponds to the value of the keyword
            'fontsize'.
        - title: str, default None
            Places the title of the plot on top of it.
        - titlepad: float, default 8.0
            Sets the distance between the title and the top of the plot
        - titlesize: float, default fontsize
            Sets the title fontsize. The default value corresponds to the value
            of the keyword 'fontsize'.
        - xrange: [float, float], default [0,1]
            Sets the range in the x-direction. If not defined the code will
            compute the range while plotting the data.
        - xscale: {'linear','log'}, default 'linear'
            If enabled (and different from True), sets automatically the scale
            on the x-axis. Data in log scale should be used with the keyword
            'log', while data in linear scale should be used with the keyword
            'linear'.
        - xticks: {[float], None, True}, default True
            If enabled (and different from True), sets manually ticks on
            x-axis. In order to completely remove the ticks the keyword should
            be used with None.
        - xtickslabels: {[str], None, True}, default True
            If enabled (and different from True), sets manually the ticks
            labels on the x-axis. In order to completely remove the ticks the
            keyword should be used with None. Note that fixed tickslabels should
            always correspond to fixed ticks.
        - xtitle: str, default None
            Sets and places the label of the x-axis.
        - yrange: [float, float], default [0,1]
            Sets the range in the y-direction. If not defined the code will
            compute the range while plotting the data.
        - yscale: {'linear','log'}, default 'linear'
            If enabled (and different from True), sets automatically the scale
            on the y-axis. Data in log scale should be used with the keyword
            'log', while data in linear scale should be used with the keyword
            'linear'.
        - yticks: {[float], None, True}, default True
            If enabled (and different from True), sets manually ticks on
            y-axis. In order to completely remove the ticks the keyword should
            be used with None.
        - ytickslabels: {[str], None, True}, default True
            If enabled (and different from True), sets manually the ticks
            labels on the y-axis. In order to completely remove the ticks the
            keyword should be used with None. Note that fixed tickslabels should
            always correspond to fixed ticks.
        - ytitle: str, default None
            Sets and places the label of the y-axis.

        ----

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
        kwargs.pop("check", check)

        # Take last axis if not specified
        ax, nax = self.ImageToolsManager.assign_ax(ax, **kwargs)

        if ax is None:
            raise ValueError("No axis can be set!")

        # Set fontsize
        self.fontsize = kwargs.get("fontsize", self.fontsize)
        plt.rcParams.update({"font.size": self.fontsize})

        # Set aspect ratio
        if kwargs.get("aspect", True) is not True:
            self.ax[nax].set_aspect(kwargs["aspect"])

        # Set xrange and yrange
        if kwargs.get("xrange") is not None:
            self.RangeManager.set_xrange(ax, nax, kwargs["xrange"], 3)
        if kwargs.get("yrange") is not None:
            self.RangeManager.set_yrange(ax, nax, kwargs["yrange"], 3)

        # Set title and axes labels
        if kwargs.get("title") is not None:
            ax.set_title(
                kwargs["title"],
                fontsize=kwargs.get("titlesize", self.fontsize),
                pad=kwargs.get("titlepad", 8.0),
            )
        if kwargs.get("xtitle") is not None:
            ax.set_xlabel(
                kwargs["xtitle"],
                fontsize=kwargs.get("labelsize", self.fontsize),
            )
        if kwargs.get("ytitle") is not None:
            ax.set_ylabel(
                kwargs["ytitle"],
                fontsize=kwargs.get("labelsize", self.fontsize),
            )
        # Set shareaxisx and shareaxisy (+ deprecated sharex and sharey)
        if kwargs.get("sharex", False) is not False:
            warnings.warn(
                "sharexs is deprecated. Use shareaxisx instead.",
                DeprecationWarning,
            )
        if kwargs.get("sharey", False) is not False:
            warnings.warn(
                "sharey is deprecated. Use shareaxisy instead.",
                DeprecationWarning,
            )
        if kwargs.get("shareaxisx", False) is not False:
            ax.sharex(kwargs["shareaxisx"])
        if kwargs.get("shareaxisy", False) is not False:
            ax.sharey(kwargs["shareaxisy"])

        # Set ticks size
        if kwargs.get("tickssize", True) is not True:
            ax.tick_params(axis="x", labelsize=kwargs["tickssize"])
            ax.tick_params(axis="y", labelsize=kwargs["tickssize"])
        else:
            ax.tick_params(axis="both", labelsize=self.fontsize)

        # Set ticks direction
        if kwargs.get("ticksdir") or self.tickspar[nax] == 0:
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
        if kwargs.get("minorticks") or self.tickspar[nax] == 0:
            mintks = kwargs.get("minorticks", "on")
            if mintks != "off":
                ax.minorticks_on()
            else:
                ax.minorticks_off()

        # Set parameter that fixes the minorticks and ticksdir
        self.tickspar[nax] = 1

        spar = {"asinh": "linear_width", "symlog": "linthresh"}

        # Scales and alpha
        if kwargs.get("xscale", True) is not True:
            xscale = kwargs["xscale"]
            xscale_param = spar.get(xscale)
            xscale_kwargs = (
                {str(xscale_param): kwargs.get("xtresh")}
                if "xtresh" in kwargs
                else {}
            )
            ax.set_xscale(xscale, **xscale_kwargs)
            self.xscale[nax] = xscale

        if kwargs.get("yscale", True) is not True:
            yscale = kwargs["yscale"]
            yscale_param = spar.get(yscale)
            yscale_kwargs = (
                {str(yscale_param): kwargs.get("ytresh")}
                if "ytresh" in kwargs
                else {}
            )
            ax.set_yscale(yscale, **yscale_kwargs)
            self.yscale[nax] = yscale

        if kwargs.get("alpha"):
            ax.set_alpha(kwargs["alpha"])

        # Set ticks and tickslabels
        xtc = kwargs.get("xticks", True)
        ytc = kwargs.get("yticks", True)
        xtl = kwargs.get("xtickslabels", True)
        ytl = kwargs.get("ytickslabels", True)
        if xtc is not True or xtl is not True:
            self.set_ticks(ax, xtc, xtl, "x")
        if ytc is not True or ytl is not True:
            self.set_ticks(ax, ytc, ytl, "y")

        # Sets grid on the axis
        if kwargs.get("grid", False) is True:
            ax.grid(True)
        elif isinstance(kwargs.get("grid", False), str):
            ax.grid(True, axis=kwargs["grid"])

        # Reinforces the tight_layout if needed
        if self.tight is not False and self.fig is not None:
            self.fig.tight_layout()

        # End of the function

    def set_ticks(
        self,
        ax: Axes,
        tc: str | list[float] | bool | None,
        tl: str | list[str] | bool | None,
        typeaxis: str,
    ) -> None:
        """Sets the ticks and ticks labels on the x- or y-axis of a
        selected axis.

        Returns
        -------
        - None

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

        ----

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
                warnings.warn(warn, UserWarning)

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
                warnings.warn(warn, UserWarning)

            # Ticks are set custom, then tickslabels are set
            if tl is None:
                set_label[typeaxis]([])
            elif isinstance(tl, str):
                set_label[typeaxis]([tl])  # Wrap single string
            elif isinstance(tl, Iterable):
                set_label[typeaxis](tl)
            else:
                raise TypeError(f"Invalid tick labels: {tl!r}")

        # Ticks are custom, tickslabels are default
        elif tc is not True:
            set_ticks[typeaxis](tc)

        # End of the function
