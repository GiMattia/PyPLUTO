from typing import Any

import numpy as np
from numpy.typing import ArrayLike

from .delegator import delegator
from .imagestate import ImageState
from .imagetools import ImageToolsManager
from .inspector import track_kwargs
from .legend import LegendManager
from .range import RangeManager
from .set_axis import AxisManager


@delegator("state")
class PlotManager:

    exposed_methods = ("plot",)

    def __init__(self, state: ImageState):
        self.state = state
        self.AxisManager = AxisManager(state)
        self.ImageToolsManager = ImageToolsManager(state)
        self.LegendManager = LegendManager(state)
        self.RangeManager = RangeManager(state)

    @track_kwargs
    def plot(
        self,
        x: ArrayLike | list[float],
        y: ArrayLike | list[float] | None = None,
        check: bool = True,
        **kwargs: Any,
    ) -> None:
        """Creation of a 1D function plot (or a 1D slice plot). It creates a
        simple figure and a single axis if none are given prior. If a single
        function argument is given, it plots the graph of that function using
        a linear variable as x parameter. However, if a pair of arrays is
        provided, it plots the second as a function of the first one.

        Returns
        -------
        - None

        Parameters
        ----------
        - alpha: float, default 1.0
            Sets the opacity of the plot, where 1.0 means total opaque and 0.0
            means total transparent.
        - aspect: 'auto' | 'equal' | float, default 'auto'
            Sets the aspect ratio of the plot.
            The 'auto' keyword is the default option (most likely the plot will
            be squared). The 'equal' keyword will set the same scaling for x and
            y. A float will fix the ratio between the y-scale and the x-scale
            (1.0 is the same as 'equal').
        - ax: ax | int | None, default None
            The axis where to plot the lines. If None, a new axis is created or
            the last axis is selected.
        - bottom: float, default 0.1
            The space from the bottom border to the last row of plots.
        - c: str, default self.color
            Determines the line color. If not defined, the program will loop
            over an array of 10 color which are different for the most common
            vision deficiencies.
        - figsize: [float, float], default [8,5]
            Sets the figure size. The default value is computed from the number
            of rows and columns.
        - fillstyle: {'full', 'left', 'right', 'bottom', 'top', 'none'},
                    default 'full'
            Sets the marker filling. The default value is the fully filled
            marker ('full').
        - fontsize: float, default 17.0
            Sets the fontsize for all the axes.
        - grid: bool, default False
            If enabled, creates a grid on the plot.
        - label: str, default None
            Associates a label to each line. Such labels will be used for the
            creation of the legend.
        - labelsize: float, default fontsize
            Sets the labels fontþsize (which is the same for both labels).
            The default value corresponds to the value of the keyword
            'fontsize'.
        - legalpha: float, default 0.8
            Sets the opacity of the legend.
        - left: float, default 0.125
            The space from the left border to the leftmost column of plots.
        - legcols: int, default 1
            Sets the number of columns that the legend should have.
        - legpad: float, default 0.8
            Sets the space between the lines (or symbols) and the correspondibg
            text in the legend.
        - legpos: int | str, default None
            If enabled, creates a legend. This keyword selects the legend
            location.
        - legsize: float, default fontsize
            Sets the fontsize of the legend. The default value is the default
            fontsize value.
        - legspace: float, default 2
            Sets the space between the legend columns, in font-size units.
        - ls: {'-', '--', '-.', ':', ' ', ect.}, default '-'
            Sets the linestyle. The choices available are the ones defined in
            the matplotlib package. Here are reported the most common ones.
        - lw: float, default 1.3
            Sets the linewidth of each line.
        - marker: {'o', 'v', '^', '<', '>', 'X', ' ', etc.}, default ' '
            Sets an optional symbol for every point. The default value is no
            marker (' ').
        - minorticks: str, default None
            If not None enables the minor ticks on the plot (for both grid
            axes).
        - ms: float, default 3
            Sets the marker size.
        - mscale: fload, default 1.0
            Sets the marker size scale in the legend.
        - proj: str, default None
            Custom projection for the plot (e.g. 3D). Recommended only if
            needed. This keyword should be used only if the axis is created.
            WARNING: pyPLUTO does not support 3D plotting for now, only 3D axes.
            The 3D plot feature will be available in future releases.
        - right: float, default 0.9
            The space from the right border to the rightmost column of plots.
        - ticksdir: {'in', 'out'}, default 'in'
            Sets the ticks direction. The default option is 'in'.
        - tickssize: float, default fontsize
            Sets the ticks fontsize (which is the same for both grid axes).
            The default value corresponds to the value of the keyword
            'fontsize'.
        - title: str, default None
            Places the title of the plot on top of it.
        - titlesize: float, default fontsize
            Sets the title fontsize. The default value corresponds to the value
            of the keyword 'fontsize'.
        - top: float, default 0.9
            The space from the top border to the first row of plots.
        - x (not optional): 1D array
            This is the x-axis variable. If y is not defined, then this becomes
            the y-axis variable.
        - xrange: [float, float], default 'Default'
            Sets the range in the x-direction. If not defined or set to
            'Default', the code will compute the range while plotting the data
            by taking the minimum and the maximum values of the x-array. In case
            of multiple lines, the code will also adapt to the previous ranges.
        - xscale: {'linear','log'}, default 'linear'
            If enabled (and different from default), sets automatically the
            scale on the x-axis. Data in log scale should be used with the
            keyword 'log', while data in linear scale should be used with the
            keyword 'linear'.
        - xticks: [float] | None | bool, default True
            If enabled (and different from True), sets manually ticks on
            x-axis. In order to completely remove the ticks the keyword should
            be used with None.
        - xtickslabels: [str] | None | bool, default True
            If enabled (and different from True), sets manually the ticks
            labels on the x-axis. In order to completely remove the ticks the
            keyword should be used with None. Note that fixed tickslabels should
            always correspond to fixed ticks.
        - xtitle: str, default None
            Sets and places the label of the x-axis.
        - y: 1D array, default [None]
            The y-axis variable.
        - yrange: [float, float], default 'Default'
            Sets the range in the y-direction. If not defined or set to
            'Default' the code will compute the range while plotting the data by
            taking the minimum and the maximum values of the y-array. In case of
            multiple lines, the code will also adapt to the previous ranges. It
            also adds a small offset.
        - yscale: {'linear','log'}, default 'linear'
            If enabled (and different from True), sets automatically the scale
            on the y-axis. Data in log scale should be used with the keyword
            'log', while data in linear scale should be used with the keyword
            'linear'.
        - yticks: [float] | None | bool, default True
            If enabled (and different from True), sets manually ticks on
            y-axis. In order to completely remove the ticks the keyword should
            be used with None.
        - ytickslabels: [str] | None | bool, default True
            If enabled (and different from True), sets manually the ticks
            labels on the y-axis. In order to completely remove the ticks the
            keyword should be used with None. Note that fixed tickslabels should
            always correspond to fixed ticks.
        - ytitle: str, default None
            Sets and places the label of the y-axis.

        Notes
        -----
        - Minorticks on single axis will be added in future releases.

        ----

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
            ... title = 'y in function of x', xtitle = 'x', ytitle = 'y')
            ...

        - Example #3: create a plot with logarithmic scale on y-axis

            >>> import pyPLUTO as pp
            >>> I = pp.Image()
            >>> I.plot(x, y, yscale = 'log')

        - Example #4: create a plot with a legend and custom ticks on x-axis

            >>> import pyPLUTO as pp
            >>> I = pp.Image()
            >>> I.plot(x, y, label = 'y', legpos = 'lower right',
            ... xticks = [0.2,0.4,0.6,0.8])
            ...

        - Example #5: create plots on already existing axes

            >>> import pypLUTO as pp
            >>> I = pp.Image()
            >>> I.create_axes(ncol = 2)
            >>> I.plot(x, y, ax = I.ax[0])
            >>> I.plot(x, y*y, ax = I.ax[1])
            >>> I.plot(x, z, ax = I.ax[0])

        """
        kwargs.pop("check", check)

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
        ax, nax = self.ImageToolsManager.assign_ax(
            kwargs.pop("ax", None), **kwargs
        )

        # Set ax parameters
        self.AxisManager.set_axis(ax=ax, check=False, **kwargs)
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
            x=x.astype(np.float64),
            y=y,
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
            copy_label: str | None = kwargs.get("label")
            kwargs["label"] = None
            self.LegendManager.legend(ax, check=False, fromplot=True, **kwargs)
            kwargs["label"] = copy_label

        # If tight_layout is enabled, is re-inforced
        if self.state.tight:
            self.state.fig.tight_layout()

        # End of the function
