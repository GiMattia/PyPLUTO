from .libraries import *

def _split_gridfile(self, i, xL, xR, nmax):
    """
    split_gridfile
    """
    if len(i.split()) == 1:
        try:
            nmax.append(int(i.split()[0]))
        except:
            pass
    if len(i.split()) == 3:
        try:
            int(i.split()[0])

            xL.append(float(i.split()[1]))
            xR.append(float(i.split()[2]))
        except:
            if i.split()[1] == 'GEOMETRY:'  : self.geom = i.split()[2]
            if i.split()[1] == 'DIMENSIONS:': self.dim  = int(i.split()[2])

def _new_split_gridfile(self, i, xL, xR, nmax):
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

def _rec_format(self):
    '''
    rec_format
    '''
    PLUTO_formats = ['dbl','vtk','flt']
    for tryformat in PLUTO_formats:
        self.pathdata = self.pathdir / (tryformat + '.out')
        if self.pathdata.is_file():
            self.format = tryformat
            break
    if not hasattr(self,"format"):
        raise FileNotFoundError('file "format".out not found!')

def _vtk_offset(self, i):
    '''
    vtk_offset
    '''
    f = open(self.filepath, 'rb')
    for l in f:
        try:
            spl0, spl1 = l.split()[0:2]
        except:
            spl0 = [None]
        if spl0 == b'SCALARS':
            var = spl1.decode()
            f.readline()
            if var == i: 
                offset = f.tell()
                f.close()
                return offset
    print('Offset not found!!')
    quit()

def _check_nout(self,nout, vfp):
    if not isinstance(nout,list):
        D = {nout: [nout],       'last': [len(vfp) - 1], 
             -1: [len(vfp) - 1],
               'all': [i for i, _ in enumerate(vfp)]}
        return D[nout]
    else:
        for index, item in enumerate(nout):
            if item == 'last' or item == -1: 
                nout[index] = len(vfp) - 1
        nout.sort()
        return nout

def _init_vardict(self, nouts, i, var, shape):
    if nouts != 1 and var not in self.D_vars.keys():
        with tempfile.NamedTemporaryFile() as temp_file:           
            sh_type = shape[::-1] if isinstance(shape, tuple) else (shape,)
            self.D_vars[var] = np.memmap(temp_file, mode='w+', dtype=np.float32, shape = (nouts,) + sh_type)
    return None

def _assign_var(self, nouts, time, var, scrh):
    if nouts != 1:
        self.D_vars[var][time] = scrh
    else:
        self.D_vars[var] = scrh
    return None

def _shape_st(self, var):
    if var in self.Dst[0:2]:
        return self.nshp_st1
    elif var in self.Dst[2:4]:
        return self.nshp_st2
    else:
        return self.nshp_st3

def _gen_offset(self, vars) -> List[str]:

    '''
    Generates offest in order to read the data.
    BLBLBL Staggered quantities, ...
    
    Parameters
    ----------

        - vars: str
            The list of variables to be loaded

    Return
    ------
        The offset of the variable
    '''

    offset: List[str] = [0]*len(vars)
    for i, var in enumerate(vars[:-1]):
        if var in self.Dst[:2]:
            offset[i+1] = offset[i] + self.gridsize_st1*self.charsize
        elif var in self.Dst[2:4]:
            offset[i+1] = offset[i] + self.gridsize_st2*self.charsize
        elif var in self.Dst[4:]:
            offset[i+1] = offset[i] + self.gridsize_st3*self.charsize    
        else:
            offset[i+1] = offset[i] + self.gridsize*self.charsize
    return offset

def _vtk_offsetfile(self) -> None:
    self.off_dict = OrderedDict()
    f = open(self.pathdata, 'rb')
    for l in f:
        try:
            spl0, spl1, spl2 = l.split()[0:3]
        except:
            spl0 = [None]
        if spl0 == b'SCALARS'  or spl0 == b'VECTORS':
            var = spl1.decode()
            f.readline()
            self.off_dict[var] = [f.tell(), spl0.decode()]
        elif spl0 == b'POINTS':
            f.readline()
            offset = f.tell()
            self.nparts = int(spl1.decode())
            self.off_dict['Position'] = [f.tell(), 'VECTORS']
    f.close()

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
        self.pathgrid = self.pathdir / 'grid.out'
        self.pathdata = self.pathdir / (try_type + '.out')
        
        # Check if the datatype.out file is present
        if self.pathdata.is_file() and self.pathgrid.is_file():
            self.format = try_type
            self.alone = False
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
        self.matching_files = glob.glob(str(pattern))

        # Check if the file is present
        if self.matching_files:
            self.format = try_type
            self.alone = True
            break

    return None



def _new_check_nout(self, nout) -> None:
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



def _findfiles(self, nout):
    """
    Finds the files to be loaded. If nout is a list, the function
    loops over the list and finds the corresponding files. If nout
    is an integer, the function finds the corresponding file. If
    nout is 'last', the function finds the last file. If nout is
    'all', the function finds all the files. Then, the function
    stores the relevant information in a dictionary Dinfo.

    Returns
    -------

        None

    Parameters
    ----------

        - nout: int
            the output file to be loaded
    """

    # Find class name
    class_name = self.__class__.__name__

    # Split the matching fils and remove double keys
    vars, outs = set(), set()
    for elem in self.matching_files:
        vars.add(elem.split('/')[-1].split('.')[0])
        outs.add(int(elem.split('.')[1]))

    # Sort the outputs in an array and check the number of outputs
    self.outlist = np.array(sorted(outs))
    self._new_check_nout(nout)
    self.lennout = len(self.nout)
    self.ntime = np.empty(self.lennout)

    # Initialize the info dictionary
    self.Dinfo = {
    'typefile':  np.empty(self.lennout, dtype = 'U20'),
    'endianess': np.empty(self.lennout, dtype = 'U20'),
    'binformat': np.empty(self.lennout, dtype = 'U20'),
    }

    # Check if we are loading particle files
    if class_name == 'LoadPart':
        if 'particles' not in vars:
            raise FileNotFoundError(f'file particles.*.{self.format} \
                                    not found!')
        self.Dinfo['typefile'][:] = 'single_file'  
        self.Dinfo['varslist'] = [[] for _ in range(self.lennout)]  
        self.Dinfo['varskeys'] = [[] for _ in range(self.lennout)] 

        # Check if we are loading a single file (to be fixed)
        if self.lennout != 1:
            raise NotImplementedError('multiple loading not implemented yet')

    # Check if fluid files are single or multiple. If multiple 
    # find the variables
    else:
        if 'data' not in vars:
            self.Dinfo['typefile'][:] = 'multiple_files'
            self.Dinfo['varslist'] = np.empty((self.lennout,len(vars)), 
                                              dtype = 'U20')
            self.Dinfo['varslist'][:] =  list(vars)
        else:
            self.Dinfo['typefile'][:] = 'single_file'  
            self.Dinfo['varslist'] = [[] for _ in range(self.lennout)]     
           
    # Compute the endpath
    format_string = f'.%04d.{self.format}'
    self.Dinfo['endpath'] = np.char.mod(format_string, self.nout)

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

    # Initialize the offset and shape arrays
    self.offset, self.shape = ({},{})

    # Open the file and read the lines
    f = open(self.filepath, 'rb')
    for l in f:

        # Split the lines (unsplit are binary data)
        try:
            spl0, spl1, spl2 = l.split()[0:3]
        except:
            break

        # FInd the dimensions of the domain
        if spl1 == b'dimensions':
            self.dim = int(spl2)

        # FInd the endianess of the file and compute the binary format
        elif spl1 == b'endianity':
            self.Dinfo['endianess'][i] = '>' if endian == b'big' else '<'
            self.Dinfo['endianess'][i] = self.D_end[endian] if endian is not None \
                                    else self.Dinfo['endianess'][i]
            scrh = 'f'if self.charsize == 4 else 'd'
            self.Dinfo['binformat'][i] = self.Dinfo['endianess'][i] + scrh

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
            self.Dinfo['varskeys'][i] = [elem.decode() for elem in l.split()[2:]]
            self.Dinfo['varslist'][i] = ['tot']

        # Find the variable dimensions
        elif spl1 == b'field_dim':
            self.vardim = np.array([int(elem.decode()) for elem in l.split()[2:]])
            self.offset['tot'] = f.tell()
            self.shape['tot']  = (self.nshp,np.sum(self.vardim))
            # To be fixed (multiple loading)
            #self.shape['tot']  = (self.maxpart,np.sum(self.vardim))

    f.close()

    # Create the key variables in the vars dictionary
    for ind, j in enumerate(self.Dinfo['varskeys'][i]):
        self.shape[j] = self.nshp 
        self._new_init_vardict(j)

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
    self.offset, self.shape = ({},{})
    endl = self.Dinfo['endianess'][i] = '>' if endian is None else self.D_end[endian]
    if self.info is True:
        self.nshp = 0
        self.Dinfo['binformat'] = np.char.add(self.Dinfo['endianess'], 
                                          'f' + str(self.charsize))

    # Open the file and read the lines
    f = open(self.filepath, 'rb')
    for l in f:

        # Split the lines (unsplit are binary data)
        try:
            spl0, spl1, spl2 = l.split()[0:3]
        except:
            continue

        # Find the coordinates and store them
        if spl0 in [j + b"_COORDINATES" for j in [b"X", b"Y", b"Z"]] and self.info is True:
            var_sel = spl0.decode()[0]
            binf = endl+'d' if spl2.decode() == 'double' else endl+'f'
            offset = f.tell()
            shape = int(spl1)
            scrh = np.memmap(self.filepath,dtype=binf,mode='r',offset=offset, shape = shape)
            exec(f"{dir_map[var_sel]} = scrh")

        # Find the scalars and compute their offset
        elif spl0 == b'SCALARS':
            var = spl1.decode()
            f.readline()
            self.offset[var] = f.tell()
            self.shape[var] = self.nshp

        # Compute the time information
        elif spl0 == b'TIME' and self.alone is True:
            binf = 8 if l.split()[3].decode() == 'double' else 4
            f.tell() 
            data  = f.read(binf) 
            self.ntime[i] = struct.unpack(endl+'d', data)[0]
        
        # Find the dimensions and store them, computing the variables shape
        elif spl0 == b'DIMENSIONS' and self.info is True:
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
    if self.Dinfo['typefile'][i] == 'single_file' and self.alone is True:
        self.Dinfo['varslist'][i] = np.array(list(self.offset.keys()))

    # Compute the centered coordinates if the file is standalone and cartesian
    if self.info is True:
        if gridvars[0] == 'self.x1r':
            self.x1  = 0.5*(self.x1r[:-1] + self.x1r[1:])
        if gridvars[1] == 'self.x2r':
            self.x2  = 0.5*(self.x2r[:-1] + self.x2r[1:])
        if gridvars[2] == 'self.x3r':
            self.x3  = 0.5*(self.x3r[:-1] + self.x3r[1:])

    # Close the file and set the info flag to False
    self.info = False
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
    self.offset, self.shape = ({},{})

    # Open the file with the h5py library
    try:
        h5file = h5py.File(self.filepath,"r",)
    except:
        raise ImportError("Dependency 'h5py' not installed, required for reading HDF5 files")
    
    # Selects the binformat
    self.Dinfo['binformat'][i] = 'd' if self.format == 'dbl.h5' else 'f'

    # If standalone file, finds the variables to be loaded
    if self.alone is True:
        self.Dinfo['varslist'][i] = list(h5file[f'Timestep_{exout}']['vars'].keys())

    # Loop over the variables and store the offset and shape
    for j in self.Dinfo['varslist'][i]:
        self.offset[j] = h5file[f'Timestep_{exout}']['vars'][j].id.get_offset()
        self.shape[j]  = h5file[f'Timestep_{exout}']['vars'][j].shape

    # If standalone file, finds the coordinates
    if self.info is True:
        self.x1   = h5file['cell_coords']['X'][:]
        self.x2   = h5file['cell_coords']['Y'][:]
        self.x3   = h5file['cell_coords']['Z'][:]
        self.x1r  = h5file['node_coords']['X'][:]
        self.x2r  = h5file['node_coords']['Y'][:]
        self.x3r  = h5file['node_coords']['Z'][:]
        self.info = False

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
    elif self.alone is True:
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
    self.offset, self.shape = ({},{})
    off_start = self.off_start if hasattr(self, 'off_start') else 0

    # Define the staggered variables shape
    grid_sizes = {
        'Bx1s': [self.nshp_st1, self.gridsize_st1], 
        'Ex1s': [self.nshp_st1, self.gridsize_st1],
        'Bx2s': [self.nshp_st2, self.gridsize_st2], 
        'Ex2s': [self.nshp_st2, self.gridsize_st2], 
        'Bx3s': [self.nshp_st3, self.gridsize_st2], 
        'Ex3s': [self.nshp_st3, self.gridsize_st2]}

    # Loop over the variables to be loaded (None for single files)
    varloop = self.Dinfo['varslist'][i] if var is None else [var]

    for var in varloop:
        # Compute the offset and shape
        grid_size = grid_sizes.get(var, [self.nshp, self.gridsize])
        self.shape[var]  = grid_size[0]
        self.offset[var] = off_start
        off_start += grid_size[1]*self.charsize

    return None



def _new_init_vardict(self, var: str) -> None:
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
    if var not in self.D_vars.keys():

        # Compute the shape of the variable
        sh_type = self.shape[var][::-1] if isinstance(self.shape[var], tuple) else (self.shape[var],)
        shape = (self.lennout,) + sh_type if self.lennout != 1 else sh_type

        # Create the dictionary key and fill the values with nan
        with tempfile.NamedTemporaryFile() as temp_file:           
            self.D_vars[var] = np.memmap(temp_file, mode='w+', dtype=np.float32, shape = shape)
            self.D_vars[var][:] = np.nan
    return None



def _new_assign_var(self, time: int, var: str, scrh: np.memmap) -> None:
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
    if self.lennout != 1:
        self.D_vars[var][time] = scrh
    else:
        self.D_vars[var] = scrh

    return None



def _store_bin_particles(self, i: int) -> None:
    """
    Routine to store the particles data. The routine loops over the
    variables and stores the data in the dictionary from the 'tot' key.
    Then the 'tot' keyword is removed from the dictionary for memory and
    clarity reasons.

    Returns
    -------

        None
    
    Parameters
    ----------

        - i: int
            the index of the file to be loaded. 
    """

    # Mask the array (to be fixed for multiple loadings)
    #masked_array = np.ma.masked_array(self.D_vars['tot'][0].astype('int'), 
    #                                                 np.isnan(self.D_vars['tot'][0]))

    # Start with column 0 (id) and loop over the variable names
    ncol = 0
    for j, var in enumerate(self.Dinfo['varskeys'][i]):

        # Compute the size of the variable and store the data
        szvar = self.vardim[j]
        if self.lennout != 1:
            # To be fixed for multiple loadings
            raise NotImplementedError('multiple loading not implemented yet')
            #self.D_vars[var][i][:] = self.D_vars['tot'][i][ncol:ncol+szvar]
        else:
            self.D_vars[var][:] = self.D_vars['tot'][ncol:ncol+szvar]

        # Update the column counter
        ncol += szvar

    # Remove the 'tot' key from the dictionary
    del self.D_vars['tot']

    return None