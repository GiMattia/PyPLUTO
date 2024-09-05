from .libraries import *

def contour(self, 
            var: NDArray, 
            **kwargs: Any
           ) -> LineCollection:
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
    
    ----

    Examples
    ========
    
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

    if 'colors' in 'kwargs' and 'cmap' in 'kwargs':
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


def streamplot(self, 
               var1, 
               var2, 
               **kwargs: Any
              ) -> LineCollection:
    """
    Plots a streamplot of a vector field. The function uses the streamplot
    function from matplotlib.pyplot. The function returns None.
    """

    if np.shape(var1) != np.shape(var2):
        raise ValueError("The shapes of the variables are different.")
    
    # Set or create figure and axes
    ax, nax = self._assign_ax(kwargs.pop('ax',None),**kwargs)
    x = np.asarray(kwargs.get('x1',np.arange(len(var1[:,0]))))
    y = np.asarray(kwargs.get('x2',np.arange(len(var1[0,:]))))

    # Keyword x1 and x2
    varx, vary = np.asarray(var1.T).copy(), np.asarray(var2.T).copy()
    if kwargs.get('transpose', False) is True: varx, vary = varx.T, vary.T

    # 
    fieldmod = np.sqrt(varx**2 + vary**2)
    vmax     = kwargs.get('vmax', np.nanmax(fieldmod))
    vmin     = kwargs.get('vmin', np.nanmin(fieldmod))

    # Apply the masks to set the corresponding elements in varx and vary to NaN
    mask = np.logical_or(fieldmod > vmax, fieldmod < vmin)
    varx[mask] = vary[mask] = np.nan

    # Set ax parameters
    self.set_axis(ax = ax, check = False, **kwargs)
    self._hide_text(nax, ax.texts)  

    # Keyword for colorbar and colorscale
    color = kwargs.get('c',None)  
    cmap  = kwargs.get('cmap',None)
    cpos  = kwargs.get('cpos',None)
    cscale = kwargs.get('cscale','norm')
    tresh = kwargs.get('tresh', max(np.abs(vmin),vmax)*0.01)

    if 'colors' in 'kwargs' and 'cmap' in 'kwargs':
        warn = "Both colors and cmap are defined. Using c."
        warnings.warn(warn)

    # Set the lines properties
    linewidth             = kwargs.get('lw',1)
    density               = kwargs.get('density',1)
    arrowstyle            = kwargs.get('arrowstyle','-|>')
    arrowsize             = kwargs.get('arrowsize',1)
    minlength             = kwargs.get('minlength',0.1)
    integration_direction = kwargs.get('integration_direction','both')
    start_points          = kwargs.get('start_points',None)
    maxlength             = kwargs.get('maxlength',5)
    broken_streamlines    = kwargs.get('brokenlines',True)

    # Set the colorbar scale
    norm = self._set_cscale(cscale, vmin, vmax, tresh)

    # Plot the streamplot
    strm = ax.streamplot(x, y, vary, varx, norm = norm, cmap = cmap, 
                               color = color, linewidth = linewidth, 
                               density = density,
                               arrowsize = arrowsize, minlength = minlength,
                               maxlength = maxlength, 
                               start_points = start_points,
                               arrowstyle = arrowstyle,
                               integration_direction = integration_direction,
                               broken_streamlines = broken_streamlines)
    
    if cpos != None:
        self.colorbar(strm, check = False, **kwargs)

    # If tight_layout is enabled, is re-inforced
    if self.tight != False:
        self.fig.tight_layout()

    del varx, vary

    return strm



