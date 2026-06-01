"""Fourier utilities manager."""

from typing import Any

import numpy as np

from pyPLUTO.loadmixin import LoadMixin
from pyPLUTO.loadstate import LoadState
from pyPLUTO.utils.inspector import track_kwargs


class FourierManager(LoadMixin):
    """Manager for Fourier transforms on loaded data."""

    def __init__(self, state: LoadState) -> None:
        self.state = state

    @track_kwargs(extra_keys={"dx", "dy", "dz"})
    def fourier(
        self, f: np.ndarray, **kwargs: Any
    ) -> tuple[list[np.ndarray], np.ndarray]:
        """Compute Fourier transform and return frequencies + amplitude."""
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
        """Check grid spacing and return scalar spacing."""
        scrh = dx[0] if not isinstance(dx, (float, int)) else dx
        if scrh <= 0:
            raise ValueError("the grid spacing must be positive!")
        return scrh
