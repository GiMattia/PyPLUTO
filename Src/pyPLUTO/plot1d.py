from .libraries import *
from .h_pypluto import _check_par

def plot(self, 
         x: list[float] | NDArray, 
         y: list[float] | NDArray | list[None] = [None], 
         check: bool = True, 
         **kwargs: Any
        ) -> None:
    """
    Plot for a 1D function (or a 1D slice).
    A simple figure and a single axis can also be created.

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
        - ax: {ax object, 'old', None}, default None
            The axis where to plot the lines. If None, a new axis is created.
            If 'old', the last considered axis will be used.
        - c: str, default ['k','#12e3c0','#3f6600','#1815c5','#f67451','#d7263d']
            Determines the line color. If not defined, the program will loop over
            an array of 6 color which are different for the most common vision
            deficiencies.
        - figsize: [float, float], default [8,5]
            Sets the figure size. The default value is computed from the number
            of rows and columns.
        - fillstyle: {'full', 'left', 'right', 'bottom', 'top', 'none'}, default 'full'
            Sets the marker filling. The default value is the fully filled marker
            ('full').
        - fontsize: float, default 17.0
            Sets the fontsize for all the axes.
        - label: str, default None
            Associates a label to each line. Such labels will be used for the
            creation of the legend.
        - labelsize: float, default fontsize
            Sets the labels fontþsize (which is the same for both labels).
            The default value corresponds to the value of the keyword 'fontsize'.
        - legcols: int, default 1
            Sets the number of columns that the legend should have.
        - legpad: float, default 0.8
            Sets the space between the lines (or symbols) and the correspondibg text
            in the legend.
        - legpos: int/str, default None
            If enabled, creates a legend. This keyword selects the legend location.
            The possible locations for the legend are indicated in the following link: 
            https://matplotlib.org/stable/api/_as_gen/matplotlib.pyplot.legend.html
        - legsize: float, default fontsize
            Sets the fontsize of the legend. The default value is the default fontsize
            value.
        - legspace: float, default 2
            Sets the space between the legend columns, in font-size units.
        - ls: {'-', '--', '-.', ':', ' ', ect.}, default '-'
            Sets the linestyle. The choices available are the ones defined
            in the matplotlib package. Here are reported the most common ones.
        - lw: float, default 1.3
            Sets the linewidth of each line.
        - marker: {'o', 'v', '^', '<', '>', 'X', ' ', etc.}, default ' '
            Sets an optional symbol for every point. The default value is no
            marker (' ').
        - minorticks: str, default None
            If not None enables the minor ticks on the plot (for both grid axes). SUL SINGOLO ASSE?
        - ms: float, default 3
            Sets the marker size.
        - proj: str, default None
            Custom projection for the plot (e.g. 3D). Recommended only if needed.
            This keyword should be used only if the axis is created.
            WARNING: pyPLUTO does not support 3D plotting for now, only 3D axes.
            The 3D plot feature will be available in future releases.
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
        - x (not optional): 1D array
            If y is not defined, then this becomes the y-axis variable.
            Otherwise, this is the x-axis variable.
        - xrange: [float, float], default 'Default'
            Sets the range in the x-direction. If not defined or set to 'Default'
            the code will compute the range while plotting the data by taking the
            minimum and the maximum values of the x-array. In case of multiple lines,
            the code will also adapt to the previous ranges.
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
        - y: 1D array, default [None]
            The y-axis variable.
        - yrange: [float, float], default 'Default'
            Sets the range in the y-direction. If not defined or set to 'Default'
            the code will compute the range while plotting the data by taking the
            minimum and the maximum values of the y-array. In case of multiple lines,
            the code will also adapt to the previous ranges. It also adds a small offset.
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

        - Example #1: create a simple plot of y as function of x
         
            >>> import pyPLUTO as pp
            >>> I = pp.Image()
            >>> I.plot(x, y)
            
         - Example #2: create a plot of y as function of x with custom range of the axes and titles
         
            >>> import pyPLUTO as pp
            >>> I = pp.Image()
            >>> I.plot(x, y, xrange = [0,100], yrange = [0.0,1.0], title = 'y in function of x', xtitle = 'x', ytitle = 'y')
            
         - Example #3: create a plot with logarithmic scale on y-axis
         
            >>> import pyPLUTO as pp
            >>> I = pp.Image()
            >>> I.plot(x, y, yscale = 'log')
            
         - Example #4: create a plot with a legend and custom ticks on x-axis
         
            >>> import pyPLUTO as pp
            >>> I = pp.Image()
            >>> I.plot(x, y, label = 'y', legpos = 'lower right', xticks = [0.2,0.4,0.6,0.8])
        

    """

    # Declare variables
    ax: Axes
    nax: int


    # Convert x and y in numpy arrays
    if y[0] is None:
        y = x
        x = np.arange(len(y))
    x = np.asarray(x)
    y = np.asarray(y)

    # Check parameters
    param: set = {'alpha', 'aspect', 'ax', 'c', 'figsize', 'fillstyle', 'fontsize', 'label', 'labelsize', 'legcols', 'legpad', 'legpos', 'legsize', 'legspace', 'ls',
             'lw', 'marker', 'minorticks', 'ms', 'proj', 'ticksdir', 'tickssize', 'title', 'titlesize', 'x', 'xrange', 'xscale', 'xticks', 'xtickslabels',
             'xtitle', 'y', 'yrange', 'yscale', 'yticks', 'ytickslabels', 'ytitle'}
    if check is True:
        _check_par(param, 'plot', **kwargs)

    # Set or create figure and axes
    ax, nax = self._assign_ax(kwargs.pop('ax',None),**kwargs)

    # Set ax parameters
    self._set_parax(ax, **kwargs)
    self._hide_text(nax, ax.texts)

    # Keyword xrange and yrange
    self._set_xrange(ax, nax, [x.min(),x.max()], self.setax[nax])
    self._set_yrange(ax, nax, [y.min(),y.max()], self.setay[nax], x = x, y = y)

    # Start plotting procedure
    ax.plot(x,y, c = kwargs.get('c',self.color[self.nline[nax]%len(self.color)]),
                 ls = kwargs.get('ls','-'), lw = kwargs.get('lw',1.3),
                 marker = kwargs.get('marker',''),
                 ms = kwargs.get('ms',3.0),label = kwargs.get('label',''),
                 fillstyle = kwargs.get('fillstyle','full'))
    if not kwargs.get('c'):
        self.nline[nax] = self.nline[nax] + 1

    # Creation of the legend
    self.legpos[nax] = kwargs.get('legpos', self.legpos[nax])
    if self.legpos[nax] != None:
        copy_label: str | None = kwargs.get('label',None)
        kwargs['label'] =  None
        legend(self, ax, check = False, fromplot = True, **kwargs)
        kwargs['label'] =  copy_label

    # If tight_layout is enabled, is re-inforced
    if self.tight != False:
        self.fig.tight_layout()

    return None

def legend(self, 
           ax: Axes | None = None, 
           check: bool = True, 
           fromplot: bool = False, 
           **kwargs: Any
          ) -> None:
    '''
    Creation of the legend (from scratch or through the lines of the plot).

    Returns
    -------

        None

    Parameters
    ----------
        - ax: axis object, default None
            The axis where to insert the legend. If None, the last considered
            axis will be used.
        - c: str, default ['k','#12e3c0','#3f6600','#1815c5','#f67451','#d7263d']
            Determines the line color. If not defined, the program will loop over
            an array of 6 color which are different for the most common vision
            deficiencies.  
        - fillstyle: {'full', 'left', 'right', 'bottom', 'top', 'none'}, default 'full'
            Sets the marker filling. The default value is the fully filled marker
            ('full'). 
        - label: [str], default None
            Associates a label to each line. If not specified, the program will
            take the label which are already associated with the plot.   
        - legcols: int, default 1
            Sets the number of columns that the legend should have.
        - legpad: float, default 0.8
            Sets the space between the lines (or symbols) and the correspondibg text
            in the legend.
        - legpos: int/str, default 0
            Selects the legend location. If not specified the standard matplotlib
            legend function will find the most suitable location.
        - legsize: float, default fontsize
            Sets the fontsize of the legend. The default value is the default fontsize
            value.
        - legspace: float, default 2
            Sets the space between the legend columns, in font-size units.
        - ls: {'-', '--', '-.', ':', ' ', ect.}, default '-'
            Sets the linestyle. The choices available are the ones defined
            in the matplotlib package. Here are reported the most common ones.
        - lw: float, default 1.3
            Sets the linewidth of each line.
        - marker: {'o', 'v', '^', '<', '>', 'X', ' ', etc.}, default ' '
            Sets an optional symbol for every point. The default value is no
            marker (' ').
        - ms: float, default 3
            Sets the marker size.

    Examples
    --------

        - Example #1: create a standard legend
        
           >>> import pyPLUTO as pp
           >>> I = pp.Image()
           >>> ax = I.create_axes()
           >>> I.plot(x,y, ax = ax, label = 'label')
           >>> I.legend(ax)
           
        - Example #2: create a legend with custom labels
        
           >>> import pyPLUTO as pp
           >>> I = pp.Image()
           >>> I.plot(x,y)
           >>> I.legend(label = 'y')
           
        - Example #3: create a double legend for four lines in a single plot
        
           >>> import pyPLUTO as pp
           >>> I = pp.Image()
           >>> I.plot(x, y1, ls = '-', c = 'k')
           >>> I.plot(x, y2, ls = '-.', c = 'r')
           >>> I.plot(x, y3, ls = '-', c = 'r')
           >>> I.plot(x, y4, ls = '-.', c = 'k')
           >>> I.legend(legpos = 'lower left', ls = ['-','-'], c = ['k','r'], label = ['black lines', 'red lines'])
           >>> I.legend(legpos = 'lower right', ls = ['-','-.'], c = ['k', 'k'], label = ['continue', 'dotted'])

    '''

    # Check parameters
    param = {'ax', 'c', 'fillstyle', 'label', 'legcols', 'legpad', 'legpos', 'legsize', 'legspace', 'ls', 'lw', 'marker', 'ms'}
    if check is True:
        _check_par(param, 'legend', **kwargs)

    # Find figure and number of the axis
    ax  = self.fig.gca() if ax is None else ax
    nax = self._check_fig(ax)

    # Finds the legend parameters (position, columns, size and spacing)
    self.legpos[nax]    = kwargs.get('legpos',   self.legpos[nax])
    self.legpar[nax][0] = kwargs.get('legsize',  self.legpar[nax][0])
    self.legpar[nax][1] = kwargs.get('legcols',  self.legpar[nax][1])
    self.legpar[nax][2] = kwargs.get('legspace', self.legpar[nax][2])
    self.legpar[nax][3] = kwargs.get('legpad',   self.legpar[nax][3])

    # Check if another unwanted legend is present and cancel it
    if fromplot is True:
        lleg = ax.get_legend()
        if lleg is not None: lleg.remove()

    # Check is custom labels are on and plot the legend
    if kwargs.get('label') is not None:
        lab = kwargs['label'] if isinstance(kwargs['label'], list) else [kwargs['label']]
        col = makelist(kwargs.get('c',['k']))
        ls  = makelist(kwargs.get('ls',['-']))
        lw  = makelist(kwargs.get('lw',[1.5]))
        mrk = makelist(kwargs.get('marker',['']))
        ms  = makelist(kwargs.get('ms',[5.0]))
        fls = makelist(kwargs.get('fillstyle',['full']))
        lines = []
        for i, val in enumerate(lab):
            lines.append(mlines.Line2D([], [], label = val, color = col[i%len(col)],
                         ls = ls[i%len(ls)], lw = lw[i%len(lw)],
                         marker = mrk[i%len(mrk)], ms = ms[i%len(ms)],
                         fillstyle = fls[i%len(fls)]))
        legg = ax.legend(handles = lines, loc = self.legpos[nax],
                  fontsize = self.legpar[nax][0], ncol = self.legpar[nax][1],
                  columnspacing = self.legpar[nax][2], handletextpad = self.legpar[nax][3])
    else:
        ms = kwargs.get('ms',1.0)
        legg = ax.legend(loc = self.legpos[nax], fontsize = self.legpar[nax][0],
                  ncol = self.legpar[nax][1], markerscale = ms,
                  columnspacing = self.legpar[nax][2], handletextpad = self.legpar[nax][3])
    ax.add_artist(legg)

    return None
