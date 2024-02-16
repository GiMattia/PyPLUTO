from .libraries import *
from .h_pypluto import _check_par

def create_axes(self, 
                ncol: int = 1, 
                nrow: int = 1, 
                check: bool = True, 
                **kwargs: Any
               ):
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

    Examples
    --------

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
    param = {'bottom', 'figsize', 'fontsize', 'hratio', 'hspace', 'left', 'ncol', 
             'nrow', 'proj', 'right', 'suptitle', 'tight', 'top', 'wratio', 'wspace'}
    if check is True:
        _check_par(param, 'create_axes', **kwargs)

    if 'fontsize' in kwargs:
        plt.rcParams.update({'font.size': kwargs['fontsize']})

    custom_plot = False
    custom_axes = ['left', 'right', 'top', 'bottom', 'hspace', 'hratio', 'wspace', 'wratio']
    if any(arg in kwargs for arg in custom_axes):
        custom_plot     = True
        kwargs['tight'] = False

        left   = kwargs.get('left',0.125)
        right  = kwargs.get('right',0.9)
        top    = kwargs.get('top',0.9)
        bottom = kwargs.get('bottom',0.1)
        hspace = kwargs.get('hspace',[])
        wspace = kwargs.get('wspace',[])
        wratio = kwargs.get('wratio',[1.0])
        hratio = kwargs.get('hratio', [1.0])

        hspace, hratio  = _check_rows(hratio, hspace, nrow)
        wspace, wratio  = _check_cols(wratio, wspace, ncol)

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
        wplot = None
        hplot = None

    if 'figsize' in kwargs:
        self.fig.set_figwidth(kwargs['figsize'][0])
        self.fig.set_figheight(kwargs['figsize'][1])
        self.figsize = kwargs['figsize']
    elif not custom_plot is True and self._set_size is False:
        self.fig.set_figwidth(6*np.sqrt(ncol))
        self.fig.set_figheight(5*np.sqrt(nrow))

    proj = kwargs.get('proj', None)

    # Add axes
    for i in range(ncol*nrow):
        self._add_ax(self.fig.add_subplot(nrow + self.nrow0, ncol + self.ncol0, 
                                           i+1, projection=proj), len(self.ax))
        if wplot is not None and hplot is not None:
            row = int(i/ncol)
            col = int(i%ncol)
            self.ax[-1].set_position(pos=(wplot[col][0], hplot[row][0],
                                          wplot[col][1], hplot[row][1]))

    # Updates rows and columns
    self.nrow0 = self.nrow0 + nrow
    self.ncol0 = self.ncol0 + ncol

    # Check length of output
    ret_ax = self.ax[0] if len(self.ax) == 1 else self.ax

    # Suptitle
    if 'suptitle' in kwargs:
        self.fig.suptitle(kwargs['suptitle'])

    # Tight layout
    self.tight = kwargs.get('tight', self.tight)
    self.fig.set_tight_layout(None if not self.tight else 'tight')
    return ret_ax

def set_axis(self, 
             ax: Axes | None = None, 
             check: bool = True, 
             **kwargs: Any
            ):
    """
        Customization of a single subplot axis.
        Properties such as the range, scale and aspect of each subplot
        should be customized here.

        Returns
        -------
            None

        Parameters
        ----------
            - alpha: float, default 1.0
                Sets the opacity of the plot, where 1.0 means total opaque and 0.0 means
                total transparent.
            - aspect: {'auto', 'equal', float}, default 'auto'
                Sets the aspect ratio of the plot.
                The 'auto' keyword is the default option (most likely the plot will
                be squared). The 'equal' keyword will set the same scaling for
                x and y. A float will fix the ratio between the y-scale and the x-scale
                (1.0 is the same as 'equal').
            - ax: ax object, default None
                The axis to customize. If None the current axis will be selected.
            - fontsize: float, default 17.0
                Sets the fontsize for all the axis components (only for the current axis).
            - labelsize: float, default fontsize
                Sets the labels fontsize (which is the same for both labels).
                The default value corresponds to the value of the keyword 'fontsize'.
            - minorticks: str, default None
                If not None enables the minor ticks on the plot (for both grid axes).
            - ticksdir: {'in', 'out'}, default 'in'
                Sets the ticks direction. The default option is 'in'.
            - tickssize: float, default fontsize
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
                If enabled (and different from 'Default'), sets automatically the scale
                on the x-axis. Data in log scale should be used with the keyword 'log',
                while data in linear scale should be used with the keyword 'linear'.
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
                If enabled (and different from 'Default'), sets automatically the scale
                on the y-axis. Data in log scale should be used with the keyword 'log',
                while data in linear scale should be used with the keyword 'linear'.
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

    Notes
    -----

        - A function which sets seprartely the maximum and the minimum value in
            both x- and y- directions is needed.

    Examples
    --------

             - Example #1: create an axis and set title and labels on both axes

               >>> import pyPLUTO as pp
               >>> I = pp.Image()
               >>> ax = I.create_axes()
               >>> I.set_axis(title = 'Title', titlesize = 30.0, xtitle = 'x-axis', ytitle = 'y-axis')

             - Example #2: create an axis, remove the ticks for the x-axis and set manually the ticks for the y-axis

               >>> import pyPLUTO as pp
               >>> I = pp.Image()
               >>> ax = I.create_axes()
               >>> I.set_axis(ax, xticks = None, yrange = [-1.0,1.0], yticks = [-0.8,-0.6,-0.4,-0.2,0,0.2,0.4,0.6,0.8])

             - Example #3: create two axes and invert the direction of the ticks in the first one

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
               >>>   I.set_axis(ax = ax[i], xtitle = 'x-axis', ytitle = 'y-title', xticks = [0.25,0.5,0.75], yticks = [0.25,0.5,0.75], xtickslabels = ['1/4','1/2','3/4'])

    """

    # Take last axis if not specified
    ax = self.fig.gca() if ax is None else ax
    nax: int = self._check_fig(ax)

    # Check for unknown keywords
    param: set = {'alpha', 'aspect', 'ax', 'fontsize', 'labelsize', 
             'minorticks', 'ticksdir', 'tickssize', 'title', 'titlepad', 
             'titlesize', 'xrange', 'xscale', 'xticks', 'xtickslabels', 
             'xtitle', 'yrange', 'yscale', 'yticks', 'ytickslabels', 'ytitle'}
    
    if check is True:
        _check_par(param, 'set_axis', **kwargs)

    # Set fontsize
    if 'fontsize' in kwargs:
        plt.rcParams.update({'font.size': self.fontsize})

    # Set aspect ratio
    if kwargs.get('aspect','Default') != 'Default':
        ax.set_aspect(kwargs['aspect'])

    # Set xrange and yrange
    if kwargs.get('xrange',None) is not None:
        self._set_xrange(ax, nax, kwargs['xrange'], 3)
    if kwargs.get('yrange',None) is not None:
        self._set_yrange(ax, nax, kwargs['yrange'], 3)

    # Set title and axes labels
    if kwargs.get('title',None) is not None:
        ax.set_title(kwargs['title'],   fontsize = kwargs.get('titlesize',self.fontsize), 
                                        pad      = kwargs.get('titlepad', 8.0))
    if kwargs.get('xtitle',None) is not None:
        ax.set_xlabel(kwargs['xtitle'], fontsize = kwargs.get('labelsize',self.fontsize))
    if kwargs.get('ytitle',None) is not None:
        ax.set_ylabel(kwargs['ytitle'], fontsize = kwargs.get('labelsize',self.fontsize))

    # Set tickssize
    if kwargs.get('tickssize','Default') != 'Default':
        ax.tick_params(axis='x', labelsize = kwargs['tickssize'])
        ax.tick_params(axis='y', labelsize = kwargs['tickssize'])

    # Minor ticks and ticks direction
    if kwargs.get('ticksdir') or self.tickspar[nax] == 0:
        tckd = kwargs.get('ticksdir', 'in')
        ax.tick_params(axis='both', which='major', direction=tckd, right='off', top='off')
        ax.tick_params(which='minor', direction=tckd, right='off', top='off')

    if kwargs.get('minorticks') or self.tickspar[nax] == 0:
        ax.minorticks_on() if kwargs.get('minorticks', 'on') != 'off' else ax.minorticks_off()

    self.tickspar[nax] = 1


    # Scales and alpha
    if kwargs.get('xscale','Default') != 'Default':
        ax.set_xscale(kwargs['xscale'])
    if kwargs.get('yscale','Default') != 'Default':
        ax.set_yscale(kwargs['yscale'])
    if kwargs.get('alpha'):
        ax.set_alpha(kwargs['alpha'])

    # Set ticks and tickslabels
    xtc: str | list[float] | None = kwargs.get('xticks', 'Default')
    ytc: str | list[float] | None = kwargs.get('yticks', 'Default')
    xtl: str | list[str] | None = kwargs.get('xtickslabels', 'Default')
    ytl: str | list[str] | None = kwargs.get('ytickslabels', 'Default')
    if xtc != 'Default' or xtl != 'Default':
        _set_xticks(ax, xtc, xtl)
    if ytc != 'Default' or ytl != 'Default':
        _set_yticks(ax, ytc, ytl)

    # Reinforces the tight_layout if needed
    if self.tight is not False:
        self.fig.tight_layout()

    return None

def _check_rows(hratio: list[float], 
                hspace: float | list[float], 
                nrow: int
               ) -> tuple[list[float], list[float]]:
    """
    Checks the width and spacing of the plots on a single column

    Returns
    -------

        - hspace: list[float]
            the space between the rows
        - hratio: list[float]
            the ratio of the rows

    Parameters
    ----------

        - hratio: list[float]
            the ratio of the rows
        - hspace: list[float]
            the space between the rows
        - nrow: int
            the number of rows in the single column
    """

    hspace = [hspace] if not isinstance(hspace, list) else hspace
    hratio = hratio + [1.0] * (nrow - len(hratio))
    hspace = hspace + [0.1] * (nrow - len(hspace) - 1)

    if len(hratio) != nrow:
        warnings.warn('WARNING! hratio has wrong length!', UserWarning)

    if len(hspace) + 1 != nrow:
        warnings.warn('WARNING! hspace has wrong length!', UserWarning)

    return hspace[:nrow - 1], hratio[:nrow]

def _check_cols(wratio: list[float], 
                wspace: float | list[float], 
                ncol: int
               ) -> tuple[list[float], list[float]]:
    """
    Checks the width and spacing of the plots on a single row

    Returns
    -------

        - wspace: list[float]
            the space between the columns
        - wratio: list[float]
            the ratio of the columns

    Parameters
    ----------

        - wratio: list[float]
            the ratio of the columns
        - wspace: list[float]
            the space between the columns
        - ncol: int
            the number of columns in the single row

    """

    '''
    check_cols function:
    Checks the width and spacing of the plots on a single row
    **Inputs:**
        wratio -- the ratio of the columns\n
        wspace -- the space between the columns\n
        ncol -- the number of columns in the single row
    '''
    wspace = [wspace] if not isinstance(wspace, list) else wspace
    wratio = wratio + [1.0] * (ncol - len(wratio))
    wspace = wspace + [0.1] * (ncol - len(wspace) - 1)

    if len(wratio) != ncol:
        warnings.warn('WARNING! wratio has wrong length!', UserWarning)

    if len(wspace) + 1 != ncol:
        warnings.warn('WARNING! wspace has wrong length!', UserWarning)

    return wspace[:ncol - 1], wratio[:ncol]

def _set_xticks(ax: Axes, 
                xtc: str | list[float] | None, 
                xtl: str | list[str] | None
               ) -> None:
    """
    Sets the ticks and ticks labels on the x-axis of a selected axis.

    Returns
    -------

        None

    Parameters
    ----------

        - ax: ax
            the selected set of axes
        - xtc: list[float]
            the ticks of the x-axis
        - xtl: list[float]
            the ticks labels of the x-axis
    """

    if xtc is None:
        ax.set_xticks([])
        ax.set_xticklabels([])
        if xtl not in {None, 'Default'}:
            warning_message: str = "Warning, tickslabels are defined with no ticks!! (function setax)"
            warnings.warn(warning_message, UserWarning)
    elif xtl != 'Default':
        if xtc != 'Default':
            ax.set_xticks(xtc)
        elif xtl is not None:
            warning_message: str = "Warning, tickslabels should be fixed only when ticks are fixed (function setax)"
            warnings.warn(warning_message, UserWarning)
        if xtl is None:
            ax.set_xticklabels([])
        else:
            ax.set_xticklabels(xtl)
    else:
        if xtc != 'Default':
            ax.set_xticks(xtc)
    return None


def _set_yticks(ax: Axes, 
                ytc: str | list[float] | None, 
                ytl : str | list[str] | None
               ) -> None:
    """
    Sets the ticks and ticks labels on the y-axis of a selected axis.

    Returns
    -------

        None

    Parameters
    ----------

        - ax: ax
            the selected set of axes
        - ytc: list[float]
            the ticks of the y-axis
        - ytl: list[float]
            the ticks labels of the y-axis
    """

    if ytc is None:
        ax.set_yticks([])
        ax.set_yticklabels([])
        if ytl not in {None, 'Default'}:
            print('Warning, define tickslabels with no ticks!! (function setax)')
    elif ytl != 'Default':
        if ytc != 'Default':
            ax.set_yticks(ytc)
        elif ytl is not None:
            print('Warning, tickslabels should be fixed only when ticks are fixed (function setax)')
        if ytl == None:
            ax.set_yticklabels([])
        else:
            ax.set_yticklabels(ytl)
    else:
        if ytc != 'Default':
            ax.set_yticks(ytc)
    return None