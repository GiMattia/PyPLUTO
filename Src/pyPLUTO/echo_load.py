from .libraries import *

def echo_load(self, nout, path, vars):
    """

    - vars
    
    
    
    
    """

    self._check_pathformat(path)

    self.geom = 'CARTESIAN'

    conv_dict = {'x': 'x1', 'y': 'x2', 'z': 'x3',
                 'rh': 'rho', 'pg': 'prs', 'se': 'ent',
                 'vx': 'vx1', 'vy': 'vx2', 'vz': 'vx3',
                 'bx': 'Bx1', 'by': 'Bx2', 'bz': 'Bx3',
                 'ex': 'Ex1', 'ey': 'Ex2', 'ez': 'Ex3'}


    grid = h5py.File(self.pathdir / 'grid.h5','r')
    for key in grid.keys():
        if key in conv_dict.keys():
            setattr(self, conv_dict[key], grid[key][:])
        else:
            setattr(self, key, grid[key][:])

    grid.close()   

    for dim in ['x1', 'x2', 'x3']:
        if hasattr(self, dim) is True:
            setattr(self, f'n{dim}', len(getattr(self, dim)))
        else:
            setattr(self, f'n{dim}', 1)

    self.dim = (self.nx1 > 1) + (self.nx2 > 1) + (self.nx3 > 1)
    self.gridsize = self.nx1*self.nx2*self.nx3

    dim_dict = {1: self.nx1, 
                2: (self.nx1,self.nx2), 
                3: (self.nx1,self.nx2,self.nx3)}
    
    self.nshp = dim_dict[self.dim]

    self.nout = nout if nout != 'last' else 0
    file = self.pathdir / f"out{self.nout:03d}.h5"

    tmp   = h5py.File(file,'r')

    self.ntime = tmp['time'][...][0]

    vars = list(tmp.keys()) + list(conv_dict.keys()) if vars is True else vars

    for key in tmp.keys():
        var = tmp[key][:]
        [var := var[0] for dim in [self.nx3, self.nx2, self.nx1] if dim == 1]
        if key in conv_dict.keys() and key in vars:
            setattr(self, conv_dict[key], var.T)
        elif key in vars:
            setattr(self, key, var.T)

        del var

    tmp.close()

    return None