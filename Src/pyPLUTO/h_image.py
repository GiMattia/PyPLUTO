from .libraries import *

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

    - None

    Parameters

    - ax: ax
        the axis to be added
    - i: int
        the index of the axis in the list

    Notes
    -----

    - None

    Examples
    --------

    - Example #1: Add the axis to the class info variables

        >>> _add_ax(ax, i)

    """

    # Append the axis to the list of axes
    self.ax.append(ax)

    # Append the axis properties to the class info variables
    self.nline.append(0)
    self.ntext.append(None)
    self.setax.append(0)
    self.setay.append(0)
    self.legpos.append(None)
    self.legpar.append([self.fontsize,1,2,0.8,0.8])
    self.vlims.append([])
    self.tickspar.append(0)
    self.shade.append('auto')

    # Position the axis index in the middle of the axis
    self.ax[i].annotate(str(i),(0.47,0.47),xycoords='axes fraction')

    # End of the function
    return None


def _hide_text(self, 
               nax: int, 
               txts: str | None
              ) -> None:
    """
    Hides the text placed when an axis is created (the axis index).

    Returns
    -------

    - None

    Parameters
    ----------

    - nax: int
        the number of the selected set of axes
    - txts: str
        the text of the selected set of axes

    Notes
    -----

    - None

    Examples
    --------

    - Example #1: Hide the text of the selected set of axes

        >>> _hide_text(nax, txts)

    """

    # Check if the text has already been removed
    if self.ntext[nax] is None:
        [txt.set_visible(False) for txt in txts]

        # Set the text as removed
        self.ntext[nax] = 1

    # End of the function
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

    Returns
    -------

    - None

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

    Notes
    -----

    - The chance to set only one limit dinamically will be implemented
      in the future.

    Examples
    --------

    - Example #1: Set the x-axis limits of the selected set of axes

        >>> _set_xrange(ax, nax, xlim, case)

    """

    # Case 0: the x-axis limits are set automatically (no previous limit)
    if case == 0:
        ax.set_xlim(xlim[0],xlim[1])

        # Case switched to 2 (previous limits are present now)
        self.setax[nax] = 2

    # Case 1: limits are already set and they should not be changed 
    #         (aka do nothing)

    # Case 2: the x-axis limit are changed automatically 
    #         (previous limit present)
    if case == 2:
        xmin = min(xlim[0],ax.get_xlim()[0])
        xmax = max(xlim[1],ax.get_xlim()[1])
        ax.set_xlim(xmin,xmax)

    # Case 3: x-axis limits are set manually
    if case == 3:
        ax.set_xlim(xlim[0],xlim[1])

        # Case switched to 1 (no change unless stated explicitly otherwise)
        self.setax[nax] = 1

    # End of the function
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

    Notes
    -----

    - The chance to set only one limit dinamically will be implemented
      in the future. 

    Examples
    --------

    - Example #1: Set the y-axis limits of the selected set of axes

        >>> _set_yrange(ax, nax, ylim, case)  
            
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

    # Case 1: limits are already set and they should not be changed 
    # (aka do nothing)

    # Case 2: the y-axis limit are changed automatically 
    #(previous limit present)
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

    # End of the function
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

    Notes
    -----

    - None

    Examples
    --------

    - Example #1: Set the axes of the figure

        >>> _assign_ax(ax, **kwargs)

    - Example #2: Set the axes of the figure (no axis selected)

        >>> _assign_ax(None, **kwargs)

    - Example #3: Set the axes of the figure (axis is a list)

        >>> _assign_ax([ax], **kwargs)

    """

    # Check if the axis is None and no axis is present (and create one)
    if ax is None and len(self.ax) == 0:
        ax = self.create_axes(ncol = 1, nrow = 1, check = False, **kwargs)

    # Check if the axis is None and an axis is present (and select the last one)
    elif ax is None and len(self.ax) > 0:
        ax  = self.fig.gca()

    # Check if the axis is a list and select the first element
    elif isinstance(ax, list):
        ax = ax[0]
    # If none of the previous cases is satisfied assert that ax is an axis
    elif not isinstance(ax, Axes):
        raise ValueError("The provided axis is not valid.")

    # Get the figure associated to the axes
    fig = ax.get_figure()

    # Check if the figure is the same as the one in the class
    if fig != self.fig:
        text = "The provided axis does not belong to the expected figure."
        raise ValueError(text)
    
    # Find the number of the axes and return it
    nax = self.ax.index(ax)

    # Return the axis and its index
    return ax, nax

def _choose_colorlines(self, 
                      numcolor: int,
                      oldcolor: bool,
                      withblack: bool = False,
                      withwhite: bool = False
                     ) -> list[str]:
    """

    Returns
    -------

    - colors: list[str]
        the list of colors for the lines

    """
    if oldcolor:    # black, red, blue, cyan, green, orange
        return ['k','#d7263d','#1815c5', '#12e3c0','#3f6600','#f67451']
    
    dictcol = { 0: '#ffffff',  1: '#e8ecfb',  2: '#d9cce3',  3: '#d1bbd7', 
                4: '#caaccb',  5: '#ba8db4',  6: '#ae76a3',  7: '#aa6f9e',
                8: '#994f88',  9: '#882e72', 10: '#1965b0', 11: '#437dbf',
               12: '#5289c7', 13: '#6195cf', 14: '#7bafde', 15: '#4eb265',
               16: '#90c987', 17: '#cae0ab', 18: '#f7f056', 19: '#f7cb45',
               20: '#f6c141', 21: '#f4a736', 22: '#f1932d', 23: '#ee8026',
               24: '#e8601c', 25: '#e65518', 26: '#dc050c', 27: '#a5170e',
               28: '#72190e', 29: '#42150a', 30: '#777777', 31: '#000000'}
    
    lstc = [10,26,18,15,14,17,9,25,28,23,11,2,5,7,16,21,8,27,4,13,19,29,1,30]

    lstc = [0] + lstc if withwhite else [31] + lstc if withblack else lstc
    return [dictcol[lstc[i]] for i in range(numcolor)]



