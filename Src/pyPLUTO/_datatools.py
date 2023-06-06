from ._libraries import *

def slices(self, var, x1 = None, x2 = None, x3 = None, diag = False):
    newvar = np.copy(var)
    if x3 != None:
        newvar = newvar[:,:,x3]
    if x2 != None:
        newvar = newvar[:,x2]
    if x1 != None:
        newvar = newvar[x1]
    if diag == 'maj':
        None
    elif diag == 'min':
        None
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
        return var, *nax
    else:
        return var
