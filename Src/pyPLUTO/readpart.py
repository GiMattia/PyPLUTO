from .libraries import *

def _inspect_bin(self, i: int, endian: str | None) -> None:
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
            _, spl1, spl2 = l.split()[0:3]
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
            #self.npart = self.nshp

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
    print(self._offset)
    # Create the key variables in the vars dictionary
    for ind, j in enumerate(self._d_info['varskeys'][i]):
        self._shape[j] = self.nshp 
        self._dictdim [j] = self._vardim[ind]  
        self._init_vardict(j)

    return None

def _inspect_vtk(self, i: int, endian: str | None) -> None:
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

    dir_map: dict[str, str]= {}
    gridvars: list[str] = []

    # Initialize the offset and shape arrays, the endianess and the coordinates dictionary
    self._offset, self._shape = ({},{})

    endl = self._d_info['endianess'][i] = '>' if endian is None else self._d_end[endian]
    if endl is None:
        raise ValueError("Error: Wrong endianess in vtk file.")

    # Open the file and read the lines
    f = open(self._filepath, 'rb')
    for l in f:

        # Split the lines (unsplit are binary data)
        try:
            spl0, spl1, _ = l.split()[0:3]

        except:
            continue

        # Find the number of points and store it
        if spl0 == b'POINTS':
            self.dim = int(spl1)
            self._offset['points'] = f.tell()
            self._shape['points']  = (self.dim,3)

        elif spl1 == b'Identity':
            f.readline()
            self._offset['id'] = f.tell()
            self._shape['id'] = self.dim
        
        elif spl1 == b'tinj':
            f.readline()
            self._offset['tinj'] = f.tell()
            self._shape['tinj'] = self.dim

        
        elif spl1 == b'Four-Velocity' or spl1 == b'Velocity':
            self._shape['vel']  = (self.dim,int(l.split()[3]))
            self._offset['vel'] = f.tell()
        
        elif spl0 == b'SCALARS':
            var = spl1.decode()
            f.readline()
            self._offset[var] = f.tell()
            self._shape[var] = self.dim
            continue

        elif spl0 == b'VECTORS':
            var = spl1.decode()
            self._shape[var]  = (self.dim,int(l.split()[3]))
            self._offset[var] = f.tell()

        # Find the variables and store them
        self._d_info['binformat'][i] = self._d_info['endianess'][i] + 'f'
        self._d_info['varslist'][i] = np.array(list(self._offset.keys()))

    f.close()
    # Create the key variables in the vars dictionary
    for ind, j in enumerate(self._d_info['varskeys'][i]):
        self._shape[j] = self.nshp 
        self._dictdim [j] = self._vardim[ind]  
        self._init_vardict(j)

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
    #masked_array = np.ma.masked_array(self._d_vars['tot'][0].astype('int'), 
    #                                          np.isnan(self._d_vars['tot'][0]))

    # Start with column 0 (id) and loop over the variable names
    ncol = 0
    for j, var in enumerate(self._d_info['varskeys'][i]):

        # Compute the size of the variable and store the data
        szvar = self._vardim[j]
        if self._lennout != 1:
            # To be fixed for multiple loadings
            raise NotImplementedError('multiple loading not implemented yet')
            #self._d_vars[var][i][:] = self._d_vars['tot'][i][ncol:ncol+szvar]
        else:
            self._d_vars[var][:] = self._d_vars['tot'][ncol:ncol+szvar]

        # Update the column counter
        ncol += szvar

    # Remove the 'tot' key from the dictionary
    #del self._d_vars['tot']

    return None

def _store_vtk_particles(self, i: int) -> None:
    """
    Routine to store the particles data. Since positions and velocities
    are stored in 2d arrays, the routine splits the data in the
    different components and stores them in the dictionary.

    Returns
    -------

        None
    
    Parameters
    ----------

        - i: int
            the index of the file to be loaded. 
    """

    # Store the position in the dictionary
    self._d_vars['x1'] = self._d_vars['points'][0]
    self._d_vars['x2'] = self._d_vars['points'][1]
    self._d_vars['x3'] = self._d_vars['points'][2]

    # Store the velocity in the dictionary
    self._d_vars['vx1'] = self._d_vars['vel'][0]
    self._d_vars['vx2'] = self._d_vars['vel'][1]
    self._d_vars['vx3'] = self._d_vars['vel'][2]

    # Remove the 'points' and 'vel' keys from the dictionary
    del self._d_vars['points']
    del self._d_vars['vel']

    return None

def _compute_offset(self, 
                    i: int, 
                    endian: str | None, 
                    exout: int, 
                    var: str | None
                   ) -> None:
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
        self._inspect_vtk(i,endian)
    else:
        self._inspect_bin(i, endian)

    return None