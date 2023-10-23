from .libraries import *

def scatter(self, x, y, **kwargs):
    '''
    Plots a scatter of particles or discrete points.

    Returns
    -------
        None

    Parameters
    ----------
        - x: str
            the x variable to plot
        - y: str
            the y variable to plot

    Examples
    --------

    '''
    # Check parameters

    # Set or create figure and axes
    ax, nax = self._assign_ax(kwargs.pop('ax',None),**kwargs)

    # Set ax parameters
    self._set_parax(ax, **kwargs)
    self._hide_text(nax, ax.texts)

    # Keyword xrange and yrange
    self._set_xrange(ax, nax, [np.nanmin(x),np.nanmax(x)], self.setax[nax])
    self._set_yrange(ax, nax, [np.nanmin(y),np.nanmax(y)], self.setay[nax], x = x, y = y)

    # Start scatter plot procedure
    ax.scatter(x, y, **kwargs)

    # Creation of the legend
    self.legpos[nax] = kwargs.get('legpos', self.legpos[nax])
    if self.legpos[nax] != None:
        copy_label = kwargs.get('label',None)
        kwargs['label'] =  None
        self.legend(ax, check = 'no', fromplot = True, **kwargs)
        kwargs['label'] =  copy_label

    # If tight_layout is enabled, is re-inforced
    if self.tight != False:
        self.fig.tight_layout()    

    return None

def histogram(self) -> None:
    return None