from .libraries import *

def _read_grid(self):
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

    # Initialize relevant lists
    nmax, xL, xR = [], [], []

    # Open and read the gridfile
    with open(self._pathgrid, 'r') as gfp:
        for i in gfp.readlines(): 
            self._split_gridfile(i, xL, xR, nmax)

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

def _read_outfile(self, nout, endian) -> None:
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

    # Open and read the 'filetype'.out file 
    vfp  = pd.read_csv(self._pathdata, delim_whitespace = True, 
                                  header = None)
    
    # Store the output and the time full list
    self.outlist  = np.array(vfp.iloc[:,0])
    self.timelist = np.array(vfp.iloc[:,1])

    # Check the output lines
    self._check_nout(nout)
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