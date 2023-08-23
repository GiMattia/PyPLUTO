from .libraries import *

def display(self,var,check = True,**kwargs):
    '''
    Plot for a 2D function (or a 2D slice) using the
    matplotlib's pcolormesh function.
    A simple figure and a single axis can also be created.

    Returns
    -------


    - Nothing is returned.

    Parameters
    ----------


    - aspect: {'auto', 'equal', float}, default 'auto'
        Sets the aspect ratio of the plot.
        The 'auto' keyword is the default option (most likely the plot will
        be squared). The 'equal' keyword will set the same scaling for
        x and y. A float will fix the ratio between the y-scale and the x-scale
        (1.0 is the same as 'equal').
    - ax: {ax object, 'old', None}, default None
        The axis where to plot the lines. If None, a new axis is created.
        If 'old', the last considered axis will be used.
    - clabel: str, default None
        Sets the label of the colorbar.
    - cmap: str, default 'hot'
       Selects the colormap. If not defined, the colormap 'hot' will be adopted.
        Some useful colormaps are: plasma, magma, seismic. Please avoid using
        colorbars like jjet or rainbow, which are not perceptively uniform and
        not suited for people with vision deficiencies.
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
    - figsize: [float, float], default [6*sqrt(ncol),5*sqrt(nrow)]
        Sets the figure size. The default value is computed from the number
        of rows and columns.
    - fontsize: float, default 17.0
        Sets the fontsize for all the axes.
    - labelsize: float, default fontsize
        Sets the labels fontsize (which is the same for both labels).
        The default value corresponds to the value of the keyword 'fontsize'.
    - lint: float, default max(abs(vmin),vmax)*0.01
        Additional parameter in presence of a composite colormap. The specific cases are the following:
        - twoslope colorscale: sets the limit between the two linear regimes.
        - symlog: sets the limit between the logaitrhmic and the linear regime.
    - minorticks: str, default None
        If not None enables the minor ticks on the plot (for both grid axes). SUL SINGOLO ASSE?
    - proj: str, default None
        Custom projection for the plot (e.g. 3D). Recommended only if needed.
        This keyword should be used only if the axis is created.
        WARNING: pyPLUTO does not support 3D plotting for now, only 3D axes.
        The 3D plot feature will be available in future releases.
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
    - transpose: True/False, default False
        Transposes the variable matrix. Use is not recommended if not really necessary
        (e.g. in case of highly customized variables and plots)
    - var (not optional): 2D array
        The array to be plotted.
    - vmax: float, default max(z)
        The maximum value of the colormap. If not defined, the maximum value
        of z will be taken.
    - vmin: float, default min(z)
        The minimum value of the colormap. If not defined, the minimum value
        of z will be taken.
    - x1: 1D/2D array, default 'Default'
        the 'x' array. If not defined, a default array will be generated
        depending on the size of z.
    - x2: 1D/2D array, default 'Default'
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
    - yrange: [float, float], default 'Default'
        Sets the range in the y-direction. If not defined or set to 'Default'
        the code will compute the range while plotting the data by taking the
        minimum and the maximum values of the x2-array.
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

    Examples
    --------

    - Example #1: create a simple 2d plot with title and colorbar on the right

       >>> import pyPLUTO as pp
       >>> I = pp.Image()
       >>> I.display(var, title = 'title', cpos = 'right')

    - Example #2: create a 2d plot with title on the axes, bottom colorbar and custom shading

       >>> import pyPLUTO as pp
       >>> I = pp.Image()
       >>> I.display(x1, x2, var, xtitle = 'x', ytitle = 'y', cpos = 'bottom', shading = 'gouraud', cpad = 0.3)

    - Example #3: create a 2d plot con custom range on axes and logarithmic scale colorbar

       >>> import pyPLUTO as pp
       >>> I = pp.Image()
       >>> I.display(var, xrange = [2,3], yrange = [2,4], cbar = 'right', cscale = 'log')

    - Example #4: create a 2d plot with a custom symmetric logarithmic colorbar with custom ticks.

       >>> import pyPLUTO as pp
       >>> I = pp.Image()
       >>> I.display(var, cpos = 'right', cmap = 'RdBu_r', cscale = 'symlog', lint = 0.001, vmin = -1, vmax = 1)

    '''

   # Check parameters
    param = {'aspect', 'ax', 'clabel', 'cmap', 'cpad', 'cpos', 'cscale', 'cticks', 'ctickslabels', 'figsize', 'fontsize', 'labelsize', 'lint', 'minorticks', 'proj', 
             'shading', 'ticksdir', 'tickssize', 'title', 'titlesize', 'transpose', 'var', 'vmax', 'vmin', 'x1', 'x2', 'xrange', 'xscale', 'xticks', 'xtickslabels',
             'xtitle', 'yrange', 'yscale', 'yticks', 'ytickslabels', 'ytitle'}
    if check is True:
        self.check_par(param, 'display', **kwargs)

    # Set or create figure and axes
    ax, nax = self.assign_ax(kwargs.pop('ax',None),**kwargs)

    # Keyword x1 and x2
    var = np.asarray(var)
    if kwargs.get('transpose', False) is True:
        var = var.T
    x = np.asarray(kwargs.get('x1',np.arange(len(var[:,0])+1)))
    y = np.asarray(kwargs.get('x2',np.arange(len(var[0,:])+1)))

    # Keywords xrange and yrange
    if not kwargs.get('xrange'):
        kwargs['xrange'] = [x.min(),x.max()]
    if not kwargs.get('yrange'):
        kwargs['yrange'] = [y.min(),y.max()]

    # Set ax parameters
    self.set_parax(ax, **kwargs)
    self.hide_text(nax, ax.texts)

    # Keywords vmin and vmax
    vmin = kwargs.get('vmin',var.min())
    vmax = kwargs.get('vmax',var.max())

    # Keyword for colorbar and colorscale
    cpos     = kwargs.get('cpos',None)
    cscale   = kwargs.get('cscale','norm')
    lint     = kwargs.get('lint',max(np.abs(vmin),vmax)*0.01)
    self.vlims[nax] = [vmin,vmax,lint]

    # Set the colorbar scale (put in function)
    norm = self.set_cscale(cscale, vmin, vmax, lint)

    # Display the image
    pcm = ax.pcolormesh(x,y,var.T, shading=kwargs.get('shading','auto'),
                        cmap = kwargs.get('cmap','afmhot'), norm = norm,
                        linewidth=0,rasterized=True)
    # Place the colorbar (use colorbar function)
    if cpos != None:
        self.colorbar(ax, check = False, **kwargs)

    # If tight_layout is enabled, is re-inforced
    if self.tight != False:
        self.fig.tight_layout()

    return None

def colorbar(self, axs = None, cax = None, check = True, **kwargs):
    '''
    method to display a colorbar in a selected position. If the keyword cax is
    enabled the colorbar is locates in a specific axis, otherwise an axis will
    be shrunk in order to place the colorbar.

    Returns
    -------

        None

    Parameters
    ----------
        - axs: axis object, default None
            The axes where the display that will be used for the colorbar is located.
            If None, the last considered axis will be used.
        - cax: axis object, default None
            The axes where the colorbar should be placed. If None, the colorbar
            will be placed next to the axis axs.
        - clabel: str, default None
            Sets the label of the colorbar.
        - cpad: float, default 0.07
            Fraction of original axes between colorbar and the axes (in case cax is
            not defined). RENDERE ADATTIVO IN BASE ALLA POSIZIONE
        - cpos: {'top','bottom','left','right'}, default 'right'
            Sets the position of the colorbar.
        - cticks: {[float], None}, default None
            If enabled (and different from None), sets manually ticks on the
            colorbar.
        - ctickslabels: str, default None
            If enabled, sets manually ticks labels on the colorbar.

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

        - Example #3: create a set of 3 displays with a colorbar on the bottom
                      Another colorbar is shown on the right of the topmost display

           >>> import pyPLUTO as pp
           >>> I = pp.Image()
           >>> ax = I.create_axes(nrow = 4)
           >>> I.display(var1, ax = ax[0])
           >>> I.colorbar(axs = ax[0])
           >>> I.display(var2, ax = ax[1])
           >>> I.display(var3, ax = ax[2])
           >>> I.colorbar(axs = ax[2], cax = ax[3])


    '''
    # Check parameters
    param = {'axs', 'cax', 'clabel', 'cpad', 'cpos', 'cticks', 'ctickslabels'}
    if check is True:
        self.check_par(param, 'colorbar', **kwargs)

    axs  = self.fig.gca() if axs is None else axs
    nax  = self.check_fig(axs)
    pcm  = axs.collections[0]
    cpad = kwargs.get('cpad',0.07)
    cpos = kwargs.get('cpos','right')
    ccor = 'vertical' if cpos in ['left','right'] else 'horizontal'

    if cax == None:
        divider = make_axes_locatable(axs)
        cax = divider.append_axes(cpos, size="7%", pad=cpad) # 0.07 right
    else:
        naxc = self.check_fig(cax)

        if self.ntext[naxc] == None:
            for txt in cax.texts:
                txt.set_visible(False)
            self.ntext[naxc] = 1
            
    cbar = self.fig.colorbar(pcm, cax=cax,label=kwargs.get('clabel',''),
                ticks = kwargs.get('cticks',None), orientation=ccor)
    ctkc = kwargs.get('ctickslabels','Default')
    if ctkc != 'Default':
        cbar.ax.set_yticklabels(ctkc)
    if self.tight == True:
        self.fig.tight_layout()
    return None
