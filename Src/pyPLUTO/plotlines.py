from .libraries import *

def contour(self, 
            var: NDArray, 
            **kwargs: Any
           ) -> None:
    """
    Plots a contour plot of a given variable. The function uses the 
    matplotlib.pyplot.contour function. The function returns None.
    
    Returns
    -------
    
    - None
    
    Parameters
    ----------
    
    - var: NDArray
        The variable to be plotted.
    
    - **kwargs: Any
        The keyword arguments of the matplotlib.pyplot.contour function.
    
    Notes
    -----
    
    - Need to improve the colorbar, now only lines are plotted and not the 
      full colormap.
    
    Examples
    --------
    
    - Example #1: Plot a contour plot of a variable
        
        >>> I.contour(D.rho, levels = 10)
    
    """

    # Set or create figure and axes
    ax, nax = self._assign_ax(kwargs.pop('ax',None),**kwargs)
    x = np.asarray(kwargs.get('x1',np.arange(len(var[:,0]))))
    y = np.asarray(kwargs.get('x2',np.arange(len(var[0,:]))))

    # Keyword x1 and x2
    var = np.asarray(var.T)
    if kwargs.get('transpose', False) is True: var = var.T

    # Set ax parameters
    self.set_axis(ax = ax, check = False, **kwargs)
    self._hide_text(nax, ax.texts)

    # Keywords vmin and vmax
    vmin = kwargs.get('vmin',np.nanmin(var))
    vmax = kwargs.get('vmax',np.nanmax(var))

    # Sets levels for the contour plot
    levels = kwargs.get('levels',np.linspace(vmin,vmax,10))

    # Keyword for colorbar and colorscale
    colors   = kwargs.get('c',None)
    cmap     = kwargs.get('cmap',None)
    cpos     = kwargs.get('cpos',None)
    cscale   = kwargs.get('cscale','norm')
    tresh    = kwargs.get('tresh', max(np.abs(vmin),vmax)*0.01)
    lint     = kwargs.get('lint',None)

    if colors in 'kwargs' and cmap in 'kwargs':
        warn = "Both colors and cmap are defined. Using c."
        warnings.warn(warn)

    # Set the colorbar scale (put in function)
    norm = self._set_cscale(cscale, vmin, vmax, tresh, lint)

    # Select shading
    alpha = kwargs.get('alpha',1.0)
    
    # Plot the contour plot
    cnt = ax.contour(x, y, var, levels = levels, norm = norm, cmap = cmap,
                                colors = colors, alpha = alpha)
    
    if cpos != None:
        self.colorbar(cnt, check = False, **kwargs)

    # If tight_layout is enabled, is re-inforced
    if self.tight != False:
        self.fig.tight_layout()

    return cnt