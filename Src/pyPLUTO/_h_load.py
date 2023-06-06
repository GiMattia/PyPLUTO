from ._libraries import *


def split_gridfile(self, i, xL, xR, nmax):
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
            if i.split()[1] == 'GEOMETRY:'  : self.D['geom'] = i.split()[2]
            if i.split()[1] == 'DIMENSIONS:': self.D['dim']  = int(i.split()[2])

def rec_format(self):
    '''
    rec_format
    '''
    for tryformat in self.PLUTO_formats:
        if os.path.isfile(self.path+'/'+tryformat+'.out'):
            self.format = tryformat
            break
    if self.format is None:
        raise FileNotFoundError('file "datatype".out not found!')

def vtk_offset(self, i):
    '''
    vtk_offset
    '''
    f = open(self.filepath, 'rb')
    for l in f:
        try:
            spl0, spl1  = l.split()[0:2]
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

def check_nout(self,nout, vfp):
    if not isinstance(nout,list):
        D = {nout: [nout], 'last': [len(vfp) - 1], 'all': list(range(len(vfp)))}
        return D[nout]
    else:
        nout.sort()
        return nout

def init_vardict(self, nouts, i, var):
    if nouts != 1 and i == 0:
        self.D[var] = [None]*nouts
    return None

def assign_var(self, nouts, time, var, scrh):
    if nouts != 1:
        self.D[var][time] = scrh
    else:
        self.D[var] = scrh
    return None

def shape_st(self, var):
    if var in self.Dst[0:2]:
        return self.D['nshp_st1']
    elif var in self.Dst[2:4]:
        return self.D['nshp_st2']
    else:
        return self.D['nshp_st3']

def gen_offset(self, vars):
    offset = [0]*len(vars)
    for i, var in enumerate(vars[:-1]):
        if var in self.Dst[:2]:
            offset[i+1] = offset[i] + self.D['gridsize_st1']*self.charsize
        elif var in self.Dst[2:4]:
            offset[i+1] = offset[i] + self.D['gridsize_st2']*self.charsize
        elif var in self.Dst[4:]:
            offset[i+1] = offset[i] + self.D['gridsize_st3']*self.charsize    
        else:
            offset[i+1] = offset[i] + self.D['gridsize']*self.charsize
    return offset
