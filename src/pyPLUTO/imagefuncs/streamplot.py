"""Module to manage the streamplot function from matplotlib.pyplot."""

import warnings
from typing import Any

import numpy as np
from matplotlib.collections import LineCollection
from numpy.typing import NDArray

from pyPLUTO.imagefuncs.colorbar import ColorbarManager
from pyPLUTO.imagefuncs.imagetools import ImageToolsManager
from pyPLUTO.imagefuncs.range import RangeManager
from pyPLUTO.imagefuncs.set_axis import AxisManager
from pyPLUTO.imagemixin import ImageMixin
from pyPLUTO.imagestate import ImageState
from pyPLUTO.utils.inspector import track_kwargs


class StreamplotManager(ImageMixin):
    """Manages the streamplot function from matplotlib.pyplot."""

    def __init__(self, state: ImageState) -> None:
        """Initialize the StreamplotManager with the given state."""
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
        """Plot a streamplot of a vector field.

        The function uses the streamplot function from matplotlib.pyplot.

        Parameters
        ----------
        - alpha: float, default 1.0
            Sets the opacity of the plot, where 1.0 is fully opaque and 0.0 is
            fully transparent.
        - arrowsize: float, default 1.0
            Sets the size of the arrows of the streamline.
        - arrowstyle: str, default '-|>'
            Sets the style of the arrows of the streamline.
        - aspect: 'auto' | 'equal' | float, default 'auto'
            Sets the aspect ratio of the plot. The 'auto' keyword is the
            default option. The 'equal' keyword sets the same scaling for x and
            y. A float fixes the ratio between the y-scale and the x-scale (1.0
            is the same as 'equal').
        - ax: ax | int | None, default None
            The axis where to plot. If None, the last considered axis will be used.
        - brokenlines: bool, default True
            Splits the streamlines in shorter segments.
        - c: str, default self.color
            Determines the color. If not defined, the program will loop over an
            array of 6 colors which are different for the most common vision
            deficiencies.
        - cmap: str, default 'hot'
            Selects the colormap. Some useful colormaps are: plasma, magma,
            seismic. Please avoid colormaps like jet or rainbow, which are not
            perceptively uniform and not suited for people with vision
            deficiencies.
        - cpos: {'top','bottom','left','right'}, default None
            Enables the colorbar and sets its position. If not defined, no
            colorbar is shown.
        - cscale: {'linear','log','symlog','twoslope'}, default 'linear'
            Sets the colorbar scale. Default is the linear ('norm') scale.
        - density: float, default 1.0
            Sets the density and closeness of the streamlines. The domain is
            divided in a 30x30 grid. When set as default, each cell contains at
            most a number of crossing streamplot line equal to this keyword.
        - extend: {'neither','both','min','max'}, default 'neither'
            Sets the extension of the triangular colorbar extension.
        - extendrect: bool, default False
            If True, the colorbar extension will be rectangular.
        - fontsize: float, default 17.0
            Sets the fontsize for all the axis components.
        - grid: bool | string, default False
            Enables/disables the grid on the plot. If True it enables both axes
            grids. If 'x' or 'y' it enables only the x- or y-axis grid.
        - integration_direction: {'forward', 'backward', 'both'}, default:'both'
            Sets the streamlines integration in the forward direction, backward
            direction, or both.
        - labelsize: float, default fontsize
            Sets the labels fontsize (which is the same for both labels). The
            default value corresponds to the value of the keyword 'fontsize'.
        - lw: float, default 1.3
            Sets the linewidth.
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
            Sets the ticks fontsize (which is the same for both grid axes). The
            default value corresponds to the value of the keyword 'fontsize'.
        - title: str, default None
            Places the title of the plot on top of it.
        - titlepad: float, default 8.0
            Sets the distance between the title and the top of the plot.
        - titlesize: float, default fontsize
            Sets the title fontsize. The default value corresponds to the value
            of the keyword 'fontsize'.
        - transpose: True/False, default False
            Transposes the variable matrix. Use is not recommended if not
            really necessary (e.g. in case of highly customized variables and
            plots).
        - tresh: float, default max(abs(vmin),vmax)*0.01
            Sets the threshold for the colormap (used with composite
            colorscales such as twoslope or symlog).
        - var1 (not optional): np.ndarray
            The x1-component of the vector field.
        - var2 (not optional): np.ndarray
            The x2-component of the vector field.
        - vmax: float
            The maximum value of the colormap.
        - vmin: float
            The minimum value of the colormap.
        - x1: np.ndarray, default 'Default'
            The x-axis array. If not defined, a default array will be
            generated.
        - x2: np.ndarray, default 'Default'
            The y-axis array. If not defined, a default array will be
            generated.
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

        - bottom: float, default varies
            The bottom limit of the axis / axes set. For the figure layout it
            is the space from the bottom border to the plot (default 0.1); for
            an inset zoom it is the bottom position of the inset (default 0.6 +
            height).
        - clabel: str, default None
            Sets the label of the colorbar.
        - cpad: float, default 0.07
            Fraction of original axes between colorbar and the axes (in axes
            units).
        - cticks: {[float], None}, default None
            If enabled (and different from None), sets manually the ticks on
            the colorbar.
        - ctickslabels: str, default None
            If enabled, sets manually ticks labels on the colorbar.
        - figsize: list[float], default varies
            Sets the figure size. The default is [6*sqrt(ncol), 5*sqrt(nrow)],
            computed from the number of rows and columns (or [8,5] for a single
            plot).
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
        - proj: str, default None
            Custom projection for the plot (e.g. 3D). Recommended only if
            needed. WARNING: pyPLUTO does not support 3D plotting for now, only
            3D axes. The 3D plot feature will be available in future releases.
        - right: float, default 0.9
            The right limit of the axis / axes set. For the figure layout it is
            the space from the right border to the plot; for an inset zoom it
            is the right position of the inset.
        - sharex: bool | str | Matplotlib axis, default False
            Enables/disables the sharing of the x-axis between the subplots.
        - sharey: bool | str | Matplotlib axis, default False
            Enables/disables the sharing of the y-axis between the subplots.
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
        - xlabelpad: float, default 4.0
            The padding between the x-axis label and the axis.
        - xtresh: float
            The threshold parameter for the x-axis symlog/asinh scale.
        - ylabelpad: float, default 4.0
            The padding between the y-axis label and the axis.
        - ytresh: float
            The threshold parameter for the y-axis symlog/asinh scale.

        Returns
        -------
        - LineCollection

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
        cmap = self.ImageToolsManager.find_cmap(kwargs.get("cmap"))
        cpos = kwargs.get("cpos")
        cscale = kwargs.get("cscale", "norm")
        tresh = kwargs.get("tresh", max(np.abs(vmin), vmax) * 0.01)
        lint = kwargs.get("lint")

        if "colors" in kwargs and "cmap" in kwargs:
            warn = "Both colors and cmap are defined. Using c."
            warnings.warn(warn, UserWarning, stacklevel=2)

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
