from .libraries import *

def _check_fig(self,ax):
    """
    Finds the figure given a set of axes.
    If the set of axes does not belong to the figure, it raises an error.

    Returns
    -------

        The number of the selected set of axes
    
    Parameters
    ----------

        - ax: axes
            the set of axes
    """

    # Get the figure associated to the axes
    fig = ax.get_figure()

    # Check if the figure is the same as the one in the class
    if fig != self.fig:
        raise ValueError("The provided axes does not belong to the expected figure.")
    
    # Find the number of the axes and return it
    nax = self.ax.index(ax)
    return nax

def _add_ax(self,ax,i):
    """
    Adds the axes properties to the class info variables.
    The corresponding axis is appended (TO CHANGE!!! or at least
    to be checked) to the list of axes.

    Returns
    -------

        None

    Parameters

        - ax: ax
            the axis to be added
        - i: int
            the index of the axis in the list
    """

    self.ax.append(ax)
    self.nline.append(0)
    self.ntext.append(None)
    self.setax.append(0)
    self.setay.append(0)
    self.legpos.append(None)
    self.legpar.append([self.fontsize,1,2,0.8])
    self.vlims.append([])
    self.tickspar.append(0)
    self.shade.append('auto')
    self.ax[i].annotate(str(i),(0.47,0.47),xycoords='axes fraction')

    return None

def _place_inset_pos(self, ax, pos):
    """
    Places an inset axes given the position (left, top, bottom, right).

    Returns
    -------

        - The inset axes

    Parameters
    ----------

        - ax: ax
            the axis where the inset axes is placed
        - pos: list[float]
            the position of the inset axes
    """

    # Compute the position of the inset axis and return it
    left   = pos[0]
    bottom = pos[2]
    width  = pos[1] - pos[0]
    height = pos[3] - pos[2]
    return ax.inset_axes([left, bottom, width, height])

def _place_inset_loc(self, ax, **kwargs):
    """
    Places an inset axes given different keywords.
    In case both top and bottom are given, the top is given priority and a warning is
    raised.

    Returns
    -------

        - The inset axes

    Parameters
    ----------

        - ax: ax
            the axis where the inset axes is placed
        - left: float
            the left boundary
        - top: float
            the top boundary
        - bottom: float
            the bottom boundary
        - width: float
            the width of the inset axis
        - height: float
            the height of the inset axis
    """

    # Check if both "top" and "bottom" keywords are given
    if kwargs.get('top') and kwargs.get('bottom'):
         warning_message = """
            Both top and bottom keywords are given, priority goes to the top"""
         warnings.warn(warning_message, UserWarning)
    
    # Compute the position of the inset axis and return it
    left   = kwargs.get('left', 0.6)
    width  = kwargs.get('width', 0.2)
    height = kwargs.get('height', 0.15)
    bottom = kwargs.get('top', 0.75) - height
    bottom = kwargs.get('bottom', 0.6)
    return ax.inset_axes([left, bottom, width, height])


def _hide_text(self, nax: int, txts: str) -> None:
    """
    Hides the text placed when an axis is created (the number of the axis).

    Returns
    -------

        None

    Parameters
    ----------

        - nax: int
            the number of the selected set of axes
        - txts: str
            the text of the selected set of axes
    """

    # Check if the text has already been removed
    if self.ntext[nax] is None:
        [txt.set_visible(False) for txt in txts]

        # Set the text as removed
        self.ntext[nax] = 1
    return None

def _set_parax(self, ax, **kwargs):
    """
    Selects the correct parameters to be set before calling the 
    set_axis method.

    Returns
    -------

        None

    Parameters
    ----------

        - ax: ax
            the selected set of axes
        - **kwargs: dict
            the selected parameters
    """
    # Set of the possible parameters
    param = {'alpha', 'aspect', 'ax', 'fontsize', 'labelsize', 'minorticks', 'ticksdir', 'tickssize', 'title', 'titlepad', 'titlesize', 'xrange', 
             'xscale', 'xticks', 'xtickslabels', 'xtitle', 'yrange', 'yscale', 'yticks', 'ytickslabels', 'ytitle'}
    
    # Initialize the parameters dictionary and insert the allowed keywords
    axpar = {}
    for i in kwargs.keys():
        if i in param:
            axpar[i] = kwargs[i]

    # Call of the function set_axis to set the parameters
    self.set_axis(ax = ax, check = False, **axpar)

    return None

def _check_par(self, par, func, **kwargs):
    """
    Checks if a parameter is in the corresponding list
    depending on the function. If the parameter does not
    belong to the list it raises a warning.

    Returns
    -------

        None

    Parameters
    ----------

        - par: list[str]
            the function parameters
        - func: str
            the name of the function
        - **kwargs: dict
            the selected parameters

    """

    # Check if the parameters are in the list
    notfound = [(i) for i in kwargs.keys() if i not in par]

    # If the parameters are not in the list, raise a warning
    if len(notfound) > 0:
        warning_message = f"""WARNING: elements {str(notfound)} not found! Please check your spelling! (function {func})"""
        warnings.warn(warning_message, UserWarning)

    return None

def _set_xrange(self, ax, nax, xlim, case):
    """
    Sets the lower and upper limits of the x-axis of a set of axes (if
    not stated otherwise later).
    IMPORTANT: PUT CHANCE TO SET ONLY ONE LIMIT!!!

    Returns
    -------

        None

    Parameters
    ----------

        - ax: ax
            the selected set of axes
        - nax: int
            the number of the selected set of axes
        - xlim: list[float]
            the limits of the x-axis
        - case: int
            the case in exam (if range is fixed or variable)
    """

    # Case 0: the x-axis limits are set automatically (no previous limit)
    if case == 0:
        ax.set_xlim(xlim[0],xlim[1])

        # Case switched to 2 (previous limits are present now)
        self.setax[nax] = 2

    # Case 1: limits are already set and they should not be changed (aka do nothing)

    # Case 2: the x-axis limit are changed automatically (previous limit present)
    if case == 2:
        xmin = min(xlim[0],ax.get_xlim()[0])
        xmax = max(xlim[1],ax.get_xlim()[1])
        ax.set_xlim(xmin,xmax)

    # Case 3: x-axis limits must be set manually
    if case == 3:
        ax.set_xlim(xlim[0],xlim[1])

        # Case switched to 1 (no change unless stated explicitly otherwise)
        self.setax[nax] = 1

    return None

def _set_yrange(self, ax, nax, ylim, case, x = None, y = None):
    """
    Sets the lower and upper limits of the y-axis of a set of axes (if
    not stated otherwise later).
    Unlike the x-axis, the y-axis limits are recovered depending on both
    the x-data and the y-data.

    IMPORTANT: PUT CHANCE TO SET ONLY ONE LIMIT!!!

    Returns
    -------

        None

    Parameters
    ----------

        - ax: ax
            the selected set of axes
        - nax: int
            the number of the selected set of axes
        - ylim: list[float]
            the limits of the y-axis
        - case: int
            the case in exam (if range is fixed or variable)
        - x: list[float]
            the x-array (to limit the y-range automatically)
        - y: list[float]
            the y-array (to limit the y-range automatically)
    """

    # Case 0: the y-axis limits are set automatically (no previous limit)
    if case == 0:

        # Find the limits of the x-axis
        yrange = np.where(np.logical_and(x >= x.min(), x <= x.max()))
        smally = y[yrange]

        # Extend slightly the range (not perfect method)
        ymin   = smally.min() - 0.1*np.abs(smally.min())
        ymax   = smally.max() + 0.1*np.abs(smally.max())
        ax.set_ylim(ymin,ymax)

        # Switch to case 2 (previous limits are present now)
        self.setay[nax] = 2

    # Case 1: limits are already set and they should not be changed (aka do nothing)

    # Case 2: the y-axis limit are changed automatically (previous limit present)
    if case == 2:

        # Find the limits of the x-axis
        yrange = np.where(np.logical_and(x >= x.min(), x <= x.max()))
        smally = y[yrange]

        # Extend slightly the range (not perfect method)        
        ymin   = smally.min() - 0.1*np.abs(smally.min())
        ymax   = smally.max() + 0.1*np.abs(smally.max())

        # Check if the limits should be changed
        ymin = np.minimum(ymin,ax.get_ylim()[0])
        ymax = np.maximum(ymax,ax.get_ylim()[1])
        ax.set_ylim(ymin,ymax)

    # Case 3: y-axis limits must be set manually
    if case == 3:
        ax.set_ylim(ylim[0],ylim[1])

        # Case switched to 1 (no change unless stated explicitly otherwise)
        self.setay[nax] = 1

    return None

def _set_xticks(self, ax, xtc, xtl):
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
            warning_message = "Warning, tickslabels are defined with no ticks!! (function setax)"
            warnings.warn(warning_message, UserWarning)
    elif xtl != 'Default':
        if xtc != 'Default':
            ax.set_xticks(xtc)
        elif xtl is not None:
            warning_message = "Warning, tickslabels should be fixed only when ticks are fixed (function setax)"
            warnings.warn(warning_message, UserWarning)
        if xtl is None:
            ax.set_xticklabels([])
        else:
            ax.set_xticklabels(xtl)
    else:
        if xtc != 'Default':
            ax.set_xticks(xtc)
    return None


def _set_yticks(self, ax, ytc, ytl):
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

def _check_rows(self, hratio, hspace, nrow):
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

def _check_cols(self, wratio, wspace, ncol):
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

def _set_cscale(self, cscale, vmin, vmax, tresh = None, lint = None):
    """
    Sets the color scale of a pcolormesh given the scale, the minimum and the maximum.

    Returns
    -------

        - norm: Normalize
            the normalization of the colormap

    Parameters
    ----------

        - cscale: str
            the scale of the colormap
        - vmin: float
            the minimum of the colormap
        - vmax: float
            the maximum of the colormap
        - tresh: float
            the threshold between subscales (twoscale or symlog color scales)
        - lint: float
            the threshold between subscales (twoscale or symlog color scales), deprecated

    """
    
    if lint is not None and tresh is not None:
        warnings.warn("'lint' and 'tresh' keyworda are both present, 'tresh' is used", UserWarning)
    elif lint is not None:
        warnings.warn("'lint' keyword is deprecated, please use 'tresh' instead", UserWarning)
        tresh = lint


    if cscale == 'log':
        norm = mcol.LogNorm(vmin = vmin,vmax = vmax)
    elif cscale == 'symlog':
        norm = mcol.SymLogNorm(vmin = vmin,vmax = vmax,linthresh = tresh)
    elif cscale == 'twoslope':
        norm = mcol.TwoSlopeNorm(vmin = vmin, vcenter = tresh, vmax = vmax)
    else:
        norm = mcol.Normalize(vmin = vmin,vmax = vmax)
    return norm

def _assign_ax(self, ax, **kwargs):
    """
    Sets the axes of the figure where the plot/feature should go.
    If no axis is present, an axis is created. If the axis is present
    but no axis is seletced, the last axis is selected.

    Returns
    -------

        - ax: ax
            the selected set of axes
        - nax: int
            the number of the selected set of axes

    Parameters
    ----------

        - ax: ax
            the selected set of axes
        - **kwargs: dict
            the selected parameters
    """

    if ax is None and len(self.ax) == 0:
        ax = self.create_axes(ncol = 1, nrow = 1, check = False, **kwargs)

    elif ax is None and len(self.ax) > 0:
        ax  = self.fig.gca()

    nax = self._check_fig(ax)
    return ax, nax

def _assign_default(self):
    """
    Assigns the default figures conditions.
    IMPORTANT! Replace the lists with a dictionary!

    Returns
    -------

        None
    
    Parameters
    ----------

        None
    """

    self.fontsize: int  = 17
    self.tight: bool = True
    self.nwin: int = 1
    self.figsize = [8,5]
    self._set_size = False
    self.nrow0    = 0
    self.ncol0    = 0
    self.ax       = []
                    # black, red, blue, cyan, green, orange
    self.color    = ['k','#d7263d','#1815c5','#12e3c0','#3f6600','#f67451']
    self.vlims    = []
    self.nline    = []
    self.ntext    = []
    self.setax    = []
    self.setay    = []
    self.legpos   = []
    self.legpar   = []
    self.tickspar = []
    self.shade    = []
    #self.LaTeX    = LaTeX
    return None

def _assign_LaTeX(self, LaTeX, fontweight):
    """
    Sets the LaTeX conditions. The option 'pgf' requires XeLaTeX
    and should be used only to get vectorial figures with minimal file size.

    Returns
    -------

        None

    Parameters
    ----------

        - LaTeX: bool
            the LaTeX option
        - fontweight: str
            the fontweight of the LaTeX text
    """
    if LaTeX is True:
        mpl.rcParams['mathtext.fontset'] = 'stix'
        mpl.rcParams['font.family'] = 'STIXGeneral'

    if LaTeX == 'pgf':
        plt.switch_backend('pgf')

        pgf_preamble = r"""
        \usepackage{amsmath}
        \usepackage{amssymb}
        \usepackage{mathptmx}
        \newcommand{\DS}{\displaystyle}
        """

        mpl.rcParams.update({
            'pgf.preamble': pgf_preamble,
            'font.family': 'serif',
            'font.weight': fontweight,
            'text.usetex': True
        })

    return None


