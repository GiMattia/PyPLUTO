from .libraries import *

def _check_fig(self, ax: Axes) -> int:
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
    fig: Figure | None = ax.get_figure()

    # Check if the figure is the same as the one in the class
    if fig != self.fig:
        raise ValueError("The provided axes does not belong to the expected figure.")
    
    # Find the number of the axes and return it
    nax: int = self.ax.index(ax)
    return nax

def _add_ax(self,
            ax: Axes,
            i: int
           ) -> None:
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


def _hide_text(self, nax: int, txts) -> None:
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

def _set_parax(self, ax: Axes, **kwargs: Any) -> None:
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
    param: set = {'alpha', 'aspect', 'ax', 'fontsize', 'labelsize', 'minorticks', 'ticksdir', 'tickssize', 'title', 'titlepad', 'titlesize', 'xrange', 
             'xscale', 'xticks', 'xtickslabels', 'xtitle', 'yrange', 'yscale', 'yticks', 'ytickslabels', 'ytitle'}
    
    # Initialize the parameters dictionary and insert the allowed keywords
    axpar: dict = {}
    for i in kwargs.keys():
        if i in param:
            axpar[i] = kwargs[i]

    # Call of the function set_axis to set the parameters
    self.set_axis(ax = ax, check = False, **axpar)

    return None

def _set_xrange(self, 
                ax: Axes, 
                nax: int, 
                xlim: list[float], 
                case: int
               ) -> None:
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
        xmin: float = min(xlim[0],ax.get_xlim()[0])
        xmax: float = max(xlim[1],ax.get_xlim()[1])
        ax.set_xlim(xmin,xmax)

    # Case 3: x-axis limits must be set manually
    if case == 3:
        ax.set_xlim(xlim[0],xlim[1])

        # Case switched to 1 (no change unless stated explicitly otherwise)
        self.setax[nax] = 1

    return None

def _set_yrange(self, 
                ax: Axes, 
                nax: int, 
                ylim: list[float], 
                case: int, 
                x: NDArray | None = None, 
                y: NDArray | None = None
                ) -> None:
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
        if x is None or y is None:
            raise ValueError("x and y arrays must be provided if case is 0")

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

        if x is None or y is None:
            raise ValueError("x and y arrays must be provided if case is 2")

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

def _assign_ax(self, 
               ax: Axes | list[Axes] | None, 
               **kwargs: Any
              ) -> tuple[Axes, int]:
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

    if isinstance(ax, list):
        ax = ax[0]
    elif ax is None:
        ax = self.fig.gca()

    nax = self._check_fig(ax)
    return ax, nax


