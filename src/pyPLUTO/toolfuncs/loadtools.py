"""Load tools manager with shared utility methods."""

import numpy as np
from numpy.typing import NDArray
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
        self, var: str | NDArray, transpose: bool = False
    ) -> np.ndarray:
        """Return variable array from input array or dataset key."""
        if isinstance(var, str):
            try:
                val = getattr(self.state, var)
                var = AttrResolver.resolve(self.state, var, val)
            except ValueError as exc:
                raise ValueError(
                    f"Variable {var} not found in the dataset."
                ) from exc
            except AttributeError as exc:
                raise ValueError(
                    f"Variable {var} not found in the dataset."
                ) from exc

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
        """Arbitrary resampling of source array to new dimension sizes."""
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
