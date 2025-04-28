from .libraries import *


def create_axes(
    self, ncol: int = 1, nrow: int = 1, check: bool = True, **kwargs: Any
) -> Axes:
    """
    Creation of a set of axes using add_subplot from the matplotlib library.

    If additional parameters (like the figure limits or the spacing)
    are given, the plots are located using set_position.
    The spacing and the ratio between the plots can be given by hand.
    In case only few custom options are given, the code computes the rest
    (but gives a small warning); in case no custom option is given, the axes
    are located through the standard methods of matplotlib.

    If more axes are created in the figure, the list of all axes is returned,
    otherwise the single axis is returned.

    Returns
    -------

    - The list of axes (if more axes are in the figure) or the axis
      (if only one axis is present)

    Parameters
    ----------

    - bottom: float, default 0.1
        The space from the bottom border to the last row of plots.
    - figsize: [float, float], default [6*sqrt(ncol),5*sqrt(nrow)]
        Sets the figure size. The default value is computed from the number
        of rows and columns.
    - fontsize: float, default 17.0
        Sets the fontsize for all the axes.
    - hratio: [float], default [1.0]
        Ratio between the rows of the plot. The default is that every plot
        row has the same height.
    - hspace: [float], default []
        The space between plot rows (in figure units). If not enough or
        too many spaces are considered, the program will remove the excess and
        fill the lacks with [0.1].
    - left: float, default 0.125
        The space from the left border to the leftmost column of plots.
    - ncol: int, default 1
        The number of columns of subplots.
    - nrow: int, default 1
        The number of rows of subplots.
    - proj: str, default None
        Custom projection for the plot (e.g. 3D). Recommended only if needed.
        WARNING: pyPLUTO does not support 3D plotting for now, only 3D axes.
        The 3D plot feature will be available in future releases.
    - right: float, default 0.9
        The space from the right border to the rightmost column of plots.
    - sharex: bool | str | Matplotlib axis, default False
        Enables/disables the sharing of the x-axis between the subplots.
    - sharey: bool | str | Matplotlib axis, default False
        Enables/disables the sharing of the y-axis between the subplots.
    - suptitle: str, default None
        Creates a figure title over all the subplots.
    - tight: bool, default True
        Enables/disables tight layout options for the figure. In case of a
        highly customized plot (e.g. ratios or space between rows and columns)
        the option is set by default to False since that option would not be
        available for standard matplotlib functions.
    - top: float, default 0.9
        The space from the top border to the first row of plots.
    - wratio: [float], default [1.0]
        Ratio between the columns of the plot. The default is that every plot
        column has the same width.
    - wspace: [float], default []
        The space between plot columns (in figure units). If not enough or
        too many spaces are considered, the program will remove the excess and
        fill the lacks with [0.1].

    Notes
    -----

    - The subplot_mosaic method of matplotlib will be implemented in future
      releases.
    - This method may return None in the future releases
    - Sharex and sharey will follow a different implementation in future
      releases

    ----

    Examples
    ========

    - Example #1: create a simple grid of 2 columns and 2 rows on a new figure

        >>> import pyPLUTO as pp
        >>> I = pp.Image()
        >>> ax = I.create_axes(ncol = 2, nrow = 2)

    - Example #2: create a grid of 2 columns with the first one having half the
        width of the second one

        >>> import pyPLUTO as pp
        >>> I = pp.Image()
        >>> ax = I.create_axes(ncol = 2, wratio = [0.5,1])

    - Example #3: create a grid of 2 rows with a lot of blank space between them

        >>> import pyPLUTO as pp
        >>> I = pp.Image()
        >>> ax = I.create_axes(nrow = 2, hspace = [0.5])

    - Example #4: create a 2x2 grid with a fifth image on the right side

        >>> import pyPLUTO as pp
        >>> I = pp.Image()
        >>> ax = I.create_axes(ncol = 2, nrow = 2, right = 0.7)
        >>> ax = I.create_axes(left = 0.75)

    """

    # Check parameters
    param = {
        "bottom",
        "figsize",
        "fontsize",
        "hratio",
        "hspace",
        "left",
        "ncol",
        "nrow",
        "proj",
        "right",
        "sharex",
        "sharey",
        "suptitle",
        "tight",
        "top",
        "wratio",
        "wspace",
    }
    if check is True:
        check_par(param, "create_axes", **kwargs)

    # Change fontsize if requested
    if "fontsize" in kwargs:
        plt.rcParams.update({"font.size": kwargs["fontsize"]})

    # Set of custom plot keywords
    custom_plot = False
    custom_axes = {
        "left",
        "right",
        "top",
        "bottom",
        "hspace",
        "hratio",
        "wspace",
        "wratio",
    }

    # Check if custom axes are given
    if any(arg in kwargs for arg in custom_axes):

        # Set the custom axes keywords
        custom_plot = True
        kwargs["tight"] = False

        # Get margins and subplots features
        left = kwargs.get("left", 0.125)
        right = kwargs.get("right", 0.9)
        top = kwargs.get("top", 0.9)
        bottom = kwargs.get("bottom", 0.1)
        hspace = kwargs.get("hspace", [])
        wspace = kwargs.get("wspace", [])
        wratio = kwargs.get("wratio", [1.0])
        hratio = kwargs.get("hratio", [1.0])

        # Check if the number of rows and columns is correct
        hspace, hratio = _check_rowcol(hratio, hspace, nrow, "rows")
        wspace, wratio = _check_rowcol(wratio, wspace, ncol, "cols")

        # Computes the height and width of every subplot
        hsize = top - bottom - sum(hspace)
        wsize = right - left - sum(wspace)
        htot = sum(hratio)
        wtot = sum(wratio)
        ll = left
        tt = top
        hplot = []
        wplot = []

        # Computes left, right of every ax
        for i in islice(range(ncol), ncol - 1):
            rr = wsize * wratio[i] / wtot
            wplot.append([ll, rr])
            ll += rr + wspace[i]

        # Computes top, bottom of every ax
        for i in islice(range(nrow), nrow - 1):
            bb = tt - hsize * hratio[i] / htot
            hplot.append([bb, tt - bb])
            tt = bb - hspace[i]

        # Append the last items without extra space
        rr = wsize * wratio[ncol - 1] / wtot
        wplot.append([ll, rr])

        bb = tt - hsize * hratio[nrow - 1] / htot
        hplot.append([bb, tt - bb])
    else:

        # Set the default axes features
        wplot = None
        hplot = None

    # Change the figure size if requested
    if "figsize" in kwargs:
        self.fig.set_figwidth(kwargs["figsize"][0])
        self.fig.set_figheight(kwargs["figsize"][1])
        self.figsize = kwargs["figsize"]
    # Set the figure size if not custom plot
    elif not custom_plot is True and self._set_size is False:
        self.fig.set_figwidth(6 * np.sqrt(ncol))
        self.fig.set_figheight(5 * np.sqrt(nrow))

    # Set the projection if requested
    proj = kwargs.get("proj", None)

    # Set sharex and sharey
    sharex = kwargs.get("sharex", False)
    sharey = kwargs.get("sharey", False)

    # Add axes and set position (if custom axes)
    for i in range(ncol * nrow):
        self._add_ax(
            self.fig.add_subplot(
                nrow + self.nrow0, ncol + self.ncol0, i + 1, projection=proj
            ),
            len(self.ax),
        )

        # Compute row and column
        row = int(i / ncol)
        col = int(i % ncol)

        # Set position if custom axes
        if wplot is not None and hplot is not None:
            self.ax[-1].set_position(
                pos=(
                    wplot[col][0],
                    hplot[row][0],
                    wplot[col][1],
                    hplot[row][1],
                )
            )

        # Share axes if requested
        if sharex is True and i > 0:
            self.ax[-1].sharex(self.ax[0])
        elif isinstance(sharex, Axes):
            self.ax[-1].sharex(sharex)
        if sharey is True and i > 0:
            self.ax[-1].sharey(self.ax[0])
        elif isinstance(sharey, Axes):
            self.ax[-1].sharey(sharey)

    # Updates rows and columns
    self.nrow0 = self.nrow0 + nrow
    self.ncol0 = self.ncol0 + ncol

    # Check length of output
    ret_ax = self.ax[0] if len(self.ax) == 1 else self.ax

    # Set figure title if requested
    if "suptitle" in kwargs:
        self.fig.suptitle(kwargs["suptitle"])

    # Tight layout (depending on the subplot creation)
    self.tight = kwargs.get("tight", self.tight)
    self.fig.set_layout_engine(None if not self.tight else "tight")

    # End of the function
    # Return the list of axes (if more than one) or the single axis (if only
    # one). WARNING: this return may be changed to None in future releases.
    return ret_ax


def set_axis(self, ax: Axes | None = None, check: bool = True, **kwargs: Any) -> None:
    """
    Customization of a single subplot axis.
    Properties such as the range, scale and aspect of each subplot
    should be customized here.

    Returns
    -------

    - None

    Parameters
    ----------

    - alpha: float, default 1.0
        Sets the opacity of the plot, where 1.0 means total opaque and 0.0 means
        total transparent.
    - aspect: {'auto', 'equal', float}, default 'auto'
        Sets the aspect ratio of the plot. The 'auto' keyword is the default
        option (most likely the plot will be squared). The 'equal' keyword will
        set the same scaling for x and y. A float will fix the ratio between the
        y-scale and the x-scale (1.0 is the same as 'equal').
    - ax: ax object, default None
        The axis to customize. If None the current axis will be selected.
    - fontsize: float, default 17.0
        Sets the fontsize for all the axis components (only for the current
        axis).
    - grid: bool | string, default False
        Enables/disables the grid on the plot. If True it enables both axes
        grids. If 'x' or 'y' it enables only the x or y axis grid.
    - labelsize: float, default fontsize
        Sets the labels fontsize (which is the same for both labels).
        The default value corresponds to the value of the keyword 'fontsize'.
    - minorticks: str, default None
        If not None enables the minor ticks on the plot (for both grid axes).
    - sharex: Matplotlib axis | False, default False
        Shares the x-axis with another axis.
    - sharey: Matplotlib axis | False, default False
        Shares the y-axis with another axis.
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
    - xrange: [float, float], default [0,1]
        Sets the range in the x-direction. If not defined the code will
        compute the range while plotting the data.
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

    - A function which sets seprartely the maximum and the minimum value in
        both x- and y- directions is needed.

    ----

    Examples
    ========

    - Example #1: create an axis and set title and labels on both axes

        >>> import pyPLUTO as pp
        >>> I = pp.Image()
        >>> ax = I.create_axes()
        >>> I.set_axis(title = 'Title', titlesize = 30.0, xtitle = 'x-axis',
        ... ytitle = 'y-axis')

    - Example #2: create an axis, remove the ticks for the x-axis and
        set manually the ticks for the y-axis

        >>> import pyPLUTO as pp
        >>> I = pp.Image()
        >>> ax = I.create_axes()
        >>> I.set_axis(ax, xticks = None, yrange = [-1.0,1.0],
        ... yticks = [-0.8,-0.6,-0.4,-0.2,0,0.2,0.4,0.6,0.8])

    - Example #3: create two axes and invert the direction of the ticks in the
        first one

        >>> import pyPLUTO as pp
        >>> I = pp.Image()
        >>> ax = I.create_axes(right = 0.7)
        >>> ax = I.create_axes(left = 0.8)
        >>> I.set_axis(ax = ax[0], ticksdir = 'out')

    - Example #4: create a 2x2 grid with axes labels and customed ticks

        >>> import pyPLUTO as pp
        >>> I = pp.Image()
        >>> ax = I.create_axes(ncol = 2, nrow = 2)
        >>> for i in [0,1,2,3]:
        ...     I.set_axis(ax = ax[i], xtitle = 'x-axis', ytitle = 'y-title',
        ...     xticks = [0.25,0.5,0.75], yticks = [0.25,0.5,0.75],
        ...     xtickslabels = ['1/4','1/2','3/4'])

    """

    # Check parameters
    param = {
        "alpha",
        "aspect",
        "ax",
        "fontsize",
        "grid",
        "labelsize",
        "minorticks",
        "sharex",
        "sharey",
        "ticksdir",
        "tickssize",
        "title",
        "titlepad",
        "titlesize",
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
        check_par(param, "set_axis", **kwargs)

    # Take last axis if not specified
    ax, nax = self._assign_ax(ax, **kwargs)

    # Set fontsize
    self.fontsize = kwargs.get("fontsize", self.fontsize)
    plt.rcParams.update({"font.size": self.fontsize})

    # Set aspect ratio
    if kwargs.get("aspect", True) is not True:
        ax.set_aspect(kwargs["aspect"])

    # Set xrange and yrange
    if kwargs.get("xrange", None) is not None:
        self._set_xrange(ax, nax, kwargs["xrange"], 3)
    if kwargs.get("yrange", None) is not None:
        self._set_yrange(ax, nax, kwargs["yrange"], 3)

    # Set title and axes labels
    if kwargs.get("title", None) is not None:
        ax.set_title(
            kwargs["title"],
            fontsize=kwargs.get("titlesize", self.fontsize),
            pad=kwargs.get("titlepad", 8.0),
        )
    if kwargs.get("xtitle", None) is not None:
        ax.set_xlabel(kwargs["xtitle"], fontsize=kwargs.get("labelsize", self.fontsize))
    if kwargs.get("ytitle", None) is not None:
        ax.set_ylabel(kwargs["ytitle"], fontsize=kwargs.get("labelsize", self.fontsize))

    # Set sharex and sharey
    if kwargs.get("sharex", False) is not False:
        ax.sharex(kwargs["sharex"])
    if kwargs.get("sharey", False) is not False:
        ax.sharey(kwargs["sharey"])

    # Set ticks size
    if kwargs.get("tickssize", True) is not True:
        ax.tick_params(axis="x", labelsize=kwargs["tickssize"])
        ax.tick_params(axis="y", labelsize=kwargs["tickssize"])
    else:
        ax.tick_params(axis="both", labelsize=self.fontsize)

    # Set ticks direction
    if kwargs.get("ticksdir") or self.tickspar[nax] == 0:
        tckd = kwargs.get("ticksdir", "in")
        ax.tick_params(
            axis="both", which="major", direction=tckd, right="off", top="off"
        )
        ax.tick_params(which="minor", direction=tckd, right="off", top="off")

    # Set minor ticks
    if kwargs.get("minorticks") or self.tickspar[nax] == 0:
        mintks = kwargs.get("minorticks", "on")
        ax.minorticks_on() if mintks != "off" else ax.minorticks_off()

    # Set parameter that fixes the minorticks and ticksdir
    self.tickspar[nax] = 1

    spar = {"asinh": "linear_width", "symlog": "linthresh"}

    # Scales and alpha
    if kwargs.get("xscale", True) is not True:
        xscale = kwargs["xscale"]
        xscale_param = spar.get(xscale)
        xscale_kwargs = (
            {xscale_param: kwargs.get("xtresh")} if "xtresh" in kwargs else {}
        )
        ax.set_xscale(xscale, **xscale_kwargs)
        self.xscale[nax] = xscale

    if kwargs.get("yscale", True) is not True:
        yscale = kwargs["yscale"]
        yscale_param = spar.get(yscale)
        yscale_kwargs = (
            {yscale_param: kwargs.get("ytresh")} if "ytresh" in kwargs else {}
        )
        ax.set_yscale(yscale, **yscale_kwargs)
        self.yscale[nax] = yscale

    if kwargs.get("alpha"):
        ax.set_alpha(kwargs["alpha"])

    # Set ticks and tickslabels
    xtc = kwargs.get("xticks", True)
    ytc = kwargs.get("yticks", True)
    xtl = kwargs.get("xtickslabels", True)
    ytl = kwargs.get("ytickslabels", True)
    if xtc is not True or xtl is not True:
        _set_ticks(ax, xtc, xtl, "x")
    if ytc is not True or ytl is not True:
        _set_ticks(ax, ytc, ytl, "y")

    # Sets grid on the axis
    if kwargs.get("grid", False) is True:
        ax.grid(True)
    elif isinstance(kwargs.get("grid", False), str):
        ax.grid(True, axis=kwargs["grid"])

    # Reinforces the tight_layout if needed
    if self.tight is not False:
        self.fig.tight_layout()

    # End of the function
    return None


def _check_rowcol(
    ratio: list[float], space: float | list[float], length: int, func: str
) -> tuple[list[float], list[float]]:
    """
    Checks the width and spacing of the plots on a single row or column.

    Returns
    -------

    - space: list[float]
        the space between the rows or columns
    - ratio: list[float]
        the ratio of the rows or columns

    Parameters
    ----------

    - ratio: list[float]
        the ratio of the rows or columns
    - space: list[float]
        the space between the rows or columns
    - length: int
        the number of rows or columns in the single row or column
    - func: str
        the function to check (rows or cols)

    Notes
    -----

    - None

    ----

    Examples
    ========

    - Example #1: ratio and space are given correctly (rows)

        >>> _check_rowcol([1,2,3], [0.1,0.2], 3, 'rows')

    - Example #2: ratio and space are given incorrectly (rows) (raises warning)

        >>> _check_rowcol([], 0.1, 3, 'rows')

    - Example #3: ratio and space are given correctly (cols)

        >>> _check_rowcol([1,2,3], [0.1,0.2], 3, 'cols')

    """

    rat = {"rows": "hratio", "cols": "wratio"}
    spc = {"rows": "hspace", "cols": "wspace"}

    # Check if space is a list
    # IF FLOAT MAKE IT LIST WITH THE VALUE!!!
    newspace = makelist(space)
    space = space if isinstance(space, list) else newspace * (length - 1)

    # Fill the lists with the default values
    ratio = ratio + [1.0] * (length - len(ratio))
    space = space + [0.1] * (length - len(space) - 1)

    # Check if the lists have the correct length
    if len(ratio) != length:
        warnings.warn(f"WARNING! {rat[func]} has wrong length!", UserWarning)
    if len(space) + 1 != length:
        warnings.warn(f"WARNING! {spc[func]} has wrong length!", UserWarning)

    # End of the function. Return the lists
    return space[: length - 1], ratio[:length]


def _set_ticks(
    ax: Axes,
    tc: str | list[float] | None,
    tl: str | list[str] | None,
    typeaxis: str,
) -> None:
    """
    Sets the ticks and ticks labels on the x- or y-axis of a selected axis.

    Returns
    -------

    - None

    Parameters
    ----------

    - ax: ax
        the selected set of axes
    - tc: list[float]
        the ticks of the x-axis
    - tl: list[float]
        the ticks labels of the x-axis
    - typeaxis: str
        the type of axis (x or y)

    Notes
    -----

    - None

    ----

    Examples
    ========

    - Example #1: set ticks and ticks labels on the x-axis

        >>> _set_ticks(ax, [0,1,2,3], ['0','1','2','3'], 'x')

    - Example #2: set ticks and ticks labels on the y-axis (no ticks)

        >>> _set_ticks(ax, None, None, 'y')

    - Example #3: set ticks and ticks labels on the x-axis (no ticks labels)

        >>> _set_ticks(ax, [0,1,2,3], None, 'x')

    """

    set_ticks = {"x": ax.set_xticks, "y": ax.set_yticks}
    set_label = {"x": ax.set_xticklabels, "y": ax.set_yticklabels}

    # Ticks are None
    if tc is None:

        set_ticks[typeaxis]([])
        set_label[typeaxis]([])

        # If tickslabels are not None raise a warning
        if tl is not None and tl is not True:
            warn = "Warning, tickslabels are defined with no" "ticks!! (function setax)"
            warnings.warn(warn, UserWarning)

    # Ticks are not None and tickslabels are custom
    elif tl is not True:

        # Ticks are not None, then are set
        if tc is not True and tl is not True:
            set_ticks[typeaxis](tc)

        # Ticks are Default with custom tickslabels, a warning is raised
        elif tl is not None:
            warn = (
                "Warning, tickslabels should be fixed only"
                "when ticks are fixed (function setax)"
            )
            warnings.warn(warn, UserWarning)

        # Ticks are set custom, then tickslabels are set
        if tl is None:
            set_label[typeaxis]([])
        else:
            set_label[typeaxis](tl)

    # Ticks are custom, tickslabels are default
    else:
        if tc is not True:
            set_ticks[typeaxis](tc)

    # End of the function
    return None
