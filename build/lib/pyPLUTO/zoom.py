import warnings
from typing import Any, cast

import numpy as np
from matplotlib.axes import Axes
from matplotlib.collections import QuadMesh

from .create_axes import CreateAxesManager
from .delegator import delegator
from .display import DisplayManager
from .imagestate import ImageState
from .imagetools import ImageToolsManager
from .inspector import track_kwargs
from .plot import PlotManager
from .set_axis import AxisManager


@delegator("state")
class ZoomManager:
    """Manager for the zoom functionality in pyPLUTO.

    This class provides methods to create inset zooms of existing plots or
    displays. It allows customization of the zoom axes, including position,
    size, and various display options."""

    exposed_methods = ("zoom",)

    def __init__(self, state: ImageState):
        """Initializes the ZoomManager with the given state."""
        self.state = state
        self.ImageToolsManager = ImageToolsManager(state)
        self.CreateAxesManager = CreateAxesManager(state)
        self.PlotManager = PlotManager(state)
        self.DisplayManager = DisplayManager(state)
        self.AxisManager = AxisManager(state)

    @track_kwargs
    def zoom(
        self, ax: Axes | int | None = None, check: bool = True, **kwargs: Any
    ) -> Axes:
        """Creation of an inset zoom of an already existent plot or display.

        It creates a set of axes within the same figure as the original plot or
        display, and can be placed anywhere in the figure.
        The zoom thus created is to all intents and purposes a self-sufficient
        plot or display, with all the necessary customization options.

        Returns
        -------
        - Axis object where the zoom plot is set

        Parameters
        ----------
        - alpha: float, default 1.0
            Sets the opacity of the plot, where 1.0 means total opaque and 0.0
            means total transparent.
        - aspect: {'auto', 'equal', float}, default 'auto'
            Sets the aspect ratio of the plot.
            The 'auto' keyword is the default option (most likely the plot will
            be squared). The 'equal' keyword will set the same scaling for
            x and y. A float will fix the ratio between the y-scale and the
            x-scale (1.0 is the same as 'equal').
        - ax: ax object, default None
            The axis to customize. If None the current axis will be selected.
        - bottom: float, default 0.6 + height
            Bottom position of the inset plot. If not defined the program will
            give a standard value.
        - clabel: str, default None
            Sets the label of the colorbar.
        - cmap: str, default 'hot'
            Selects the colormap. If not defined, the colormap 'hot' will be
            adopted.
            Some useful colormaps are: plasma, magma, seismic. Please avoid
            using colorbars like jet or rainbow, which are not perceptively
            uniform and not suited for people with vision deficiencies.
            All the colormap available are listed in the following link:
            https://matplotlib.org/stable/tutorials/colors/colormaps.html
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
        - fontsize: float, default 17.0
            Sets the fontsize for all the axis components (only for the current
            axis).
        - grid: bool, default False
            Enables the grid.
        - height: float, default 0.15
            Height of the inset zoom. It is used to defind the top (if not
            previously defined).
        - label: str, default None
            Associates a label to each line. Such labels will be used for the
            creation of the legend.
        - labelsize: float, default fontsize
            Sets the labels fontsize (which is the same for both labels).
            The default value corresponds to the value of the keyword
            'fontsize'.
        - left: float, default 0.6
            Left position of the inset plot.
        - minorticks: str, default None
            If not None enables the minor ticks on the plot (for both grid
            axes).
        - pos: [float,float,float,float], default None
            Position of the inset plot (left, right, bottom, top).
            If missing the code will look for the single keywords
            (top/bottom, left, width, height).
        - shading: {'flat,'nearest','auto','gouraud'}, default 'auto'
            The shading between the grid points. If not defined, the shading
            will be one between 'flat' and 'nearest' depending on the size of
            the x,y and z arrays. The 'flat' shading works only if, given a NxM
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
        - top: float, default bottom + height
            Top position of the inset plot. If both top and bottom keywords are
            present the priority will go to the top keyword.
        - transpose: True/False, default False
            Transposes the variable matrix. Use is not recommended if not really
            necessary (e.g. in case of highly customized variables and plots)
        - tresh: float, default max(abs(vmin),vmax)*0.01
            Additional parameter in presence of a composite colormap. The
            specific cases are the following:
            - twoslope colorscale: sets the limit between the two linear
            regimes.
            - symlog: sets the limit between the logarithmic and the linear
            regime.
        - var: 2D array
            The array to be plotted.
        - vmax: float, default max(z)
            The maximum value of the colormap. If not defined, the maximum value
            of z will be taken.
        - vmin: float, default min(z)
            The minimum value of the colormap. If not defined, the minimum value
            of z will be taken.
        - width: float, default 0.15
            Width of the inset zoom. It is used to define the right border.
        - x1: 1D/2D array, default 'Default'
            the 'x' array. If not defined, a default array will be generated
            depending on the size of z.
        - x2: 1D/2D array, default 'Default'
            the 'y' array. If not defined, a default array will be generated
            depending on the size of z.
        - xrange: [float, float], default [0,1]
            Sets the range in the x-direction. If not defined the code will
            compute the range while plotting the data.
        - xscale: {'linear','log'}, default 'linear'
            If enabled (and different from 'Default'), sets automatically the
            scale on the x-axis. Data in log scale should be used with the
            keyword 'log', while data in linear scale should be used with the
            keyword 'linear'.
        - xticks: {[float], None, 'Default'}, default 'Default'
            If enabled (and different from 'Default'), sets manually ticks on
            x-axis. In order to completely remove the ticks the keyword should
            be used with None.
        - xtickslabels: {[str], None, 'Default'}, default 'Default'
            If enabled (and different from 'Default'), sets manually the ticks
            labels on the x-axis. In order to completely remove the ticks the
            keyword should be used with None. Note that fixed tickslabels should
            always correspond to fixed ticks.
        - xtitle: str, default None
            Sets and places the label of the x-axis.
        - yrange: [float, float], default [0,1]
            Sets the range in the y-direction. If not defined the code will
            compute the range while plotting the data.
        - yscale: {'linear','log'}, default 'linear'
            If enabled (and different from 'Default'), sets automatically the
            scale on the y-axis. Data in log scale should be used with the
            keyword 'log', while data in linear scale should be used with the
            keyword 'linear'.
        - yticks: {[float], None, 'Default'}, default 'Default'
            If enabled (and different from 'Default'), sets manually ticks on
            y-axis. In order to completely remove the ticks the keyword should
            be used with None.
        - ytickslabels: {[str], None, 'Default'}, default 'Default'
            If enabled (and different from 'Default'), sets manually the ticks
            labels on the y-axis. In order to completely remove the ticks the
            keyword should be used with None. Note that fixed tickslabels should
            always correspond to fixed ticks.
        - ytitle: str, default None
            Sets and places the label of the y-axis.
        - zoomcolor: str, default 'k'
            Sets the color of the inset zoom lines
        - zoomlines: bool, default True
            Keyword in order to add/remove the inset zoom lines. The default
            option is True.

        ----

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
        kwargs.pop("check", check)

        self.state.tight = False

        # Set or create figure and axes
        ax, nax = self.ImageToolsManager.assign_ax(ax, **kwargs)

        if self.state.fig is None:
            raise ValueError(
                "No figure is present. Please create a figure first."
            )

        # Sets position of the zoom
        if kwargs.get("pos"):
            axins = self.place_inset_pos(ax, kwargs["pos"])
        else:
            axins = self.place_inset_loc(ax, **kwargs)
        kwargs["fontsize"] = kwargs.get("fontsize", self.state.fontsize)
        kwargs["titlesize"] = kwargs.get("titlesize", self.state.fontsize)

        self.state.ax.append(axins)
        self.CreateAxesManager.add_ax(axins, len(self.state.ax))

        # Set ticks (None is the default value)
        if "xticks" not in kwargs:
            kwargs["xticks"] = None
        if "yticks" not in kwargs:
            kwargs["yticks"] = None

        self.AxisManager.set_axis(ax=axins, check=False, **kwargs)

        pcm = ax.collections

        # Plots the lines
        pcm = ax.collections
        if len(pcm) > 0:
            self.zoomdisplay(ax, nax, axins, **kwargs)
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
        """Plots the lines on the inset zoom"""
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
            )

    def zoomdisplay(
        self, ax: Axes, nax: int, axins: Axes, **kwargs: Any
    ) -> None:
        """Plots the zoom on the inset zoom, for a display plot"""
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
        xc = kwargs.pop("x1", ccd[:, :, 0])
        yc = kwargs.pop("x2", ccd[:, :, 1])

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

        self.DisplayManager.display(
            pcm0, x1=xc, x2=yc, ax=axins, check=False, shading=psh, **kwargs
        )

    def place_inset_pos(self, ax: Axes, pos: list[float]) -> Axes:
        """Places an inset axes given the position (left, top, bottom,
        right).

        Returns
        -------
        - The inset axes

        Parameters
        ----------
        - ax: ax object
            The axis where the inset axes is placed.
        - pos: list[float]
            The position of the inset axes.

        """
        # Compute the position of the inset axis and return it
        left = pos[0]
        bottom = pos[2]
        width = pos[1] - pos[0]
        height = pos[3] - pos[2]
        return ax.inset_axes((left, bottom, width, height))

    def place_inset_loc(self, ax: Axes, **kwargs: Any) -> Axes:
        """Places an inset axes given different keywords. In case both
        top and bottom are given, the top is given priority and a
        warning is raised.

        Returns
        -------
        - The inset axes

        Parameters
        ----------
        - ax: ax object
            The axis where the inset axes is placed.
        - left: float
            The left boundary of the axes.
        - top: float
            The top boundary of the axes.
        - bottom: float
            The bottom boundary of the axes.
        - width: float
            The width of the inset axis.
        - height: float
            The height of the inset axis.

        """
        # Check if both "top" and "bottom" keywords are given
        if kwargs.get("top") and kwargs.get("bottom"):
            warn = (
                "Both top and bottom keys are given, priority goes to the top"
            )
            warnings.warn(warn, UserWarning)

        # Compute the position of the inset axis and return it
        left = kwargs.get("left", 0.6)
        width = kwargs.get("width", 0.2)
        height = kwargs.get("height", 0.15)
        bottom = kwargs.get("top", 0.75) - height
        bottom = kwargs.get("bottom", 0.6)

        return ax.inset_axes((left, bottom, width, height))
