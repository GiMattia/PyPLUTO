from typing import Any

import numpy as np
from matplotlib.collections import PathCollection
from numpy.typing import NDArray

from .colorbar import ColorbarManager
from .delegator import delegator
from .imagestate import ImageState
from .imagetools_new import ImageToolsManager
from .inspector import track_kwargs
from .legend import LegendManager
from .range import RangeManager
from .set_axis import AxisManager


@delegator("state")
class ScatterManager:

    exposed_methods = ("scatter",)

    def __init__(self, state: ImageState):
        self.state = state

        self.AxisManager = AxisManager(state)
        self.ColorbarManager = ColorbarManager(state)
        self.ImageToolsManager = ImageToolsManager(state)
        self.LegendManager = LegendManager(state)
        self.RangeManager = RangeManager(state)

    @track_kwargs
    def scatter(
        self,
        x: NDArray[np.generic] | list[float],
        y: NDArray[np.generic] | list[float],
        check: bool = True,
        **kwargs: Any,
    ) -> PathCollection:
        """Scatter plot for a 2D function (or a 2D slice) using the
        matplotlib's scatter function. A simple figure and a single axis can
        also be created.

        Returns
        -------
        - The scatter plot

        Parameters
        ----------
        - alpha: float, default 1.0
            Sets the transparency of the plot.
        - aspect: {'auto', 'equal', float}, default 'auto'
            Sets the aspect ratio of the plot. The 'auto' keyword is the default
            option (most likely the plot will be squared). The 'equal' keyword
            will set the same scaling for x and y. A float will fix the ratio
            between the y-scale and the x-scale (1.0 is the same as 'equal').
        - ax: axis object
        The axis where to plot the scatter. If not given, the last considered
        axis will be used.
        - c: str, default self.color
            Determines the scatter plot color. If not defined, the program will
            loop over an array of 6 color which are different for the most
            common vision deficiencies.
        - clabel: str, default None
            Sets the colorbar label.
        - cmap: str, default 'hot'
            Selects the colormap. If not defined, the colormap 'hot' will be
            adopted. Some useful colormaps are: plasma, magma, seismic. Please
            avoid using colorbars like jjet or rainbow, which are not
            perceptively uniform and not suited for people with vision
            deficiencies.

        - cpos: {'top','bottom','left','right'}, default None
            Enables the colorbar (if defined), default position on the right.
        - cscale: {'linear','log','symlog','twoslope'}, default 'linear'
            Sets the colorbar scale. Default is the linear ('norm') scale.
        - edgecolors: str, default None
            Enables a contouring color for the markers.
        - fontsize: float, default 17.0
            Sets the fontsize for all the axis components (only for the current
            axis).
        - grid: bool, default False
            Enables/disables the grid on the plot.
        - label: str, default None
            Associates a label to be used for the creation of the legend.
        - labelsize: float, default fontsize
            Sets the labels fontsize (which is the same for both labels).
            The default value corresponds to the value of the keyword
            'fontsize'.
        - legpos: int/str, default None
            If enabled, creates a legend. This keyword selects the legend
            location.
        - marker: {'o', 'v', '^', '<', '>', 'X', ' ', etc.}, default ' '
            Sets an optional symbol for every point. The default value is no
            marker (' ').
        - minorticks: str, default None
            If not None enables the minor ticks on the plot (for both grid
            axes).
        - ms: float, default 3
            Sets the marker size.
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
        - tresh: float, default max(abs(vmin),vmax)*0.01
            Sets the threshold for the colormap. If not defined, the threshold
            will
            be set to 1% of the maximum absolute value of the variable.
            The default cases are the following:
            - twoslope colorscale: sets the limit between the two linear
            regimes.
            - symlog: sets the limit between the logaitrhmic and the linear
            regime.
        - vmax: float
            The maximum value of the colormap.
        - vmin: float
            The minimum value of the colormap.
        - x (not optional): 1D array
            The x-axis variable.
        - xrange: [float, float], default 'Default'
            Sets the range in the x-direction. If not defined or set to
            'Default' the code will compute the range while plotting the data by
            taking the minimum and the maximum values of the x1-array.
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
        - y (not optional): 1D array
            The y-axis variable.
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

        Notes
        -----
        - The scatter with legend is still preliminary

        ----

        Examples
        --------
        - Example #1: Plot a scatter plot of a variable

            >>> I.scatter(x, y)

        - Example #2: Plot a scatter plot of a variable with a colorbar

            >>> I.scatter(x, y, cmap = 'hot', c = x**2 + y**2,cpos = 'right')

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
        if not kwargs.get("xrange") and not self.state.setax[nax] == 1:
            kwargs["xrange"] = [x.min(), x.max()]
        if not kwargs.get("yrange") and not self.state.setay[nax] == 1:
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
        norm = self.ImageToolsManager.set_cscale(cscale, vmin, vmax, tresh)

        # Start scatter plot procedure
        pcm = ax.scatter(
            x,
            y,
            cmap=kwargs.get("cmap"),
            norm=norm,
            c=kwargs.get("c"),
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
