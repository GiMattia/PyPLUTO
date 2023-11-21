from .libraries import *

def _split_gridfile(self, i, xL, xR, nmax):
    """
    Splits the gridfile, storing the information in the variables
    passed by the function. Dimensions and geometry are stored in 
    the class

    Return
    ------

        None

    Parameters
    ----------

        None
    """

    # If the splitted line has only one string, try to convert it
    # to an integer (number of cells in a dimension). 
    if len(i.split()) == 1:
        try:
            nmax.append(int(i.split()[0]))
        except:
            pass
    
    # CHeck if the splitted line has three strings
    if len(i.split()) == 3:
        # Try to convert the first string to an integer (cell number 
        # in a dimension) and the other two to floats (left and right cell boundaries)
        try:
            int(i.split()[0])
            xL.append(float(i.split()[1]))
            xR.append(float(i.split()[2]))
        
        # Check if the keyword is geometry or dimensions and
        # store the information in the class
        except:
            if i.split()[1] == 'GEOMETRY:'  : self.geom = i.split()[2]
            if i.split()[1] == 'DIMENSIONS:': self.dim  = int(i.split()[2])

    return None

def _check_typeout(self, datatype: str, type_out: List[str],
                         type_lon: List[str]) -> List[str]:
    """
    Loops over possible formats in order to find, at first the 
    grid.out file, then the datatype.out file. If the datatype.out
    file is found, the file format is selected and the flag alone is
    set to False.

    Returns
    -------

        None

    Parameters
    ----------

        - datatype: str
            the format selected by the user (if not then is None)
        - type_out: [str]
            the list of possible formats for the output file
        - type_lon: [str]
            the list of possible formats for the output file
            (not used here but in _check_typelon)
    """

    # Loop over the possible formats
    for try_type in type_out:

        # Check if the grid.out file is present
        self._pathgrid  = self.pathdir / 'grid.out'
        self._pathdata = self.pathdir / (try_type + '.out')
        
        # Check if the datatype.out file is present
        if self._pathdata.is_file() and self._pathgrid.is_file():
            self.format = try_type
            self._alone = False
            break
        
    return None



def _check_typelon(self, datatype: str, type_out: List[str],
                         type_lon: List[str]) -> List[str]:
    """
    Loops over posisble formats in order to find matching files
    with the datatype. If the file is found, the file format is
    selected and the flag alone is set to True.

    Returns
    -------

        None
    
    Parameters
    ----------

        - datatype: str
            the format selected by the user (if not then is None)
        - type_out: [str]
            the list of possible formats for the output file
            (not used here but in _check_typeout)
        - type_lon: [str]
            the list of possible formats for the output file
    """

    # Loop over the possible formats
    for try_type in type_lon:

        # Create the pattern to be searched
        pattern = self.pathdir / ('*.*.' + try_type)
        self._matching_files = glob.glob(str(pattern))

        # Check if the file is present
        if self._matching_files:
            self.format = try_type
            self._alone = True
            break

    return None



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
    last = self.outlist.tolist()[-1]

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
        raise ValueError(f"Error: Wrong output file(s) {self.nout}.")
    
    return None



def _inspect_bin(self, i: int, endian: str) -> None:
    """
    Routine to inspect the binary file and find the variables, the offset
    and the shape. The routine loops over the lines of the file and
    finds the relevant information. The routine then creates a key 'tot'
    in the offset and shape dictionaries, which contains the offset and
    shape of the whole data.

    Returns
    -------

        None

    Parameters
    ----------

        - i: int
            the index of the file to be loaded.
        - endian: str
            the endianess of the files.

    """

    # Initialize the offset, shape arrays and dimensions dictionary
    self._offset, self._shape, self._dictdim = ({},{},{})

    # Open the file and read the lines
    f = open(self._filepath, 'rb')
    for l in f:

        # Split the lines (unsplit are binary data)
        try:
            spl0, spl1, spl2 = l.split()[0:3]
        except:
            break

        # Find the dimensions of the domain
        if spl1 == b'dimensions':
            self.dim = int(spl2)

        # Find the endianess of the file and compute the binary format
        elif spl1 == b'endianity':
            self._d_info['endianess'][i] = '>' if endian == b'big' else '<'
            self._d_info['endianess'][i] = self._d_end[endian] if endian is not None \
                                    else self._d_info['endianess'][i]
            scrh = 'f'if self._charsize == 4 else 'd'
            self._d_info['binformat'][i] = self._d_info['endianess'][i] + scrh

        # Find the number of particles in the datafile and the maximum
        # number of particles in the simulation
        elif spl1 == b'nparticles':
            self.nshp = int(l.split()[2])
            self.npart = self.nshp

        # To be fixed (multiple loading)
        elif spl1 == b'idCounter':
            self.maxpart = np.max([int(l.split()[2]), self.maxpart])

        # Find the time information
        elif spl1 == b'time':
            self.ntime[i] = float(spl2)

        # Find the variable names
        elif spl1 == b'field_names':
            self._d_info['varskeys'][i] = [elem.decode() for elem in l.split()[2:]]
            self._d_info['varslist'][i] = ['tot']

        # Find the variable dimensions
        elif spl1 == b'field_dim':
            self._vardim = np.array([int(elem.decode()) for elem in l.split()[2:]])
            self._offset['tot'] = f.tell()
            self._shape['tot']  = (self.nshp,np.sum(self._vardim))
            # To be fixed (multiple loading)
            #self._shape['tot']  = (self.maxpart,np.sum(self.vardim))

    f.close()
    # Create the key variables in the vars dictionary
    for ind, j in enumerate(self._d_info['varskeys'][i]):
        self._shape[j] = self.nshp 
        self._dictdim [j] = self._vardim[ind]  
        self._init_vardict(j)

    return None



def _inspect_vtk(self, i: int, endian: str) -> None:
    """
    Routine to inspect the vtk file and find the variables, the offset
    and the shape. The routine loops over the lines of the file and
    finds the relevant information. The routine also finds the time
    information if the file is standalone. The routine also finds the
    coordinates if the file is standalone and cartesian.

    Returns
    -------

        None

    Parameters
    ----------

        - i: int
            the index of the file to be loaded.
        - endian: str
            the endianess of the files.
    """

    # Initialize the offset and shape arrays, the endianess and the coordinates dictionary
    self._offset, self._shape = ({},{})
    endl = self._d_info['endianess'][i] = '>' if endian is None else self._d_end[endian]
    if self._info is True:
        self.nshp = 0
        self._d_info['binformat'] = np.char.add(self._d_info['endianess'], 
                                          'f' + str(self._charsize))

    # Open the file and read the lines
    f = open(self._filepath, 'rb')
    for l in f:

        # Split the lines (unsplit are binary data)
        try:
            spl0, spl1, spl2 = l.split()[0:3]
        except:
            continue

        # Find the coordinates and store them
        if spl0 in [j + b"_COORDINATES" for j in [b"X", b"Y", b"Z"]] and self._info is True:
            var_sel = spl0.decode()[0]
            binf = endl+'d' if spl2.decode() == 'double' else endl+'f'
            offset = f.tell()
            shape = int(spl1)
            scrh = np.memmap(self._filepath,dtype=binf,mode='r',offset=offset, shape = shape)
            exec(f"{dir_map[var_sel]} = scrh")

        # Find the scalars and compute their offset
        elif spl0 == b'SCALARS':
            var = spl1.decode()
            f.readline()
            self._offset[var] = f.tell()
            self._shape[var] = self.nshp

        # Compute the time information
        elif spl0 == b'TIME' and self._alone is True:
            binf = 8 if l.split()[3].decode() == 'double' else 4
            f.tell() 
            data  = f.read(binf) 
            self.ntime[i] = struct.unpack(endl+'d', data)[0]
        
        # Find the dimensions and store them, computing the variables shape
        elif spl0 == b'DIMENSIONS' and self._info is True:
            self.nx1, self.nx2, self.nx3 = [max(int(i) - 1, 1) for i in l.split()[1:4]]
            if self.nx3 == 1 and self.nx2 == 1:
                self.nshp = self.nx1 
                gridvars = ['self.x1r', 'self.x2', 'self.x3']
            elif self.nx3 == 1:
                self.nshp = (self.nx2, self.nx1)
                gridvars = ['self.x1r', 'self.x2r', 'self.x3']
            else:
                self.nshp = (self.nx3, self.nx2, self.nx1)   
                gridvars = ['self.x1r', 'self.x2r', 'self.x3r']  
            dir_map = {'X': gridvars[0],
                       'Y': gridvars[1],
                       'Z': gridvars[2]}                                       

        # Unstructured grids (non-cartesian geometries)
        elif spl1 == b'STRUCTURED_GRID':
            raise NotImplementedError('non-cartesian standalone vtk\'s have not been implemented yet')
        
    # Find the variables and store them (only if single_file)
    if self._d_info['typefile'][i] == 'single_file' and self._alone is True:
        self._d_info['varslist'][i] = np.array(list(self._offset.keys()))

    # Compute the centered coordinates if the file is standalone and cartesian
    if self._info is True:
        if gridvars[0] == 'self.x1r':
            self.x1  = 0.5*(self.x1r[:-1] + self.x1r[1:])
        if gridvars[1] == 'self.x2r':
            self.x2  = 0.5*(self.x2r[:-1] + self.x2r[1:])
        if gridvars[2] == 'self.x3r':
            self.x3  = 0.5*(self.x3r[:-1] + self.x3r[1:])

    # Close the file and set the info flag to False
    self._info = False
    f.close()
    
    return None



def _inspect_h5(self, i: int, exout: int) -> None:
    """
    Inspects the h5 files (static grid) in order to find offset and shape
    of the different variables. If the files are standalone, 
    the routine also finds the coordinates.

    Returns
    -------

        None
    
    Parameters
    ----------

        - i: int
            the index of the file to be loaded.
        - exout: int
            the index of the output to be loaded.
    """

    # Initialize the offset and shape arrays
    self._offset, self._shape = ({},{})

    # Open the file with the h5py library
    try:
        h5file = h5py.File(self._filepath,"r",)
    except:
        raise ImportError("Dependency 'h5py' not installed, required for reading HDF5 files")
    
    # Selects the binformat
    self._d_info['binformat'][i] = 'd' if self.format == 'dbl.h5' else 'f'

    # If standalone file, finds the variables to be loaded
    if self._alone is True:
        self._d_info['varslist'][i] = list(h5file[f'Timestep_{exout}']['vars'].keys())

    # Loop over the variables and store the offset and shape
    for j in self._d_info['varslist'][i]:
        self._offset[j] = h5file[f'Timestep_{exout}']['vars'][j].id.get_offset()
        self._shape[j]  = h5file[f'Timestep_{exout}']['vars'][j].shape

    # If standalone file, finds the coordinates
    if self._info is True:
        self.x1   = h5file['cell_coords']['X'][:]
        self.x2   = h5file['cell_coords']['Y'][:]
        self.x3   = h5file['cell_coords']['Z'][:]
        self.x1r  = h5file['node_coords']['X'][:]
        self.x2r  = h5file['node_coords']['Y'][:]
        self.x3r  = h5file['node_coords']['Z'][:]
        self._info = False

    # Close the file
    h5file.close()

    return None



def _compute_offset(self, i: int, endian: str, exout: int, var: str) -> None:
    """
    Routine to compute the offset and shape of the variables to be
    loaded. The routine calls different functions depending on the
    file format.

    Returns
    -------

        None
    
    Parameters
    ----------

        - i: int
            the index of the file to be loaded.
        - endian: str
            the endianess of the files.
        - exout: int
            the index of the output to be loaded.
        - var: str
            the variable to be loaded.
    """

    # Depending on the file calls different routines
    if self.format == 'vtk':
        self._inspect_vtk(i, endian)
    elif self.format in {'dbl.h5','flt.h5'}:
        self._inspect_h5(i, exout)
    elif self._alone is True:
        self._inspect_bin(i, endian)
    else:
        self._offset_bin(i, var)

    return None



def _offset_bin(self, i: int, var: str) -> None:
    """
    Routine to compute the offset and shape of the variables to be
    loaded. The routine, knowing the grid shape, computes the offset
    and stores the shape dependng on wether the variable is staggered 
    or not.

    Returns
    -------

        None

    Parameters
    ----------

        - i: int
            the index of the file to be loaded.
        - var: str
            the variable to be loaded.
    """

    # Initialize the offset and shape dictionaries and
    # the offset starting point
    self._offset, self._shape = ({},{})
    off_start = self._off_start if hasattr(self, 'off_start') else 0

    # Define the staggered variables shape
    grid_sizes = {
        'Bx1s': [self._nshp_st1, self._gridsize_st1], 
        'Ex1s': [self._nshp_st1, self._gridsize_st1],
        'Bx2s': [self._nshp_st2, self._gridsize_st2], 
        'Ex2s': [self._nshp_st2, self._gridsize_st2], 
        'Bx3s': [self._nshp_st3, self._gridsize_st2], 
        'Ex3s': [self._nshp_st3, self._gridsize_st2]}

    # Loop over the variables to be loaded (None for single files)
    varloop = self._d_info['varslist'][i] if var is None else [var]

    for var in varloop:
        # Compute the offset and shape
        grid_size = grid_sizes.get(var, [self.nshp, self.gridsize])
        self._shape[var]  = grid_size[0]
        self._offset[var] = off_start
        off_start += grid_size[1]*self._charsize

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
            varsh = self._dictdim[var]
            shape = (varsh,) + sh_type if varsh != 1 else sh_type
        else:
            shape = (self._lennout,) + sh_type if self._lennout != 1 else sh_type

        # Create the dictionary key and fill the values with nan
        with tempfile.NamedTemporaryFile() as temp_file:           
            self._d_vars[var] = np.memmap(temp_file, mode='w+', dtype=np.float32, shape = shape)
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