from .libraries import *
    
def fourier(self, 
            f: np.ndarray, 
            check: bool = True,
            **kwargs: Any
           ) -> tuple[list[np.ndarray], np.ndarray]:
    """
    Compute the Fourier transform of a given array. The function uses the
    numpy.fft.fftn function. The function returns a tuple containing the
    transformed array and the frequency array (which is a list of arrays if
    the input is in 2D or 3D).

    Returns
    -------

    - f: np.ndarray
        The transformed array.
    - freqs: np.ndarray
        The frequency array. It is a list of arrays if the input is in 2D or 3D.

    Parameters
    ----------

    - dx: float | int | list | np.ndarray | None, default None
        The grid spacing. If None, the grid spacing is set to 1.
    - dy: float | int | list | np.ndarray | None, default None
        The grid spacing. If None, the grid spacing is set to 1.
    - dz: float | int | list | np.ndarray | None, default None
        The grid spacing. If None, the grid spacing is set to 1.
    - f: np.ndarray
        The array to be transformed.
    - xdir: bool, default True
        If True, the x-direction is transformed. 
    - ydir: bool, default True
        If True, the y-direction is transformed.
    - zdir: bool, default True
        If True, the z-direction is transformed.

    Notes
    -----

    - None

    ----

    Examples
    ========

    - Example #1: Compute the Fourier transform of a given array

        >>> freqs, f = fourier(func)

    - Example #2: Compute the Fourier transform of a given array in 2D with 
      custom grid spacing

        >>> freqs, f = fourier(func, dx=1, dy=1)

    - Example #3: Compute the Fourier transform of a 3D without considering 
      the x-direction

        >>> freqs, f = fourier(func, xdir=False)

    """

    # Check parameters
    param = {'dx','dy','dz','xdir','ydir','zdir'}
    if check is True:
        check_par(param, 'fourier', **kwargs)
    
    # Convert the input array to a numpy array
    f = np.asarray(f)
    
    # Check the dimensions of the input array
    dim = f.ndim
    shp = f.shape
    print(shp, dim)

    # Define the axes to include in the Fourier transform
    axes  = []
    freqs = []

    # Check if dx/dy/dz are provided.
    dir_par = [('dx', 'dx1', 'xdir', 0), 
               ('dy', 'dx2', 'ydir', 1), 
               ('dz', 'dx3', 'zdir', 2)]

    # Define the grid spacing
    spacing = {}

    # Loop over directions
    for pars, def_attr, dir, numdir in dir_par:

        # If the number of dimensions is less than the number of directions
        # break
        if dim <= numdir:
            break

        # Check if the grid spacing is provided
        try:
            spacing[pars] = _fourier_spacing(kwargs[pars])
        # If the grid spacing is not provided or not valid, use the default 
        # grid spacing (and set it to 1 if it still not valid)
        except:
            spacing[pars] = _fourier_spacing(getattr(self, def_attr))
            spacing[pars] = 1.0 if spacing[pars] is None else spacing[pars]
        # Check if the Fourier transform should be computed in this direction
        if kwargs.get(dir,True) is True and dim > numdir:
            axes.append(numdir)
            # Compute the frequencies
            freqs.append(2.0*np.pi*np.fft.rfftfreq(shp[numdir], spacing[pars]))

    # Compute the Fourier transform
    fk = np.fft.fftn(f, axes = axes)

    # Return the Fourier transform and the corresponding frequencies
    slices = tuple(slice(0, dim//2 + 1) for dim in shp)
    freqs = freqs[0] if len(freqs) == 1 else freqs
    return freqs, np.abs(fk[slices])


def _fourier_spacing(dx: float | int | list | np.ndarray
                    ) -> float:
    """
    Check the grid spacing and return the correct value. If the grid spacing
    is not valid (negative), raise an error.

    Returns
    -------

    - scrh: float
        The grid spacing.

    Parameters
    ----------

    - dx: float | int | list | np.ndarray
        The grid spacing.

    Notes
    -----

    - None

    ----

    Examples
    ========

    - Example #1: Check the grid spacing and return the correct value

        >>> scrh = fourier_spacing(dx)
        
    """

    # Check if the grid spacing is a list or numpy array, then take the first 
    # element
    scrh = dx[0] if not isinstance(dx, (float,int)) else dx

    # Check if the grid spacing is positive, if not raise an error
    if scrh <= 0:
        raise ValueError(f"the grid spacing must be positive!")
    
    # Return the grid spacing
    return scrh    
