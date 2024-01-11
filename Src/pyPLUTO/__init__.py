from .libraries import *

class Load:
    """
    Load class.
    It loads the data.
    Attributes: blablabla
    Methods available: blablablax2
    """

    def __init__(self, 
                 nout: int | str | list[int|str] | None = 'last', 
                 path: str  = './', 
                 datatype: str | None = None, 
                 vars: str | list[str] | bool | None =  True,  
                 text: bool = True, 
                 alone: bool | None = False,
                 multiple: bool = False, 
                 endian: str | None = None 
                )-> None:
        """
        Initialization of the Load class.
        The initialization corresponds to the loading, if wanted, of one or 
        more datafiles for the fluid.
        The data are loaded in a memory mapped numpy multidimensional array. 
        Such approach does not load the full data until needed.
        Basic operations (i.e. no numpy) are possible, as well as slicing the 
        arrays, without fully loading the data.

        Returns
        -------

            The class, with the grid and the loaded variables.

        Parameters
        ----------

            - nout: int | str | list | None, default 'last'
                The files to be loaded. Possible choices are int 
                values (which correspond to the number of the output
                file), strings ('last', which corresponds to the last
                file, 'all', which corresponds to all files) or a 
                list of the aforementioned types.
                Note that the 'all' value should be used carefully, 
                e.g. only when the data need to be shown interactively.
                IMPORTANT!!! CHECK THAT IF YOU LOAD DIFFERENT STUFF IT DOES NOT EXPECT THE
                SAME NUMBER OF OUTPUTS OR THE SAME RESOLUTION!!!
            - path: str, default'./'
                The path of the folder where the files should be 
                loaded.
            - datatype: str | None, default None
                The format of the data file. If not specified, the code will 
                look for the format from the list of possible formats.
                HDF5 (AMR) and tab formats have not been implemented yet.
            - vars: str | list | bool | None, default True
                The variables to be loaded. The default value, True, 
                corresponds to all the variables.
            - text: bool, default True
                If a quick text (explaining the path and few information) 
                should be shown. In case the user needs a more detailed 
                information of the structure and attributes loaded from the 
                class, the __str__ method provides a easy display of all the 
                important information.
            - alone: bool | None, default False
                If the files are standalone. If False, the code will look for 
                the grid file in the folder. If True, the code will look for 
                the grid information within the data files. Should be used only
                for non-binary files.
            - multiple: bool, default False
                If the files are multiple. If False, the code will look for the
                single files, otherwise for the multiple files each 
                corresponding to the loaded variables. Should be used only if 
                both single files and multiple files are present in the same 
                format for the same datatype.
            - endian: str | None, default None
                Endianess of the datafiles. Should be used only if specific 
                architectures are used, since the code computes it by itself. 
                Valid values are 'big' and 'little' (or '<' and '>').

        Examples (CHECK)

            >>> import pyPLUTO as pp
            >>> D = pp.Load()
            Loading folder ./,     output [0]

            >>> D = pp.Load(nout = 0)
            Loading folder ./,     output [0]

            >>> D = pp.Load(nout = 'last')
            Loading folder ./,     output [1]

            >>> D = pp.Load(nout = 'all')
            Loading folder ./,     output [0, 1, 2, 3, 4]

            >>> D = pp.Load(nout = [0,1,2])
            Loading folder ./,     output [0, 1, 2]

            >>> D = pp.Load(nout = [0,1,2], vars = ['rho','vel1'])
            Loading folder ./,     output [0, 1, 2]

            >>> D = pp.Load(nout = [0,1,2], vars = ['rho','vel1'], text = False)
            
            >>> D = pp.Load(data = 'vtk', nout = 0)
            Loading folder ./,     output [0]

            >>> D = pp.Load(data = 'vtk', nout = 0, vars = ['rho','vel1'])
            Loading folder ./,     output [0]

            >>> D = pp.Load(path = './data/', nout = 0)
            Loading folder ./data/,     output [0]
        """

        # Check if the user wants to load the data
        if nout is None:
            return

        # Import the methods needed from other files
        from .readdata  import _check_pathformat, _find_format
        from .readdata  import _findfiles, _load_variables
        from .readfluid import _read_grid, _read_outfile
        
        # Initialization or declaration of variables (used in this file)
        self.nout: np.ndarray # Output to be loaded
        self._d_end: dict[str | None, str | None]  # Endianess dictionary
        self._multiple: bool    # Bool for single or multiple files
        self._alone: bool | None = None # Bool for standalone files
        self._info: bool # Bool for info (linked to alone)
        self._d_vars: dict = {} # The dictionary of variables

        # Initialization or declaration of variables (used in other files)
        self.pathdir: Path   # Path to the simulation directory
        self.format: str | None = None    # The format of the files to be loaded
        self.outlist: np.ndarray # The list of outputs to be loaded (CHECK TYPEHINT)
        self.timelist: np.ndarray # The list of times to be loaded (CHECK TYPEHINT)
        self.ntime: np.ndarray # The time array
        self.set_vars: set[str] # The set of variables to be loaded
        self.set_outs: set[int] # The set of outputs to be loaded 
        self.geom: str # The geometry of the simulation
        self.dim: int # The dimension of the simulation
        self.nshp: int | tuple[int, ...] # The shape of the grid
        self.nfile_lp: int | None  = None  # File number for the lp methods

        self._charsize: int # The data size in the files
        self._lennout: int # The number of outputs to be loaded
        self._d_info: dict[str, Any] # Info dictionary (CHECK TYPEHINT)
        self._matching_files: list[str] # The list of files to be loaded
        self._pathgrid: Path # Path to the grid file
        self._pathdata: Path | None = None # Path to the data files to be loaded
        self._filepath: Path # The filepath to be loaded
        self._load_vars: list[str] # The list of variables to be loaded
        self._offset: dict[str, int] # The offset of the variables
        self._shape: dict[str, tuple[int, ...]] # The shape of the variables
        self._vardim: list[int] # The dimension of the variables
        self._dictdim: dict # The dictionary of dimensions (CHECK TYPEHINT)   

        # Declaration of the grid variables
        self.x1: np.ndarray; self.x2: np.ndarray; self.x3: np.ndarray
        self.x1r: np.ndarray; self.x2r: np.ndarray; self.x3r: np.ndarray
        self.x1c: np.ndarray; self.x2c: np.ndarray
        self.x1rc: np.ndarray; self.x2rc: np.ndarray
        self.dx1: np.ndarray; self.dx2: np.ndarray; self.dx3: np.ndarray
        self.nx1: int; self.nx2: int; self.nx3: int
        self.gridsize: int
        self.gridlist3: list[str]
        self.x1p: np.ndarray; self.x2p: np.ndarray
        self.x1rp: np.ndarray; self.x2rp: np.ndarray

        self._gridsize_st1: int; self._nshp_st1: np.ndarray
        self._gridsize_st2: int; self._nshp_st2: np.ndarray
        self._gridsize_st3: int; self._nshp_st3: np.ndarray
    

        _nout_out: int | list[int]       # Output to be printed

        # Check the input endianess
        self._d_end = {'big':'>', 'little':'<', '>':'>', '<':'<', None:None} 
        
        if endian not in self._d_end.keys():
            raise ValueError(f"Invalid endianess. \
                             Valid values are {self._d_end.keys()}")
        
        # Check the input multiple
        if not isinstance (multiple, bool):
            raise TypeError("Invalid data type. 'multiple' must be a boolean.")
        else:
            self._multiple = multiple

       
        _check_pathformat(self, path)
            
        # Find the format of the data files
        _find_format(self, datatype, alone)

        # Find relevant informations without opening the files (e.g.
        # the number of files to be loaded) or opening the *.out files
        if self._alone is True:
            _findfiles(self, nout)
            self._info = True
        else:
            _read_grid(self)
            _read_outfile(self, nout, endian)
            self._info = False

        # For every output load the desired variables
        for i, exout in enumerate(self.nout):
            _load_variables(self, vars,i,exout,endian)

        # Assign the variables to the class
        for key in self._d_vars:
            setattr(self, key, self._d_vars[key])

        # Print loaded folder and output
        if text: 
            _nout_out = self.nout[0] if len(self.nout) == 1 else list(self.nout)
            print(f"Loading folder {path},     output {_nout_out}")

        return   
 
    def __str__(self):
        # CHECK

        txtshp = self.nshp if isinstance(self.nshp, int) else self.nshp[::-1]
        text3 = f"""        - Projections {['x1c','x2c','x1rc','x2rc']}\n"""
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
        - Grid shape    (nshp)     {txtshp}
        - Output loaded (nout)     {self.nout}
        - Time loaded   (ntime)    {self.ntime}

        Public attributes available:
        - Number of cells in each direction {['nx1','nx2','nx3']}
        - Grid values (cell center)         {['x1','x2','x3']}
        - Grid values (face center)         {['x1r','x2r','x3r']}
        - Cells size                        {['dx1','dx2','dx3']}
        - Time attributes                   {['outlist','timelist']}\n{text3}        
        Variables available:
        {self._d_info['varslist'][0]}
        Variables loaded: 
        {self._load_vars}

        Public methods available: WIP...

        Please refrain from using "private" methods and attributes.
        """
        return text


class LoadPart:

    def __init__(self, 
                 nout: int | str | None = 'last',   
                 path: str  = './' , 
                 datatype: str | None = None, 
                 vars: str | list[str] | bool | None =  True,  
                 text: bool = True, 
                 alone: bool = False,
                 endian: str | None = None,
                 nfile_lp: int | None = None
                ) -> None:
        # Check if the user wants to load the data
        if nout is None:
            return
        
        # Import the methods needed from other files
        from .readdata  import _check_pathformat, _find_format
        from .readdata  import _findfiles, _load_variables
        from .readpart  import _store_bin_particles

        # Initialization or declaration of variables (used in this file)
        self._d_end: dict[str | None, str | None]  # Endianess dictionary
        self._multiple: bool    # Bool for single or multiple files
        self._alone: bool | None = None # Bool for standalone files
        self._info: bool # Bool for info (linked to alone)
        self.nout: Any | list[Any] # Output to be loaded
        self._d_vars: dict = {} # The dictionary of variables

        # Initialization or declaration of variables (used in other files)
        self.pathdir: Path   # Path to the simulation directory
        self.format: str | None = None    # The format of the files to be loaded
        self._charsize: int # The data size in the files
        self.outlist: np.ndarray # The list of outputs to be loaded (CHECK TYPEHINT)
        self.timelist: np.ndarray # The list of times to be loaded (CHECK TYPEHINT)
        self._lennout: int # The number of outputs to be loaded
        self.ntime: np.ndarray # The time array
        self._d_info: dict[str, Any] # Info dictionary (CHECK TYPEHINT)
        self.set_vars: set[str] # The set of variables to be loaded
        self.set_outs: set[int] # The set of outputs to be loaded   
        self._matching_files: list[str] # The list of files to be loaded
        self._pathgrid: Path # Path to the grid file
        self._pathdata: Path | None = None # Path to the data files to be loaded
        self._filepath: Path # The filepath to be loaded
        self._load_vars: list[str] # The list of variables to be loaded
        self._offset: dict[str, int] # The offset of the variables
        self._shape: dict[str, tuple[int, ...]] # The shape of the variables
        self.geom: str # The geometry of the simulation
        self.dim: int # The dimension of the simulation
        self.nshp: int | tuple[int, ...] # The shape of the grid
        self._dictdim: dict # The dictionary of dimensions (CHECK TYPEHINT)
        self.nfile_lp: int | None  = nfile_lp  # File number for the lp methods
        self.maxpart: int = 0  # Max number of particles in the simulation
        self._vardim: np.ndarray # The dimension of the variables

        # Check the input endianess
        self._d_end = {'big': '>', 'little': '<', 
                       '>': '>', '<': '<', None: None} # Endianess dictionary
        
        if endian not in self._d_end.keys():
            raise ValueError(f"Invalid endianess. \
                             Valid values are {self._d_end.keys()}")

        # Check the path and verify that it is a folder
        _check_pathformat(self, path)
            
        # Find the format of the data files
        _find_format(self, datatype, alone)

        # Find relevant informations without opening the files (e.g.
        # the number of files to be loaded)
        _findfiles(self, nout)
        self.into = True

        # For every output load the desired variables and store them in the class
        for i, exout in enumerate(self.nout):
            _load_variables(self, vars,i,exout,endian)
            if self.format != 'vtk':
                _store_bin_particles(self, i)  
            else: 
                raise NotImplementedError("vtk files have not been fully implemented yet")

        # Assign the variables to the class
        for key in self._d_vars:
            setattr(self, key, self._d_vars[key])
        
        # Mask (Not currently, to be done) the id array and convert to int
        self.id = self.id.astype('int')
        '''
        # NEEDED FOR MULTIPLE LOADINGS?
        with warnings.catch_warnings():
            warnings.simplefilter("ignore", category=RuntimeWarning)
            self.id = np.ma.masked_array(self.id.astype('int'), np.isnan(self.id))
        '''

        # Print loaded folder and output
        if text is not False: 
            _nout_output = self.nout[0] if len(self.nout) == 1 else list(self.nout)
            print(f"Particles: loading folder {path},     output {_nout_output}")
        return
          
    def __str__(self):
        return f'''
        LoadPart class.
        It loads the particles.
        Attributes: blablabla
        Methods available: blablablax2
        Please refrain from using "private" methods.
        '''


class Image:

    def __init__(self, LaTeX: bool | str = True, 
                       text: bool = False, 
                       fig: int | str | Figure | SubFigure | None = None, 
                       **kwargs):
        """
        
        """

        self._assign_default()
        self._assign_LaTeX(LaTeX, kwargs.get('fontweight','normal'))        
        self._create_fig(fig, **kwargs)
        if text is not False:

            print(f"Creating Figure in window {self.nwin}")

    def __str__(self):
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
          Adds a set of [nrow,ncol] subplots to the figure.
        - set_axis
          Changes the parameter of a specific subplot
        - plot
          Plots one line in a subplot
        - legend
          Places one legend in a subplot
        - display
          Plots a 2D quantity in a subplot
        - colorbar
          Places a colorbar in a subplot or next to a subplot
        - zoom
          Creates an inset zoom region of a subplot
        - text
          Places the text in the figure or in a subplot
        

        Please refrain from using "private" methods and attributes.
        """

    from .h_image  import _place_inset_pos, _place_inset_loc
    from .h_image  import _set_parax, _check_par, _set_xrange, _set_yrange
    from .h_image  import _set_xticks, _set_yticks, _check_rows, _check_cols
    from .h_image  import _hide_text, _set_cscale
    from .h_image  import _check_fig, _add_ax, _assign_ax
    from .h_image  import _assign_default, _assign_LaTeX

    from .fig        import _create_fig, create_axes, set_axis
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
                pass

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
    from .lines     import fieldlines, field_interp, adv_field_line
    from .lines     import check_closed_line

from .pytools   import savefig, show, ring