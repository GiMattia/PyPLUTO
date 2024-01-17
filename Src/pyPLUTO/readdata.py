from .libraries import *
from .__init__ import Load, LoadPart

def _check_pathformat(self: Load | LoadPart, path: str) -> None:
    """
    Check if the path is consistent, i.e. if the path is given 
    through a non-empty string. If the path is consistent, it is 
    converted to a Path object. Then, a check is performed to see if
    the path is a directory. The path is stored in the class as a 
    Path object self.pathdir.

    Returns
    -------

        None

    Parameters
    ----------
        - path: str
            the path to the simulation directory
    """

    # Check if the path is a non-empty string. Then convert the 
    # string to a Path object
    if not isinstance(path, str):
        raise TypeError("Invalid data type. 'path' must be a "\
                        "non-empty string.")
    elif not path.strip():
        raise ValueError("'path' cannot be an empty string.")
    else:
        self.pathdir = Path(path)

    # Check that the path is a directory
    if not self.pathdir.is_dir():
        raise NotADirectoryError(f"Directory {self.pathdir} not found.")

    return None



def _find_format(self: Load | LoadPart, datatype: str | None, 
                       alone: bool | None) -> None:
    """
    Finds the format of the data files to load.
    At first, the code checks the filetype to be loaded (if fluid or
    particles). Then, depending on the filetype given, the code 
    checks if the corresponding filetype is present Depending on the
    properties of the filetype and of the type of the output (if
    fluid or particles) different checks are performed. 
    If no format is given or if the given format is not found, the
    code checks the presence other filetypes in the directory. If no
    file is found, an error is raised. CUrrent filetypes available 
    are dbl, flt, vtk, dbl.h5 and flt.h5.

    Returns
    -------

        None

    Parameters
    ----------

        - datatype: str, default None
            the file format. If None the format is recovered between 
            (in order) dbl, flt, vtk, dbl.h5 and flt.h5.
            Formats hdf5 (AMR) and tab have not been implemented yet.
        - alone: bool, default False
            if the output files are standalone or they require a .out
            file to be loaded. Only suggested for fluid files, .vtk
            format and standalone files, otherwise the code finds 
            the alone property by itself.
    """

    # Import the methods needed from other files
    from .h_load import _check_typeout, _check_typelon 

    # Initialization or declaration of variables
    type_out: list[str] # The list of possible filetypes for .out files
    type_lon: list[str] # The list of possible filetypes for standalone files
    typeout0: list[str] # The list of checked filetypes for .out files
    typelon0: list[str] # The list of checked filetypes for standalone files
    funcf: list[Callable] # The list of functions to be called
    class_name: str  = self.__class__.__name__ # The class name
    dbl: set[str] = {"dbl","dbl.h5"} # The set of double filetypes
    dict_func: dict[str, list[str]] # The dictionary of functions
    funcf: list[Callable] # The list of functions to be called
    scrh: str # The error message
    

    # Define the possible filetypes and set the keyword "alone" accordingly
    if class_name == 'Load':
        type_out = ['dbl','flt','vtk','dbl.h5','flt.h5','tab']
        type_lon = ['vtk','dbl.h5','flt.h5','tab']
        if datatype in {'dbl','flt'}:
            alone = False
    elif class_name == 'LoadPart':
        alone = True
        type_out = []
        type_lon = ['dbl', 'flt', 'vtk']
    else:
        raise NameError("Invalid class name.")
    
    # Check if the given datatype is valid
    if datatype not in type_out + type_lon + [None]:
        raise ValueError(f"Invalid datatype {datatype}.")
    
    # Create the list of types to iterate over

    typeout0 , typelon0 = ([], []) if \
                    datatype is not None else (type_out, type_lon)
    type_out = [datatype] if  datatype in type_out else typeout0
    type_lon = [datatype] if  datatype in type_lon else typelon0
    
    # Create the list of functions to be called (.out or alone)
    funcf = [_check_typeout] if len(type_out) > 0 \
                                   and alone is not True else []
    funcf += [_check_typelon] if len(type_lon) > 0 \
                                   and alone is not False else []
    
    # Define the dictionary for the function argument
    dict_func = {'_check_typeout': type_out, '_check_typelon': type_lon}

    # Iterate over the functions to be called
    for do_check in funcf:
        do_check(self, dict_func[do_check.__name__])

        # Check if the format has been found
        if self.format is not None:
            # Store the charsize depending on the format
            self._charsize = 8 if self.format in dbl else 4
            return None
        
    # No file has been found, so raise an error
    scrh = f"No available type has been found in {self.pathdir}."
    if datatype is not None:
        scrh = f"Type {datatype} not found."
    raise FileNotFoundError(scrh)



def _findfiles(self: Load | LoadPart, nout: int | str | list[int|str] | None) -> None:
    """
    Finds the files to be loaded. If nout is a list, the function
    loops over the list and finds the corresponding files. If nout
    is an integer, the function finds the corresponding file. If
    nout is 'last', the function finds the last file. If nout is
    'all', the function finds all the files. Then, the function
    stores the relevant information in a dictionary _d_info.

    Returns
    -------

        None

    Parameters
    ----------

        - nout: int
            the output file to be loaded
    """
    # Import the methods needed for the initialization
    from .h_load import _varsouts_f, _varsouts_p, _varsouts_lp
    from .h_load import _check_nout

    # Initialization or declaration of variables
    condition: int # Condition for particles LP 
    format_string: str # The format string for the files
    class_name: str = self.__class__.__name__ # The class name
    self.set_vars = set() 
    self.set_outs = set()
    
    # Create a dictionary of functions to be called
    # (0 = fluid, 1 = particles, 2 = lagrangian particles)
    varsouts: dict[int, Callable] = {0: _varsouts_f, 
                                     1: _varsouts_p, 
                                     2: _varsouts_lp}
    
    # Set the condition for the dictionary
    condition = (class_name == 'LoadPart') + (self.nfile_lp is not None)

    # Loop over the matching files and call the functions
    for elem in self._matching_files:
        varsouts[condition](self, elem)       

    # Sort the outputs in an array and check the number of outputs
    self.outlist = np.array(sorted(self.set_outs))
    _check_nout(self, nout)
    self._lennout = len(self.nout)
    self.ntime = np.empty(self._lennout)

    # Initialize the info dictionary
    self._d_info = {}
    self._d_info['typefile']  = np.empty(self._lennout, dtype = 'U20')
    self._d_info['endianess'] = np.empty(self._lennout, dtype = 'U20')
    self._d_info['binformat'] = np.empty(self._lennout, dtype = 'U20')

    # Check if we are loading particle files
    if class_name == 'LoadPart':
        if 'particles' not in self.set_vars:
            raise FileNotFoundError(f'file particles.*.{self.format} \
                                    not found!')
        self._d_info['typefile'][:] = 'single_file'  
        self._d_info['varslist'] = [[] for _ in range(self._lennout)]  
        self._d_info['varskeys'] = [[] for _ in range(self._lennout)]
        
        # Check if we are loading a single file (to be fixed)
        if self._lennout != 1:
            raise NotImplementedError('multiple loading not implemented yet')

    # Check if fluid files are single or multiple. If multiple 
    # find the variables
    else:
        if 'data' not in self.set_vars or self._multiple is True:
            self._d_info['typefile'][:] = 'multiple_files'
            self._d_info['varslist'] = np.empty((self._lennout, \
                                       len(self.set_vars)), dtype = 'U20')
            self._d_info['varslist'][:] =  list(self.set_vars)
        else:
            self._d_info['typefile'][:] = 'single_file'  
            self._d_info['varslist'] = [[] for _ in range(self._lennout)]     
           
    # Compute the endpath
    if self.nfile_lp is None:
        format_string = f'.%04d.{self.format}'
    else:
        format_string = f'.%04d_ch{self.nfile_lp:02d}.{self.format}'
    self._d_info['endpath'] = np.char.mod(format_string, self.nout)

    return None



def _load_variables(self: Load | LoadPart, 
                    vars: str | list[str] | bool | None, 
                    i: int, 
                    exout: int, 
                    endian: str | None) -> None:
    """
    Loads the variables in the class. The function checks if the
    variables to be loaded are valid and then loads them. If the
    variables are not valid, an error is raised. If the variables
    are valid, the function loads them in the class through memory
    mapping. The offset and shape of each variable is computed depenging
    on the format and typefile characteristics. In case the files are
    standalone, the relevand time and grid information is loaded.

    Returns
    -------

        None

    Parameters
    ----------

        - vars: bool, default True
            if True all the variables are loaded, otherwise just a selection
            is loaded.
        - i: int
            the index of the file to be loaded.
        - exout: int
            the index of the output to be loaded.
        - endian: bool
            the endianess of the files. If True the endianess is big, 
            otherwise it is little.
    """

    # Import the methods needed from other files
    from .readfluid import _read_tabfile
    from .h_load    import _compute_offset, _init_vardict, _assign_var

    # Find the class name and find the single_file filepath
    class_name: str = self.__class__.__name__
    if class_name == 'Load':
        self._filepath = self.pathdir / ('data' + self._d_info['endpath'][i])
    else:
        self._filepath = self.pathdir / ('particles' + \
                                                  self._d_info['endpath'][i])

    # If files in single_file format, inspect the file
    # or compute the offset and shape
    if self._d_info['typefile'][i] == 'single_file':
        _compute_offset(self, i, endian, exout, None)

    # Check if only specific variables should be loaded
    if vars is True:
        self._load_vars = self._d_info['varslist'][i]
    else:
        self._load_vars = makelist(vars)

    if self.format  == 'tab':
        _read_tabfile(self, i)
        return None

    # Loop over the variables to be loaded
    for j in self._load_vars:
    
        # Change filepath, offset and shape in case of multiple_files
        if self._d_info['typefile'][i] == 'multiple_files':
            self._filepath = self.pathdir / (j + self._d_info['endpath'][i])
            _compute_offset(self, i, endian, exout, j)

        # Initialize the variables dictionary
        _init_vardict(self, j) if self._lennout != 1 else None

        # Load the variable through memory mapping and store them in the class
        scrh = np.memmap(self._filepath,self._d_info['binformat'][i],mode="r+",
                         offset=self._offset[j], shape = self._shape[j]).T
        _assign_var(self, i, j, scrh)

    return None

# NOT SURE IF NECESSARY
"""
def _delete_vars(self):
    allowed_vars = self.gridlist1
    method_names = ['_delete_vars', '_rec_format']

    allowed_dict = {var: getattr(self, var) for var in allowed_vars}
    self.__dict__ = allowed_dict

    for method_name in method_names:
        if method_name in self.__class__.__dict__:
            delattr(self.__class__, method_name)
"""