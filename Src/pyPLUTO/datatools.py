from .libraries import *

def slices(self, 
           var: NDArray, 
           x1: int | list | None = None, 
           x2: int | list | None = None, 
           x3: int | list | None = None, 
           diag: bool | None = None
          ):
    newvar = np.copy(var)
    if x3 != None:
        newvar = newvar[:,:,x3]
    if x2 != None:
        newvar = newvar[:,x2]
    if x1 != None:
        newvar = newvar[x1]
    if diag == 'maj':
        pass
    elif diag == 'min':
        pass
    return newvar

def mirror(self, oldvar, dirs = None, xax = None, yax = None):
    spp = [*dirs]
    var = np.copy(oldvar)
    axx = np.copy(xax)
    axy = np.copy(yax)
    dim = np.ndim(var) - 1
    nax = []
    for dir in spp:
        lvx = len(var[:,0]) if dim == 1 else len(var)
        lvy = len(var[0,:]) if dim == 1 else len(var)
        choices = {'l' :[(lvx,0),((lvx,0),(0,0))],'r' :[(0,lvx),((0,lvx),(0,0))],
                   't' :[(0,lvy),((0,0),(0,lvy))],'b' :[(lvy,0),((0,0),(lvy,0))]}
        var = np.pad(var,choices[dir][dim], 'symmetric')
        if xax is not None and dir in {'l', 'r'}:
            axx = np.pad(axx,choices[dir][0],'reflect',reflect_type='odd')
        if yax is not None and dir in {'t', 'b'}:
            axy = np.pad(axy,choices[dir][0],'reflect',reflect_type='odd')
    xax is not None and nax.append(axx)
    yax is not None and nax.append(axy)
    if len(nax) > 0:
        return var, nax
    else:
        return var
