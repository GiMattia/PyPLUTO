from .libraries import *
    
def fourier(self, 
            f: np.ndarray, 
            **kwargs: Any
           ) -> tuple[list[np.ndarray], np.ndarray]:
    """

    """
    
    # Convert the input array to a numpy array
    f = np.asarray(f)
    
    # Check the dimensions of the input array
    dim = f.ndim
    shp = f.shape

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
    for param, def_attr, dir, numdir in dir_par:
        # Check if the grid spacing is provided
        try:
            spacing[param] = fourier_spacing(kwargs[param])
        # If the grid spacing is not provided or not valid, use the default 
        # grid spacing (and set it to 1 if it still not valid)
        except:
            spacing[param] = fourier_spacing(getattr(self, def_attr))
            spacing[param] = 1.0 if spacing[param] is None else spacing[param]
        # Check if the Fourier transform should be computed in this direction
        if kwargs.get(dir,True) is True and dim > numdir:
            axes.append(numdir)
            # Compute the frequencies
            freqs.append(2.0*np.pi*np.fft.rfftfreq(shp[numdir], spacing[param]))

    # Compute the Fourier transform
    fk = np.fft.fftn(f, axes = axes)

    # Return the Fourier transform and the corresponding frequencies
    slices = tuple(slice(0, dim//2 + 1) for dim in shp)
    return freqs, fk[slices]

def fourier_spacing(dx: float | int | list | np.ndarray
                   ) -> float:
    """
    Check the grid spacing and return the correct value.

    
    """
    # Check if the grid spacing is a list or numpy array, then take the first 
    # element
    scrh = dx[0] if not isinstance(dx, (float,int)) else dx

    # Check if the grid spacing is positive, if not raise an error
    if scrh <= 0:
        raise ValueError(f"the grid spacing must be positive!")
    
    # Return the grid spacing
    return scrh    