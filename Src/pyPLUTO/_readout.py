from ._libraries import *

def find_format(self, datatype):
    '''
    Finds the format of the data files to load.
    If no format is given the first format found between
    dbl, vtk and flt (in this order) is taken.

    Returns
    -------

        None

    Parameters
    ----------

        - datatype: str, default None
            the file format. If None the format is recovered between (in
            order) dbl, vtk and flt.
            HDF5 and tab formats have not been implemented yet.
    '''

    # Check if the file grid.out exists and that the path is a directory
    if not self.pathdir.is_dir():
        raise NotADirectoryError(f'directory {self.pathdir} not found!')
    self.pathgrid = self.pathdir / 'grid.out'
    if not self.pathgrid.is_file():
        raise FileNotFoundError(f'directory {self.pathdir} has no grid.out!')

    # Recover the file format needed to load the files
    if datatype is None:
        self.rec_format(self)
    else:
        self.pathdata = self.pathdir  / (datatype + '.out')
        if self.pathdata.is_file():
            self.format = datatype
        else:
            raise FileNotFoundError(f'file {datatype}.out not found!')

    # Store the charsize depending on the format
    self.charsize = 8 if self.format == 'dbl' else 4
    return None

def read_grid(self):
    '''
    The file grid.out is read and all the grid information are stored
    in the Load class.
    Such information are the dimensions, the geometry, the center and edges
    of each cell, the grid shape and size and, in case of non cartesian
    coordinates, the transformed cartesian coordinates (only 2D for now).
    The full non-cartesian 3D transformations have not been implemented yet.

    Returns
    -------
        None
    '''

    # Initialize relevant lists
    nmax = []
    xL   = []
    xR   = []

    # Open and read the gridfile
    with open(self.pathgrid, 'r') as gfp:
        for i in gfp.readlines(): self.split_gridfile(self,i, xL, xR, nmax)

    # Compute nx1, nx2, nx3
    self.D['nx1'], self.D['nx2'], self.D['nx3'] = nmax
    nx1p2 = self.D['nx1'] + self.D['nx2']
    nx1p3 = self.D['nx1'] + self.D['nx2'] + self.D['nx3']

    # Compute the centered grid values
    self.D['x1']  = np.asarray([0.5*(xL[i]+xR[i]) for i in range(self.D['nx1'])])
    self.D['dx1'] = np.asarray([(xR[i]-xL[i])     for i in range(self.D['nx1'])])
    self.D['x2']  = np.asarray([0.5*(xL[i]+xR[i]) for i in range(self.D['nx1'],nx1p2)])
    self.D['dx2'] = np.asarray([(xR[i]-xL[i])     for i in range(self.D['nx1'],nx1p2)])
    self.D['x3']  = np.asarray([0.5*(xL[i]+xR[i]) for i in range(nx1p2,        nx1p3)])
    self.D['dx3'] = np.asarray([(xR[i]-xL[i])     for i in range(nx1p2,        nx1p3)])

    # Determine the grid shape
    if self.D['dim'] == 1:
        self.D['nshp']     = (self.D['nx1'])
        self.D['nshp_st1'] = (self.D['nx1'] + 1)
    if self.D['dim'] == 2:
        self.D['nshp']     = (self.D['nx2'],self.D['nx1'])
        self.D['nshp_st1'] = (self.D['nx2'],self.D['nx1'] + 1)
        self.D['nshp_st2'] = (self.D['nx2'] + 1,self.D['nx1'])
    if self.D['dim'] == 3:
        self.D['nshp']     = (self.D['nx3'],self.D['nx2'],self.D['nx1'])
        self.D['nshp_st1'] = (self.D['nx3'],self.D['nx2'],self.D['nx1'] + 1)
        self.D['nshp_st2'] = (self.D['nx3'],self.D['nx2'] + 1,self.D['nx1'])
        self.D['nshp_st3'] = (self.D['nx3'] + 1,self.D['nx2'],self.D['nx1'])
    #DDDDD = {True: 1, False: 0}
    #print(DDDDD[self.D['dim'] == 1], DDDDD[self.D['dim'] == 2], DDDDD[self.D['dim'] == 3])

    # Compute the grid values at the interfaces
    self.D['x1r']     = np.zeros(len(self.D['x1']) + 1)
    self.D['x2r']     = np.zeros(len(self.D['x2']) + 1)
    self.D['x3r']     = np.zeros(len(self.D['x3']) + 1)

    self.D['x1r'][1:] = self.D['x1']     + self.D['dx1']/2.0
    self.D['x1r'][0]  = self.D['x1r'][1] - self.D['dx1'][0]
    self.D['x2r'][1:] = self.D['x2']     + self.D['dx2']/2.0
    self.D['x2r'][0]  = self.D['x2r'][1] - self.D['dx2'][0]
    self.D['x3r'][1:] = self.D['x3']     + self.D['dx3']/2.0
    self.D['x3r'][0]  = self.D['x3r'][1] - self.D['dx3'][0]

    # Compute the cartesian grid coordinates (non-cartesian geometry)
    # STILL VERY INCOMPLETE

    if self.D['geom'] == 'POLAR':
        self.D['x1c']  = np.outer(np.cos(self.D['x2']),  self.D['x1'])
        self.D['x2c']  = np.outer(np.sin(self.D['x2']),  self.D['x1'])
        self.D['x1rc'] = np.outer(np.cos(self.D['x2r']), self.D['x1r'])
        self.D['x2rc'] = np.outer(np.sin(self.D['x2r']), self.D['x1r'])
        self.gridlist3 = ['x1c','x2c','x1rc','x2rc']
    elif self.D['geom'] == 'SPHERICAL':
        self.D['x1p']  = np.outer(np.sin(self.D['x2']),  self.D['x1'])
        self.D['x2p']  = np.outer(np.cos(self.D['x2']),  self.D['x1'])
        
        self.D['x1rp'] = np.outer(np.sin(self.D['x2r']), self.D['x1r'])
        self.D['x2rp'] = np.outer(np.cos(self.D['x2r']), self.D['x1r'])
        
        self.gridlist3 = ['x1c','x2c','x1rc','x2rc']


    # Compute the gridsize
    self.D['gridsize']     =  self.D['nx1']*self.D['nx2']*self.D['nx3']
    self.D['gridsize_st1'] = (self.D['nx1'] + 1)*self.D['nx2']*self.D['nx3']
    self.D['gridsize_st2'] = self.D['nx1']*(self.D['nx2'] + 1)*self.D['nx3']
    self.D['gridsize_st3'] = self.D['nx1']*self.D['nx2']*(self.D['nx3'] + 1)

    # Create grid lists (for output purposes)
    self.gridlist1 = ['nx1','nx2','nx3','x1 ','x2 ','x3 ']
    self.gridlist2 = ['dx1','dx2','dx3','x1r','x2r','x3r']
    self.gridlist4 = ['gridsize','nshp','dim','geom']
    return None

def read_vars(self, nout):
    '''
    Reads tfe 'filetype'.out file and stores the relevant information within the
    class. Such information are the time array, the output variables, the file
    type (single or multiples), the endianess, the simulation path and the bin
    format. All these information are relevant in order to open the output files
    and access the data.

    Returns
    -------
        None

    Parameters
    ----------
        - nout: int, default 'last'
            the output file to be opened. If default ('last'), the last file
    '''

    # Initialize the info dictionary
    self.Dinfo = {}

    # Open and read the 'filetype'.out file
    with open(self.pathdata, 'r') as f:
        vfp = f.readlines()
    #print(f'dcghdwcjhdgcjsh {len(vfp)}')

    # REMEMBER TO TRANSFORM THEM IN ARRAYS
    self.D['timelist'] = []
    self.D['outlist']  = []

    # Check the output line
    time    = self.check_nout(self, nout, vfp)
    lentime = len(time)

    # Store the relevant information in a dictionary
    arrinfo = ['typefile','endianess','binformat','varslist','endpath']
    for i in arrinfo:
        self.Dinfo[i]   = [None]*lentime
    if len(time) > 1:
        self.D['nout']  = np.zeros(lentime, dtype=int)
        self.D['ntime'] = np.zeros(lentime)
    for j, timeval in enumerate(time):
        try:
            vinfo   = vfp[timeval].split()
        except:
            vinfo   = vfp[0].split()
        self.Dinfo['typefile'][j]  = vinfo[4]
        self.Dinfo['endianess'][j] = "<" if vinfo[5] == "little" else ">"
        if self.format == 'vtk': self.Dinfo['endianess'][j] = ">"
        self.Dinfo['binformat'][j] = self.Dinfo['endianess'][j]+'f'+str(self.charsize)
        self.Dinfo['varslist'][j]  = vinfo[6:]
        self.Dinfo['endpath'][j]   = f'.{timeval:04d}.{self.format}'
        if len(time) > 1:
            self.D['ntime'][j] = float(vinfo[1])
            self.D['nout'][j]  = int(timeval)
        else:
            self.D['ntime'] = float(vinfo[1])
            self.D['nout']  = int(timeval)

    self.addvarlist = ['timelist','ntime','nout','outlist']

    # Reconstruct the time array
    for line in vfp:
        self.D['outlist'].append(int(line.split()[0]))
        self.D['timelist'].append(float(line.split()[1]))

    return None

def load_vars(self, vars, i, exout, text):
    '''
    Loads the variables. If default, all the variables are loaded.

    Returns
    -------
        None

    Parameters
    ----------
        - vars: [str], default None
            the variables to be loaded. If None all the variables are loaded.

    '''
    type_dict = {'single_file':    'single file',
                 'multiple_files': 'multiple files'}

    # Check if time is correct
    lentime = len(self.D['timelist'])
    if exout >= lentime:
        print(f'Wrong input file, {exout} is higher than {lentime}')
        return None
    elif text == True:
        is_singlefile = type_dict[self.Dinfo['typefile'][i]]
        print(f'Output file:      {exout}   ({is_singlefile})')

    # Check if only specific variables should be loaded
    if vars is True:
        load_vars = self.Dinfo['varslist'][i]
    elif isinstance(vars, list):
        load_vars = vars
    else:
        load_vars = [vars]

    # Reconstruct full filepath
    self.filepath = self.pathdir / ('data' + self.Dinfo['endpath'][i])

    # Compute non-vtk offset
    self.Dst = ['Bx1s','Ex1s','Bx2s','Ex2s','Bx3s','Ex3s']
    if self.format != 'vtk':
        st_offs = self.gen_offset(self,self.Dinfo['varslist'][i])

    # Loop on loading variables
    for j in load_vars:

        numvar = self.Dinfo['varslist'][i].index(j)

        # Change filepath and offset in case of multiples_files
        if self.Dinfo['typefile'][i] == 'multiple_files':
            self.filepath = self.pathdir / (j + self.Dinfo['endpath'][i])
            numvar = 0

        # Compute offset in case of 'vtk'
        if self.format != 'vtk':
            offset = st_offs[numvar]
        else:
            offset = self.vtk_offset(self,j)

        # If variable is staggered change the shape
        if j in self.Dst:
            shape = self.shape_st(self, j)
        else:
            shape = self.D['nshp']
        #faeshape = (len(self.D['noutlist']),) + shape
        #print(faeshape)
        self.init_vardict(self, len(self.D['noutlist']), i, j, shape)

        # Load the variable through memory mapping
        scrh = np.memmap(self.filepath,self.Dinfo['binformat'][i],mode="c",offset=offset, shape = shape).T
        self.assign_var(self, len(self.D['noutlist']), i, j, scrh)

    if text == True:
        print('Output variables: '+str(self.Dinfo['varslist'][i]))
        print('Loaded variables: '+str(load_vars))

    return None
