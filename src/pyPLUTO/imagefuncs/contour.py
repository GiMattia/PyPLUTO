"""Module for managing contour plots in image displays."""

from __future__ import annotations

import warnings
from typing import Unpack

import numpy as np
from matplotlib.axes import Axes
from matplotlib.contour import QuadContourSet
from numpy.typing import ArrayLike

from pyPLUTO.imagefuncs.colorbar import ColorbarManager
from pyPLUTO.imagefuncs.imagetools import ImageToolsManager
from pyPLUTO.imagefuncs.range import RangeManager
from pyPLUTO.imagefuncs.set_axis import AxisManager
from pyPLUTO.imagekwargs import ContourKwargs
from pyPLUTO.imagemixin import ImageMixin
from pyPLUTO.imagestate import ImageState
from pyPLUTO.utils.inspector import track_kwargs


class ContourManager(ImageMixin):
    """Class to manage contour plots in the image.

    This class provides methods to create contour plots of variables in the
    image class. It allows for customization of the contour lines, colorbars,
    and other properties.
    """

    def __init__(self, state: ImageState) -> None:
        """Initialize the ContourManager with the given state."""
        self.state = state
        self.AxisManager = AxisManager(state)
        self.ColorbarManager = ColorbarManager(state)
        self.ImageToolsManager = ImageToolsManager(state)
        self.RangeManager = RangeManager(state)

    @track_kwargs
    def contour(
        self,
        var: ArrayLike,
        ax: Axes | list[Axes] | int | None = None,
        _check: bool = True,
        **kwargs: Unpack[ContourKwargs],
    ) -> QuadContourSet:
        """Plot the contour lines of a 2D variable.

        The lines are drawn with matplotlib's contour. The variable is indexed
        as var[x, y], the PLUTO order, and is transposed on the way to
        matplotlib, which wants var[y, x]. The coordinates x1 and x2 are the
        points where the values sit, one per cell, so without them the lines
        are drawn on the cell indices.

        The lines are colored by the colormap, through the same color scales
        a map uses (cscale, vmin, vmax, tresh). The default colormap differs
        from the one of display, so lines drawn over a map stand out from it.
        A single color c replaces the colormap: matplotlib accepts only one of
        the two, so c wins over cmap, with a warning.

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
        - c: str | list[str], default None
            The color of the lines, or one color per level. If not defined,
            the lines are colored by the colormap. If given together with
            cmap, c is used and a warning is raised.
        - clabel: str, default None
            Sets the label of the colorbar.
        - cmap: str, default 'viridis'
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
        - extend: {'neither','both','min','max'}, default 'neither'
            Sets the extension of the triangular colorbar extension.
        - extendrect: bool, default False
            If True, the colorbar extension will be triangular.
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
        - levels: int | np.ndarray, default None
            The number of levels or the list of levels for the contours. If
            not defined, 10 levels are evenly spaced between vmin and vmax. An
            integer is a hint to matplotlib, which picks round values following
            the color scale (evenly spaced, or by decades with cscale='log').
            An array is used as it is.
        - lw: float, default 1.3
            Sets the linewidth.
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
        - sharex: bool | str | Matplotlib axis, default False
            Enables/disables the sharing of the x-axis between the subplots.
        - sharey: bool | str | Matplotlib axis, default False
            Enables/disables the sharing of the y-axis between the subplots.
        - sharexaxes: bool | int | 'all' | 'row' | 'col' | Axes, default False
            Shares the x-axis between the subplots: True or 'all' with the
            first of them, 'row' and 'col' within each row or column, an
            index with that axis of the image, an Axes with that axis.
        - shareyaxes: bool | int | 'all' | 'row' | 'col' | Axes, default False
            Shares the y-axis between the subplots, as sharexaxes does.
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
        - transpose: True/False, default False
            Declares the variable as var[y, x] instead of var[x, y]. Use is
            not recommended if not really necessary (e.g. in case of highly
            customized variables and plots).
        - tresh: float, default max(abs(vmin),vmax)*0.01
            Sets the threshold for the colormap (used with composite
            colorscales such as twoslope or symlog).
        - var (not optional): np.ndarray
            The variable to be plotted.
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
        - x1: np.ndarray, default 'Default'
            The x-axis array. If not defined, a default array will be
            generated.
        - x2: np.ndarray, default 'Default'
            The y-axis array. If not defined, a default array will be
            generated.
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
        - QuadContourSet

        Examples
        --------
        - Example #1: Plot a contour plot of a variable

            >>> I.contour(D.rho, levels=10)

        - Example #2: Black contour lines over a map of the same variable

            >>> I.display(D.rho, x1=D.x1, x2=D.x2, cpos="right")
            >>> I.contour(D.rho, x1=D.x1, x2=D.x2, c="k", levels=[0.5, 1.0])

        """
        if self.state.fig is None:
            raise ValueError(
                "No figure is present. Please create a figure first.",
            )

        # Set or create figure and axes
        ax, nax = self.ImageToolsManager.assign_ax(ax, _check=False, **kwargs)

        var = np.asarray(var)

        # Transpose first, so the default coordinates follow the drawn shape
        if kwargs.get("transpose", False) is True:
            var = var.T

        # Keyword x1 and x2
        x = np.asarray(kwargs.get("x1", np.arange(len(var[:, 0]))))
        y = np.asarray(kwargs.get("x2", np.arange(len(var[0, :]))))

        # matplotlib wants the variable as var[y, x]
        var = var.T

        # Set ax parameters
        self.AxisManager.set_axis(ax=ax, _check=False, **kwargs)
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
        lw = kwargs.get("lw", 1.3)

        # matplotlib accepts only one of the two, so c wins
        if "c" in kwargs and "cmap" in kwargs:
            warn = "Both c and cmap are defined. Using c."
            warnings.warn(warn, UserWarning, stacklevel=2)
            cmap = None

        # Set the colorbar scale (put in function)
        norm = self.ImageToolsManager.set_cscale(cscale, vmin, vmax, tresh)

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
            self.ColorbarManager.colorbar(cnt, _check=False, **kwargs)

        # If tight_layout is enabled, is re-inforced
        if self.state.tight:
            self.state.fig.tight_layout()

        return cnt
