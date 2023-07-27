from ._libraries import *

class Load:

    '''
    def __new__(cls, *args, **kwargs):
        new_instance = super().__new__(cls)

        if kwargs.get('nout', 'last') is None:
            return new_instance
        else:
            new_instance.__init__(nout = 'last', path = './' , datatype = None, 
                     vars = True, text = True)
            return new_instance
    '''



    def __init__(self, nout = 'last', path = './' , datatype = None, 
                     vars = True, text = True):

        self.D_vars = {}
        self.pathdir = Path(path)
        if text is not False:
            print(f'Loading folder:   {path}')
        if text is True:
            print(f'Preferred format: {datatype}')

        self._find_format(datatype)
        if datatype == None and text == True:
            print(f'Format found:     {self.format}')

        self._read_grid()
        self._read_vars(nout)   
        if text is not False:
            print(f'Dimensions:       {self.dim}')
            print(f'Geometry:         {self.geom}')
        if text is True:
            print('Grid variables:   '+str(self.gridlist1)[:-1]+',')
            print('                   '+str(self.gridlist2)[1:-1]+',')
            try:
                print('                  '+str(self.gridlist3)[1:-1]+',')
            except:
                None
            print('                   '+str(self.gridlist4)[1:])
            print('Time variables:   '+str(self.addvarlist))

        if isinstance(self.nout, np.ndarray):
            self.noutlist = self.nout
            self.varfiles = []
        else:
            self.noutlist = np.atleast_1d(self.nout)

        self.varlist = {}
        for i, exout in enumerate(self.noutlist):
            self._load_vars(vars,i,exout,text)
        
        for key in self.D_vars:
            setattr(self, key, self.D_vars[key])

        #self._delete_vars() 

    def __str__(self):
        return f'''
        Load class.
        It loads the data.
        Attributes: blablabla
        Methods available: blablablax2
        Please refrain from using "private" methods.
        '''
    
    from ._readout import _find_format, _read_grid, _read_vars, _load_vars, _delete_vars
    from ._h_load  import split_gridfile, rec_format, vtk_offset, gen_offset
    from ._h_load  import check_nout, init_vardict, assign_var, shape_st
    
class Image:

    def __init__(self,LaTeX = True, text = False, fig = None, **kwargs):

        self.fontsize = 17
        self.tight    = True
        self.nwin     = 1
        self.figsize  = [8,5]
        self.set_size = False
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
        self.parax    = ['fontsize','xrange','yrange','title','xtitle','ytitle',
                         'titlesize','labelsize','tickssize','xticks','yticks',
                         'xtickslabels','ytickslabels','xscale','yscale','alpha',
                         'ticksdir','minorticks','aspect']
        self.parfig   = ['fig','tight','figsize','fontsize','nwin','suptitle']
        self.parplot  = ['axes','c','ls','lw','marker','ms','label','fillstyle',
                         'legend','legsize','legcols', 'pos']
        self.pardis   = ['axes','x1', 'x2','vmin','vmax','shading','cmap','cbar',
                         'clabel','cscale','cticks','ctickslabels','lint']
        self.parzoom  = ['left', 'width', 'top', 'height', 'pos', 'ind']
        self.LaTeX    = LaTeX

        if LaTeX is True:
            mpl.rcParams['mathtext.fontset'] = "stix"
            mpl.rcParams['font.family'] = "STIXGeneral"

        if LaTeX == 'pgf':
            plt.switch_backend('pgf')

            pgf_preamble = r"""
            \usepackage{amsmath}
            \usepackage{amssymb}
            \usepackage{mathptmx}
            \newcommand{\DS}{\displaystyle}
            """

            fontweight = kwargs.get('fontweight','normal')
            mpl.rcParams.update({
                "pgf.preamble": pgf_preamble,
                "font.family": 'serif',
                "font.weight": fontweight,
                "text.usetex": True
            })



        if text == True:
            print('Creating Figure')

        self.create_fig(fig, **kwargs)

    def __str__(self):
        return f'''
        Image class.
        It plots the data.
        Attributes: blablabla
        Methods available: blablablax2
        Please refrain from using "private" methods.
        '''

    from ._h_image  import place_inset_pos, place_inset_loc
    from ._h_image  import set_parax, check_par, set_xrange, set_yrange
    from ._h_image  import set_xticks, set_yticks, check_rows, check_cols
    from ._h_image  import hide_text, set_cscale
    from ._h_image  import check_fig, add_ax, assign_ax

    from ._fig      import create_fig, create_axes, set_axis
    from ._plot     import plot, legend
    from ._display  import display, colorbar
    from ._interact import interactive, update_slider
    from ._figtools import savefig, show, text
    from ._zoom     import zoom, zoomplot, zoomdisplay

    from .ploadparticles import ploadparticles


class Tools:

    def __init__(self,D):
        self.Grid = {}
        self.gridlist = ['nx1','nx2','nx3','x1','x2','x3',
                         'dx1','dx2','dx3','x1r','x2r','x3r',
                         'x1c','x2c','x1rc','x2rc',
                         'gridsize','nshp','dim','geom']
        for i in self.gridlist:
            try:
                self.Grid[i] = getattr(D,i)
            except:
                None

    def __str__(self):
        return f'''
        Tools class.
        It manipulates the data.
        Attributes: blablabla
        Methods available: blablablax2
        Please refrain from using "private" methods.
        '''

    from ._datatools import slices, mirror
    from ._nabla     import gradient
    from ._lines     import fieldlines, field_interp, adv_field_line, check_closed_line

from ._pytools   import savefig, show

class LoadPart:
    def __init__(self, nout = 'last', path = './' , datatype = None, 
                     vars = True, text = True):
        raise NotImplementedError('Loading of particles has not been implemented yet')
          
    def __str__(self):
        return f'''
        LoadPart class.
        It loads the particles.
        Attributes: blablabla
        Methods available: blablablax2
        Please refrain from using "private" methods.
        '''
