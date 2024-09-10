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
    
    - cnt: LineCollection
        The set of contour lines of the given variable.
    
    Parameters
    ----------
    
    - alpha: float, default 1.0
        Sets the transparency of the contour lines.
    - ax: {ax object, 'old', None}, default None
        The axis where to plot the lines. If None, a new axis is created.
        If 'old', the last considered axis will be used.
    - c: str, default ['k','#12e3c0','#3f6600','#1815c5','#f67451','#d7263d']
        Determines the contour lines plot. If not defined, the program will loop
        over an array of 6 color which are different for the most common vision
        deficiencies.
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
    - levels: np.ndarray
        The levels of the contour lines.
    - transpose: True/False, default False
        Transposes the variable matrix. Use is not recommended if not really 
        necessary (e.g. in case of highly customized variables and plots).
    - tresh: float, default max(abs(vmin),vmax)*0.01
        Sets the threshold for the colormap. If not defined, the threshold will
        be set to 1% of the maximum absolute value of the variable.
        The default cases are the following:
        - twoslope colorscale: sets the limit between the two linear regimes.
        - symlog: sets the limit between the logaitrhmic and the linear regime.
    - var: np.ndarray
        The variable to be plotted.
    - vmax: float
        The maximum value of the colormap.
    - vmin: float
        The minimum value of the colormap.
    - x1: 1D array, default 'Default'
        The 'x' array.
    - x2: 1D array, default 'Default'
        The 'y' array.

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
               check: bool = True,
               **kwargs: Any
              ) -> LineCollection:
    """
    Plots a streamplot of a vector field. The function uses the streamplot
    function from matplotlib.pyplot.

    Returns
    -------

    - strm: LineCollection
        The streamplot of the given vector field.

    Parameters
    ----------

    - arrowsize: float, default 1.0
        Sets the size of the arrows of the streamline.
    - arrowstyle: str, default '-|>'
        Sets the style of the arrows of the streamline.
    - ax: axis object
        The axis where to plot the streamlines. If not given, the last 
        considered axis will be used.
    - brokenlines: bool, default True
        Splits the streamlines in shorter segments.
    - c: str, default ['k','#12e3c0','#3f6600','#1815c5','#f67451','#d7263d']
        Determines the streamplot color. If not defined, the program will loop
        over an array of 6 color which are different for the most common vision
        deficiencies.
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
    - density: float, default 1.0
        Sets the density and closeness of the streamlines. The domain is divided
        in a 30x30 grid. When set as default, each cells contains at most a 
        number of crossing streamplot line equal to this keyword. 
    - integration_direction: {'forward', 'backward', 'both'}, default: 'both'
        Sets the streamlines integration in the forward direction, backward
        direction, or both.
    - lw: float, default 1.0
        Sets the width of the streamlines.
    - maxlength: float, default 5.0
        Sets the maximum length of a streamline in coordinates units.
    - minlength: float, default 0.1
        Sets the minimum length of a streamline in coordinates units.
    - start_points: np.ndarray, default None
        Sets the starting points of the streamlines, if a more controlled plot
        is wanted.
    - transpose: True/False, default False
        Transposes the variable matrix. Use is not recommended if not really 
        necessary (e.g. in case of highly customized variables and plots)
    - tresh: float, default max(abs(vmin),vmax)*0.01
        Sets the threshold for the colormap. If not defined, the threshold will
        be set to 1% of the maximum absolute value of the variable.
        The default cases are the following:
        - twoslope colorscale: sets the limit between the two linear regimes.
        - symlog: sets the limit between the logaitrhmic and the linear regime.
    - var1: np.ndarray
        The x1-component of the vector field.
    - var2: np.ndarray
        The x2-component of the vector field.
    - vmax: float
        The maximum value of the vector field norm.
    - vmin: float
        The minimum value of the vector field norm.
    - x1: np.ndarray
        The x-axis variable.
    - x2: np.ndarray
        The y-axis variable.

    Notes
    -----

    - None

    ----

    Examples
    ========

    AGGIUNGERE ESEMPI

    """

    # Check parameters
    param = {'arrowsize','arrowstyle','ax','brokenlines','c','cmap','cpos',
             'cscale','density','integration_direction','lw','maxlength',
             'minlength','start_points','transpose','tresh','vmax','vmin','x1',
             'x2'}
    if check is True:
        check_par(param, 'scatter', **kwargs)

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
