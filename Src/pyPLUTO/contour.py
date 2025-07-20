import warnings
from typing import Any

import numpy as np
from matplotlib.contour import QuadContourSet
from numpy.typing import NDArray

from .colorbar import ColorbarManager
from .delegator import delegator
from .imagestate import ImageState
from .imagetools import ImageToolsManager
from .inspector import track_kwargs
from .range import RangeManager
from .set_axis import AxisManager


@delegator("state")
class ContourManager:
    """Class to manage contour plots in the image.

    This class provides methods to create contour plots of variables in the
    image class. It allows for customization of the contour lines, colorbars,
    and other properties."""

    exposed_methods = ("contour",)

    def __init__(self, state: ImageState):
        """Initialize the ContourManager with the given state."""
        self.state = state
        self.AxisManager = AxisManager(state)
        self.ColorbarManager = ColorbarManager(state)
        self.ImageToolsManager = ImageToolsManager(state)
        self.RangeManager = RangeManager(state)

    @track_kwargs
    def contour(
        self, var: NDArray[np.generic], _check: bool = True, **kwargs: Any
    ) -> QuadContourSet:
        """Plots a contour plot of a given variable. The function uses the
        matplotlib.pyplot.contour function. The function returns None.

        Returns
        -------
        - cnt: LineCollection
            The set of contour lines of the given variable.

        Parameters
        ----------
        - alpha: float, default 1.0
            Sets the transparency of the contour lines.
        - aspect: {'auto', 'equal', float}, default 'auto'
            Sets the aspect ratio of the plot. The 'auto' keyword is the default
            option (most likely the plot will be squared). The 'equal' keyword
            will set the same scaling for x and y. A float will fix the ratio
            between the y-scale and the x-scale (1.0 is the same as 'equal').
        - ax: {ax object, 'old', None}, default None
            The axis where to plot the lines. If None, a new axis is created.
            If 'old', the last considered axis will be used.
        - c: str, default self.color
            Determines the contour lines plot. If not defined, the program will
            loop over an array of 6 color which are different for the most
            common vision deficiencies.
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
        - extend: {'neither','both','min','max'}, default 'neither'
            Sets the extension of the triangular colorbar extension.
        - extendrect: bool, default False
            If True, the colorbar extension will be rectangular.
        - fontsize: float, default 17.0
            Sets the fontsize for all the axis components (only for the current
            axis).
        - grid: bool, default False
            Enables/disables the grid on the plot.
        - labelsize: float, default fontsize
            Sets the labels fontsize (which is the same for both labels).
            The default value corresponds to the value of the keyword
            'fontsize'.
        - levels: np.ndarray
            The levels of the contour lines.
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
        - transpose: True/False, default False
            Transposes the variable matrix. Use is not recommended if not really
            necessary (e.g. in case of highly customized variables and plots).
        - tresh: float, default max(abs(vmin),vmax)*0.01
            Sets the threshold for the colormap. If not defined, the threshold
            will be set to 1% of the maximum absolute value of the variable.
            The default cases are the following:
            - twoslope colorscale: sets the limit between the two linear
            regimes.
            - symlog: sets the limit between the logaitrhmic and the linear
            regime.
        - var (not optional): np.ndarray
            The variable to be plotted.
        - vmax: float
            The maximum value of the colormap.
        - vmin: float
            The minimum value of the colormap.
        - x1: 1D array, default 'Default'
            The 'x' array.
        - x2: 1D array, default 'Default'
            The 'y' array.
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
        - Example #1: Plot a contour plot of a variable

            >>> I.contour(D.rho, levels=10)

        """
        # kwargs.pop("check", _check)

        # Set or create figure and axes
        ax, nax = self.ImageToolsManager.assign_ax(
            kwargs.pop("ax", None), **kwargs
        )

        if self.state.fig is None:
            raise ValueError(
                "No figure is present. Please create a figure first."
            )

        # Keyword x1 and x2
        x = np.asarray(kwargs.get("x1", np.arange(len(var[:, 0]))))
        y = np.asarray(kwargs.get("x2", np.arange(len(var[0, :]))))

        # Transpose if needed
        var = np.asarray(var.T)
        if kwargs.get("transpose", False) is True:
            var = var.T

        # Set ax parameters
        self.AxisManager.set_axis(ax=ax, check=False, **kwargs)
        self.ImageToolsManager.hide_text(nax, ax.texts)

        # Keywords vmin and vmax
        vmin = kwargs.get("vmin", np.nanmin(var))
        vmax = kwargs.get("vmax", np.nanmax(var))

        # Sets levels for the contour plot
        levels = kwargs.get("levels", np.linspace(vmin, vmax, 10))

        # Keyword for colorbar and colorscale
        colors = kwargs.get("c")
        cmap = self.ImageToolsManager.find_cmap(kwargs.get("cmap"))
        cpos = kwargs.get("cpos")
        cscale = kwargs.get("cscale", "norm")
        tresh = kwargs.get("tresh", max(np.abs(vmin), vmax) * 0.01)
        lint = kwargs.get("lint")
        lw = kwargs.get("lw", 1.0)

        if "colors" in kwargs and "cmap" in kwargs:
            warn = "Both colors and cmap are defined. Using c."
            warnings.warn(warn)

        # Set the colorbar scale (put in function)
        norm = self.ImageToolsManager.set_cscale(
            cscale, vmin, vmax, tresh, lint
        )

        # Select shading
        alpha = kwargs.get("alpha", 1.0)

        # Plot the contour plot
        cnt = ax.contour(
            x,
            y,
            var,
            levels=levels,
            norm=norm,
            cmap=cmap,
            colors=colors,
            alpha=alpha,
            linewidths=lw,
        )

        if cpos is not None:
            self.ColorbarManager.colorbar(cnt, check=False, **kwargs)

        # If tight_layout is enabled, is re-inforced
        if self.state.tight:
            self.state.fig.tight_layout()

        return cnt
