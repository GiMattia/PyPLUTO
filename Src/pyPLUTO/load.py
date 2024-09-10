from .libraries   import *

class Load:
    """
    The Load class loads the data (fluid) from the output files. The 
    initialization corresponds to the loading, if wanted, of one or more 
    datafiles for the fluid. The data are loaded in a memory mapped numpy 
    multidimensional array. Such approach does not load the full data until 
    needed. Basic operations (i.e. no numpy) are possible, as well as slicing 
    the arrays, without fully loading the data.

    Returns
    -------

    - None

    Parameters
    ----------

    - alone: bool | None, default False
        If the files are standalone. If False, the code will look for the 
        grid file in the folder. If True, the code will look for the grid 
        information within the data files. Should be used only for non-binary 
        files.
    - datatype: str | None, default None
        The format of the data file. If not specified, the code will look for 
        the format from the list of possible formats. HDF5 (AMR) formats have 
        not been implemented yet.
    - endian: str | None, default None
        Endianess of the datafiles. Should be used only if specific 
        architectures are used, since the code computes it by itself. Valid 
        values are 'big' and 'little' (or '<' and '>').
    - multiple: bool, default False
        If the files are multiple. If False, the code will look for the single 
        files, otherwise for the multiple files each corresponding to the loaded
        variables. Should be used only if both single files and multiple files 
        are present in the same format for the same datatype.
    - nout: int | str | list | None, default 'last'
        The files to be loaded. Possible choices are int values (which 
        correspond to the number of the output file), strings ('last', which 
        corresponds to the last file, 'all', which corresponds to all files) or 
        a list of the aforementioned types. Note that the 'all' value should be 
        used carefully, e.g. only when the data need to be shown interactively. 
    - path: str, default './'
        The path of the folder where the files should be loaded.
    - text: bool, default True
        If True, the folder and output are printed. In case the user needs a 
        more detailed information of the structure and attributes loaded from 
        the class, the __str__ method provides a easy display of all the 
        important information.
    - vars: str | list | bool | None, default True
        The variables to be loaded. The default value, True, corresponds to all 
        the variables.
        
    Notes
    -----

    - Warning if the .out files are not found.

    ----

    Examples
    ========

    - Example #1: Load the data from the default folder and output
        
        >>> D = pp.Load()
        Loading folder ./,     output [0]

    - Example #2: Load the data from the default folder but output 0    

        >>> D = pp.Load(nout = 0)
        Loading folder ./,     output [0]

    - Example #3: Load the data from the default folder but last output is 
        specified    

        >>> D = pp.Load(nout = 'last')
        Loading folder ./,     output [1]

    - Example #4: Load the data from the default folder and all outputs    

        >>> D = pp.Load(nout = 'all')
        Loading folder ./,     output [0, 1, 2, 3, 4]

    - Example #5: Load the data from the default folder and multiple 
        selected outputs    

        >>> D = pp.Load(nout = [0,1,2])
        Loading folder ./,     output [0, 1, 2]

    - Example #6: Load the data from the default folder and multiple selected 
        outputs and variables    

        >>> D = pp.Load(nout = [0,1,2], vars = ['rho','vel1'])
        Loading folder ./,     output [0, 1, 2]

    - Example #7: Load the data from the default folder, multiple selected
        outputs and variables, without text

        >>> D = pp.Load(nout = [0,1,2], vars = ['rho','vel1'], text = False)
            
    - Example #8: Load the data from the default format with selected output
        and format
        
        >>> D = pp.Load(data = 'vtk', nout = 0)
        Loading folder ./,     output [0]

    - Example #9: Load the data from the default folder with selected output, 
        variables and format

        >>> D = pp.Load(data = 'vtk', nout = 0, vars = ['rho','vel1'])
        Loading folder ./,     output [0]
        
    - Example #10: Load the data from a specific folder with selected output  
        
        >>> D = pp.Load(path = './data/', nout = 0)
        Loading folder ./data/,     output [0]

    """

    def __init__(self, 
                 nout: int | str | list[int|str] | None = 'last', 
                 path: str  = './', 
                 datatype: str | None = None, 
                 vars: str | list[str] | bool | None =  True,  
                 text: bool = True, 
                 alone: bool | None = None,
                 multiple: bool = False, 
                 endian: str | None = None 
                ) -> None:

        # Check if the user wants to load the data
        if nout is None:
            return
        
        # Initialization or declaration of variables (used in this file)
        self.nout: NDArray # Output to be loaded
        self._d_end: dict[str | None, str | None]  # Endianess dictionary
        self._multiple: bool    # Bool for single or multiple files
        self._alone: bool | None = None # Bool for standalone files
        self._info: bool = True # Bool for info (linked to alone)
        self._d_vars: dict = {} # The dictionary of variables

        # Initialization or declaration of variables (used in other files)
        self.pathdir: Path   # Path to the simulation directory
        self.format: str | None = None    # The format of the files to be loaded
        self.outlist: NDArray # The list of outputs to be loaded
        self.timelist: NDArray # The list of times to be loaded
        self.ntime: NDArray # The time array
        self.set_vars: set[str] # The set of variables to be loaded
        self.set_outs: set[int] # The set of outputs to be loaded 
        self.geom: str # The geometry of the simulation
        self.dim: int # The dimension of the simulation
        self.nshp: int | tuple[int, ...] # The shape of the grid
        self.nfile_lp: int | None  = None  # File number for the lp methods

        self._charsize: int # The data size in the files
        self._lennout: int # The number of outputs to be loaded
        self._d_info: dict[str, Any] # Info dictionary
        self._matching_files: list[str] # The list of files to be loaded
        self._pathgrid: Path # Path to the grid file
        self._pathdata: Path | None = None # Path to the data files to be loaded
        self._filepath: Path # The filepath to be loaded
        self._load_vars: list[str] # The list of variables to be loaded
        self._offset: dict[str, int] # The offset of the variables
        self._shape: dict[str, tuple[int, ...]] # The shape of the variables
        self._vardim: list[int] # The dimension of the variables
        self._dictdim: dict # The dictionary of dimensions 

        # Declaration of the grid variables
        self.x1: NDArray; self.x2: NDArray; self.x3: NDArray # centered grid
        self.x1r: NDArray; self.x2r: NDArray; self.x3r: NDArray # staggered grid
        self.x1c: NDArray; self.x2c: NDArray # cartesian centered grid 
        self.x1rc: NDArray; self.x2rc: NDArray # cartesian staggered grid
        self.dx1: NDArray; self.dx2: NDArray; self.dx3: NDArray # cell size
        self.nx1: int; self.nx2: int; self.nx3: int # number of cells
        self.gridsize: int # total number of cells
        self.gridlist3: list[str] 
        self.x1p: NDArray; self.x2p: NDArray 
        self.x1rp: NDArray; self.x2rp: NDArray

        self._gridsize_st1: int; self._nshp_st1: NDArray
        self._gridsize_st2: int; self._nshp_st2: NDArray
        self._gridsize_st3: int; self._nshp_st3: NDArray
    
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

        # Check if the path is an existing directory
        self._check_pathformat(path)
            
        # Find the format of the data files
        self._find_format(datatype, alone)

        # Find relevant informations without opening the files (e.g.
        # the number of files to be loaded) or opening the *.out files
        if self._alone is True:
            self._findfiles(nout)
        else:
            self._read_outfile(nout, endian)

        # For every output load the desired variables
        for i, exout in enumerate(self.nout):
            self._load_variables(vars,i,exout,endian)

        # Assign the variables to the class
        for key in self._d_vars:
            setattr(self, key, self._d_vars[key])

        # Transpose nshp (to match with variables)
        try:
            self.nshp = self.nshp[::-1] if self.dim > 1 else self.nshp
        except:
            pass

        # Print loaded folder and output
        if text: 
            _nout_out = self.nout[0] if len(self.nout) == 1 else list(self.nout)
            print(f"Load: folder {path},     output {_nout_out}")

        return   
    
 
    def __str__(self):

        txtshp = self.nshp if isinstance(self.nshp, int) else self.nshp[::-1]
        text3 = f"        - Projections {['x1c','x2c','x1rc','x2rc']}\n"
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

        Public methods available: 
        
        - slices
        - mirror
        - cartesian_vector
        - reshape_cartesian
        - write_file
        - fourier
        - nabla
        - find_contour
        - find_fieldlines
        - vector_field


        Please refrain from using "private" methods and attributes.
        """
        return text
    
    
    def __getattr__(self, name):
        try:
            return getattr(self, f'_{name}')
        except:
            raise AttributeError(f"'Load' object has no attribute '{name}'")
         
    from .readformat  import _check_pathformat, _find_format
    from .readdata    import _load_variables, _check_nout, _findfiles
    from .readdata    import _init_vardict, _assign_var
    from .readgridout import _read_gridfile, _read_outfile, _split_gridfile
    from .readgridout import _read_grid_vtk, _read_grid_h5
    from .readfluid   import _compute_offset, _inspect_h5, _inspect_vtk
    from .readfluid   import _offset_bin, _read_tabfile
    from .write_files import _write_h5, write_file
    from .read_files  import _read_h5, read_file
    from .transform   import slices, mirror, cartesian_vector, reshape_cartesian
    from .fourier     import fourier
    from .findlines   import find_contour, find_fieldlines
    from .findlines   import _check_var  
    from .nabla       import gradient, curl, divergence
    