"""PlotManager class."""

from __future__ import annotations

from typing import Unpack

import numpy as np
from matplotlib.axes import Axes
from numpy.typing import ArrayLike

from pyPLUTO.imagefuncs.imagetools import ImageToolsManager
from pyPLUTO.imagefuncs.legend import LegendManager
from pyPLUTO.imagefuncs.range import RangeManager
from pyPLUTO.imagefuncs.set_axis import AxisManager
from pyPLUTO.imagekwargs import PlotKwargs
from pyPLUTO.imagemixin import ImageMixin
from pyPLUTO.imagestate import ImageState
from pyPLUTO.utils.inspector import track_kwargs


class PlotManager(ImageMixin):
    """PlotManager class.

    It provides methods to create and manage plots in the
    image. It is designed to work with the Image class and allows for dynamic
    creation of plots based on the current state of the image. The class uses
    the AxisManager, ImageToolsManager, LegendManager, and RangeManager to
    handle the display and plotting of the images, axes, legends, and ranges,
    respectively.
    """

    def __init__(self, state: ImageState) -> None:
        """Initialize the PlotManager with the given state."""
        self.state = state
        self.AxisManager = AxisManager(state)
        self.ImageToolsManager = ImageToolsManager(state)
        self.LegendManager = LegendManager(state)
        self.RangeManager = RangeManager(state)

    @track_kwargs
    def plot(
        self,
        x: ArrayLike,
        y: ArrayLike | None = None,
        ax: Axes | list[Axes] | int | None = None,
        _check: bool = True,
        **kwargs: Unpack[PlotKwargs],
    ) -> None:
        """Creation of a 1D function plot (or a 1D slice plot).

        This function plots a 1D function or a 1D slice. It creates a
        simple figure and a single axis if none are given prior. If a single
        function argument is given, it plots the graph of that function using
        a linear variable as x parameter. However, if a pair of arrays is
        provided, it plots the second as a function of the first one.

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
            Determines the color. If not defined, the program will loop
            over an array of 6 colors which are different for the most common
            vision deficiencies.
        - edgecolor: list[str], default [None]
            Sets the edge color of the legend. The default value is black
            ('k').
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
        - wratio: [float], default [1.0]
            Ratio between the columns of the plot. The default is that every
            plot column has the same width.
        - wspace: [float], default []
            The space between plot columns (in figure units). If not enough or
            too many spaces are considered, the program will remove the excess
            and fill the lacks with [0.1].
        - x (not optional): 1D array
            This is the x-axis variable. If y is not defined, then this becomes
            the y-axis variable.
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
        - y: 1D array, default [None]
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
        - None

        Examples
        --------
        - Example #1: create a simple plot of y as function of x

            >>> import pyPLUTO as pp
            >>> I = pp.Image()
            >>> I.plot(x, y)

        - Example #2: create a plot of y as function of x with custom range of
            the axes and titles

            >>> import pyPLUTO as pp
            >>> I = pp.Image()
            >>> I.plot(x, y, xrange = [0,100], yrange = [0.0,1.0],
                title = 'y in function of x', xtitle = 'x', ytitle = 'y')

        - Example #3: create a plot with logarithmic scale on y-axis

            >>> import pyPLUTO as pp
            >>> I = pp.Image()
            >>> I.plot(x, y, yscale="log")

        - Example #4: create a plot with a legend and custom ticks on x-axis

            >>> import pyPLUTO as pp
            >>> I = pp.Image()
            >>> I.plot(x, y, label = 'y', legpos = 'lower right',
                xticks = [0.2,0.4,0.6,0.8])

        - Example #5: create plots on already existing axes

            >>> import pypLUTO as pp
            >>> I = pp.Image()
            >>> I.create_axes(ncol=2)
            >>> I.plot(x, y, ax=I.ax[0])
            >>> I.plot(x, y * y, ax=I.ax[1])
            >>> I.plot(x, z, ax=I.ax[0])

        """
        # If only one argument is given, it is the y-axis
        if y is None:
            y = np.asarray(x, dtype=float)
            x = np.arange(y.size, dtype=float)
        else:
            # Convert x and y in numpy arrays
            x = np.asarray(x, dtype=float)
            y = np.asarray(y, dtype=float)

        if self.state.fig is None:
            raise ValueError(
                "No figure is present. Please create a figure first."
            )

        # Set or create figure and axes
        ax, nax = self.ImageToolsManager.assign_ax(ax, _check=False, **kwargs)

        # Set ax parameters
        self.AxisManager.set_axis(ax=ax, _check=False, **kwargs)
        self.ImageToolsManager.hide_text(nax, ax.texts)

        # Keyword xrange and yrange
        self.RangeManager.set_xrange(
            ax,
            nax,
            [np.nanmin(x), np.nanmax(x)],
            self.state.setax[nax],
        )
        self.RangeManager.set_yrange(
            ax,
            nax,
            [np.nanmin(y), np.nanmax(y)],
            self.state.setay[nax],
            data=(x.astype(np.float64), y),
            #    x=x.astype(np.float64),
            #    y=y,
        )

        # Set color line and increase the number of lines (if default color)
        col_line = kwargs.get(
            "c", self.state.color[self.state.nline[nax] % len(self.state.color)]
        )
        if not kwargs.get("c"):
            self.state.nline[nax] = self.state.nline[nax] + 1

        # Start plotting procedure
        ax.plot(
            x,
            y,
            c=col_line,
            ls=kwargs.get("ls", "-"),
            lw=kwargs.get("lw", 1.3),
            marker=kwargs.get("marker", ""),
            ms=kwargs.get("ms", 3.0),
            label=kwargs.get("label", ""),
            fillstyle=kwargs.get("fillstyle", "full"),
        )

        # Creation of the legend
        self.state.legpos[nax] = kwargs.get("legpos", self.state.legpos[nax])
        if self.state.legpos[nax] is not None:
            copy_label = kwargs.get("label")
            kwargs["label"] = None
            self.LegendManager.legend(ax, _check=False, fromplot=True, **kwargs)
            kwargs["label"] = copy_label

        # If tight_layout is enabled, is re-inforced
        if self.state.tight:
            self.state.fig.tight_layout()

        # End of the function
