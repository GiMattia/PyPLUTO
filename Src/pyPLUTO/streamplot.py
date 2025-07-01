import warnings
from typing import Any

import numpy as np
from matplotlib.collections import LineCollection
from numpy.typing import NDArray

from .colorbar import ColorbarManager
from .delegator import delegator
from .imagestate import ImageState
from .imagetools import ImageToolsManager
from .inspector import track_kwargs
from .range import RangeManager
from .set_axis import AxisManager


@delegator("state")
class StreamplotManager:

    exposed_methods = ("streamplot",)

    def __init__(self, state: ImageState):
        self.state = state

        self.AxisManager = AxisManager(state)
        self.ColorbarManager = ColorbarManager(state)
        self.ImageToolsManager = ImageToolsManager(state)
        self.RangeManager = RangeManager(state)

    @track_kwargs
    def streamplot(
        self,
        var1: NDArray[np.generic],
        var2: NDArray[np.generic],
        check: bool = True,
        **kwargs: Any,
    ) -> LineCollection:
        """Plots a streamplot of a vector field. The function uses the
        streamplot function from matplotlib.pyplot.

        Returns
        -------
        - strm: LineCollection
            The streamplot of the given vector field.

        Parameters
        ----------
        - alpha: float, default 1.0
            Sets the opacity of the plot, where 1.0 means total opaque and 0.0
            means total transparent.
        - arrowsize: float, default 1.0
            Sets the size of the arrows of the streamline.
        - arrowstyle: str, default '-|>'
            Sets the style of the arrows of the streamline.
        - aspect: {'auto', 'equal', float}, default 'auto'
            Sets the aspect ratio of the plot. The 'auto' keyword is the default
            option (most likely the plot will be squared). The 'equal' keyword
            will set the same scaling for x and y. A float will fix the ratio
            between the y-scale and the x-scale (1.0 is the same as 'equal').
        - ax: axis object
            The axis where to plot the streamlines. If not given, the last
            considered axis will be used.
        - brokenlines: bool, default True
            Splits the streamlines in shorter segments.
        - c: str, default self.color
            Determines the streamplot color. If not defined, the program will
            loop over an array of 6 color which are different for the most
            common vision deficiencies.
        - cmap: str, default 'hot'
            Selects the colormap. If not defined, the colormap 'hot' will be
            adopted. Some useful colormaps are: plasma, magma, seismic. Please
            avoid using colorbars like jjet or rainbow, which are not
            perceptively uniform and not suited for people with vision
            deficiencies.
            All the colormap available are listed in the following link:
            https://matplotlib.org/stable/tutorials/colors/colormaps.html
        - cpos: {'top','bottom','left','right'}, default None
            Enables the colorbar (if defined), default position on the right.
        - cscale: {'linear','log','symlog','twoslope'}, default 'linear'
            Sets the colorbar scale. Default is the linear ('norm') scale.
        - density: float, default 1.0
            Sets the density and closeness of the streamlines. The domain is
            divided in a 30x30 grid. When set as default, each cells contains at
            most a number of crossing streamplot line equal to this keyword.
        - extend: {'neither','both','min','max'}, default 'neither'
            Sets the extension of the triangular colorbar extension.
        - extendrect: bool, default False
            If True, the colorbar extension will be rectangular.
        - fontsize: float, default 17.0
            Sets the fontsize for all the axis components (only for the current
            axis).
        - grid: bool, default False
            Enables/disables the grid on the plot.
        - integration_direction: {'forward', 'backward', 'both'}, default:'both'
            Sets the streamlines integration in the forward direction, backward
            direction, or both.
        - labelsize: float, default fontsize
            Sets the labels fontsize (which is the same for both labels).
            The default value corresponds to the value of the keyword
            'fontsize'.
        - lw: float, default 1.0
            Sets the width of the streamlines.
        - maxlength: float, default 5.0
            Sets the maximum length of a streamline in coordinates units.
        - minlength: float, default 0.1
            Sets the minimum length of a streamline in coordinates units.
        - minorticks: str, default None
            If not None enables the minor ticks on the plot (for both grid
            axes).
        - start_points: np.ndarray, default None
            Sets the starting points of the streamlines, if a more controlled
            plot is wanted.
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
            necessary (e.g. in case of highly customized variables and plots)
        - tresh: float, default max(abs(vmin),vmax)*0.01
            Sets the threshold for the colormap. If not defined, the threshold
            will be set to 1% of the maximum absolute value of the variable.
            The default cases are the following:
            - twoslope colorscale: sets the limit between the two linear
            regimes.
            - symlog: sets the limit between the logaitrhmic and the linear
            regime.
        - var1 (not optional): np.ndarray
            The x1-component of the vector field.
        - var2 (not optional): np.ndarray
            The x2-component of the vector field.
        - vmax: float
            The maximum value of the vector field norm.
        - vmin: float
            The minimum value of the vector field norm.
        - x1: np.ndarray
            The x-axis variable.
        - x2: np.ndarray
            The y-axis variable.
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

        Notes
        -----
        - None

        ----

        Examples
        --------
        - Example #1: Plot a streamplot of a vector field

            >>> I.streamplot(D.Bx1, D.Bx2)

        """
        kwargs.pop("check", check)

        if np.shape(var1) != np.shape(var2):
            raise ValueError("The shapes of the variables are different.")

        # Set or create figure and axes
        ax, nax = self.ImageToolsManager.assign_ax(
            kwargs.pop("ax", None), **kwargs
        )

        if self.state.fig is None:
            raise ValueError(
                "No figure is present. Please create a figure first."
            )

        x = np.asarray(kwargs.get("x1", np.arange(len(var1[:, 0]))))
        y = np.asarray(kwargs.get("x2", np.arange(len(var1[0, :]))))

        # Keyword x1 and x2
        varx, vary = (
            np.array(var2.T, dtype=float, copy=True),
            np.array(var1.T, dtype=float, copy=True),
        )
        if kwargs.get("transpose", False) is True:
            varx, vary = varx.T, vary.T

        fieldmod = np.sqrt(varx**2 + vary**2)
        vmax = kwargs.get("vmax", np.nanmax(fieldmod))
        vmin = kwargs.get("vmin", np.nanmin(fieldmod))

        # Apply the masks to set the corresponding elements
        # in varx and vary to NaN
        mask = np.logical_or(fieldmod > vmax, fieldmod < vmin)
        varx[mask] = vary[mask] = np.nan

        # Set ax parameters
        self.AxisManager.set_axis(ax=ax, check=False, **kwargs)
        self.ImageToolsManager.hide_text(nax, ax.texts)

        # Keyword for colorbar and colorscale
        color = kwargs.get("c")
        cmap = kwargs.get("cmap")
        cpos = kwargs.get("cpos")
        cscale = kwargs.get("cscale", "norm")
        tresh = kwargs.get("tresh", max(np.abs(vmin), vmax) * 0.01)
        lint = kwargs.get("lint")

        if "colors" in kwargs and "cmap" in kwargs:
            warn = "Both colors and cmap are defined. Using c."
            warnings.warn(warn)

        # Set the lines properties
        linewidth = kwargs.get("lw", 1)
        density = kwargs.get("density", 1)
        arrowstyle = kwargs.get("arrowstyle", "-|>")
        arrowsize = kwargs.get("arrowsize", 1)
        minlength = kwargs.get("minlength", 0.1)
        integration_direction = kwargs.get("integration_direction", "both")
        start_points = kwargs.get("start_points")
        maxlength = kwargs.get("maxlength", 5)
        broken_streamlines = kwargs.get("brokenlines", True)

        # Set the colorbar scale (put in function)
        norm = self.ImageToolsManager.set_cscale(
            cscale, vmin, vmax, tresh, lint
        )

        # Plot the streamplot
        strm = ax.streamplot(
            x,
            y,
            vary,
            varx,
            norm=norm,
            cmap=cmap,
            color=color,
            linewidth=linewidth,
            density=density,
            arrowsize=arrowsize,
            minlength=minlength,
            maxlength=maxlength,
            start_points=start_points,
            arrowstyle=arrowstyle,
            integration_direction=integration_direction,
            broken_streamlines=broken_streamlines,
        )

        if cpos is not None:
            self.ColorbarManager.colorbar(strm.lines, check=False, **kwargs)

        # If tight_layout is enabled, is re-inforced
        if self.state.tight:
            self.state.fig.tight_layout()

        del varx, vary

        return strm.lines
