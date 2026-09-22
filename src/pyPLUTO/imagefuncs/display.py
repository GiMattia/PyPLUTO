"""Module to manage the display of 2D plots in the image."""

from __future__ import annotations

from typing import Unpack

import numpy as np
from matplotlib.axes import Axes
from matplotlib.collections import QuadMesh
from numpy.typing import ArrayLike

from pyPLUTO.imagefuncs.colorbar import ColorbarManager
from pyPLUTO.imagefuncs.imagetools import ImageToolsManager
from pyPLUTO.imagefuncs.range import RangeManager
from pyPLUTO.imagefuncs.set_axis import AxisManager
from pyPLUTO.imagekwargs import DisplayKwargs
from pyPLUTO.imagemixin import ImageMixin
from pyPLUTO.imagestate import ImageState
from pyPLUTO.utils.inspector import track_kwargs


class DisplayManager(ImageMixin):
    """Class to manage the display of 2D plots in the image.

    This class provides methods to create and manage 2D plots using matplotlib's
    pcolormesh function. It allows for customization of the plot's appearance,
    colorbar, axes, and other properties.
    """

    def __init__(self, state: ImageState) -> None:
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
        ax: Axes | list[Axes] | int | None = None,
        _check: bool = True,
        **kwargs: Unpack[DisplayKwargs],
    ) -> QuadMesh:
        """Plot for a 2D function using the matplotlib's pcolormesh function.

        A simple figure and a single axis can also be
        created.

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
        - shading: {'flat', 'nearest', 'auto', 'gouraud'}, default 'auto'
            The shading between the grid points. If not defined, the shading
            will be one between 'flat' and 'nearest' depending on the size of
            the x, y and z arrays. The 'flat' shading works only if, given a
            NxM z-array, the x- and y-arrays have sizes of, respectively, N+1
            and M+1. All the other shadings require a N x-array and a M
            y-array.
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
        - transpose: True/False, default False
            Transposes the variable matrix. Use is not recommended if not
            really necessary (e.g. in case of highly customized variables and
            plots).
        - tresh: float, default max(abs(vmin),vmax)*0.01
            Sets the threshold for the colormap (used with composite
            colorscales such as twoslope or symlog).
        - var (not optional): 2D array
            The array to be plotted.
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
        - QuadMesh

        Examples
        --------
        - Example #1: create a simple 2d plot with title and colorbar on the
            right

            >>> import pyPLUTO as pp
            >>> I = pp.Image()
            >>> I.display(var, title="title", cpos="right")

        - Example #2: create a 2d plot with title on the axes, bottom colorbar
            and custom shading

            >>> import pyPLUTO as pp
            >>> I = pp.Image()
            >>> I.display(var, x1 = x1, x2 = x2, xtitle = 'x', ytitle = 'y',
                    cpos = 'bottom', shading = 'gouraud', cpad = 0.3)

        - Example #3: create a 2d plot con custom range on axes and logarithmic
            scale colorbar

            >>> import pyPLUTO as pp
            >>> I = pp.Image()
            >>> I.display(var, xrange = [2,3], yrange = [2,4], cpos = 'right',
                        cscale = 'log')

        - Example #4: create a 2d plot with a custom symmetric logarithmic
            colorbar with custom ticks.

            >>> import pyPLUTO as pp
            >>> I = pp.Image()
            >>> I.display(var, cpos = 'right', cmap = 'RdBu_r',
                        cscale = 'symlog', tresh = 0.001, vmin = -1, vmax = 1)

        """
        if self.fig is None:
            raise ValueError(
                "No figure is present. Please create a figure first.",
            )

        # Set or create figure and axes
        ax, nax = self.ImageToolsManager.assign_ax(ax, _check=False, **kwargs)

        # Keyword x1 and x2
        var = np.asarray(var)
        if kwargs.get("transpose", False):
            var = var.T
        x = np.asarray(kwargs.get("x1", np.arange(len(var[:, 0]) + 1)))
        y = np.asarray(kwargs.get("x2", np.arange(len(var[0, :]) + 1)))

        # Set ax parameters
        self.AxisManager.set_axis(ax=ax, _check=False, **kwargs)
        self.ImageToolsManager.hide_text(nax, ax.texts)

        # Keywords xrange and yrange: the range is the domain, with nothing
        # added to it, and the axis is left free for what comes next
        strict = self.RangeManager.strictrange
        xlim = self.map_extent(x, var.shape[0])
        ylim = self.map_extent(y, var.shape[1])
        self.RangeManager.set_xrange(ax, nax, xlim, strict)
        self.RangeManager.set_yrange(ax, nax, ylim, strict)

        # gouraud interpolates between the centers and would leave the outer
        # half cell of the domain unpainted. A vertex on each border, holding
        # the value of the cell it belongs to, fills it with that value, as
        # the other shadings do, and changes nothing in between
        if (
            kwargs.get("shading") == "gouraud"
            and x.size == var.shape[0]
            and y.size == var.shape[1]
        ):
            x = np.concatenate(([xlim[0]], x, [xlim[1]]))
            y = np.concatenate(([ylim[0]], y, [ylim[1]]))
            var = np.pad(var, 1, mode="edge")

        # Keywords vmin and vmax
        vmin = kwargs.get("vmin", np.nanmin(var))
        vmax = kwargs.get("vmax", np.nanmax(var))

        # Keyword for colorbar and colorscale
        cpos = kwargs.get("cpos")
        cscale = kwargs.get("cscale", "norm")
        tresh = kwargs.get("tresh", max(np.abs(vmin), vmax) * 0.01)
        self.vlims[nax] = [vmin, vmax, tresh]

        # Set the colorbar scale (put in function)
        norm = self.ImageToolsManager.set_cscale(cscale, vmin, vmax, tresh)

        # Select shading
        shade = kwargs.get("shading", "auto")
        alpha = kwargs.get("alpha", 1.0)

        cmap = self.ImageToolsManager.find_cmap(kwargs.get("cmap", "plasma"))

        # Display the image
        pcm = ax.pcolormesh(
            x,
            y,
            var.T,
            shading=shade,
            cmap=cmap,
            norm=norm,
            linewidth=0,
            rasterized=True,
            alpha=alpha,
        )

        # Place the colorbar (use colorbar function)
        if cpos is not None:
            self.ColorbarManager.colorbar(pcm, _check=False, **kwargs)

        # If tight_layout is enabled, is re-inforced
        if self.tight:
            self.fig.tight_layout()

        return pcm

    def map_extent(self, coord: np.ndarray, ncells: int) -> list[float]:
        """Find the limits of a map along one direction.

        The coordinates of a map are either the edges of the cells, one more
        than there are cells, or their centers, one per cell. Given the
        centers, the frame is still the edges, half a cell beyond the first
        and the last of them: the domain ends there, and framing the centers
        instead leaves whatever sits in that half cell -- a field line ending
        on the border, a particle at the wall -- outside a map it belongs to.

        Every shading reaches the same edges: 'gouraud' interpolates between
        the centers only, so the map is given a vertex on each border to
        paint the half cell beyond them.

        Parameters
        ----------
        - coord (not optional): np.ndarray
            The coordinates of the map along one direction.
        - ncells (not optional): int
            The number of cells of the variable along that direction.

        Returns
        -------
        - list[float]

        Examples
        --------
        - Example #1: the extent of a map drawn on three cell centers

            >>> _map_extent(np.array([0.5, 1.5, 2.5]), 3)
            [0.0, 3.0]

        """
        if coord.size != ncells:
            return [float(coord.min()), float(coord.max())]

        # A single cell has no spacing to take half of, so it is given the
        # same width matplotlib gives it
        if coord.size < 2:
            return [float(coord[0]) - 0.5, float(coord[0]) + 0.5]

        first = float(coord[0]) - (float(coord[1]) - float(coord[0])) / 2
        last = float(coord[-1]) + (float(coord[-1]) - float(coord[-2])) / 2
        return [min(first, last), max(first, last)]
