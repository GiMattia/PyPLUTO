from .libraries import *

def _read_tabfile(self, 
                  i: int
                 ) -> None:
    """
    Reads the data.****.tab file and stores the relevant information within the 
    class. Such information are the grid variables, the output variables and the
    output time.

    Returns
    -------
    
    - None

    Parameters
    ----------

    - i (not optional): int
        The index of the file to be loaded.

    Notes
    -----

    - None

    ----

    Examples
    ========

    - Example #1: Read the data.0000.tab file

        >>> _read_tabfile(0)

    """
    
    # Initialize the dictionary
    Dict_tab = {}
    
    # Open and read the data.****.tab file, computing the empty lines
    vfp = pd.read_csv(str(self._filepath), delim_whitespace = True, 
                                  header = None, skip_blank_lines=False)
    
    # Find the empty lines
    scrhlines   = vfp.isnull().all(axis=1)
    empty_lines = vfp[scrhlines].shape[0]

    # If the file is empty the grid is 1D, otherwise 2D
    if empty_lines > 0:

        # Remove the empty lines
        vfp['block'] = scrhlines.cumsum()
        vfp = vfp[~scrhlines]

        # Store the grid variables if not present
        if not hasattr(self,'dim'):
            lines_in_block = vfp.groupby('block').size()

            # Store the gridsize
            self.nx1 = empty_lines
            self.nx2 = len(lines_in_block)
            
    # Store the grid variables
    self.x1 = np.array(vfp.iloc[:,0]).reshape(self.nx2, self.nx1)
    self.x2 = np.array(vfp.iloc[:,1]).reshape(self.nx2, self.nx1)
    num_cols = len(vfp.columns)

    # Create the variable names if not present
    if len(self._d_info['varslist'][i]) == 0:
        self._d_info['varslist'][i] = [f'var{i}' for i in range(num_cols - 2)]
    if len(self._load_vars) == 0:
        self._load_vars = self._d_info['varslist'][i]
        
    # Store the variables
    for j in range(2, num_cols-1):
        var: str = self._d_info['varslist'][i][j-2]
        Dict_tab[var] = np.array(vfp.iloc[:,j])
        if empty_lines > 0:
            Dict_tab[var] = Dict_tab[var].reshape(self.nx2, self.nx1)
        if var in self._load_vars:
            setattr(self, var, Dict_tab[var])

    return None


def _inspect_vtk(self, 
                 i: int, 
                 endian: str | None
                ) -> None:
    """
    Routine to inspect the vtk file and find the variables, the offset and the 
    shape. The routine loops over the lines of the file and finds the relevant 
    information. The routine also finds the time information if the file is 
    standalone. The routine also finds the coordinates if the file is standalone
    and cartesian.

    Returns
    -------

    - None

    Parameters
    ----------

    - endian (not optional): str | None
        The endianess of the files.
    - i (not optional): int
        The index of the file to be loaded.

    Notes
    -----

    - None

    ----

    Examples
    ========

    - Example #1: Inspect the vtk file

        >>> _inspect_vtk(0, 'big')

    - Example #2: Inspect the vtk file

        >>> _inspect_vtk(0, 'little')

    """

    dir_map: dict[str, str]= {}
    gridvars: list[str] = []

    # Initialize the offset and shape arrays, the endianess and the coordinates 
    # dictionary
    self._offset, self._shape = ({},{})
    endl = self._d_info['endianess'][i] = '>' if endian is None else \
                                          self._d_end[endian]
    if endl is None:
        raise ValueError("Error: Wrong endianess in vtk file.")
    if self._info is True:
        self.nshp = 0
        self._d_info['binformat'] = np.char.add(self._d_info['endianess'], 
                                          'f' + str(self._charsize))
    
    # Open the file and read the lines
    f = open(self._filepath, 'rb')

    for l in f:

        # Split the lines (unsplit are binary data or useless lines)
        try:
            spl0, spl1, spl2 = l.split()[0:3]
        except:
            continue

        # Find the coordinates and store them
        if spl0 in [j + b"_COORDINATES" for j in [b"X", b"Y", b"Z"]] and \
           self._info is True:
            self.geom = 'CARTESIAN'
            var_sel = spl0.decode()[0]
            binf = endl+'d' if spl2.decode() == 'double' else endl+'f'
            offset = f.tell()
            shape = int(spl1)
            scrh = np.memmap(self._filepath,dtype=binf,mode='r', 
                             offset=offset, shape = shape)
            exec(f"{dir_map[var_sel]} = scrh")

        elif spl0 == b'POINTS' and self._info is True:
            binf = endl+'d' if spl2.decode() == 'double' else endl+'f'
            offset = f.tell()
            shape = int(spl1)
            scrh = np.memmap(self._filepath,dtype  = binf, 
                                            mode   = 'r', 
                                            offset = offset, 
                                            shape  = 3*shape)

            for j in range(self.dim):
                exec(f"{gridvars[j]} = scrh[{j}::3]")
                exec(f"{gridvars[j]} = {gridvars[j]}.reshape({nshp_grid})")
            self.geom = 'UNKNOWN'

        # Find the scalars and compute their offset
        elif spl0 == b'SCALARS':
            break
            """
            var = spl1.decode()
            f.readline()
            self._offset[var] = f.tell()
            self._shape[var] = self.nshp
            """

        # Compute the time information
        elif spl0 == b'TIME' and self._alone is True:
            binf = 8 if l.split()[3].decode() == 'double' else 4
            f.tell() 
            data  = f.read(binf) 
            self.ntime[i] = struct.unpack(endl+'d', data)[0]
        
        # Find the dimensions and store them, computing the variables shape
        elif spl0 == b'DIMENSIONS' and self._info is True:
            nshp_grid = [int(i) for i in l.split()[1:4]]
            self.nx1, self.nx2, self.nx3 = \
                      [max(int(i) - 1, 1) for i in l.split()[1:4]]
            if self.nx3 == 1 and self.nx2 == 1:
                self.dim  = 1
                self.nshp = self.nx1 
                nshp_grid = (self.nx1 + 1)
                gridvars  = ['self.x1r', 'self.x2', 'self.x3']     
            elif self.nx3 == 1:
                self.dim  = 2
                self.nshp = (self.nx2, self.nx1)
                nshp_grid = (self.nx2 + 1, self.nx1 + 1)
                gridvars  = ['self.x1r', 'self.x2r', 'self.x3']
            else:
                self.dim = 3
                self.nshp = (self.nx3, self.nx2, self.nx1)   
                nshp_grid = (self.nx3 + 1, self.nx2 + 1, self.nx1 + 1)
                gridvars = ['self.x1r', 'self.x2r', 'self.x3r']  
            dir_map = {'X': gridvars[0],
                       'Y': gridvars[1],
                       'Z': gridvars[2]} 


    # New memmap strategy for vtk files
    mmapped_file = mmap.mmap(f.fileno(), 0, access=mmap.ACCESS_READ)
    search_pos = 0
    while True:
        scalars_pos = mmapped_file.find(b'SCALARS', search_pos)
        if scalars_pos == -1:
            break  # No more occurrences found

        # Move to the end of the 'SCALARS' line
        line_end = mmapped_file.find(b'\n', scalars_pos)
        line     = mmapped_file[scalars_pos:line_end]
        parts    = line.split()
        var      = parts[1].decode()

        # Move to the start of the scalar data
        lookup_table_pos = mmapped_file.find(b'LOOKUP_TABLE default', \
                                                       line_end)
        offset = mmapped_file.find(b'\n', lookup_table_pos) + 1

        if self._info is not True:
            scrh = offset - scalars_pos + self.gridsize*4 + 1
            for var in self._d_info['varslist'][i]:
                self._offset[var] = offset
                self._shape[var]  = self.nshp
                offset = offset + scrh + len(var) - \
                                        len(self._d_info['varslist'][i][0])
            break
        else:
            self._offset[var] = offset
            self._shape[var]  = self.nshp

        search_pos = line_end + 1  # Continue searching after the current line

    mmapped_file.close()                          

    # Find the variables and store them (only if single_file)
    if self._d_info['typefile'][i] == 'single_file' and self._alone is True:
        self._d_info['varslist'][i] = np.array(list(self._offset.keys()))

    # Compute the centered coordinates if the file is standalone and cartesian
    if self._info is True:
        print(self.geom)

        self._read_grid_vtk(gridvars)
        self._info = False

    # Close the file
    f.close()
    
    return None


def _inspect_h5(self, 
                i: int, 
                exout: int
               ) -> None:
    """
    Inspects the h5 files (static grid) in order to find offset and shape of the
    different variables. If the files are standalone, the routine also finds the
    coordinates.

    Returns
    -------

    - None
    
    Parameters
    ----------

    - exout (not optional): int
        The index of the output to be loaded.
    - i (not optional): int
        The index of the file to be loaded.

    Notes
    -----

    - None

    ----

    Examples
    ========

    - Example #1: Load all the variables

        >>> _inspect_h5(0, 0)

    """

    # Initialize the offset and shape arrays
    self._offset, self._shape = ({},{})

    # Open the file with the h5py library
    h5file  = h5py.File(self._filepath,"r")
    
    # Selects the binformat
    self._d_info['binformat'][i] = 'd' if self.format == 'dbl.h5' else 'f'

    try:
        cellvs = h5file[f'Timestep_{exout}']['vars']
    except:
        cellvs = {}
    try:
        stagvs = h5file[f'Timestep_{exout}']['stag_vars']
    except:
        stagvs = {}

    # If standalone file, finds the variables to be loaded, else 
    # remove variables in the .out file that are not present in the actual file
    if self._alone is True:
        self._d_info['varslist'][i] = set(cellvs.keys()) | set(stagvs.keys())
    else:
        self._d_info['varslist'][i] = set(self.varsh5)

    # Loop over the variables and store the offset and shape
    for j in self._d_info['varslist'][i]:
        if j in cellvs:
            self._offset[j] = cellvs[j].id.get_offset()
            self._shape[j]  = cellvs[j].shape
        elif j in stagvs:
            self._offset[j] = stagvs[j].id.get_offset()
            self._shape[j]  = stagvs[j].shape
        else:
            raise ValueError(f"Error: Variable {j} not found in the HDF5 file.")

    # If standalone file, finds the coordinates
    if self._info is True:
        self.x1   = h5file['cell_coords']['X'][:]
        self.x2   = h5file['cell_coords']['Y'][:]
        self.x3   = h5file['cell_coords']['Z'][:]
        self.x1r  = h5file['node_coords']['X'][:]
        self.x2r  = h5file['node_coords']['Y'][:]
        self.x3r  = h5file['node_coords']['Z'][:]
        self._read_grid_h5()
        self._info = False

    # Close the file
    h5file.close()

    return None


def _compute_offset(self, 
                    i: int, 
                    endian: str | None, 
                    exout: int, 
                    var: str | None
                   ) -> None:
    """
    Routine to compute the offset and shape of the variables to be loaded. The 
    routine calls different functions depending on the file format.

    Returns
    -------

    - None
    
    Parameters
    ----------

    - endian (not optional): str | None
        The endianess of the files.
    - exout (not optional): int
        The index of the output to be loaded.
    - i (not optional): int
        The index of the file to be loaded.
    - var (not optional): str | None
        The variable to be loaded.

    Notes
    -----

    - None

    ----

    Examples
    ========

    - Example #1: Load all the variables

        >>> _compute_offset(0, True, 0, True)

    """

    if self._alone is not True:
        # Read the grid file
        self._read_gridfile()

    # Depending on the file calls different routines
    if self.format == 'tab':
        self._read_tabfile(i)
    elif self.format == 'vtk':
        self._inspect_vtk(i,endian)
    elif self.format in {'dbl.h5','flt.h5'}:
        self._inspect_h5(i, exout)
    elif self.format == 'hdf5':
        self._inspect_hdf5(i, exout)
    else:
        self._offset_bin(i, var)

    return None


def _offset_bin(self, 
                i: int, 
                var: str | None
               ) -> None:
    """
    Routine to compute the offset and shape of the variables to be loaded. The 
    routine, knowing the grid shape, computes the offset and stores the shape 
    dependng on wether the variable is staggered or not.

    Returns
    -------

    - None

    Parameters
    ----------

    - i (not optional): int
        The index of the file to be loaded.
    - var (not optional): str
        The variable to be loaded.
    
    Notes
    -----

    - None

    ----

    Examples
    ========

    - Example #1: Load all the variables

        >>> _offset_bin(0, True)

    """

    # Read the grid file if not already read
    if self._info is True:
        self._read_gridfile()
        self._info = False

    # Initialize the offset and shape dictionaries and the offset starting point
    self._offset, self._shape = ({},{})
    off_start = 0

    # Define the staggered variables shape (Magnetic and electric field)
    grid_sizes = {
        'Bx1s': [self._nshp_st1, self._gridsize_st1], 
        'Ex1s': [self._nshp_st1, self._gridsize_st1],
        'Bx2s': [self._nshp_st2, self._gridsize_st2], 
        'Ex2s': [self._nshp_st2, self._gridsize_st2], 
        'Bx3s': [self._nshp_st3, self._gridsize_st3], 
        'Ex3s': [self._nshp_st3, self._gridsize_st3]}

    # Loop over the variables to be loaded (None for single files)
    varloop = self._d_info['varslist'][i] if var is None else [var]

    for var in varloop:
        # Get the grid shape and size (centered or staggered)
        grid_size = grid_sizes.get(var, [self.nshp, self.gridsize])
        self._shape[var]  = grid_size[0]
        # Assign the offset
        self._offset[var] = off_start
        # Move to next variable
        off_start += grid_size[1]*self._charsize

    # End of function
    return None
