from .libraries import *

def slices(self, 
           var: NDArray, 
           check: bool = True,
           diag: bool | None = None,
           x1: int | list | None = None, 
           x2: int | list | None = None, 
           x3: int | list | None = None,           
           **kwargs: Any
          ):
    """
    Function that slices the variable in the 3 directions.
    Also, it can slice the diagonal of the variable.

    Returns
    -------

    - newvar: NDArray
        The sliced variable.

    Parameters
    ----------

    - axis1: int | None, default None
        Axis to be used as the first axis of the 2-D sub-arrays from which the 
        diagonals should be taken. Defaults to first axis (0).
    - axis2: int | None, default None
        Axis to be used as the second axis of the 2-D sub-arrays from which the
        diagonals should be taken. Defaults to second axis (1).
    - diag: bool | None, default None
        If not None (or 'min'), slice the main diagonal of the variable.
        If 'min', slice the opposite diagonal.
    - offset: int | None, default None
        Offset of the diagonal from the main diagonal. Can be positive or 
        negative. Defaults to main diagonal (0).
    - var: NDArray
        The variable to slice.
    - x1: int | list | None, default None
        The slice in the 1st direction.
    - x2: int | list | None, default None
        The slice in the 2nd direction.
    - x3: int | list | None, default None
        The slice in the 3rd direction.
    
    Notes
    -----

    - None

    ----

    ========
    Examples
    ========

    - Example #1: Slice the variable in the 3 directions
        
        >>> slices(var, x1 = 0, x2 = 0, x3 = 0)

    - Example #2: Slice the variable in the diagonal

        >>> slices(var, diag = True)

    - Example #3: Slice the variable in the opposite diagonal

        >>> slices(var, diag = 'min')  

    """
    # Check the kwargs parameters
    param = {'axis1','axis2','offset'}
    if check is True:
        check_par(param, 'slice', **kwargs)

    # Make a copy to not modify the variable
    newvar = np.copy(var)

    # Slice the diagonal
    if diag is not None:
        if diag == 'min':
            newvar = np.diagonal(np.flipud(newvar),**kwargs)
        else:
            newvar = np.diagonal(newvar,**kwargs)

    # Slice 3rd direction
    if x3 is not None:
        newvar = newvar[:,:,x3]

    # Slice 2nd direction
    if x2 is not None:
        newvar = newvar[:,x2]

    # Slice 1st direction
    if x1 is not None:
        newvar = newvar[x1]

    # End of the function, return the sliced array
    return newvar

def mirror(self, 
           var: NDArray, 
           dirs = 'l', 
           xax = None, 
           yax = None
          ):
    """
    Function that mirrors the variable in the specified directions.
    Multiple directions can be specified.

    Returns
    -------

    - newvar: NDArray
        The mirrored variable.
    - xax: NDArray
        The mirrored x-axis.
    - yax: NDArray
        The mirrored y-axis.

    Parameters
    ----------

    - dirs: str | list, default 'l'
        The directions to mirror the variable. Can be 'l', 'r', 't', 'b' or a
        list or combination of them.
    - var: NDArray
        The variable to mirror.
    - xax: NDArray | None, default None
        The x-axis to mirror.
    - yax: NDArray | None, default None
        The y-axis to mirror.

    Notes
    -----

    - None

    ----

    ========
    Examples
    ========

    - Example #1: Mirror the variable in the left direction
            
        >>> mirror(var, dirs = 'l')
    
    - Example #2: Mirror the variable in the right direction with axis

        >>> mirror(var, dirs = 'r', xax = xax)

    - Example #3: Mirror the variable in the top and left directions

        >>> mirror(var, dirs = ['t','l'])

    - Example #4: Mirror the variable in the top and left directions (no list)

        >>> mirror(var, dirs = 'tl')

    - Example #5: Mirror the variable in the left direction three times

        >>> mirror(var, dirs = 'lll')

    """
    spp = [*dirs] if not isinstance(dirs, list) else dirs
    newvar, axx, axy = np.copy(var), np.copy(xax), np.copy(yax)
    dim = np.ndim(var) - 1
    if dim > 1:
        raise ValueError("Mirror function does not works for 3D arrays")
    nax = []
    for dir in spp:
        lvx = len(newvar[:,0]) if dim == 1 else len(var)
        lvy = len(newvar[0,:]) if dim == 1 else len(var)
        choices = {'l' :[(lvx,0),((lvx,0),(0,0))],
                   'r' :[(0,lvx),((0,lvx),(0,0))],
                   't' :[(0,lvy),((0,0),(0,lvy))],
                   'b' :[(lvy,0),((0,0),(lvy,0))]}
        newvar = np.pad(newvar,choices[dir][dim], 'symmetric')
        if xax is not None and dir in {'l', 'r'}:
            axx = np.pad(axx,choices[dir][0],'reflect',reflect_type='odd')
        if yax is not None and dir in {'t', 'b'}:
            axy = np.pad(axy,choices[dir][0],'reflect',reflect_type='odd')
    xax is not None and nax.append(axx)
    yax is not None and nax.append(axy)
    if len(nax) > 1:
        return newvar, nax
    elif len(nax) > 0:
        return newvar, nax[0]
    else:
        return newvar
    

def repeat(self, 
           var: NDArray, 
           dirs: str | list, 
           xax: NDArray | None = None, 
           yax: NDArray | None = None
          ):
    """
    Function that repeats the variable in the specified directions.
    Multiple directions can be specified.

    Returns
    -------

    - newvar: NDArray

    Parameters
    ----------

    - dirs: str | list
        The directions to repeat the variable. Can be 'l', 'r', 't', 'b' or a
        list or combination of them.
    - var: NDArray
        The variable to repeat.
    - xax: NDArray | None, default None
        The x-axis to repeat. 
    - yax: NDArray | None, default None
        The y-axis to repeat.

    Notes
    -----

    - None

    ----

    ========
    Examples
    ========

    - Example #1: Repeat the variable in the left direction

        >>> repeat(var, dirs = 'l')
    
    - Example #2: Repeat the variable in the right direction with axis

        >>> repeat(var, dirs = 'r', xax = xax)

    - Example #3: Repeat the variable in the top and left directions

        >>> repeat(var, dirs = ['t','l'])

    - Example #4: Repeat the variable in the top and left directions (no list)

        >>> repeat(var, dirs = 'tl')

    """

    spp = [*dirs] if not isinstance(dirs, list) else dirs
    newvar, axx, axy = np.copy(var), np.copy(xax), np.copy(yax)

    for dir in spp:
        lvx = len(newvar[:,0])
        lvy = len(newvar[0,:])
        choices = {'l' :[(lvx,0),((lvx,0),(0,0))],
                   'r' :[(0,lvx),((0,lvx),(0,0))],
                   't' :[(0,lvy),((0,0),(0,lvy))],
                   'b' :[(lvy,0),((0,0),(lvy,0))]}
        newvar = np.pad(newvar,choices[dir][1], 'wrap')
        if xax is not None and dir in {'l', 'r'}:
            axx = np.pad(axx,choices[dir][0],'wrap')
        if yax is not None and dir in {'t', 'b'}:
            axy = np.pad(axy,choices[dir][0],'wrap')

    if xax is not None and yax is not None:
        return newvar, axx, axy
    elif xax is not None:
        return newvar, axx
    elif yax is not None:
        return newvar, axy
    else:
        return newvar


def cartesian_vector(self,
                     var: str | None = None,
                     **kwargs: Any
                    )-> tuple[NDArray]:
    """
    Function that reshapes a variable into a cartesian vector.    

    """

    vars = {'B' : ['Bx', 'By', 'Bz'], 
            'E' : ['Ex', 'Ey', 'Ez'], 
            'v' : ['vx', 'vy', 'vz']}
    
    if var is not None:
        var_0 = [self.check_var(v, kwargs.get('transpose', False)) \
                               for v in vars[var]]
    elif 'var1' in kwargs and 'var2' in kwargs:
        var_0 = [self.check_var(kwargs['var1'], kwargs.get('transpose', False)),
                 self.check_var(kwargs['var2'], kwargs.get('transpose', False))]
    if 'var3' in kwargs:
        var_0.append(self.check_var(kwargs['var3'], 
                                    kwargs.get('transpose', False)))
    raise NotImplementedError("Function not implemented yet.")


def reshape_cartesian(self,
                      *args: Any,
                      **kwargs: Any
                     )-> tuple[NDArray]:
    """
    Function that reshapes a variable into a cartesian grid.


    """
        
    # Get the variable, if it is a string, get the variable from the dataset.
    # The .T is used to transpose the variable to the correct shape.
    vars = []
    newv = []
    for i in args:
        vars.append(self._check_var(i, kwargs.get('transpose', False)))

    # Get the grid information
    x1 = kwargs.get('x1',self.x1)
    x2 = kwargs.get('x2',self.x2)

    # Get the grid limits
    xx = x1[:, np.newaxis]*np.cos(x2)
    yy = x1[:, np.newaxis]*np.sin(x2)
    xmin, xmax = xx.min(), xx.max()
    ymin, ymax = yy.min(), yy.max()

    del xx, yy

    # Get the number of grid points of the new grid
    nx1 = int(kwargs.get('nx1', len(x1)))
    nx2 = int(kwargs.get('nx2', nx1*(ymax-ymin)//(xmax-xmin)))

    # Get the cartesian grid
    xc0 = np.linspace(xmin, xmax, nx1)
    yc0 = np.linspace(ymin, ymax, nx2)
    xc, yc = np.meshgrid(xc0, yc0)

    # Create the new grid
    x1, x2, vars = reshape_uniform(x1, x2, *vars, **kwargs)

    # Convert grid
    ww, nn = _convert2cartgrid(xc, yc, x1, x2)   

    xcong = congrid(xc,(nx1,nx2),method='linear')
    ycong = congrid(yc,(nx1,nx2),method='linear')

    for i, var in enumerate(vars):
        newv.append(np.sum([ww[j]*var.flat[nn[j]] for j in range(4)], axis = 0))
        newv[i] = congrid(newv[i],(nx1,nx2),method='linear').T


    return xcong, ycong, *newv



def reshape_uniform(x1, x2, *args, **kwargs):
    """
    Reshapes a non-uniform grid into a uniform grid.

    Parameters:
    var1 (numpy.ndarray): The first variable to be reshaped.
    var2 (numpy.ndarray): The second variable to be reshaped.
    x1 (numpy.ndarray): The first coordinate of the grid.
    x2 (numpy.ndarray): The second coordinate of the grid.

    Returns:
    tuple: A tuple containing the reshaped x1, x2, varx, and vary.
    """
    uniform_x = all(np.diff(x1)==np.diff(x1)[0])
    uniform_y = all(np.diff(x2)==np.diff(x2)[0])

    nx1new = kwargs.get('nx1', len(x1))
    nx2new = kwargs.get('nx2', len(x2))

    uniform_x = False if nx1new != len(x1) else uniform_x
    uniform_y = False if nx2new != len(x2) else uniform_y

    newvars = []

    if not uniform_x or not uniform_y:
        
        x1new = np.linspace(x1.min(), x1.max(), nx1new) if \
                not uniform_x else x1
        x2new = np.linspace(x2.min(), x2.max(), nx2new) if \
                not uniform_y else x2

        for i in args:
            interp = RectBivariateSpline(x2, x1, i.T)
            newvars.append(interp(x2new, x1new))

    else:
        x1new = x1
        x2new = x2
        newvars = [arg for arg in args]
        
    return x1new, x2new, newvars


def _convert2cartgrid(R, Z, new_r, new_t):

    print(np.shape(R), np.shape(Z), np.shape(new_r), np.shape(new_t))

    # Convert Cartesian coordinates (R, Z) to polar (Rs, Th)
    Rs = np.sqrt(R**2 + Z**2)

    Th = np.arctan2(Z, R)
    Th = np.where(Th < 0, Th + 2*np.pi, Th)  # Ensure Th is in [0, 2pi]

    # Clip Rs and Th to the range of the new grid
    Rs_clipped = np.clip(Rs, new_r[0], new_r[-1])
    Th_clipped = np.clip(Th, new_t[0], new_t[-1])

    # Normalize Rs and Th to the new grid indices
    ra  = (len(new_r) - 1) * (Rs_clipped - new_r[0]) / (new_r[-1] - new_r[0])
    tha = (len(new_t) - 1) * (Th_clipped - new_t[0]) / (new_t[-1] - new_t[0])

    # Get the integer and fractional parts of the grid indices
    rn, dra = np.divmod(ra, 1)
    thn, dtha = np.divmod(tha, 1)
    rn, thn = rn.astype(int), thn.astype(int)

    # Ensure indices are within bounds
    rn = np.clip(rn, 0, len(new_r) - 2)
    thn = np.clip(thn, 0, len(new_t) - 2)

    # Bilinear interpolation
    lrx = len(new_r)
    NN1 = rn + thn * lrx
    NN2 = (rn + 1) + thn * lrx
    NN3 = rn + (thn + 1) * lrx
    NN4 = (rn + 1) + (thn + 1) * lrx

    w1 = (1 - dra) * (1 - dtha)
    w2 = dra * (1 - dtha)
    w3 = (1 - dra) * dtha
    w4 = dra * dtha

    return [w1, w2, w3, w4], [NN1, NN2, NN3, NN4]


def congrid(a, newdims, method='linear', center=False, minusone=False):
    """
    Arbitrary resampling of source array to new dimension sizes.

    Inputs:
    - a: The array to be resampled.
    - newdims: A tuple representing the shape of the resampled data.
    - method: Interpolation method ('nearest', 'linear', 'spline').
    - center: If True, interpolation points are at the centers of the bins.
    - minusone: Adjusts interpolation calculation to avoid extrapolating beyond input bounds.

    Output:
    - Resampled array with shape corresponding to newdims.
    """
    # Ensure input is a floating-point array for interpolation
    a = a.astype(float, copy=False)

    olddims = np.array(a.shape)
    newdims = np.asarray(newdims, dtype=int)

    if olddims.size != newdims.size:
        raise ValueError("Dimension mismatch: newdims must have the same number of dimensions as the input array.")

    m1 = int(minusone)
    ofs = 0.5 if center else 0.0

    # Generate the original grid
    old_grid = [np.arange(n) for n in olddims]

    # Generate the new grid, scaled to match the new dimensions
    new_grid = np.meshgrid(*[
        np.linspace(ofs, olddims[i] - 1 - ofs, num=newdims[i])
        for i in range(len(olddims))
    ], indexing='ij')

    # Stack the coordinates for RegularGridInterpolator
    new_coords = np.stack(new_grid, axis=-1)

    if method == 'spline':
        # Use spline interpolation with map_coordinates
        scale = (olddims - m1) / (newdims - m1)
        coords = np.array(new_grid) * scale[:, None, None]
        return map_coordinates(a, coords, order=3, mode='nearest')

    else:
        # Use RegularGridInterpolator for 'linear' and 'nearest' methods
        interpolator = RegularGridInterpolator(old_grid, a, method=method, 
                                               bounds_error=False, fill_value=None)
        return interpolator(new_coords)