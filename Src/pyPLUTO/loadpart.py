from .libraries import *
from .readformat  import _check_pathformat, _find_format
from .readdata    import _load_variables, _check_nout, _findfiles
from .readdata    import _init_vardict, _assign_var
from .readpart    import _store_bin_particles, _store_vtk_particles
from .readpart    import _inspect_bin, _inspect_vtk, _compute_offset

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
        self.outlist: NDArray # The list of outputs to be loaded (CHECK TYPEHINT)
        self.timelist: NDArray # The list of times to be loaded (CHECK TYPEHINT)
        self._lennout: int # The number of outputs to be loaded
        self.ntime: NDArray # The time array
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
        self._find_format(datatype, alone)

        # Find relevant informations without opening the files (e.g.
        # the number of files to be loaded)
        self._findfiles(nout)
        self.into = True

        # For every output load the desired variables and store them in the class
        for i, exout in enumerate(self.nout):
            self._load_variables(vars,i,exout,endian)
            if self.format != 'vtk':
                self._store_bin_particles(i)  
            else:
                self._store_vtk_particles(i)
           # else: 
            #    raise NotImplementedError("vtk files have not been fully implemented yet")

        # Assign the variables to the class
        for key in self._d_vars:
            setattr(self, key, self._d_vars[key])
        
        # Mask (Not currently, to be done) the id array and convert to int
        if self.format != 'vtk':
            self.id = self.id.astype('int')
        else:
            self.id = self.id.view('>i4')

        """
        # NEEDED FOR MULTIPLE LOADINGS?
        with warnings.catch_warnings():
            warnings.simplefilter("ignore", category=RuntimeWarning)
            self.id = np.ma.masked_array(self.id.astype('int'), np.isnan(self.id))
        """

        # Print loaded folder and output
        if text is not False: 
            _nout_output = self.nout[0] if len(self.nout) == 1 else list(self.nout)
            print(f"Particles: loading folder {path},     output {_nout_output}")
        return
          
    def __str__(self):
        return f"""
        LoadPart class.
        It loads the particles.
        Attributes: blablabla
        Methods available: blablablax2
        Please refrain from using "private" methods.
        """

    def __getattr__(self, name):
        try:
            return getattr(self, f'_{name}')
        except:
            raise AttributeError(f"'Load' object has no attribute '{name}'")

    def _check_pathformat(self,*args,**kwargs):
        return _check_pathformat(self,*args,**kwargs)
    
    def _find_format(self,*args,**kwargs):
        return _find_format(self,*args,**kwargs)
    
    def _findfiles(self,*args,**kwargs):
        return _findfiles(self,*args,**kwargs)
    
    def _load_variables(self,*args,**kwargs):
        return _load_variables(self,*args,**kwargs)
    
    def _check_nout(self,*args,**kwargs):
        return _check_nout(self,*args,**kwargs)
    
    def _init_vardict(self,*args,**kwargs):
        return _init_vardict(self,*args,**kwargs)

    def _assign_var(self,*args,**kwargs):
        return _assign_var(self,*args,**kwargs)
    
    def _store_bin_particles(self,*args,**kwargs):
        return _store_bin_particles(self,*args,**kwargs)
    
    def _store_vtk_particles(self,*args,**kwargs):
        return _store_vtk_particles(self,*args,**kwargs)
    
    def _inspect_bin(self,*args,**kwargs):
        return _inspect_bin(self,*args,**kwargs)
    
    def _inspect_vtk(self,*args,**kwargs):
        return _inspect_vtk(self,*args,**kwargs)
    
    def _compute_offset(self,*args,**kwargs):
        return _compute_offset(self,*args,**kwargs)
    
