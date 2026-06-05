"""Fourier utilities manager."""

from typing import Any

import numpy as np

from pyPLUTO.loadmixin import LoadMixin
from pyPLUTO.loadstate import LoadState
from pyPLUTO.utils.inspector import track_kwargs


class FourierManager(LoadMixin):
    """Manager for Fourier transforms on loaded data."""

    def __init__(self, state: LoadState) -> None:
        """Initialize the Fourier manager with the given load state."""
        self.state = state

    @track_kwargs(extra_keys={"dx", "dy", "dz"})
    def fourier(
        self, f: np.ndarray, **kwargs: Any
    ) -> tuple[list[np.ndarray], np.ndarray]:
        """Compute the Fourier transform of a given array.

        The function uses the numpy.fft.fftn function. The function returns a
        tuple containing the transformed array and the frequency array (which is
        a list of arrays if the input is in 2D or 3D).

        Returns
        -------
        - f: np.ndarray
            The transformed array.
        - freqs: np.ndarray | list[np.ndarray]
            The frequency array. It is a list of arrays if the input is in 2D or
            3D.

        Parameters
        ----------
        - dx: float | int | list | np.ndarray | None, default None
            The grid spacing. If None, the grid spacing is set to 1.
        - dy: float | int | list | np.ndarray | None, default None
            The grid spacing. If None, the grid spacing is set to 1.
        - dz: float | int | list | np.ndarray | None, default None
            The grid spacing. If None, the grid spacing is set to 1.
        - f (not optional): np.ndarray
            The array to be transformed.
        - xdir: bool, default True
            If True, the x-direction is transformed.
        - ydir: bool, default True
            If True, the y-direction is transformed.
        - zdir: bool, default True
            If True, the z-direction is transformed.

        ----

        Examples
        --------
        - Example #1: Compute the Fourier transform of a given array

            >>> freqs, f = fourier(func)

        - Example #2: Compute the Fourier transform of a given array in 2D with
        custom grid spacing

            >>> freqs, f = fourier(func, dx=1, dy=1)

        - Example #3: Compute the Fourier transform of a 3D without considering
        the x-direction

            >>> freqs, f = fourier(func, xdir=False)

        """
        f = np.asarray(f)
        dim = f.ndim
        shp = f.shape

        axes = []
        freqs = []

        dir_par = [
            ("dx", "dx1", "xdir", 0),
            ("dy", "dx2", "ydir", 1),
            ("dz", "dx3", "zdir", 2),
        ]

        spacing = {}

        for pars, def_attr, direction, numdir in dir_par:
            if dim <= numdir:
                break

            try:
                spacing[pars] = self._fourier_spacing(kwargs[pars])
            except ValueError:
                spacing[pars] = self._fourier_spacing(getattr(self, def_attr))
                spacing[pars] = 1.0 if spacing[pars] is None else spacing[pars]

            if kwargs.get(direction, True) is True and dim > numdir:
                axes.append(numdir)
                freqs.append(
                    2.0 * np.pi * np.fft.rfftfreq(shp[numdir], spacing[pars])
                )

        fk = np.fft.fftn(f, axes=axes)

        slices = tuple(slice(0, ndim // 2 + 1) for ndim in shp)
        out_freqs = freqs[0] if len(freqs) == 1 else freqs
        return out_freqs, np.abs(fk[slices])

    @staticmethod
    def _fourier_spacing(dx: float | int | list | np.ndarray) -> float:
        """Check the grid spacing and return the correct value.

        If the grid spacing is not valid (negative), raise an error.

        Returns
        -------
        - scrh: float
            The grid spacing.

        Parameters
        ----------
        - dx (not optional): float | int | list | np.ndarray
            The grid spacing.

        ----

        Examples
        --------
        - Example #1: Check the grid spacing and return the correct value

            >>> scrh = fourier_spacing(dx)

        """
        scrh = dx[0] if not isinstance(dx, (float, int)) else dx
        if scrh <= 0:
            raise ValueError("the grid spacing must be positive!")
        return scrh
