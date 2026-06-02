"""Transform utilities manager."""

from typing import Any

import numpy as np
from numpy.typing import NDArray
from scipy.interpolate import RectBivariateSpline

from pyPLUTO.loadmixin import LoadMixin
from pyPLUTO.loadstate import LoadState
from pyPLUTO.toolfuncs.findlines import FindLinesManager
from pyPLUTO.toolfuncs.loadtools import LoadToolsManager
from pyPLUTO.utils.inspector import track_kwargs


class TransformManager(LoadMixin):
    """Manager for transform and slicing helpers."""

    def __init__(self, state: LoadState) -> None:
        """Initialize the transform manager and its helper sub-managers.

        Parameters
        ----------
        - state: LoadState
            The load state object providing grid arrays and dataset variables.

        Returns
        -------
        - None

        """
        self.state = state
        self.LoadToolsManager = LoadToolsManager(state)
        self.FindLinesManager = FindLinesManager(state)

    @track_kwargs(extra_keys={"axis1", "axis2", "offset"})
    def slices(
        self,
        var: NDArray,
        diag: bool | None = None,
        x1: int | list | None = None,
        x2: int | list | None = None,
        x3: int | list | None = None,
        **kwargs: Any,
    ) -> np.ndarray:
        """Slice a variable along axes and optionally along a diagonal."""
        newvar = np.copy(var)

        if diag is not None:
            if diag == "min":
                newvar = np.diagonal(np.flipud(newvar), **kwargs)
            else:
                newvar = np.diagonal(newvar, **kwargs)

        if x3 is not None:
            newvar = newvar[:, :, x3]

        if x2 is not None:
            newvar = newvar[:, x2]

        if x1 is not None:
            newvar = newvar[x1]

        return newvar

    def mirror(
        self, var: NDArray, dirs: str | list = "l", xax=None, yax=None
    ) -> list[np.ndarray]:
        """Mirror a variable in one or more directions."""
        spp = [*dirs] if not isinstance(dirs, list) else dirs
        newvar, axx, axy = np.copy(var), np.copy(xax), np.copy(yax)
        dim = np.ndim(var) - 1
        if dim > 1:
            raise ValueError("Mirror function does not works for 3D arrays")
        nax = []
        for direction in spp:
            lvx = len(newvar[:, 0]) if dim == 1 else len(var)
            lvy = len(newvar[0, :]) if dim == 1 else len(var)
            choices = {
                "l": [(lvx, 0), ((lvx, 0), (0, 0))],
                "r": [(0, lvx), ((0, lvx), (0, 0))],
                "t": [(0, lvy), ((0, 0), (0, lvy))],
                "b": [(lvy, 0), ((0, 0), (lvy, 0))],
            }
            newvar = np.pad(newvar, choices[direction][dim], "symmetric")
            if xax is not None and direction in {"l", "r"}:
                axx = np.pad(
                    axx, choices[direction][0], "reflect", reflect_type="odd"
                )
            if yax is not None and direction in {"t", "b"}:
                axy = np.pad(
                    axy, choices[direction][0], "reflect", reflect_type="odd"
                )
        xax is not None and nax.append(axx)
        yax is not None and nax.append(axy)
        if len(nax) > 1:
            return newvar, nax
        elif len(nax) > 0:
            return newvar, nax[0]
        else:
            return newvar

    def repeat(
        self,
        var: NDArray,
        dirs: str | list,
        xax: NDArray | None = None,
        yax: NDArray | None = None,
    ) -> np.ndarray:
        """Repeat a variable in one or more directions."""
        raise NotImplementedError("Function repeat not implemented yet")

    @track_kwargs
    def cartesian_vector(
        self, var: str | None = None, **kwargs: Any
    ) -> tuple[NDArray, ...]:
        """Convert vector components to Cartesian coordinates."""
        vars = {
            "B": ["Bx1", "Bx2", "Bx3"],
            "E": ["Ex1", "Ex2", "Ex3"],
            "v": ["vx1", "vx2", "vx3"],
        }

        if var is not None:
            var_0 = [
                self.FindLinesManager._check_var(
                    v, kwargs.get("transpose", False)
                )
                for v in vars[var]
            ]
        elif "var1" in kwargs and "var2" in kwargs:
            var_0 = [
                self.FindLinesManager._check_var(
                    kwargs["var1"], kwargs.get("transpose", False)
                ),
                self.FindLinesManager._check_var(
                    kwargs["var2"], kwargs.get("transpose", False)
                ),
            ]
        else:
            raise ValueError("Either var or var1 and var2 must be specified.")

        if "var3" in kwargs:
            var_0.append(
                self.FindLinesManager._check_var(
                    kwargs["var3"], kwargs.get("transpose", False)
                )
            )

        x2 = kwargs.get("x2", self.x2)
        x3 = kwargs.get("x3", self.x3)

        if self.geom == "SPHERICAL":
            varr = var_0[0] * np.sin(x2) + var_0[1] * np.cos(x2)
            varz = var_0[0] * np.cos(x2) - var_0[1] * np.sin(x2)
            if self.dim == 3:
                varx = varr * np.cos(x3) - var_0[2] * np.sin(x3)
                vary = varr * np.sin(x3) + var_0[2] * np.cos(x3)
                if kwargs.get("fullout", False):
                    return varx, vary, varz, varr
                else:
                    return varx, vary, varz
            else:
                return varr, varz

        elif self.geom == "POLAR":
            varx = var_0[0] * np.cos(x2) - var_0[1] * np.sin(x2)
            vary = var_0[0] * np.sin(x2) + var_0[1] * np.cos(x2)
            return varx, vary
        raise ValueError(f"Geometry {self.geom} not supported")

    @track_kwargs
    def reshape_cartesian(
        self, *args: Any, **kwargs: Any
    ) -> tuple[NDArray, ...]:
        """Reshape cylindrical/spherical data onto a Cartesian grid."""
        vars = []
        newv = []
        for i in args:
            vars.append(
                self.FindLinesManager._check_var(
                    i, kwargs.get("transpose", False)
                )
            )

        x1 = kwargs.pop("x1", self.x1)
        x2 = kwargs.pop("x2", self.x2)

        xx = x1[:, np.newaxis] * np.cos(x2)
        yy = x1[:, np.newaxis] * np.sin(x2)

        xmin, xmax = xx.min(), xx.max()
        ymin, ymax = yy.min(), yy.max()

        del xx, yy

        nx1 = int(kwargs.get("nx1", len(x1)))
        nx2 = int(kwargs.get("nx2", nx1 * (ymax - ymin) / (xmax - xmin)))

        if self.geom == "SPHERICAL":
            xc0 = np.linspace(xmin, xmax, nx2)
            yc0 = np.linspace(ymin, ymax, nx1)
            xc, yc = np.meshgrid(xc0, yc0, indexing="xy")
        else:
            xc0 = np.linspace(xmin, xmax, nx1)
            yc0 = np.linspace(ymin, ymax, nx2)
            xc, yc = np.meshgrid(xc0, yc0, indexing="ij")

        x1, x2, vars = self.reshape_uniform(x1, x2, *vars, **kwargs)

        ww, nn = self._convert2cartgrid(xc, yc, x1, x2)

        xcong = self.LoadToolsManager.congrid(xc, (nx1, nx2), method="linear")
        ycong = self.LoadToolsManager.congrid(yc, (nx1, nx2), method="linear")

        for i, var in enumerate(vars):
            newv.append(
                np.sum([ww[j] * var.flat[nn[j]] for j in range(4)], axis=0)
            )
            newv[i] = self.LoadToolsManager.congrid(
                newv[i], (nx1, nx2), method="linear"
            )

        if self.geom == "SPHERICAL":
            return ycong[:, 0], xcong[0], *newv
        else:
            return xcong[:, 0], ycong[0], *newv

    @track_kwargs
    def reshape_uniform(self, x1, x2, *args, **kwargs):
        """Reshape a non-uniform 2D grid into a uniform one."""
        uniform_x = all(np.diff(x1) == np.diff(x1)[0])
        uniform_y = all(np.diff(x2) == np.diff(x2)[0])

        nx1new = kwargs.get("nx1", len(x1))
        nx2new = kwargs.get("nx2", len(x2))

        uniform_x = False if nx1new != len(x1) else uniform_x
        uniform_y = False if nx2new != len(x2) else uniform_y

        newvars = []

        if not uniform_x or not uniform_y:
            x1new = (
                np.linspace(x1.min(), x1.max(), nx1new) if not uniform_x else x1
            )
            x2new = (
                np.linspace(x2.min(), x2.max(), nx2new) if not uniform_y else x2
            )

            for i in args:
                interp = RectBivariateSpline(x2, x1, i.T)
                newvars.append(interp(x2new, x1new))

        else:
            x1new = x1
            x2new = x2
            newvars = [arg for arg in args]

        return x1new, x2new, newvars

    def _convert2cartgrid(self, R, Z, new_r, new_t):
        """Convert a spherical/polar grid to Cartesian helper weights."""
        Rs = np.sqrt(R**2 + Z**2)

        Th = np.arctan2(Z, R)
        Th = np.where(Th < 0, Th + 2 * np.pi, Th)

        Rs_clipped = np.clip(Rs, new_r[0], new_r[-1])
        Th_clipped = np.clip(Th, new_t[0], new_t[-1])

        ra = (len(new_r) - 1) * (Rs_clipped - new_r[0]) / (new_r[-1] - new_r[0])
        tha = (
            (len(new_t) - 1) * (Th_clipped - new_t[0]) / (new_t[-1] - new_t[0])
        )

        rn, dra = np.divmod(ra, 1)
        thn, dtha = np.divmod(tha, 1)
        rn, thn = rn.astype(int), thn.astype(int)

        rn = np.clip(rn, 0, len(new_r) - 2)
        thn = np.clip(thn, 0, len(new_t) - 2)

        lrx = len(new_r)
        NN1 = rn + thn * lrx
        NN2 = (rn + 1) + thn * lrx
        NN3 = rn + (thn + 1) * lrx
        NN4 = (rn + 1) + (thn + 1) * lrx

        w1 = (1 - dra) * (1 - dtha)
        w2 = dra * (1 - dtha)
        w3 = (1 - dra) * dtha
        w4 = dra * dtha

        return [w1, w2, w3, w4], [NN1, NN2, NN3, NN4]
