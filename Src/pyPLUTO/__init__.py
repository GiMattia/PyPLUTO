from .libraries import *

class OldLoad:

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
                       vars =  True,  text: bool = True, alone: bool = False):
        '''
        Initialization of the Load class.
        The initialization corresponds to the loading, if wanted, of one or more
        datafiles for the fluid.
        The data are loaded in a numpy multidimensional array through memory mapping. Such approach
        does not load the data until needed.
        Basic operations (i.e. no numpy) are possible, as well as slicing the arrays, without
        fully loading the data.

        Returns
        -------

            The class, with the grid and the loaded variables.

        Parameters
        ----------

            - nout: int/str/list, default 'last'
                The files to be loaded. Possible choices are int values (which
                correspond to the number of the output file), strings ('last', which
                corresponds to the last file, 'all', which corresponds to all files)
                or a list of the aforementioned types.
                Note that the 'all' value should be used carefully, e.g. when the
                data need to be shown interactively.
            - path: str, default'./'
                The path of the folder where the files should be loaded.
            - datatype: str, default None
                The format of the data file. If not specified, the code will look for 
                the format from the list ['dbl','vtk','flt'] in the following order.
                HDF5 and tab formats have not been implemented yet.
            - vars: str/list/bool, default True
                The variables to be loaded. The default value, True, corresponds to all the
                variables.
            - text: bool, default True
                If a quick text (explaining the path and few information) should be
                shown. In case the user needs a more detailed information of the structure
                and attributes loaded from the class, the __str__ method provides
                a easy display of all the important information.
        '''

        self._check_pathformat(path)

        if text is not False: print(f'Loading folder:   {path}')
            
        self._find_format(datatype, alone)

        self._read_grid()
        self._read_varsout(nout)   
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
        - Current path loaded (pathdir)      {self.pathdir} 
        - Format loaded       (format)       {self.format}

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
    
    from .readdata  import _check_pathformat, _find_format
    from .readfluid import _find_formatout, _read_grid, _read_varsout
    from .readfluid import _load_vars #, _delete_vars
    from .h_load    import _split_gridfile, _rec_format, _vtk_offset, _gen_offset
    from .h_load    import _check_nout, _init_vardict, _assign_var, _shape_st
    
class Image:

    def __init__(self,LaTeX = True, text: bool = False, fig = None, **kwargs):

       # self.assign_default()
       # self.assign_LaTeX(LaTeX)

        self.fontsize: int  = 17
        self.tight:    bool = True
        self.nwin:     int  = 1
        self.figsize = [8,5]
        self._set_size = False
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
                'pgf.preamble': pgf_preamble,
                'font.family': 'serif',
                'font.weight': fontweight,
                'text.usetex': True
            })

        self.create_fig(fig, **kwargs)
        if text is not False:
            print(f"Creating Figure in window {self.nwin}")

    def __str__(self):
        plt.rcParams['text.usetex'] = True
        plt.rcParams['text.latex.preamble'] = r'\usepackage{amsmath}'
        return rf"""
        Image class.
        It plots the data.

        Image properties:
        - Figure size        (figsize)       {self.figsize}
        - Window number      (nwin)          {self.nwin}
        - Number of subplots (nrow0 x ncol0) {self.nrow0} x {self.ncol0}
        - Global fontsize    (fontsize)      {self.fontsize}

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
        - display
          Plots a 2D quantity in a subplot
        - colorbar
          Places a colorbar in a subplotor next to a subplot
        - zoom
          Creates an inset zom region of a subplot
        - text
          Places the text in the figure or in a subplot
        - interactive
          Creates a slider of a quantity as function of time
        

        Please refrain from using "private" methods and attributes.
        """

    from .h_image  import _place_inset_pos, _place_inset_loc
    from .h_image  import _set_parax, _check_par, _set_xrange, _set_yrange
    from .h_image  import _set_xticks, _set_yticks, _check_rows, _check_cols
    from .h_image  import _hide_text, _set_cscale
    from .h_image  import _check_fig, _add_ax, _assign_ax

    from .fig        import create_fig, create_axes, set_axis
    from .plot       import plot, legend
    from .display    import display, colorbar
    from .interact   import interactive, _update_slider
    from .figtools   import savefig, show, text
    from .zoom       import zoom, _zoomplot, _zoomdisplay
    from .plot_part  import scatter, histogram


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

    from .datatools import slices, mirror
    from .nabla     import gradient
    from .lines     import fieldlines, field_interp, adv_field_line, check_closed_line

from .pytools   import savefig, show



class LoadPart:
    def __init__(self, nout = 'last', path: str  = './' , 
                       datatype: str = None, vars =  True,  
                       text: bool = True, alone: bool = True,
                       multiple: bool = False, endian: str = None):
        # Check if the user wants to load the data
        if nout is None:
            return

        self.D_vars   = {}   # Dictionary of variables loaded
        self.D_info   = {}   # Dictionary of info loaded
        self.pathdata = None # Path to the data files to be loaded
        self.D_end    = {'big': '>', 'little': '<', None: None} # Endianess dictionary
        self.maxpart  = 0  # Max number of particles in the simulation
        if endian not in self.D_end.keys():
            raise ValueError(f"Invalid endianess. Valid values are {self.D_end.keys()}")

        # Check the path and verify that it is a folder
        self._check_pathformat(path)
            
        # Find the format of the data files
        self._new_find_format(datatype, alone)

        # Find relevant informations without opening the files (e.g.
        # the number of files to be loaded)
        self._findfiles(nout)
        self.into = True

        # For every output load the desired variables and store them in the class
        for i, exout in enumerate(self.nout):
            self._new_load_vars(vars,i,exout,endian)
            if self.format != 'vtk':
                self._store_bin_particles(i)  
            else: 
                raise NotImplementedError('vtk files have not been fully implemented yet')

        # Assign the variables to the class
        for key in self.D_vars:
            setattr(self, key, self.D_vars[key])
        
        # Mask (Not currently, to be done) the id array and convert to int
        self.id = self.id.astype('int')
        '''
        with warnings.catch_warnings():
            warnings.simplefilter("ignore", category=RuntimeWarning)
            self.id = np.ma.masked_array(self.id.astype('int'), np.isnan(self.id))
        '''

        # Print loaded folder and output
        if text is not False: 
            nout_output = self.nout[0] if len(self.nout) == 1 else list(self.nout)
            print(f"Particles: loading folder {path},     output {nout_output}")
        return
          
    def __str__(self):
        return f'''
        LoadPart class.
        It loads the particles.
        Attributes: blablabla
        Methods available: blablablax2
        Please refrain from using "private" methods.
        '''

    from .readdata  import _check_pathformat, _new_find_format, _new_load_vars
    from .readfluid import _new_read_grid, _read_outfile
    from .h_load    import _check_typeout, _check_typelon 
    from .h_load    import _new_split_gridfile, _new_check_nout
    from .h_load    import _findfiles   
    from .h_load    import _inspect_bin, _inspect_vtk, _inspect_h5
    from .h_load    import _compute_offset, _offset_bin, _new_init_vardict
    from .h_load    import _new_assign_var, _store_bin_particles

class Load:

    def __init__(self, nout = 'last', path: str  = './' , 
                       datatype: str = None, vars =  True,  
                       text: bool = True, alone: bool = False,
                       multiple: bool = False, endian: str = None):
        """
        Initialization of the Load class.
        The initialization corresponds to the loading, if wanted, of one or more
        datafiles for the fluid.
        The data are loaded in a numpy multidimensional array through memory mapping. Such approach
        does not load the data until needed.
        Basic operations (i.e. no numpy) are possible, as well as slicing the arrays, without
        fully loading the data.

        Returns
        -------

            The class, with the grid and the loaded variables.

        Parameters
        ----------

            - nout: int/str/list, default 'last'
                The files to be loaded. Possible choices are int 
                values (which correspond to the number of the output
                file), strings ('last', which corresponds to the last
                file, 'all', which corresponds to all files) or a 
                list of the aforementioned types.
                Note that the 'all' value should be used carefully, 
                e.g. when the data need to be shown interactively.
            - path: str, default'./'
                The path of the folder where the files should be 
                loaded.
            - datatype: str, default None
                The format of the data file. If not specified, the 
                code will look for the format from the list ['dbl','vtk','flt'] in the following order.
                HDF5 and tab formats have not been implemented yet.
            - vars: str/list/bool, default True
                The variables to be loaded. The default value, True, corresponds to all the
                variables.
            - text: bool, default True
                If a quick text (explaining the path and few information) should be
                shown. In case the user needs a more detailed information of the structure
                and attributes loaded from the class, the __str__ method provides
                a easy display of all the important information.
            - alone: bool, default False
                If the files are standalone. If False, the code will look for the
                grid file in the folder. If True, the code will look for the grid
                information within the data files. Should be used only for non-binary files.
            - multiple: bool, default False
                If the files are multiple. If False, the code will look for the
                single files, otherwise for the multiple files each corresponding to the
                loaded variables. Should be used only if both single files and multiple files are
                present.
            - endian: str, default None
                Endianess of the datafiles. Should be used only if specificachitectures
                are used, since the code computes it by itself. Valid values are 'big' and 'little'.
        """

        # Check if the user wants to load the data
        if nout is None:
            return

        self.D_vars   = {}   # Dictionary of variables loaded
        self.D_info   = {}   # Dictionary of info loaded
        self.pathdata = None # Path to the data files to be loaded
        self.D_end = {'big': '>', 'little': '<', None: None} # Endianess dictionary
        if endian not in self.D_end.keys():
            raise ValueError(f"Invalid endianess. Valid values are {self.D_end.keys()}")

        # Check the path and verify that it is a folder
        self._check_pathformat(path)
            
        # Find the format of the data files
        self._new_find_format(datatype, alone)

        # Find relevant informations without opening the files (e.g.
        # the number of files to be loaded) or opening the *.out files
        if self.alone is not True:
            self._new_read_grid()
            self._read_outfile(nout, endian)
            self.info = False
        else:
            self._findfiles(nout)
            self.info = True

        # For every output load the desired variables
        for i, exout in enumerate(self.nout):
            self._new_load_vars(vars,i,exout,endian)

        # Assign the variables to the class
        for key in self.D_vars:
            setattr(self, key, self.D_vars[key])

        # Print loaded folder and output
        if text is not False: 
            nout_output = self.nout[0] if len(self.nout) == 1 else list(self.nout)
            print(f"Loading folder {path},     output {nout_output}")

        return      

    def __str__(self):
        text3 = f"""        - Cartesian projection              {['x1c','x2c','x1rc','x2rc']}\n"""
        text3 = text3 if self.geom != 'CARTESIAN' else ""

        text = f"""
        Load class.
        It loads the data.

        File properties:
        - Current path loaded (pathdir)      {self.pathdir} 
        - Format loaded       (format)       {self.format}

        Simulation properties
        - Dimensions    (dim)      {self.dim}
        - Geometry      (geom)     {self.geom}
        - Grid size     (gridsize) {self.gridsize}
        - Grid shape    (nshp)     {self.nshp[::-1]}
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
        """
        return text
    
    from .readdata  import _check_pathformat, _new_find_format, _new_load_vars
    from .readfluid import _new_read_grid, _read_outfile
    from .h_load    import _check_typeout, _check_typelon 
    from .h_load    import _new_split_gridfile, _new_check_nout
    from .h_load    import _findfiles   
    from .h_load    import _inspect_bin, _inspect_vtk, _inspect_h5
    from .h_load    import _compute_offset, _offset_bin, _new_init_vardict
    from .h_load    import _new_assign_var