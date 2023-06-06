from ._libraries import *

print('Welcome to pyPLUTO!')

class Load:

    D = {}

    def __new__(cls, nout = 'last', path = './' , datatype = None, 
                     vars = True, text = True):
        
        cls.path = path if path[-1] == '/' else path+'/'
        if text is True:
            print('Loading folder:   '+str(cls.path))
            print('Preferred format: '+str(datatype))

        cls.PLUTO_formats = ['dbl','vtk','flt']
        cls.find_format(cls,datatype)
        if datatype == None and text == True:
            print('Format found:     '+str(cls.format))

        cls.read_grid(cls)
        cls.read_vars(cls,nout)
        if text == True:
            print('Dimensions:       '+str(cls.D['dim']))
            print('Geometry:         '+str(cls.D['geom']))
            print('Grid variables:   '+str(cls.gridlist1)[:-1]+',')
            print('                   '+str(cls.gridlist2)[1:-1]+',')
            try:
                print('                  '+str(cls.gridlist3)[1:-1]+',')
            except:
                None
            print('                   '+str(cls.gridlist4)[1:])
            print('Time variables:   '+str(cls.addvarlist))

        if isinstance(cls.D['nout'], list):
            cls.D['noutlist'] = cls.D['nout']
        else:
            cls.D['noutlist'] = [cls.D['nout']]
        for i, exout in enumerate(cls.D['noutlist']):
            cls.load_vars(cls,vars,i,exout,text)
        
        return cls.Dict2Class(cls.D)

    class Dict2Class():
        def __init__(self, my_dict):
            for key in my_dict:
                setattr(self, key, my_dict[key])

    from ._readout import find_format, read_grid, read_vars, load_vars
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

    from ._datatools import slices, mirror
    from ._nabla     import gradient
    from ._lines     import fieldlines, field_interp, adv_field_line, check_closed_line

from ._pytools   import savefig, show
