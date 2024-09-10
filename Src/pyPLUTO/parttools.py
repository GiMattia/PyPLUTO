from .libraries import *

def spectrum(self, 
             var = None, 
             scale = 'lin', 
             check: bool = True,
             **kwargs
            ) -> list[np.ndarray]:
    """
    Compute the spectrum of a given particle variable.

    Returns
    -------

    - bins: np.ndarray
        The x1 array of the histogram.
    - hist: np.ndarray
        The x2 array of the histogram.

    Parameters
    ----------

    - nbins: int
        The number of bins wanted for the histogram.
    - scale: {'lin','log'}, default 'lin'
        The scale of the histogram, linear or logarithmic.
    - var: np.ndarray
        The chosen variable for the histogram.
    - vmin: float
        The minimum value of the chosen variable.
    - vmax: float
        The maximum value of the chosen variable.

    Notes
    -----

    - CONTROLLARE SE CI SONO TUTTE LE KEYWORDS

    ----

    Examples
    ========    

    INSERIRE UN ESEMPIO
    
    """

    # Check parameters
    param = {'nbins','vmin','vmax'}
    if check is True:
        check_par(param, 'spectrum', **kwargs)

    # Set limits
    vmin = kwargs.get('vmin',np.nanmin(var))
    vmax = kwargs.get('vmax',np.nanmax(var))

    # Set the number of bins
    nbins = kwargs.get('nbins',100)

    # Set the bins
    bins = np.linspace(vmin,vmax,nbins) if scale == 'lin' else \
           np.logspace(np.log10(vmin),np.log10(vmax),nbins)
    
    bins = kwargs.get('bins') if bin in kwargs else bins

    # Compute the histogram
    hist, bins = np.histogram(var,bins = bins, range = (vmin,vmax),
                                  density = kwargs.get('density',True))

    bins = 0.5*(bins[1:] + bins[:-1])
    # Return the histogram
    return hist, bins


def select(self,
           var: np.ndarray, 
           cond: str | Callable, 
           sort: bool = False, 
           ascending: bool = True
          ) -> np.ndarray:
    """
    QUALCOSA

    Returns
    -------

    - indx: np.ndarray

    Parameters
    ----------

    - ascending
    - cond
    - sort
    - var

    Notes
    -----

    - SCRIVERE

    ----

    Examples
    ========

    AGGIUNGERE

    """

    # Determine the indices that satisfy the condition
    if isinstance(cond, str):
        warn = ("The condition should be a callable function to "
                "avoid security issues.")

        condition = f"var {cond}"
        indx = np.where(eval(condition))[0]

    elif callable(cond):
        indx = np.where(cond(var))[0]
    else:
        err = ("Condition must be either a string or a callable "
               "(e.g., a lambda function)")
        raise ValueError(err)
    
    # Sort the indices if requested
    if sort:
        sort_order = np.argsort(var[indx])
        sort_order = sort_order[::-1] if not ascending else sort_order
        indx = indx[sort_order]
    
    return indx
