from .libraries import *
from .__init__ import Load, LoadPart

def _read_grid(self: Load) -> None:
    """
    The file grid.out is read and all the grid information are stored
    in the Load class.
    Such information are the dimensions, the geometry, the center and edges
    of each cell, the grid shape and size and, in case of non cartesian
    coordinates, the transformed cartesian coordinates (only 2D for now).
    The full non-cartesian 3D transformations have not been implemented yet.

    Returns
    -------

        None

    Parameters
    ----------

        None
    """

    # Import the methods needed from other files
    from .h_load import _split_gridfile

    # Initialize relevant lists
    nmax, xL, xR = [], [], []

    # Open and read the gridfile
    with open(self._pathgrid, 'r') as gfp:
        for i in gfp.readlines(): 
            _split_gridfile(self, i, xL, xR, nmax)

    # Compute nx1, nx2, nx3
    self.nx1, self.nx2, self.nx3 = nmax
    nx1p2 = self.nx1 + self.nx2
    nx1p3 = self.nx1 + self.nx2 + self.nx3

    # Compute the centered and staggered grid values
    self.x1r = np.array(xL[0:self.nx1] + [xR[self.nx1-1]])
    self.x1  = 0.5*(self.x1r[:-1] + self.x1r[1:])
    self.dx1 = self.x1r[1:] - self.x1r[:-1]

    self.x2r = np.array(xL[self.nx1:nx1p2] + [xR[nx1p2-1]])
    self.x2  = 0.5*(self.x2r[:-1] + self.x2r[1:])
    self.dx2 = self.x2r[1:] - self.x2r[:-1]

    self.x3r = np.array(xL[nx1p2:nx1p3] + [xR[nx1p3-1]])
    self.x3  = 0.5*(self.x3r[:-1] + self.x3r[1:])
    self.dx3 = self.x3r[1:] - self.x3r[:-1]

    # Define grid shapes based on dimensions
    nx1s, nx2s, nx3s = self.nx1 + 1, self.nx2 + 1, self.nx3 + 1
    GRID_SHAPES = {
        1: lambda nx1, _, __: (nx1, nx1s, None, None),
        2: lambda nx1, nx2, _: ((nx2, nx1), (nx2, nx1s),
                                (nx2s, nx1), None),
        3: lambda nx1, nx2, nx3: ((nx3, nx2, nx1), (nx3, nx2, nx1s),
                             (nx3, nx2s, nx1), (nx3s, nx2, nx1))}

    # Determine grid shape based on dimension
    (self.nshp, self._nshp_st1, self._nshp_st2, self._nshp_st3) = \
        GRID_SHAPES[self.dim](self.nx1, self.nx2, self.nx3)

    # Compute the cartesian grid coordinates (non-cartesian geometry)
    # STILL VERY INCOMPLETE (3D spherical missing and needs testing)

    if self.geom == 'POLAR':

        x1_2D, x2_2D   = np.meshgrid(self.x1, 
                                     self.x2, indexing='ij')
        x1r_2D, x2r_2D = np.meshgrid(self.x1r, 
                                     self.x2r, indexing='ij')

        self.x1c  = np.cos(x2_2D)*x1_2D
        self.x2c  = np.sin(x2_2D)*x1_2D
        self.x1rc = np.cos(x2r_2D)*x1r_2D
        self.x2rc = np.sin(x2r_2D)*x1r_2D
        #self.x1c  = np.outer(np.cos(self.x2),  self.x1)
        #self.x2c  = np.outer(np.sin(self.x2),  self.x1)
        #self.x1rc = np.outer(np.cos(self.x2r), self.x1r)
        #self.x2rc = np.outer(np.sin(self.x2r), self.x1r)

        self.gridlist3 = ['x1c','x2c','x1rc','x2rc']
        del x1_2D, x2_2D, x1r_2D, x2r_2D
    elif self.geom == 'SPHERICAL':
        x1_2D, x2_2D   = np.meshgrid(self.x1, 
                                     self.x2, indexing='ij')
        x1r_2D, x2r_2D = np.meshgrid(self.x1r, 
                                     self.x2r, indexing='ij')

        self.x1p  = (np.sin(x2_2D)*x1_2D).T
        self.x2p  = (np.cos(x2_2D)*x1_2D).T
        self.x1rp = (np.sin(x2r_2D)*x1r_2D).T
        self.x2rp = (np.cos(x2r_2D)*x1r_2D).T
        #self.x1p  = np.outer(np.sin(self.x2),  self.x1)
        #self.x2p  = np.outer(np.cos(self.x2),  self.x1)
        #self.x1rp = np.outer(np.sin(self.x2r), self.x1r)
        #self.x2rp = np.outer(np.cos(self.x2r), self.x1r)
        
        self.gridlist3 = ['x1c','x2c','x1rc','x2rc']
        del x1_2D, x2_2D, x1r_2D, x2r_2D


    # Compute the gridsize both centered and staggered
    self.gridsize      = self.nx1*self.nx2*self.nx3
    self._gridsize_st1 = nx1s*self.nx2*self.nx3
    self._gridsize_st2 = self.nx1*nx2s*self.nx3
    self._gridsize_st3 = self.nx1*self.nx2*nx3s

    return None

def _read_outfile(self: Load, nout, endian) -> None:
    """
    Reads the datatype.out file and stores the relevant information
    within the class. Such information are the time array, the output
    variables, the file type (single or multiples), the endianess, 
    the simulation path and the bin format. All these information are
    relevant in order to open the output files and access the data.

    Returns
    -------

        None

    Parameters
    ----------

        - nout: int
            the output file to be opened. If default ('last'), the
            code assumes the last file should be opened. Other 
            options available are 'last' (all the files should be 
            opened) and -1 (same as 'last')
    """

    # Import the methods needed from other files
    from .h_load import _check_nout

    # Open and read the 'filetype'.out file 
    vfp = pd.read_csv(str(self._pathdata), delim_whitespace = True, 
                                  header = None)
    
    # Store the output and the time full list
    self.outlist  = np.array(vfp.iloc[:,0])
    self.timelist = np.array(vfp.iloc[:,1])

    # Check the output lines
    _check_nout(self, nout)
    self.ntime = self.timelist[self.nout]
    self._lennout = len(self.nout)

    # Initialize the info dictionary
    self._d_info = {
    'typefile':  np.array(vfp.iloc[self.nout,4]),
    'endianess': np.where(vfp.iloc[self.nout,5] == 'big', '>', '<'),
    }

    # Compute the endianess (vtk have always big endianess).
    # If endian is given, it is used instead of the one in the file.
    self._d_info['endianess'][:] = '>' if self.format == 'vtk' \
                                    else self._d_info['endianess']
    self._d_info['endianess'][:] = self._d_end[endian] if endian is not None \
                                    else self._d_info['endianess']
    
    # Store the variables list
    self._d_info['varslist'] = np.array(vfp.iloc[self.nout,6:])

    # Compute binformat and endpath
    self._d_info['binformat'] = np.char.add(self._d_info['endianess'], 
                                          'f' + str(self._charsize))
    format_string = f'.%04d.{self.format}'
    self._d_info['endpath'] = np.char.mod(format_string, self.nout)

    return None


def _read_tabfile(self: Load | LoadPart, i: int) -> None:
    """
    Reads the data.****.tab file and stores the relevant information
    within the class. Such information are the grid variables, the
    output variables and the output time.

    Returns
    -------
    
        None

    Parameters
    ----------

        - i: int
            the index of the file to be loaded.

    """
    
    # Check that the loaded class is correct
    if isinstance(self, LoadPart):
        raise TypeError("Error: tab files and LoadPart are not compatible.")
    
    # Initialize the dictionary
    Dict_tab: dict[str, NDArray] = {}
    
    # Open and read the data.****.tab file, computing the empty lines
    vfp = pd.read_csv(str(self._filepath), delim_whitespace = True, 
                                  header = None, skip_blank_lines=False)
    scrhlines: pd.Series = vfp.isnull().all(axis=1)
    empty_lines: int = vfp[scrhlines].shape[0]

    # If the file is empty, the grid is 1D
    if empty_lines > 0:

        # Remove the empty lines
        vfp['block'] = scrhlines.cumsum()
        vfp = vfp[~scrhlines]

        # Store the grid variables if not present
        if not hasattr(self,'dim'):
            lines_in_block = vfp.groupby('block').size()

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

def _inspect_vtk(self: Load | LoadPart, i: int, endian: str | None) -> None:
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

    # Be sure that the class loaded is correct:
    if isinstance(self, LoadPart):
        raise TypeError("Error: Wrong class loaded.")

    dir_map: dict[str, str]= {}
    gridvars: list[str] = []

    # Initialize the offset and shape arrays, the endianess and the coordinates dictionary
    self._offset, self._shape = ({},{})
    endl = self._d_info['endianess'][i] = '>' if endian is None else self._d_end[endian]
    if endl is None:
        raise ValueError("Error: Wrong endianess in vtk file.")
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