from .libraries import *

def _check_fig(self,ax):
    '''
    findfig function:
        Finds the figure given a set of axes.
        **Inputs:**
            ax  -- the set of axes\n
    '''
    fig = ax.get_figure()
    assert fig == self.fig, "The provided axes does not belong to the expected figure."
    nax = self.ax.index(ax)
    return nax

def _add_ax(self,ax,i):
    '''
    addax function:
        Appends all the parameters in the hidden variables
        **Inputs:**
            ax -- the set of axes to add
            i  -- the index of the axis in the list
    '''
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
    '''
    place_inset_pos function:
        Inserts a set of inset axes (given the position).
        **Inputs:**
            ax  -- the set of axes to add
            pos -- the axis position within the figure
    '''
    left   = pos[0]
    bottom = pos[2]
    width  = pos[1] - pos[0]
    height = pos[3] - pos[2]
    return ax.inset_axes([left, bottom, width, height])

def _place_inset_loc(self, ax, **kwargs):
    '''
    place_inset_loc function:
        Inserts a set of inset axes (given the limits).
        **Inputs:**
            ax       -- the set of axes to add
            **kwargs -- the selected parameters
    '''
    if kwargs.get('top') and kwargs.get('bottom'):
        print('Both top and bottom keywords are given, priority goes to the top')
    left   = kwargs.get('left', 0.6)
    width  = kwargs.get('width', 0.2)
    height = kwargs.get('height', 0.15)
    bottom = kwargs.get('top', 0.75) - height
    bottom = kwargs.get('bottom', 0.6)
    return ax.inset_axes([left, bottom, width, height])


def _hide_text(self, nax: int, txts: str) -> None:
    '''
    hide_text function:
        Hides the text number from the plots.
        **Inputs:**
            nax  -- number of the selected set of axes
            txts -- text of the selected set of axes
    '''
    if self.ntext[nax] is None:
        [txt.set_visible(False) for txt in txts]
        self.ntext[nax] = 1
    return None

def _set_parax(self, ax, **kwargs):
    '''
    set_parax function:
        Sets the axes parameters through the function setaxis
        from the plot/display functions.
        **Input:**
            ax       -- the selected set of axes
            **kwargs -- the selected parameters
    '''
    param = {'alpha', 'aspect', 'ax', 'fontsize', 'labelsize', 'minorticks', 'ticksdir', 'tickssize', 'title', 'titlepad', 'titlesize', 'xrange', 
             'xscale', 'xticks', 'xtickslabels', 'xtitle', 'yrange', 'yscale', 'yticks', 'ytickslabels', 'ytitle'}
    axpar = {}
    for i in kwargs.keys():
        if i in param:
            axpar[i] = kwargs[i]
    self.set_axis(ax = ax, check = False, **axpar)

    return None

def _check_par(self, par, func, **kwargs):
    '''
    check_par function:
        Checks if a parameter is in the corresponding list
        depending on the function. If the praemeter does not
        belong to the list it raises a warning.
        **Inputs:**
            par      -- the function parameters
            func     -- the name of the function
            **kwargs -- the selected parameters
    '''
    notfound = [(i) for i in kwargs.keys() if i not in par]
    if len(notfound) > 0:
        print(f'WARNING: elements {str(notfound)} not found! Please check your spelling! (function {func})')
    return None

def _set_xrange(self, ax, nax, xlim, case):
    '''
    set_xrange function:
        Sets the xlim of a set of axes and fixes it (if not
        stated otherwise later).
        **Inputs:**
            ax   -- the selected set of axes
            nax  -- the number of the selected set of axes
            xlim -- the limits of the x-axis
            case -- the case in exam (if range is fixed or variable)
    '''
    if case == 0:
        ax.set_xlim(xlim[0],xlim[1])
        self.setax[nax] = 2
    if case == 2:
        xmin = min(xlim[0],ax.get_xlim()[0])
        xmax = max(xlim[1],ax.get_xlim()[1])
        ax.set_xlim(xmin,xmax)
    if case == 3:
        ax.set_xlim(xlim[0],xlim[1])
        self.setax[nax] = 1
    return None

def _set_yrange(self, ax, nax, ylim, case, x = None, y = None):
    '''
    set_yrange function:
        Sets the ylim of a set of axes and fixes it (if not
        stated otherwise later).
        **Inputs:**
            ax   -- the selected set of axes
            nax  -- the number of the selected set of axes
            ylim -- the limits of the y-axis
            case -- the case in exam (if range is fixed or variable)
            x    -- the x-array (to limit the y-range automatically)
            y    -- the y-array (to limit the y-range automatically)

    FIX CASE 0 IT DOES NOT WORK
    '''
    if case == 0:
        yrange = np.where(np.logical_and(x >= x.min(), x <= x.max()))
        smally = y[yrange]
        ymin   = smally.min() - 0.1*np.abs(smally.min())
        ymax   = smally.max() + 0.1*np.abs(smally.max())
        ax.set_ylim(ymin,ymax)
        self.setay[nax] = 2
    if case == 2:
        yrange = np.where(np.logical_and(x >= x.min(), x <= x.max()))
        smally = y[yrange]
        ymin   = smally.min() - 0.1*np.abs(smally.min())
        ymax   = smally.max() + 0.1*np.abs(smally.max())
        ymin = np.minimum(ymin,ax.get_ylim()[0])
        ymax = np.maximum(ymax,ax.get_ylim()[1])
        ax.set_ylim(ymin,ymax)
    if case == 3:
        ax.set_ylim(ylim[0],ylim[1])
        self.setay[nax] = 1
    return None

def _set_xticks(self, ax, xtc, xtl):
    '''
    set_xticks function:
        Sets ticks and tickslabels on the x-axis
        **Inputs:**
            ax -- the axis\n
            xtc -- the ticks on the x-axis\n
            xtl -- the ticklabels on the x-axis
    '''
    if xtc is None:
        ax.set_xticks([])
        ax.set_xticklabels([])
        if xtl not in (None, 'Default'):
            print('Warning, define tickslabels with no ticks!! (function setax)')
    elif xtl != 'Default':
        if xtc != 'Default':
            ax.set_xticks(xtc)
        elif xtl is not None:
            print('Warning, tickslabels should be fixed only when ticks are fixed (function setax)')
        if xtl is None:
            ax.set_xticklabels([])
        else:
            ax.set_xticklabels(xtl)
    else:
        if xtc != 'Default':
            ax.set_xticks(xtc)
    return None


def _set_yticks(self, ax, ytc, ytl):
    '''
    set_ticks function:
        Sets ticks and tickslabels on the x-axis
        **Inputs:**
            ax -- the axis\n
            ytc -- the ticks on the y-axis\n
            ytl -- the ticklabels on the y-axis
    '''
    if ytc is None:
        ax.set_yticks([])
        ax.set_yticklabels([])
        if ytl not in (None, 'Default'):
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
    '''
    check_rows function:
    Checks the width and spacing of the plots on a single column
    **Inputs:**
        hratio -- the ratio of the rows\n
        hspace -- the space between the rows\n
        nrow -- the number of rows in the single column
    '''
    hspace = [hspace] if not isinstance(hspace, list) else hspace
    hratio = hratio + [1.0] * (nrow - len(hratio))
    hspace = hspace + [0.1] * (nrow - len(hspace) - 1)

    if len(hratio) != nrow:
        warnings.warn('WARNING! hratio has wrong length!!!', UserWarning)

    if len(hspace) + 1 != nrow:
        warnings.warn('WARNING! hspace has wrong length!!!', UserWarning)

    return hspace[:nrow - 1], hratio[:nrow]

def _check_cols(self, wratio, wspace, ncol):
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
        print('WARNING! wratio has wrong length!!!')

    if len(wspace) + 1 != ncol:
        print('WARNING! wspace has wrong length!!!')

    return wspace[:ncol - 1], wratio[:ncol]

def _set_cscale(self, cscale, vmin, vmax, lint):
    '''
    set_cscale function:
        Sets the colorscale of a pcolormesh
        **Inputs:**
            cscale -- the colorscale (default is linear)
            vmin -- the colormap minimum
            vmax -- the colormap maximum
            lint -- the threshold between log and lin in the symlog scale
    '''
    if cscale == 'log':
        norm = mcol.LogNorm(vmin = vmin,vmax = vmax)
    elif cscale == 'symlog':
        norm = mcol.SymLogNorm(vmin = vmin,vmax = vmax,linthresh = lint)
    elif cscale == 'twoslope':
        norm = mcol.TwoSlopeNorm(vmin = vmin, vcenter = lint, vmax = vmax)
    else:
        norm = mcol.Normalize(vmin = vmin,vmax = vmax)
    return norm

def _assign_ax(self, ax, **kwargs):

    if ax is None and len(self.ax) == 0:
        ax = self.create_axes(ncol = 1, nrow = 1, check = False, **kwargs)

    elif ax is None and len(self.ax) > 0:
        ax  = self.fig.gca()

    nax = self._check_fig(ax)
    return ax, nax