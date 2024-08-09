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

    Examples
    --------

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

    Examples
    --------

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

    Examples
    --------

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



def reshape_cartesian(self,
                      var: NDArray
                     )-> tuple[NDArray]:
    """
    Function that reshapes a variable into a cartesian grid.

    """