"""Module to manage the zoom functionality in pyPLUTO."""

from __future__ import annotations

import warnings
from typing import Any, Unpack, cast

import numpy as np
from matplotlib.axes import Axes
from matplotlib.collections import QuadMesh

from pyPLUTO.imagefuncs.create_axes import CreateAxesManager
from pyPLUTO.imagefuncs.display import DisplayManager
from pyPLUTO.imagefuncs.imagetools import ImageToolsManager
from pyPLUTO.imagefuncs.plot import PlotManager
from pyPLUTO.imagefuncs.set_axis import AxisManager
from pyPLUTO.imagekwargs import SetLocKwargs, ZoomKwargs
from pyPLUTO.imagemixin import ImageMixin
from pyPLUTO.imagestate import ImageState
from pyPLUTO.utils.inspector import track_kwargs


class ZoomManager(ImageMixin):
    """Manager for the zoom functionality in pyPLUTO.

    This class provides methods to create inset zooms of existing plots or
    displays. It allows customization of the zoom axes, including position,
    size, and various display options.
    """

    def __init__(self, state: ImageState) -> None:
        """Initialize the ZoomManager with the given state."""
        self.state = state
        self.ImageToolsManager = ImageToolsManager(state)
        self.CreateAxesManager = CreateAxesManager(state)
        self.PlotManager = PlotManager(state)
        self.DisplayManager = DisplayManager(state)
        self.AxisManager = AxisManager(state)

    @track_kwargs
    def zoom(
        self,
        ax: Axes | list[Axes] | int | None = None,
        _check: bool = True,
        **kwargs: Unpack[ZoomKwargs],
    ) -> Axes:
        """Creation of an inset zoom of an already existent plot or display.

        It creates a set of axes within the same figure as the original plot or
        display, and can be placed anywhere in the figure.
        The zoom thus created is to all intents and purposes a self-sufficient
        plot or display, with all the necessary customization options.

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
        - ax: ax object, default None
            The axis to customize. If None the current axis will be selected.
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
        - height: float, default 0.15
            The height of the axis / axes set (used for an inset zoom).
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
        - minorticks: str, default None
            If not None enables the minor ticks on the plot (for both grid
            axes).
        - ncol: int, default 1
            The number of columns of subplots.
        - nrow: int, default 1
            The number of rows of subplots.
        - pos: [float,float,float,float], default None
            Position of the inset plot (left, right, bottom, top).
            If missing the code will look for the single keywords
            (top/bottom, left, width, height).
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
        - var: str | list[str] | np.ndarray | bool | None, default True
            The variable to be loaded / plotted. When loading, it selects the
            variables (True loads all, or pass a string or list for a subset);
            when plotting, it is the array to display.
        - vmax: float
            The maximum value of the variable to be computed / plotted.
        - vmin: float
            The minimum value of the variable to be computed / plotted.
        - width: float, default 0.15
            The width of the axis / axes set (used for an inset zoom).
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
        - zoomcolor: str, default 'k'
            Sets the color of the inset zoom lines.
        - zoomlines: bool, default True
            Keyword in order to add/remove the inset zoom lines. The default
            option is True.

        Returns
        -------
        - Axes

        Examples
        --------
        - Example #1: create a simple zoom of a 1d plot

            >>> import pyPLUTO as pp
            >>> I = pp.Image()
            >>> I.plot(x1, var)
            >>> I.zoom(pos = [0.1,0.2,0.1,0.3], xrange = [1,10], y
            ... range = [10,20])

        - Example #2: create a simple zoom of a 2d plot

            >>> import pyPLUTO as pp
            >>> I = pp.Image()
            >>> I.display(var, x1=x1, x2=x2)
            >>> I.zoom(
            ...     left=0.8,
            ...     bottom=0.9,
            ...     height=0.2,
            ...     width=0.2,
            ...     xrange=[1, 10],
            ...     yrange=[10, 20],
            ... )

        - Example #3: create a zoom of a different quantity over a 2d plot

            >>> import pyPLUTO as pp
            >>> I = pp.Image()
            >>> I.display(var, x1=x1, x2=x2)
            >>> I.zoom(var=var2, xrange=[1, 10], yrange=[10, 20])

        """
        self.state.tight = False

        # Set or create figure and axes
        ax, nax = self.ImageToolsManager.assign_ax(ax, _check=False, **kwargs)

        if self.state.fig is None:
            raise ValueError(
                "No figure is present. Please create a figure first."
            )

        # Sets position of the zoom
        if kwargs.get("pos"):
            axins = self.place_inset_pos(ax, kwargs["pos"])
        else:
            axins = self.place_inset_loc(ax, _check=False, **kwargs)
        kwargs["fontsize"] = kwargs.get("fontsize", self.state.fontsize)
        kwargs["titlesize"] = kwargs.get("titlesize", self.state.fontsize)

        self.state.ax.append(axins)
        self.CreateAxesManager.add_ax(axins, len(self.state.ax))

        # Set ticks (None is the default value)
        if "xticks" not in kwargs:
            kwargs["xticks"] = None
        if "yticks" not in kwargs:
            kwargs["yticks"] = None

        self.AxisManager.set_axis(ax=axins, _check=False, **kwargs)

        pcm = ax.collections

        # Plots the lines
        pcm = ax.collections
        if len(pcm) > 0:
            self.zoomdisplay(ax, nax, axins, _check=False, **kwargs)
        else:
            self.zoomplot(ax, axins)

        # Indicates the inset zoom
        zoomc = kwargs.get("zoomcolor", "k")
        if kwargs.get("zoomlines", True) is True:
            ax.indicate_inset_zoom(axins, edgecolor=zoomc)

        axins.spines["left"].set_color(zoomc)
        axins.spines["bottom"].set_color(zoomc)
        axins.spines["right"].set_color(zoomc)
        axins.spines["top"].set_color(zoomc)

        return axins

    def zoomplot(self, ax: Axes, axins: Axes) -> None:
        """Plot the lines on the inset zoom.

        Parameters
        ----------
        - ax: Axes
            The axis containing the lines to be plotted.
        - axins: Axes
            The inset axis where the lines will be plotted.

        Returns
        -------
        - None
        """
        lines = ax.get_lines()
        for i in lines:
            self.PlotManager.plot(
                i.get_xdata(),
                i.get_ydata(),
                c=i.get_color(),
                ls=i.get_linestyle(),
                lw=i.get_linewidth(),
                marker=i.get_marker(),
                ms=i.get_markersize(),
                ax=axins,
                _check=False,
            )

    @track_kwargs
    def zoomdisplay(
        self,
        ax: Axes,
        nax: int,
        axins: Axes,
        _check: bool = True,
        **kwargs: Unpack[ZoomKwargs],
    ) -> None:
        """Plot the zoom on the inset zoom, for a display plot.

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
        - ax: ax object, default None
            The axis to customize. If None the current axis will be selected.
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
        - var: str | list[str] | np.ndarray | bool | None, default True
            The variable to be loaded / plotted. When loading, it selects the
            variables (True loads all, or pass a string or list for a subset);
            when plotting, it is the array to display.
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
        - zoomcolor: str, default 'k'
            Sets the color of the inset zoom lines.

        Returns
        -------
        - None

        """
        pcm = ax.collections[0]
        pnr = str(pcm.norm).split()[0].split(".")[2]
        dict_norm = {
            "Normalize": "norm",
            "LogNorm": "log",
            "SymLogNorm": "symlog",
            "TwoSlopeNorm": "twoslope",
        }

        kwargs["cmap"] = kwargs.pop("cmap", pcm.cmap)
        kwargs["cscale"] = kwargs.pop("cscale", dict_norm[pnr])

        if not isinstance(pcm, QuadMesh):
            raise TypeError(
                "The zoom can be applied only to a QuadMesh object."
            )

        ccd = cast(np.ndarray[Any, Any], pcm.get_coordinates())
        kwargs["x1"] = xc = kwargs.pop("x1", ccd[:, :, 0])
        kwargs["x2"] = yc = kwargs.pop("x2", ccd[:, :, 1])

        psh = kwargs.pop("shading", getattr(pcm, "_shading", "flat"))
        leny = len(xc[0]) if np.ndim(yc) > 1 else len(yc)
        lxc = len(xc) - 1 if psh == "flat" else len(xc)
        lyc = leny - 1 if psh == "flat" else leny
        # if psh == 'flat':
        #    lxc = len(xc) - 1
        #    lyc = len(xc[0]) - 1
        # else:
        #    lxc = len(xc)
        #    lyc = len(xc[0])
        arr = pcm.get_array()
        if "var" in kwargs and arr is not None:
            pcm0 = kwargs.pop("var", None)
        elif arr is not None:
            pcm0 = arr.reshape((lxc, lyc)).T
        else:
            raise ValueError(
                "No variable is present in the zoom display. "
                "Please provide a variable to plot."
            )
        # pcm0 = kwargs.pop('var', pcm.reshape((lxc, lyc)).T)
        kwargs["vmin"] = kwargs.pop("vmin", self.state.vlims[nax][0])
        kwargs["vmax"] = kwargs.pop("vmax", self.state.vlims[nax][1])
        kwargs["tresh"] = kwargs.pop("tresh", self.state.vlims[nax][2])
        kwargs["shading"] = psh
        if pcm0 is not None and not isinstance(pcm0, str):
            kwargs["var"] = pcm0
            self.DisplayManager.display(ax=axins, _check=False, **kwargs)

    def place_inset_pos(self, ax: Axes, pos: list[float]) -> Axes:
        """Place an inset axes given the position (left, top, bottom, right).

        Parameters
        ----------
        - ax: ax object
            The axis where the inset axes is placed.
        - pos: list[float]
            The position of the inset axes.

        Returns
        -------
        - Axes

        """
        # Compute the position of the inset axis and return it
        left = pos[0]
        bottom = pos[2]
        width = pos[1] - pos[0]
        height = pos[3] - pos[2]
        return ax.inset_axes((left, bottom, width, height))

    @track_kwargs
    def place_inset_loc(
        self, ax: Axes, _check: bool = True, **kwargs: Unpack[SetLocKwargs]
    ) -> Axes:
        """Place an inset axes given different keywords.

        In case both top and bottom are given, the top is given priority and a
        warning is raised.

        Parameters
        ----------
        - ax: ax object
            The axis where the inset axes is placed.
        - left: float, default varies
            The left limit of the axis / axes set. For the figure layout it is
            the space from the left border to the plot (default 0.125); for an
            inset zoom it is the left position of the inset (default 0.6).
        - bottom: float, default varies
            The bottom limit of the axis / axes set. For the figure layout it
            is the space from the bottom border to the plot (default 0.1); for
            an inset zoom it is the bottom position of the inset (default 0.6 +
            height).
        - right: float, default varies
            The right limit of the axis / axes set. For the figure layout it is
            the space from the right border to the plot (default 0.9); for an
            inset zoom it is the right position of the inset (default left +
            0.15).
        - top: float, default varies
            The top limit of the axis / axes set. For the figure layout it is
            the space from the top border to the plot (default 0.9); for an
            inset zoom it is the top position of the inset (default bottom +
            height).
        - width: float, default 0.15
            The width of the axis / axes set (used for an inset zoom).
        - height: float, default 0.15
            The height of the axis / axes set (used for an inset zoom).

        Returns
        -------
        - Axes

        """
        # Check if both "top" and "bottom" keywords are given
        if kwargs.get("top") and kwargs.get("height"):
            warn = "Both top and height are specified. Using top and height."
            warnings.warn(warn, UserWarning, stacklevel=2)

        if kwargs.get("right") and kwargs.get("width"):
            warn = "Both right and width are specified. Using right and width."
            warnings.warn(warn, UserWarning, stacklevel=2)

        # Compute the position of the inset axis and return it
        left = kwargs.get("left", 0.6)
        right = kwargs.get("right", left + 0.15)
        width = kwargs.get("width", right - left)
        bottom = kwargs.get("bottom", 0.6)
        top = kwargs.get("top", bottom + 0.15)
        height = kwargs.get("height", top - bottom)

        return ax.inset_axes((left, bottom, width, height))
