"""ScatterManager class."""

from typing import Any

import numpy as np
from matplotlib.collections import PathCollection

from pyPLUTO.imagefuncs.colorbar import ColorbarManager
from pyPLUTO.imagefuncs.imagetools import ImageToolsManager
from pyPLUTO.imagefuncs.legend import LegendManager
from pyPLUTO.imagefuncs.range import RangeManager
from pyPLUTO.imagefuncs.set_axis import AxisManager
from pyPLUTO.imagemixin import ImageMixin
from pyPLUTO.imagestate import ImageState
from pyPLUTO.utils.inspector import track_kwargs


class ScatterManager(ImageMixin):
    """Manager for the scatter plot of a 2D function.

    A simple figure and a single axis can also be created.
    """

    def __init__(self, state: ImageState) -> None:
        """Initialize the ScatterManager with the given state."""
        self.state = state

        self.AxisManager = AxisManager(state)
        self.ColorbarManager = ColorbarManager(state)
        self.ImageToolsManager = ImageToolsManager(state)
        self.LegendManager = LegendManager(state)
        self.RangeManager = RangeManager(state)

    @track_kwargs
    def scatter(
        self,
        x: np.ndarray | list[float],
        y: np.ndarray | list[float],
        check: bool = True,
        **kwargs: Any,
    ) -> PathCollection:
        """Scatter plot for a 2D function (or a 2D slice).

        A simple figure and a single axis can also be created.

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
        - ax: ax | int | None, default None
            The axis where to plot. If None, the last considered axis will be
            used.
        - bottom: float, default varies
            The bottom limit of the axis / axes set. For the figure layout it
            is the space from the bottom border to the plot (default 0.1); for
            an inset zoom it is the bottom position of the inset (default 0.6 +
            height).
        - c: str, default self.color
            Determines the color. If not defined, the program will loop over an
            array of 6 colors which are different for the most common vision
            deficiencies.
        - clabel: str, default None
            Sets the label of the colorbar.
        - cmap: str, default 'hot'
            Selects the colormap. Some useful colormaps are: plasma, magma,
            seismic. Please avoid colormaps like jet or rainbow, which are not
            perceptively uniform and not suited for people with vision
            deficiencies.
        - cpad: float, default 0.07
            Fraction of original axes between colorbar and the axes (in axes
            units).
        - cpos: {'top','bottom','left','right'}, default None
            Enables the colorbar and sets its position. If not defined, no
            colorbar is shown.
        - cscale: {'linear','log','symlog','twoslope'}, default 'linear'
            Sets the colorbar scale. Default is the linear ('norm') scale.
        - cticks: {[float], None}, default None
            If enabled (and different from None), sets manually the ticks on
            the colorbar.
        - ctickslabels: str, default None
            If enabled, sets manually ticks labels on the colorbar.
        - edgecolor: list[str], default [None]
            Sets the edge color of the legend. The default value is black
            ('k').
        - edgecolors: str, default None
            Enables a contouring color for the markers.
        - extend: {'neither','both','min','max'}, default 'neither'
            Sets the extension of the triangular colorbar extension.
        - extendrect: bool, default False
            If True, the colorbar extension will be triangular.
        - figsize: list[float], default varies
            Sets the figure size. The default is [6*sqrt(ncol), 5*sqrt(nrow)],
            computed from the number of rows and columns (or [8,5] for a single
            plot).
        - fillstyle: {'full', 'left', 'right', 'bottom', 'top', 'none'},
            default 'full'
            Sets the marker filling. The default value is the fully filled
            marker ('full').
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
        - label: str, default None
            Associates a label to the plot, used for the creation of the
            legend.
        - labelsize: float, default fontsize
            Sets the labels fontsize (which is the same for both labels). The
            default value corresponds to the value of the keyword 'fontsize'.
        - left: float, default varies
            The left limit of the axis / axes set. For the figure layout it is
            the space from the left border to the plot (default 0.125); for an
            inset zoom it is the left position of the inset (default 0.6).
        - legalpha: float, default 0.8
            Sets the opacity of the legend.
        - legcols: int, default 1
            Sets the number of columns that the legend should have.
        - legpad: float, default 0.8
            Sets the space between the lines (or symbols) and the corresponding
            text in the legend.
        - legpos: int | str, default None
            If defined, creates a legend at the specified location.
        - legsize: float, default fontsize
            Sets the fontsize of the legend. The default value is the default
            fontsize value.
        - legspace: float, default 2
            Sets the space between the legend columns, in font-size units.
        - ls: {'-', '--', '-.', ':', ' ', etc.}, default '-'
            Sets the linestyle. The choices available are the ones defined in
            the matplotlib package.
        - lw: float, default 1.3
            Sets the linewidth.
        - marker: {'o', 'v', '^', '<', '>', 'X', ' ', etc.}, default ' '
            Sets an optional symbol for every point. The default value is no
            marker (' ').
        - minorticks: str, default None
            If not None enables the minor ticks on the plot (for both grid
            axes).
        - ms: float, default 3
            Sets the marker size.
        - mscale: float, default 1.0
            Sets the marker scale. The default value is 1.0.
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
        - sharex: bool | str | Matplotlib axis, default False
            Enables/disables the sharing of the x-axis between the subplots.
        - sharey: bool | str | Matplotlib axis, default False
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
        - tresh: float, default max(abs(vmin),vmax)*0.01
            Sets the threshold for the colormap (used with composite
            colorscales such as twoslope or symlog).
        - vmax: float
            The maximum value of the variable to be computed / plotted.
        - vmin: float
            The minimum value of the variable to be computed / plotted.
        - wratio: [float], default [1.0]
            Ratio between the columns of the plot. The default is that every
            plot column has the same width.
        - wspace: [float], default []
            The space between plot columns (in figure units). If not enough or
            too many spaces are considered, the program will remove the excess
            and fill the lacks with [0.1].
        - x (not optional): 1D array
            The x-axis variable.
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
        - y (not optional): 1D array
            The y-axis variable.
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
        - PathCollection

        ----

        Examples
        --------
        - Example #1: Plot a scatter plot of a variable

            >>> I.scatter(x, y)

        - Example #2: Plot a scatter plot of a variable with a colorbar

            >>> I.scatter(x, y, cmap="hot", c=x**2 + y**2, cpos="right")

        """
        # Convert x and y to numpy arrays (if necessary)
        x = np.asarray(x)
        y = np.asarray(y)

        kwargs.pop("check", check)

        # Set or create figure and axes
        ax, nax = self.ImageToolsManager.assign_ax(
            kwargs.pop("ax", None), **kwargs
        )

        if self.state.fig is None:
            raise ValueError(
                "No figure is present. Please create a figure first."
            )
        # Keywords xrange and yrange
        if not kwargs.get("xrange") and self.state.setax[nax] != 1:
            kwargs["xrange"] = [x.min(), x.max()]
        if not kwargs.get("yrange") and self.state.setay[nax] != 1:
            kwargs["yrange"] = [y.min(), y.max()]

        # Set ax parameters
        self.AxisManager.set_axis(ax=ax, check=False, **kwargs)
        self.ImageToolsManager.hide_text(nax, ax.texts)

        # Keywords vmin and vmax
        c = kwargs.get("c")
        # If c is a list convert to array
        vmin = (
            kwargs.get("vmin", 0.0)
            if c is None or isinstance(c, str)
            else kwargs.get("vmin", np.nanmin(np.asarray(c)))
        )
        vmax = (
            kwargs.get("vmax", 0.0)
            if c is None or isinstance(c, str)
            else kwargs.get("vmax", np.nanmax(np.asarray(c)))
        )

        # Keyword for colorbar and colorscale
        cpos = kwargs.get("cpos")
        cscale = kwargs.get("cscale", "norm")
        tresh = kwargs.get("tresh", max(np.abs(vmin), vmax) * 0.01)
        self.state.vlims[nax] = [vmin, vmax, tresh]

        # Set the colorbar scale
        if not isinstance(c, str) and c is not None:
            norm = self.ImageToolsManager.set_cscale(cscale, vmin, vmax, tresh)
            cmap = self.ImageToolsManager.find_cmap(kwargs.get("cmap"))
        else:
            norm = None
            cmap = None

        # Start scatter plot procedure
        pcm = ax.scatter(
            x,
            y,
            cmap=cmap,
            norm=norm,
            c=c,
            s=kwargs.get("ms", 3),
            edgecolors=kwargs.get("edgecolors", "none"),
            alpha=kwargs.get("alpha", 1.0),
            marker=kwargs.get("marker", "o"),
        )

        # Creation of the legend
        self.state.legpos[nax] = kwargs.get("legpos", self.state.legpos[nax])
        if self.state.legpos[nax] is not None:
            copy_label = kwargs.get("label")
            kwargs["label"] = None
            self.LegendManager.legend(ax, check=False, fromplot=True, **kwargs)
            kwargs["label"] = copy_label

        # Place the colorbar (use colorbar function)
        if cpos is not None:
            self.ColorbarManager.colorbar(pcm, check=False, **kwargs)

        # If tight_layout is enabled, is re-inforced
        if self.state.tight:
            self.state.fig.tight_layout()

        return pcm
