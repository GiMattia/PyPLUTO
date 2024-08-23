from .libraries import *

def spectrum(self, 
             var = None, 
             scale = 'lin', 
             **kwargs
            ):
    """
    Compute the spectrum of a given particle variable

    Parameters
    ----------

    ...
    
    """

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
    ...

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