import warnings
from typing import Any

import matplotlib.colors as mcol
import numpy as np
from matplotlib.collections import QuadMesh
from mpl_toolkits.axes_grid1 import make_axes_locatable
from numpy.typing import NDArray

from .h_pypluto import check_par


def display(self, var: NDArray, check: bool = True, **kwargs: Any) -> QuadMesh:
    """Plot for a 2D function (or a 2D slice) using the
    matplotlib's pcolormesh function.
    A simple figure and a single axis can also be created.

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
        x and y. A float will fix the ratio between the y-scale and the x-scale
        (1.0 is the same as 'equal').
    - ax: ax | int | None, default None
        The axis where to plot the lines. If None, a new axis is created.
        If 'old', the last considered axis will be used.
    - bottom: float, default 0.1
        The space from the bottom border to the plot.
    - clabel: str, default None
        Sets the label of the colorbar.
    - cmap: str, default 'plasma'
        Selects the colormap. If not defined, the colormap 'plasma' will be
        adopted. Some useful colormaps are: plasma, magma, seismic. Please avoid
        using colorbars like jet or rainbow, which are not perceptively uniform
        and not suited for people with vision deficiencies.
        All the colormap available are listed in the following link:
        https://matplotlib.org/stable/tutorials/colors/colormaps.html
    - cpad: float, default 0.07
        Fraction of original axes between colorbar and the axes (in case cax is
        not defined).
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
        The default value corresponds to the value of the keyword 'fontsize'.
    - left: float, default 0.125
        The space from the left border to the plot.
    - minorticks: str, default None
        If not None enables the minor ticks on the plot (for both grid axes).
    - proj: str, default None
        Custom projection for the plot (e.g. 3D). Recommended only if needed.
        This keyword should be used only if the axis is created.
        WARNING: pyPLUTO does not support 3D plotting for now, only 3D axes.
        The 3D plot feature will be available in future releases.
    - right: float, default 0.9
        The space from the right border to the plot.
    - shading: {'flat,'nearest','auto','gouraud'}, default 'auto'
        The shading between the grid points. If not defined, the shading will
        one between 'flat' and 'nearest' depending on the size of the x,y and
        z arrays. The 'flat' shading works only if, given a NxM z-array, the
        x- and y-arrays have sizes of, respectively, N+1 and M+1. All the other
        shadings require a N x-array and a M y-array.
        More informations in the following link:
        https://matplotlib.org/stable/gallery/images_contours_and_fields/pcolormesh_grids.html
    - ticksdir: {'in', 'out'}, default 'in'
        Sets the ticks direction. The default option is 'in'.
    - tickssize: float, default fontsize
        Sets the ticks fontsize (which is the same for both grid axes).
        The default value corresponds to the value of the keyword 'fontsize'.
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
        Sets the threshold for the colormap. If not defined, the threshold will
        be set to 1% of the maximum absolute value of the variable.
        The default cases are the following:
        - twoslope colorscale: sets the limit between the two linear regimes.
        - symlog: sets the limit between the logaitrhmic and the linear regime.
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
        Sets the range in the x-direction. If not defined or set to 'Default'
        the code will compute the range while plotting the data by taking the
        minimum and the maximum values of the x1-array.
    - xscale: {'linear','log'}, default 'linear'
        If enabled (and different from 'Default'), sets automatically the scale
        on the x-axis. Data in log scale should be used with the keyword 'log',
        while data in linear scale should be used with the keyword 'linear'.
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
        Sets the range in the y-direction. If not defined or set to 'Default'
        the code will compute the range while plotting the data by taking the
        minimum and the maximum values of the x2-array.
    - yscale: {'linear','log'}, default 'linear'
        If enabled (and different from 'Default'), sets automatically the scale
        on the y-axis. Data in log scale should be used with the keyword 'log',
        while data in linear scale should be used with the keyword 'linear'.
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

    Notes
    -----
    - If not x or y is given, no shading can be selected. This issue will be
        fixed in future releases.

    ----

    Examples
    --------
    - Example #1: create a simple 2d plot with title and colorbar on the right

        >>> import pyPLUTO as pp
        >>> I = pp.Image()
        >>> I.display(var, title = 'title', cpos = 'right')

    - Example #2: create a 2d plot with title on the axes, bottom colorbar and
        custom shading

        >>> import pyPLUTO as pp
        >>> I = pp.Image()
        >>> I.display(x1, x2, var, xtitle = 'x', ytitle = 'y', cpos = 'bottom',
                      shading = 'gouraud', cpad = 0.3)

    - Example #3: create a 2d plot con custom range on axes and logarithmic
        scale colorbar

        >>> import pyPLUTO as pp
        >>> I = pp.Image()
        >>> I.display(var, xrange = [2,3], yrange = [2,4], cbar = 'right',
                      cscale = 'log')

    - Example #4: create a 2d plot with a custom symmetric logarithmic colorbar
        with custom ticks.

        >>> import pyPLUTO as pp
        >>> I = pp.Image()
        >>> I.display(var, cpos = 'right', cmap = 'RdBu_r', cscale = 'symlog',
                      tresh = 0.001, vmin = -1, vmax = 1)

    """
    # Check parameters
    param = {
        "alpha",
        "aspect",
        "ax",
        "bottom",
        "clabel",
        "cmap",
        "cpad",
        "cpos",
        "cscale",
        "cticks",
        "ctickslabels",
        "extend",
        "extendrect",
        "figsize",
        "fontsize",
        "grid",
        "labelsize",
        "left",
        "minorticks",
        "proj",
        "right",
        "shading",
        "ticksdir",
        "tickssize",
        "title",
        "titlesize",
        "top",
        "transpose",
        "tresh",
        "vmax",
        "vmin",
        "x1",
        "x2",
        "xrange",
        "xscale",
        "xticks",
        "xtickslabels",
        "xtitle",
        "yrange",
        "yscale",
        "yticks",
        "ytickslabels",
        "ytitle",
    }
    if check is True:
        check_par(param, "display", **kwargs)

    # Set or create figure and axes
    ax, nax = self._assign_ax(kwargs.pop("ax", None), **kwargs)

    # Keyword x1 and x2
    var = np.asarray(var)
    if kwargs.get("transpose", False) is True:
        var = var.T
    x = np.asarray(kwargs.get("x1", np.arange(len(var[:, 0]) + 1)))
    y = np.asarray(kwargs.get("x2", np.arange(len(var[0, :]) + 1)))

    # Keywords xrange and yrange
    if not kwargs.get("xrange") and not self.setax[nax] == 1:
        kwargs["xrange"] = [x.min(), x.max()]
    if not kwargs.get("yrange") and not self.setay[nax] == 1:
        kwargs["yrange"] = [y.min(), y.max()]

    # Set ax parameters
    self.set_axis(ax=ax, check=False, **kwargs)
    self._hide_text(nax, ax.texts)

    # Keywords vmin and vmax
    vmin = kwargs.get("vmin", np.nanmin(var))
    vmax = kwargs.get("vmax", np.nanmax(var))

    # Keyword for colorbar and colorscale
    cpos = kwargs.get("cpos")
    cscale = kwargs.get("cscale", "norm")
    tresh = kwargs.get("tresh", max(np.abs(vmin), vmax) * 0.01)
    lint = kwargs.get("lint")
    self.vlims[nax] = [vmin, vmax, tresh]

    # Set the colorbar scale (put in function)
    norm = self._set_cscale(cscale, vmin, vmax, tresh, lint)

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
        self.colorbar(pcm, check=False, **kwargs)

    # If tight_layout is enabled, is re-inforced
    if self.tight:
        self.fig.tight_layout()

    return pcm


def scatter(
    self,
    x: NDArray | list[float],
    y: NDArray | list[float],
    check: bool = True,
    **kwargs: Any,
) -> QuadMesh:
    """Scatter plot for a 2D function (or a 2D slice) using the matplotlib's
    scatter function. A simple figure and a single axis can also be created.

    Returns
    -------
    - The scatter plot

    Parameters
    ----------
    - alpha: float, default 1.0
        Sets the transparency of the plot.
    - aspect: {'auto', 'equal', float}, default 'auto'
        Sets the aspect ratio of the plot. The 'auto' keyword is the default
        option (most likely the plot will be squared). The 'equal' keyword will
        set the same scaling for x and y. A float will fix the ratio between the
        y-scale and the x-scale (1.0 is the same as 'equal').
    - ax: axis object
       The axis where to plot the scatter. If not given, the last considered
       axis will be used.
    - c: str, default ['k','#12e3c0','#3f6600','#1815c5','#f67451','#d7263d']
        Determines the scatter plot color. If not defined, the program will loop
        over an array of 6 color which are different for the most common vision
        deficiencies.
    - clabel: str, default None
        Sets the colorbar label.
    - cmap: str, default 'hot'
        Selects the colormap. If not defined, the colormap 'hot' will be
        adopted. Some useful colormaps are: plasma, magma, seismic. Please avoid
        using colorbars like jjet or rainbow, which are not perceptively uniform
        and not suited for people with vision deficiencies.
        All the colormap available are listed in the following link:
        https://matplotlib.org/stable/tutorials/colors/colormaps.html
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
        The default value corresponds to the value of the keyword 'fontsize'.
    - legpos: int/str, default None
        If enabled, creates a legend. This keyword selects the legend location.
        The possible locations for the legend are indicated in the following
        link:
        https://matplotlib.org/stable/api/_as_gen/matplotlib.pyplot.legend.html
    - marker: {'o', 'v', '^', '<', '>', 'X', ' ', etc.}, default ' '
        Sets an optional symbol for every point. The default value is no marker
        (' ').
    - minorticks: str, default None
        If not None enables the minor ticks on the plot (for both grid axes).
    - ms: float, default 3
        Sets the marker size.
    - ticksdir: {'in', 'out'}, default 'in'
        Sets the ticks direction. The default option is 'in'.
    - tickssize: float | bool, default True
        Sets the ticks fontsize (which is the same for both grid axes).
        The default value corresponds to the value of the keyword 'fontsize'.
    - title: str, default None
        Places the title of the plot on top of it.
    - titlepad: float, default 8.0
        Sets the distance between the title and the top of the plot
    - titlesize: float, default fontsize
        Sets the title fontsize. The default value corresponds to the value
        of the keyword 'fontsize'.
    - tresh: float, default max(abs(vmin),vmax)*0.01
        Sets the threshold for the colormap. If not defined, the threshold will
        be set to 1% of the maximum absolute value of the variable.
        The default cases are the following:
        - twoslope colorscale: sets the limit between the two linear regimes.
        - symlog: sets the limit between the logaitrhmic and the linear regime.
    - vmax: float
        The maximum value of the colormap.
    - vmin: float
        The minimum value of the colormap.
    - x (not optional): 1D array
        The x-axis variable.
    - xrange: [float, float], default 'Default'
        Sets the range in the x-direction. If not defined or set to 'Default'
        the code will compute the range while plotting the data by taking the
        minimum and the maximum values of the x1-array.
    - xscale: {'linear','log'}, default 'linear'
        If enabled (and different from True), sets automatically the scale
        on the x-axis. Data in log scale should be used with the keyword 'log',
        while data in linear scale should be used with the keyword 'linear'.
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
        on the y-axis. Data in log scale should be used with the keyword 'log',
        while data in linear scale should be used with the keyword 'linear'.
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

    # Check parameters
    param = {
        "alpha",
        "aspect",
        "ax",
        "c",
        "clabel",
        "cmap",
        "cpos",
        "cscale",
        "edgecolors",
        "fontsize",
        "grid",
        "label",
        "labelsize",
        "legpos",
        "marker",
        "ms",
        "minorticks",
        "ticksdir",
        "tickssize",
        "title",
        "titlepad",
        "titlesize",
        "tresh",
        "vmax",
        "vmin",
        "xrange",
        "xscale",
        "xticks",
        "xtickslabels",
        "xtitle",
        "yrange",
        "yscale",
        "yticks",
        "ytickslabels",
        "ytitle",
    }

    if check is True:
        check_par(param, "scatter", **kwargs)

    # Set or create figure and axes
    ax, nax = self._assign_ax(kwargs.pop("ax", None), **kwargs)

    # Keywords xrange and yrange
    if not kwargs.get("xrange") and not self.setax[nax] == 1:
        kwargs["xrange"] = [x.min(), x.max()]
    if not kwargs.get("yrange") and not self.setay[nax] == 1:
        kwargs["yrange"] = [y.min(), y.max()]

    # Set ax parameters
    self.set_axis(ax=ax, check=False, **kwargs)
    self._hide_text(nax, ax.texts)

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
    self.vlims[nax] = [vmin, vmax, tresh]

    # Set the colorbar scale
    norm = self._set_cscale(cscale, vmin, vmax, tresh)

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
    self.legpos[nax] = kwargs.get("legpos", self.legpos[nax])
    if self.legpos[nax] is not None:
        copy_label = kwargs.get("label")
        kwargs["label"] = None
        self.legend(ax, check="no", fromplot=True, **kwargs)
        kwargs["label"] = copy_label

    # Place the colorbar (use colorbar function)
    if cpos is not None:
        self.colorbar(pcm, check=False, **kwargs)

    # If tight_layout is enabled, is re-inforced
    if self.tight:
        self.fig.tight_layout()

    return pcm


def colorbar(self, pcm=None, axs=None, cax=None, check=True, **kwargs) -> None:
    """Method to display a colorbar in a selected position. If the keyword cax is
    enabled the colorbar is located in a specific axis, otherwise an axis will
    be shrunk in order to place the colorbar.

    Returns
    -------
    - None

    Parameters
    ----------
    - axs: axis object, default None
        The axes where the display that will be used for the colorbar is
        located. If None, the last considered axis will be used.
    - cax: axis object, default None
        The axes where the colorbar should be placed. If None, the colorbar
        will be placed next to the axis axs.
    - clabel: str, default None
        Sets the label of the colorbar.
    - cpad: float, default 0.07
        Fraction of original axes between colorbar and the axes (in case cax is
        not defined).
    - cpos: {'top','bottom','left','right'}, default 'right'
        Sets the position of the colorbar.
    - cticks: {[float], None}, default None
        If enabled (and different from None), sets manually ticks on the
        colorbar.
    - ctickslabels: str, default None
        If enabled, sets manually ticks labels on the colorbar.
    - extend: {'neither','both','min','max'}, default 'neither'
        Sets the extension of the triangular colorbar extension.
    - extendrect: bool, default False
        If True, the colorbar extension will be rectangular.
    - pcm: QuadMesh | PathCollection | None, default None
        The collection to be used for the colorbar. If None, the axs will be
        used. If both pcm and axs are not None, pcm will be used.

    Notes
    -----
    - If multiple subplots are present, multiple colorbars cannot be created
      from the display routine. This issue must be fixed in future releases.
    - Colorbar should not overlap the plot or other colormaps
    - Exted the colormap to more positions (e.g., top, bottom) with correct
      spacing

    ----

    Examples
    --------
    - Example #1: create a standard colorbar on the right

        >>> import pyPLUTO as pp
        >>> I = pp.Image()
        >>> I.display(var)
        >>> I.colorbar()

    - Example #2: create a colorbar in a different axis

        >>> import pyPLUTO as pp
        >>> I = pp.Image()
        >>> ax = I.create_axes(ncol = 2)
        >>> I.display(var, ax = ax[0])
        >>> I.colorbar(axs = ax[0], cax = ax[1])

    - Example #3: create a set of 3 displays with a colorbar on the bottom.
        Another colorbar is shown on the right of the topmost display

        >>> import pyPLUTO as pp
        >>> I = pp.Image()
        >>> ax = I.create_axes(nrow = 4)
        >>> I.display(var1, ax = ax[0])
        >>> I.colorbar(axs = ax[0])
        >>> I.display(var2, ax = ax[1])
        >>> I.display(var3, ax = ax[2])
        >>> I.colorbar(axs = ax[2], cax = ax[3])

    """
    # Check parameters
    param = {
        "clabel",
        "cpad",
        "cpos",
        "cticks",
        "ctickslabels",
        "extend",
        "extendrect",
    }
    if check is True:
        check_par(param, "colorbar", **kwargs)

    # If pcm and a source axes are selected, raise a warning and use pcm
    if pcm is not None and axs is not None:
        warn = "Both pcm and axs are not None, pcm will be used"
        warnings.warn(warn, UserWarning)

    # Select the source axis
    axs = pcm.axes if pcm is not None else axs if axs is not None else self.fig.gca()
    axs, _ = self._assign_ax(axs, **kwargs)

    # Select the keywords
    pcm = axs.collections[0] if pcm is None else pcm
    cpad = kwargs.get("cpad", 0.07)
    cpos = kwargs.get("cpos", "right")
    ccor = "vertical" if cpos in ["left", "right"] else "horizontal"

    # Assign the colorbar axis, if cax is None create a new one
    if cax is None:
        divider = make_axes_locatable(axs)
        cax = divider.append_axes(cpos, size="7%", pad=cpad)  # 0.07 right
    else:
        cax, naxc = self._assign_ax(cax, **kwargs)
        self._hide_text(naxc, cax.texts)

    # Place the colorbar
    cbar = self.fig.colorbar(
        pcm,
        cax=cax,
        label=kwargs.get("clabel", ""),
        ticks=kwargs.get("cticks"),
        orientation=ccor,
        extend=kwargs.get("extend", "neither"),
        extendrect=kwargs.get("extendrect", False),
    )

    # Set the tickslabels
    ctkc = kwargs.get("ctickslabels", "Default")
    if ctkc != "Default":
        cbar.ax.set_yticklabels(ctkc)

    # Ensure, if needed, the tight layout
    if self.tight:
        self.fig.tight_layout()

    # End of function


def _set_cscale(
    self,
    cscale: str,
    vmin: float,
    vmax: float,
    tresh: float,
    lint: float | None = None,
):
    """Sets the color scale of a pcolormesh given the scale, the minimum and the
    maximum.

    Returns
    -------
    - norm: Normalize
        The normalization of the colormap

    Parameters
    ----------
    - cscale (not optional): {'linear','log','symlog','twoslope'}, default 'linear'
        Sets the colorbar scale. Default is the linear ('norm') scale.
    - tresh (not optional): float
        Sets the threshold for the colormap. If not defined, the threshold will
        be set to 1% of the maximum absolute value of the variable.
        The default cases are the following:
        - twoslope colorscale: sets the limit between the two linear regimes.
        - symlog: sets the limit between the logaitrhmic and the linear regime.
    - vmax (not optional): float
        The maximum value of the colormap.
    - vmin (not optional): float
        The minimum value of the colormap.

    Notes
    -----
    - The lint keyword is deprecated, please use tresh instead

    ----

    Examples
    --------
    - Example #1: set a linear colormap between 0 and 1

        >>> _set_cscale('linear', 0.0, 1.0)

    - Example #2: set a logarithmic colormap between 0.1 and 1

        >>> _set_cscale('log', 0.1, 1.0)

    - Example #3: set a twoslope colormap between -1 and 1 with threshold 0.1

        >>> _set_cscale('twoslope', -1.0, 1.0, 0.1)

    """
    if lint is not None:
        warnings.warn(
            "'lint' keyword is deprecated, please use \
                       'tresh' instead",
            UserWarning,
        )

    if cscale == "log":
        norm = mcol.LogNorm(vmin=vmin, vmax=vmax)
    elif cscale == "symlog":
        norm = mcol.SymLogNorm(vmin=vmin, vmax=vmax, linthresh=tresh)
    elif cscale == "twoslope" or cscale == "2slope":
        norm = mcol.TwoSlopeNorm(vmin=vmin, vmax=vmax, vcenter=tresh)
    elif cscale == "power":
        norm = mcol.PowerNorm(gamma=tresh, vmin=vmin, vmax=vmax)
    elif cscale == "asinh":
        norm = mcol.AsinhNorm(vmin=vmin, vmax=vmax, linear_width=tresh)
    else:
        norm = mcol.Normalize(vmin=vmin, vmax=vmax)

    return norm
