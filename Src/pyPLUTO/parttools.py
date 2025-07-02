import warnings
from collections.abc import Callable

import numpy as np

from .h_pypluto import check_par


def spectrum(
    self, var=None, scale="lin", check: bool = True, **kwargs
) -> list[np.ndarray]:
    """Compute the spectrum of a given particle variable.

    Returns
    -------
    - bins: np.ndarray
        The x1 array of the histogram.
    - hist: np.ndarray
        The x2 array of the histogram.

    Parameters
    ----------
    - density: bool, default False
        If True, the histogram is normalized.
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

    ----

    Examples
    --------
    - Example #1: Compute the spectrum of the particles velocity

        >>> import pyPLUTO as pp
        >>> D = pp.LoadPart(0)
        >>> v2 = D.vx1**2 + D.vx2**2 + D.vx3**2
        >>> pp.spectrum(v2, scale = 'log')

    """
    # Check parameters
    param = {"density", "nbins", "vmin", "vmax"}
    if check is True:
        check_par(param, "spectrum", **kwargs)

    # Set limits
    vmin = kwargs.get("vmin", np.nanmin(var))
    vmax = kwargs.get("vmax", np.nanmax(var))

    # Set the number of bins
    nbins = kwargs.get("nbins", 100)

    # Set the bins
    bins = (
        np.linspace(vmin, vmax, nbins)
        if scale == "lin"
        else np.logspace(np.log10(vmin), np.log10(vmax), nbins)
    )

    bins = kwargs.get("bins") if bin in kwargs else bins

    # Compute the histogram
    hist, bins = np.histogram(
        var, bins=bins, range=(vmin, vmax), density=kwargs.get("density", True)
    )

    # Compute the bin centers
    bins = 0.5 * (bins[1:] + bins[:-1])

    # Return the histogram
    return hist, bins


def select(
    self,
    var: np.ndarray,
    cond: str | Callable,
    sort: bool = False,
    ascending: bool = True,
) -> np.ndarray:
    """Selects or sorts the indices that satisfy a given condition for
    the particles. The condition is given by a string or a callable
    function.

    Returns
    -------
    - indx: np.ndarray

    Parameters
    ----------
    - ascending: bool, default True
        If True, the indices are sorted in ascending order.
    - cond (not optional): str | Callable
        The condition to be satisfied.
    - sort: bool, default False
        If True, the indices are sorted in descending (or ascending) order.
    - var (not optional): np.ndarray
        The chosen variable for the selection.

    ----

    Examples
    --------
    - Example #1: Select the indices that satisfy a condition

        >>> import pyPLUTO as pp
        >>> D = pp.LoadPart(0)
        >>> indx = pp.select(D.vx1, 'vx1 > 0.0')
        >>> print(indx)

    - Example #2: Sort the indices that satisfy a condition through a callable

        >>> import pyPLUTO as pp
        >>> D = pp.LoadPart(0)
        >>> indx = pp.select(D.vx1, lambda v: v > 0 sort = True)
        >>> print(indx)

    """
    # Determine the indices that satisfy the condition
    if isinstance(cond, str):
        warn = (
            "The condition should be a callable function to "
            "avoid security issues."
        )
        warnings.warn(warn)

        condition = f"var {cond}"
        indx = np.where(eval(condition))[0]

    elif callable(cond):
        indx = np.where(cond(var))[0]
    else:
        err = (
            "Condition must be either a string or a callable "
            "(e.g., a lambda function)"
        )
        raise ValueError(err)

    # Sort the indices if requested
    if sort:
        sort_order = np.argsort(var[indx])
        sort_order = sort_order[::-1] if not ascending else sort_order
        indx = indx[sort_order]

    return indx
