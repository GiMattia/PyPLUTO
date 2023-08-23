from .libraries import *

def _split_gridfile(self, i, xL, xR, nmax):
    '''
    split_gridfile
    '''
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
             -1: [len(vfp) - 1], 'all': [i for i, _ in enumerate(vfp)]}
        return D[nout]
    else:
        for index, item in enumerate(nout):
            if item == 'last' or item == -1: nout[index] = len(vfp) - 1
        nout.sort()
        return nout

def _init_vardict(self, nouts, i, var, shape):
    if nouts != 1 and var not in self.D_vars.keys():
        with tempfile.NamedTemporaryFile() as temp_file:           
            sh_type = shape[::-1] if isinstance(shape, tuple) else (shape,)
            self.D_vars[var] = np.memmap(temp_file, mode='w+', dtype=np.float32, shape = (nouts,) + sh_type)
        #self.D_vars[var] = np.empty((nouts,), dtype=np.memmap)
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
