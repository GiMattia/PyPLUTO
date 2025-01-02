from .libraries import *

class LoadPart:
    """
    Load the particles from the simulation. The class is used to load the 
    particles from the simulation and store the data in the class attributes. 
    The data are loaded in a memory mapped numpy multidimensional array. Such 
    approach does not load the full data until needed. Basic operations (i.e. 
    no numpy) are possible, as well as slicing the arrays, without fully loading
    the data. At the moment, only one output can be loaded at a time.

    Returns
    -------

    - None

    Parameters
    ----------

    - datatype: str, default None
        The format of the data files to be loaded. If None, the code
        finds the format between dbl, flt and vtk.
    - endian: str | None, default None
        The endianess of the data files. If None, the code finds the 
        endianess.
    - nfile_lp: int | None, default None
        The file number for the lp methods. If None, the code finds the 
        file number.
    - nout: int | str | list | None, default 'last'
        The output number to be loaded. If 'last' the last output is loaded.
        If None, the data are not loaded.
    - path: str, default './'
        The path to the simulation directory.
    - text: bool, default True
        If True, the folder and output are printed.
        In case the user needs a more detailed information of the structure 
        and attributes loaded from the class, the __str__ method provides a 
        easy display of all the important information.
    - vars: str | list | bool | None, default True
        The variables to be loaded. If True, all the variables are loaded.
        If None, the data are not loaded.
    
    Notes
    -----

    - In future releases, multiple output files will be accessible at the 
        same time.

    ----

    Examples
    ========

    - Example #1: Load the last output from the simulation

        >>> LoadPart()

    - Example #2: Load the last output from the simulation with a specific
        endianess

        >>> LoadPart(endian = 'big')

    - Example #3: Load the last output from the simulation with a specific
        set of variables

        >>> LoadPart(vars = ['rho','vx','vy','vz'])

    - Example #4: Load the last output from the simulation without printing
        the folder and the specific output loaded
    
        >>> LoadPart(0, text = False) 

    - Example #5: Load the last output from the simulation without loading
        the data

        >>> LoadPart(nout = None)

    - Example #6: Load the last output from the simulation with a specific
        file number for the lp methods
    
        >>> LoadPart(nfile_lp = 1)

    """
        
    def __init__(self, 
                 nout: int | str | None = 'last',   
                 path: str  = './' , 
                 datatype: str | None = None, 
                 vars: str | list[str] | bool | None =  True,  
                 text: bool = True, 
                 endian: str | None = None,
                 nfile_lp: int | None = None
                ) -> None:
        
        # Check if the user wants to load the data
        if nout is None:
            return

        # Initialization or declaration of variables (used in this file)
        self.nout: NDArray # Output to be loaded
        self._d_end: dict[str | None, str | None]  # Endianess dictionary
        self._multiple: bool    # Bool for single or multiple files
        self._alone: bool = True # Bool for standalone files
        self._info: bool # Bool for info (linked to alone)
        self._d_vars: dict = {} # The dictionary of variables

        # Initialization or declaration of variables (used in other files)
        self.pathdir: Path   # Path to the simulation directory
        self.format: str | None = None    # The format of the files to be loaded
        self._charsize: int # The data size in the files
        self.outlist: NDArray # The list of outputs to be loaded
        self.timelist: NDArray # The list of times to be loaded
        self._lennout: int # The number of outputs to be loaded
        self.ntime: NDArray # The time array
        self._d_info: dict[str, Any] # Info dictionary
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
        self._dictdim: dict # The dictionary of dimensions
        self.nfile_lp: int | None  = nfile_lp  # File number for the lp methods
        self.maxpart: int = 0  # Max number of particles in the simulation
        self._vardim: NDArray # The dimension of the variables

        # Check the input endianess
        self._d_end = {'big': '>', 'little': '<', 
                       '>': '>', '<': '<', None: None} # Endianess dictionary
        
        if endian not in self._d_end.keys():
            raise ValueError(f"Invalid endianess. \
                             Valid values are {self._d_end.keys()}")

        # Check the path and verify that it is a folder
        self._check_pathformat(path)
            
        # Find the format of the data files
        self._find_format(datatype, True)

        # Find relevant informations without opening the files (e.g.
        # the number of files to be loaded)
        self._findfiles(nout)

        # For every output, load the desired variables and store 
        # them in the class
        for i, exout in enumerate(self.nout):
            self._load_variables(vars,i,exout,endian)
            if self.format != 'vtk':
                self._store_bin_particles(i)  
            else:
                self._store_vtk_particles(i)

        # Assign the variables to the class
        for key in self._d_vars:
            setattr(self, key, self._d_vars[key])

        # Change the id variable to int depending on the format loaded
        if self.format != 'vtk':
            self.id = self.id.astype('int')
        else:
            self.id = self.id.view('>i4')


        # Print loaded folder and output
        if text is not False: 
            _nout_out = self.nout[0] if len(self.nout) == 1 else list(self.nout)
            print(f"LoadPart: folder {path},     output {_nout_out}")
        return


    def __str__(self):
        text =  f"""
        LoadPart class.
        It loads the particles.
        
        File properties:
        - Current path loaded (pathdir)      {self.pathdir} 
        - Format loaded       (format)       {self.format}

        Simulation properties
        - N. particles  (maxpart)  {self.maxpart}
        - Output loaded (nout)     {self.nout}
        - Time loaded   (ntime)    {self.ntime}
        
        Variables loaded: 
        {self._d_vars.keys()}

        Public methods available: 
        
        - select
        - spectrum

        Please refrain from using "private" methods and attributes.
        """
        return text


    def __getattr__(self, name):
        try:
            return getattr(self, f'_{name}')
        except:
            raise AttributeError(f"'LoadPart' object has no attribute '{name}'")

    from .parttools   import  spectrum, select
    from .readformat  import _check_pathformat, _find_format
    from .readdata    import _load_variables, _check_nout, _findfiles
    from .readdata    import _init_vardict, _assign_var
    from .readpart    import _store_bin_particles, _store_vtk_particles
    from .readpart    import _inspect_bin, _inspect_vtk, _compute_offset
    