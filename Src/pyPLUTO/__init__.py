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



    def __init__(self, nout = 'last', path: str  = './' , datatype: str = None, 
                       vars =  True,  text: bool = True):

        self._check_parameters(nout, path, datatype, vars, text)

        if text is not False:
            print(f'Loading folder:   {path}')

        self._find_formatdata(datatype)

        self._read_grid()
        self._read_vars(nout)   
        if text is not False: print(f'Dimensions: {self.dim} ({self.geom})')
    
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
        if text is not False: print(f'Output loaded: {self.nout}')
        

        #self._delete_vars() 

    def __str__(self):
        text3 = f'''        - Cartesian projection              {['x1c','x2c','x1rc','x2rc']}\n''' 
        text3 = text3 if self.geom != 'CARTESIAN' else ""

        text = f'''
        Load class.
        It loads the data.

        File properties:
        - Current path loaded      {self.pathdir} 
        - Format loaded            {self.format}

        Simulation properties
        - Dimensions    (dim)      {self.dim}
        - Geometry      (geom)     {self.geom}
        - Grid size     (gridsize) {self.gridsize}
        - Grid shape    (nshp)     {self.nshp}
        - Output loaded (nout)     {self.nout}
        - Time loaded   (ntime)    {self.ntime}

        Public attributes available:
        - Number of cells in each direction {['nx1','nx2','nx3']}
        - Grid values (cell center)         {['x1','x2','x3']}
        - Grid values (face center)         {['x1r','x2r','x3r']}
        - Cells size                        {['dx1','dx2','dx3']}
        - Time attributes                   {['outlist','timelist']}\n{text3}        
        Variables available:
        {self.Dinfo['varslist'][0]}
        Variables loaded: 
        {self.load_vars}

        Public methods available: WIP...

        Please refrain from using "private" methods and attributes.
        '''
        return text
    
    from .readdata import _check_parameters, _find_formatdata, _read_grid, _read_vars
    from .readdata import _load_vars, _delete_vars
    from .h_load   import _split_gridfile, _rec_format, _vtk_offset, _gen_offset
    from .h_load   import _check_nout, _init_vardict, _assign_var, _shape_st
    
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

        self.create_fig(fig, **kwargs)
        if text is not False:
            print(f'Creating Figure in window {self.nwin}')

    def __str__(self):
        plt.rcParams['text.usetex'] = True
        plt.rcParams['text.latex.preamble'] = r'\usepackage{amsmath}'
        return rf'''
        Image class.
        It plots the data.

        Image properties:
        - Figure size:        {self.figsize}
        - Window number:      {self.nwin}
        - Number of subplots: {self.nrow0}x{self.ncol0}
        - Global fontsize:    {self.fontsize}

        Public attributes available: WIP...

        Public methods available: 
        - create_axes
          It adds a set of [nrow,ncol] subplots to the figure.
        - set_axis
          Changes the parameter of a specific subplot
        - plot
          Plots one line in a subplot
        - legend
          Places a legend in a subplot
        - dipslay
          Plots a D quantity in a subplot
        - colorbar
          Places a colorbar in a subplotor next to a subplot
        - zoom
          Creates an inset zom region of a subplot
        - text
          Places the text in the figure or in a subplot
        - interactive
          Creates a slider of a quantity as function of time
        

        Please refrain from using "private" methods and attributes.
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

    from ._readpart import _find_format