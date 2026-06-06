"""Load tools manager with shared utility methods."""

from __future__ import annotations

import numpy as np
from scipy.interpolate import RegularGridInterpolator
from scipy.ndimage import map_coordinates

from pyPLUTO.loadmixin import LoadMixin
from pyPLUTO.loadstate import LoadState
from pyPLUTO.utils.resolver import AttrResolver


class LoadToolsManager(LoadMixin):
    """Manager for internal load utilities."""

    def __init__(self, state: LoadState) -> None:
        """Initialize the LoadToolsManager with the given state."""
        self.state = state

    def check_var(
        self, var: str | np.ndarray, transpose: bool = False
    ) -> np.ndarray:
        """Check and return a variable.

        If the variable is a numpy array, it is simply returned (and the
        transpose is taken into account). If the variable is a string, the
        variable is retrieved from the dataset. If the variable is not found, an
        error is raised.

        Returns
        -------
        - var: np.ndarray
            The variable.

        Parameters
        ----------
        - var (not optional): str | np.ndarray
            The variable to be checked.
        - transpose: bool, default False
            If True, the variable is transposed.

        Examples
        --------
        - Example #1: var is a numpy array

            >>> var = np.array([1, 2, 3])
            >>> D._check_var(var, False)
            array([1, 2, 3])

        - Example #2: var is a string

            >>> D = pp.Load()
            >>> D._check_var("Bx1", False)
            D.Bx1

        """
        if isinstance(var, str):
            try:
                val = getattr(self.state, var)
                var = np.asarray(AttrResolver.resolve(self.state, var, val))
            except ValueError as exc:
                raise ValueError(
                    f"Variable {var} not found in the dataset."
                ) from exc

        if not isinstance(var, np.ndarray):
            raise TypeError("The input is not associated to a numpy array.")
        if transpose is True:
            var = var.T

        return var

    def congrid(
        self,
        a: np.ndarray,
        newdims: tuple[int, ...] | list[int] | np.ndarray,
        method: str = "linear",
        center: bool = False,
        minusone: bool = False,
    ) -> np.ndarray:
        """Arbitrary resampling of source array to new dimension sizes.

        Returns
        -------
        - The resampled array.

        Parameters
        ----------
        - a: np.ndarray
            The array to be resampled.
        - newdims: tuple
            The new dimension sizes.
        - method: str, default 'linear'
            The interpolation method to be used.
        - center: bool, default False
            If True, centers the resampled array at the new dimensions.
        - minusone: bool, default False
            If True, the new dimensions should be larger by 1 in each dimension.

        Examples
        --------
        - Example #1: Resample the grid

            >>> newvar = _congrid(newvar, (10, 10))

        """
        a = a.astype(float, copy=False)

        olddims = np.array(a.shape)
        newdims = np.asarray(newdims, dtype=int)

        if olddims.size != newdims.size:
            raise ValueError(
                "Dimension mismatch: newdims must have the same number "
                "of dimensions as the input array."
            )

        m1 = int(minusone)
        ofs = 0.5 if center else 0.0

        old_grid = [np.arange(n) for n in olddims]

        new_grid = np.meshgrid(
            *[
                np.linspace(ofs, olddims[i] - 1 - ofs, num=newdims[i])
                for i in range(len(olddims))
            ],
            indexing="ij",
        )

        new_coords = np.stack(new_grid, axis=-1)

        if method == "spline":
            scale = (olddims - m1) / (newdims - m1)
            coords = np.array(new_grid) * scale[:, None, None]
            return map_coordinates(a, coords, order=3, mode="nearest")

        interpolator = RegularGridInterpolator(
            old_grid, a, method=method, bounds_error=False, fill_value=None
        )
        return interpolator(new_coords)
