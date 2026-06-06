"""Docstring for PartToolsManager."""

from __future__ import annotations

import warnings
from collections.abc import Callable
from typing import Any

import numpy as np

from pyPLUTO.baseloadstate import BaseLoadState
from pyPLUTO.utils.inspector import track_kwargs


class PartToolsManager:
    """Manager for particle analysis helpers."""

    def __init__(self, state: BaseLoadState) -> None:
        """Initialize the particle tools manager with the given load state.

        Parameters
        ----------
        - state: BaseLoadState
            The load state object carrying particle variable data.

        Returns
        -------
        - None

        """
        self.state = state

    @track_kwargs
    def spectrum(
        self,
        var: np.ndarray,
        scale: str = "lin",
        vmin: float | None = None,
        vmax: float | None = None,
        _check: bool = True,
        **kwargs: Any,
    ) -> tuple[np.ndarray, np.ndarray]:
        """Compute the spectrum of a given particle variable.

        Parameters
        ----------
        - bins: int | np.ndarray, default 100
            The bin edges for the histogram.
        - normalize: bool, default True
            If True, the histogram is normalized.
        - nbins: int
            The number of bins wanted for the histogram.
        - scale: {'lin','log'}, default 'lin'
            The scale of the histogram, linear or logarithmic.
        - var: np.ndarray
            The chosen variable for the histogram.
        - vmin: float, default min(var)
            The minimum value of the chosen variable.
        - vmax: float, default max(var)
            The maximum value of the chosen variable.

        Returns
        -------
        - tuple[np.ndarray, np.ndarray]

        Examples
        --------
        - Example #1: Compute the spectrum of the particles velocity

            >>> import pyPLUTO as pp
            >>> D = pp.LoadPart(0)
            >>> v2 = D.vx1**2 + D.vx2**2 + D.vx3**2
            >>> pp.spectrum(v2, scale="log")

        """
        # Set limits
        vmin = vmin if vmin is not None else np.nanmin(var)
        vmax = vmax if vmax is not None else np.nanmax(var)

        # Set the number of bins
        nbins = kwargs.get("nbins", 100)

        # Set the bins
        bins = (
            np.linspace(vmin, vmax, nbins)
            if scale == "lin"
            else np.logspace(np.log10(vmin), np.log10(vmax), nbins)
        )
        bins = kwargs.get("bins", bins)

        # Compute the histogram
        if kwargs.get("density") is not None:
            warn = (
                "The 'density' keyword is deprecated and will be removed "
                "in a future version. Use 'normalize' instead."
            )
            warnings.warn(warn, DeprecationWarning, stacklevel=2)
        hist, bins = np.histogram(
            var,
            bins=bins,
            range=(vmin, vmax),
            density=kwargs.get("normalize", True),
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
        """Select or sort particle indices matching a condition.

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

        Returns
        -------
        - np.ndarray

        Examples
        --------
        - Example #1: Select the indices that satisfy a condition

            >>> import pyPLUTO as pp
            >>> D = pp.LoadPart(0)
            >>> indx = pp.select(D.vx1, "vx1 > 0.0")
            >>> print(indx)

        - Example #2: Sort the indices through a callable

            >>> import pyPLUTO as pp
            >>> D = pp.LoadPart(0)
            >>> indx = pp.select(D.vx1, lambda v: v > 0, sort=True)
            >>> print(indx)

        """
        # Determine the indices that satisfy the condition
        if isinstance(cond, str):
            warn = (
                "The condition should be a callable function to "
                "avoid security issues."
            )
            warnings.warn(warn, UserWarning, stacklevel=2)

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
