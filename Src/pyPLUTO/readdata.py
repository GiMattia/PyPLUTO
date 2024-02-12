from .libraries import *

def _load_variables(self, 
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
        self._compute_offset(i, endian, exout, None)

    # Check if only specific variables should be loaded
    if vars is True:
        self._load_vars = self._d_info['varslist'][i]
    else:
        self._load_vars = makelist(vars)

    if self.format  == 'tab':
        return None

    # Loop over the variables to be loaded
    for j in self._load_vars:
    
        # Change filepath, offset and shape in case of multiple_files
        if self._d_info['typefile'][i] == 'multiple_files':
            self._filepath = self.pathdir / (j + self._d_info['endpath'][i])
            self._compute_offset(i, endian, exout, j)

        # Initialize the variables dictionary
        self._init_vardict(j) if self._lennout != 1 else None

        # Load the variable through memory mapping and store them in the class
        scrh = np.memmap(self._filepath,self._d_info['binformat'][i],mode="r+",
                         offset=self._offset[j], shape = self._shape[j]).T
        self._assign_var(i, j, scrh)

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

def _check_nout(self, nout) -> None:
    """
    Finds the number of datafile to be loaded. If nout is a list,
    the function checks if the list contains the keyword 'last' or
    -1. If so, the keyword is replaced with the last file number.
    If nout is a string, the function checks if the string contains
    the keyword 'last' or -1. If so, the keyword is replaced with
    the last file number. If nout is an integer, the function
    returns a list containing the integer. If nout is 'all', the
    function returns a list containing all the file numbers.

    Returns
    -------

        None

    Parameters
    ----------

        - nout: int
            the output file to be loaded
    """

    # Assign the last possible output file
    last: int = self.outlist.tolist()[-1]

    # Check if nout is a list and change the keywords
    if not isinstance(nout,list):
        Dnout = {nout: nout, 'last': last, -1: last, 
                'all': self.outlist}[nout]
    else:
        Dnout = [last if i in {'last', -1} else i for i in nout]
    
    # Sort the list, compute the corresponding time and return its 
    # length
    self.nout  = np.sort(np.unique(np.atleast_1d(Dnout)))
    if np.any(~np.isin(self.nout, self.outlist)):
        raise ValueError(f"Error: Wrong output file(s) {self.nout} \
                         in path {self.pathdir}.")
    
    return None

def _findfiles(self, nout: int | str | list[int|str] | None) -> None:
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
    self._check_nout(nout)
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

def _init_vardict(self, var: str) -> None:
    """
    If not initialized, a new dictionary is created to store the
    variables. The dictionary is stored in the class.
    The shape of the dictionary is computed depending on the
    number of outputs and the shape of the variable.

    Returns
    -------

        None

    Parameters
    ----------

        - var: str
            the variable to be loaded.
    """

    # If the variable is not initialized, create a new dictionary
    if var not in self._d_vars.keys():

        # Compute the shape of the variable
        sh_type = self._shape[var][::-1] if isinstance(self._shape[var], tuple) else (self._shape[var],)
        if self.__class__.__name__ == 'LoadPart':
            # IMPORTANT! TO BE CHANGED WHEN MULTIPLE LOAD IS IMPLEMENTED
            varsh = self._dictdim[var]
            shape = (varsh,) + sh_type if varsh != 1 else sh_type
        else:
            shape = (self._lennout,) + sh_type if self._lennout != 1 else sh_type

        # Create the dictionary key and fill the values with nan
        with tempfile.NamedTemporaryFile() as temp_file:           
            self._d_vars[var] = np.memmap(temp_file, mode='w+', dtype=np.float32, shape = shape) # type: ignore
            self._d_vars[var][:] = np.nan
    return None



def _assign_var(self, time: int, var: str, scrh: np.memmap) -> None:
    """
    Assigns the memmap object to the dictionary. If the number of
    outputs is 1, the variable is stored directly in the dictionary,
    otherwise the variable is stored in the dictionary at the
    corresponding output.

    Returns
    -------

        None

    Parameters
    ----------

        - time: int
            the output file to be loaded
        - var: str
            the variable to be loaded.
        - scrh: np.memmap
            the memmap object containing the data to be stored.
    """

    # Assign the memmap object to the dictionary
    if self._lennout != 1:
        self._d_vars[var][time] = scrh
    else:
        self._d_vars[var] = scrh

    return None



def _varsouts_f(self, elem: str) -> None:
    """
    From the matching files finds the variables and the outputs
    for the fluid files (variables are to be intended here as the 
    first part of the output filename, they are the effective 
    variables only in case of multiple files).

    Returns
    -------

        None

    Parameters
    ----------

        - elem: str
            the matching file

    """

    # Splits the matching filename
    vars: str = elem.split('/')[-1].split('.')[0]
    outs: int = int(elem.split('.')[1])

    # Finds the variables and the outputs
    if vars != 'particles':
        self.set_vars.add(vars)
        self.set_outs.add(outs)

    return None



def _varsouts_p(self, elem: str) -> None:
    """
    From the matching files finds the outputs
    for the particle files (not LP).

    Returns
    -------

        None

    Parameters
    ----------

        - elem: str
            the matching file

    """

    # Splits the matching filename
    vars: str = elem.split('/')[-1].split('.')[0]
    outs: int = int(elem.split('.')[1])

    # Finds the outputs
    if vars == 'particles':
        self.set_vars.add(vars)
        self.set_outs.add(outs)

    return None



def _varsouts_lp(self, elem: str) -> None:
    """
    From the matching files finds the outputs
    for the LP files.

    Returns
    -------

        None

    Parameters
    ----------

        - elem: str
            the matching file

    """

    # Initialization or declaration of variables
    outn: int # The output number
    outc: int # The output ch number

    # Splits the matching filename
    vars: str = elem.split('/')[-1].split('.')[0].split('_')[0]
    outs: str = elem.split('.')[1]
    
    # Finds the outputs
    if vars == 'particles':
        outn = int(outs.split('_')[0])
        outc = int(outs.split('_')[1][2:])

        # Checks the _ch_ number
        if outc == self.nfile_lp:
            self.set_vars.add(vars)
            self.set_outs.add(outn)
        else:
            raise ValueError(f"Invalid number {self.nfile_lp}.")
        
    return None