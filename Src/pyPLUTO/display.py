from typing import Any

import numpy as np
from matplotlib.collections import QuadMesh
from numpy.typing import ArrayLike

from .colorbar import ColorbarManager
from .delegator import delegator
from .imagestate import ImageState
from .imagetools import ImageToolsManager
from .inspector import track_kwargs
from .range import RangeManager
from .set_axis import AxisManager


@delegator("state")
class DisplayManager:
    """Class to manage the display of 2D plots in the image.

    This class provides methods to create and manage 2D plots using matplotlib's
    pcolormesh function. It allows for customization of the plot's appearance,
    colorbar, axes, and other properties."""

    exposed_methods = ("display",)

    def __init__(self, state: ImageState):
        """Initialize the DisplayManager with the given state."""
        self.state = state
        self.ColorbarManager = ColorbarManager(state)
        self.ImageToolsManager = ImageToolsManager(state)
        self.RangeManager = RangeManager(state)
        self.AxisManager = AxisManager(state)

    @track_kwargs
    def display(
        self,
        var: ArrayLike,
        check: bool = True,
        **kwargs: Any,
    ) -> QuadMesh:
        """Plot for a 2D function (or a 2D slice) using the matplotlib's
        pcolormesh function. A simple figure and a single axis can also be
        created.

        Returns
        -------
        - The 2D plot

        Parameters
        ----------
        - alpha: float, default 1.0
            Sets the transparency of the plot.
        - aspect: {'auto', 'equal', float}, default 'auto'
            Sets the aspect ratio of the plot.
            The 'auto' keyword is the default option (most likely the plot will
            be squared). The 'equal' keyword will set the same scaling for
            x and y. A float will fix the ratio between the y-scale and the
            x-scale (1.0 is the same as 'equal').
        - ax: ax | int | None, default None
            The axis where to plot the lines. If None, a new axis is created.
            If 'old', the last considered axis will be used.
        - bottom: float, default 0.1
            The space from the bottom border to the plot.
        - clabel: str, default None
            Sets the label of the colorbar.
        - cmap: str, default 'plasma'
            Selects the colormap. If not defined, the colormap 'plasma' will be
            adopted. Some useful colormaps are: plasma, magma, seismic. Please
            avoid using colorbars like jet or rainbow, which are not
            perceptively uniform and not suited for people with vision
            deficiencies.
        - cpad: float, default 0.07
            Fraction of original axes between colorbar and the axes (in case cax
            is not defined).
        - cpos: {'top','bottom','left','right'}, default None
            Enables the colorbar (if defined), default position on the right.
        - cscale: {'linear','log','symlog','twoslope'}, default 'linear'
            Sets the colorbar scale. Default is the linear ('norm') scale.
        - cticks: {[float], None}, default None
            If enabled (and different from None), sets manually ticks on the
            colorbar.
        - ctickslabels: str, default None
            If enabled, sets manually ticks labels on the colorbar.
        - extend: {'neither','both','min','max'}, default 'neither'
            Sets the extension of the triangular colorbar extension.
        - extendrect: bool, default False
            If True, the colorbar extension will be rectangular.
        - figsize: [float, float], default [6*sqrt(ncol),5*sqrt(nrow)]
            Sets the figure size. The default value is computed from the number
            of rows and columns.
        - fontsize: float, default 17.0
            Sets the fontsize for all the axes.
        - grid: Bool, default False
            Enables the grid on the plot.
        - labelsize: float, default fontsize
            Sets the labels fontsize (which is the same for both labels).
            The default value corresponds to the value of the keyword
            'fontsize'.
        - left: float, default 0.125
            The space from the left border to the plot.
        - minorticks: str, default None
            If not None enables the minor ticks on the plot (for both grid
            axes).
        - proj: str, default None
            Custom projection for the plot (e.g. 3D). Recommended only if
            needed.
            This keyword should be used only if the axis is created.
            WARNING: pyPLUTO does not support 3D plotting for now, only 3D axes.
            The 3D plot feature will be available in future releases.
        - right: float, default 0.9
            The space from the right border to the plot.
        - shading: {'flat,'nearest','auto','gouraud'}, default 'auto'
            The shading between the grid points. If not defined, the shading
            will one between 'flat' and 'nearest' depending on the size of the
            x,y and z arrays. The 'flat' shading works only if, given a NxM
            z-array, the x- and y-arrays have sizes of, respectively, N+1 and
            M+1. All the other shadings require a N x-array and a M y-array.
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
            The space from the top border to the plot.
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
        - var (not optional): 2D array
            The array to be plotted.
        - vmax: float, default max(var)
            The maximum value of the colormap. If not defined, the maximum value
            of z will be taken.
        - vmin: float, default min(var)
            The minimum value of the colormap. If not defined, the minimum value
            of z will be taken.
        - x1: np.ndarray, default 'Default'
            the 'x' array. If not defined, a default array will be generated
            depending on the size of z.
        - x2: np.ndarray, default 'Default'
            the 'y' array. If not defined, a default array will be generated
            depending on the size of z.
        - xrange: [float, float], default 'Default'
            Sets the range in the x-direction. If not defined or set to
            'Default' the code will compute the range while plotting the data by
            taking the minimum and the maximum values of the x1-array.
        - xscale: {'linear','log'}, default 'linear'
            If enabled (and different from 'Default'), sets automatically the
            scale on the x-axis. Data in log scale should be used with the
            keyword 'log', while data in linear scale should be used with the
            keyword 'linear'.
        - xticks: [float] | None | bool, default True
            If enabled (and different from 'Default'), sets manually ticks on
            x-axis. In order to completely remove the ticks the keyword should
            be used with None.
        - xtickslabels: [str] | None | bool, default True
            If enabled (and different from 'Default'), sets manually the ticks
            labels on the x-axis. In order to completely remove the ticks the
            keyword should be used with None. Note that fixed tickslabels should
            always correspond to fixed ticks.
        - xtitle: str, default None
            Sets and places the label of the x-axis.
        - yrange: [float, float], default 'Default'
            Sets the range in the y-direction. If not defined or set to
            'Default' the code will compute the range while plotting the data by
            taking the minimum and the maximum values of the x2-array.
        - yscale: {'linear','log'}, default 'linear'
            If enabled (and different from 'Default'), sets automatically the
            scale on the y-axis. Data in log scale should be used with the
            keyword 'log', while data in linear scale should be used with the
            keyword 'linear'.
        - yticks: [float] | None | bool, default True
            If enabled (and different from 'Default'), sets manually ticks on
            y-axis. In order to completely remove the ticks the keyword should
            be used with None.
        - ytickslabels: [float] | None | bool, default True
            If enabled (and different from 'Default'), sets manually the ticks
            labels on the y-axis. In order to completely remove the ticks the
            keyword should be used with None. Note that fixed tickslabels should
            always correspond to fixed ticks.
        - ytitle: str, default None
            Sets and places the label of the y-axis.

        ----

        Examples
        --------
        - Example #1: create a simple 2d plot with title and colorbar on the
            right

            >>> import pyPLUTO as pp
            >>> I = pp.Image()
            >>> I.display(var, title = 'title', cpos = 'right')

        - Example #2: create a 2d plot with title on the axes, bottom colorbar
            and custom shading

            >>> import pyPLUTO as pp
            >>> I = pp.Image()
            >>> I.display(x1, x2, var, xtitle = 'x', ytitle = 'y',
                    cpos = 'bottom', shading = 'gouraud', cpad = 0.3)

        - Example #3: create a 2d plot con custom range on axes and logarithmic
            scale colorbar

            >>> import pyPLUTO as pp
            >>> I = pp.Image()
            >>> I.display(var, xrange = [2,3], yrange = [2,4], cbar = 'right',
                        cscale = 'log')

        - Example #4: create a 2d plot with a custom symmetric logarithmic
            colorbar with custom ticks.

            >>> import pyPLUTO as pp
            >>> I = pp.Image()
            >>> I.display(var, cpos = 'right', cmap = 'RdBu_r',
                        cscale = 'symlog', tresh = 0.001, vmin = -1, vmax = 1)

        """
        kwargs.pop("check", check)

        # Set or create figure and axes
        ax, nax = self.ImageToolsManager.assign_ax(
            kwargs.pop("ax", None), **kwargs
        )

        if self.state.fig is None:
            raise ValueError(
                "No figure is present. Please create a figure first."
            )
        # Keyword x1 and x2
        var = np.asarray(var)
        if kwargs.get("transpose", False) is True:
            var = var.T
        x = np.asarray(kwargs.get("x1", np.arange(len(var[:, 0]) + 1)))
        y = np.asarray(kwargs.get("x2", np.arange(len(var[0, :]) + 1)))

        # Keywords xrange and yrange
        if not kwargs.get("xrange") and not self.state.setax[nax] == 1:
            kwargs["xrange"] = [x.min(), x.max()]
        if not kwargs.get("yrange") and not self.state.setay[nax] == 1:
            kwargs["yrange"] = [y.min(), y.max()]
        # Set ax parameters
        self.AxisManager.set_axis(ax=ax, check=False, **kwargs)
        self.ImageToolsManager.hide_text(nax, ax.texts)

        # Keywords vmin and vmax
        vmin = kwargs.get("vmin", np.nanmin(var))
        vmax = kwargs.get("vmax", np.nanmax(var))

        # Keyword for colorbar and colorscale
        cpos = kwargs.get("cpos")
        cscale = kwargs.get("cscale", "norm")
        tresh = kwargs.get("tresh", max(np.abs(vmin), vmax) * 0.01)
        lint = kwargs.get("lint")
        self.state.vlims[nax] = [vmin, vmax, tresh]

        # Set the colorbar scale (put in function)
        norm = self.ImageToolsManager.set_cscale(
            cscale, vmin, vmax, tresh, lint
        )

        # Select shading
        shade = kwargs.get("shading", "auto")
        alpha = kwargs.get("alpha", 1.0)

        # Display the image
        pcm = ax.pcolormesh(
            x,
            y,
            var.T,
            shading=shade,
            cmap=kwargs.get("cmap", "plasma"),
            norm=norm,
            linewidth=0,
            rasterized=True,
            alpha=alpha,
        )

        # Place the colorbar (use colorbar function)
        if cpos is not None:
            self.ColorbarManager.colorbar(pcm, check=False, **kwargs)

        # If tight_layout is enabled, is re-inforced
        if self.state.tight:
            self.state.fig.tight_layout()

        return pcm
