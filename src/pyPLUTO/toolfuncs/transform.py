"""Transform utilities manager."""

from __future__ import annotations

from typing import Unpack

import numpy as np
from scipy.interpolate import RectBivariateSpline

from pyPLUTO.loadkwargs import (
    CartesianVectorKwargs,
    ReshapeKwargs,
    SlicesKwargs,
)
from pyPLUTO.loadmixin import LoadMixin
from pyPLUTO.loadstate import LoadState
from pyPLUTO.toolfuncs.findlines import FindLinesManager
from pyPLUTO.toolfuncs.loadtools import LoadToolsManager
from pyPLUTO.utils.inspector import track_kwargs


class TransformManager(LoadMixin):
    """Manager for transform and slicing helpers."""

    def __init__(self, state: LoadState) -> None:
        """Initialize the transform manager and its helper sub-managers."""
        self.state = state
        self.LoadToolsManager = LoadToolsManager(state)
        self.FindLinesManager = FindLinesManager(state)

    @track_kwargs(extra_keys={"axis1", "axis2", "offset"})
    def slices(
        self,
        var: np.ndarray,
        diag: bool | str | None = None,
        x1: int | list | None = None,
        x2: int | list | None = None,
        x3: int | list | None = None,
        _check: bool = True,
        **kwargs: Unpack[SlicesKwargs],
    ) -> np.ndarray:
        """Slice the variable in the 3 directions.

        Also, it can slice the diagonal of the variable.

        Returns
        -------
        - newvar: np.ndarray
            The sliced variable.

        Parameters
        ----------
        - axis1: int | None, default None
            Axis to be used as the first axis of the 2-D sub-arrays from which
            the diagonals should be taken. Defaults to first axis (0).
        - axis2: int | None, default None
            Axis to be used as the second axis of the 2-D sub-arrays from which
            the diagonals should be taken. Defaults to second axis (1).
        - diag: bool | None, default None
            If not None (or 'min'), slice the main diagonal of the variable.
            If 'min', slice the opposite diagonal.
        - offset: int | None, default None
            Offset of the diagonal from the main diagonal. Can be positive or
            negative. Defaults to main diagonal (0).
        - var: np.ndarray
            The variable to slice.
        - x1: int | list | None, default None
            The slice in the 1st direction.
        - x2: int | list | None, default None
            The slice in the 2nd direction.
        - x3: int | list | None, default None
            The slice in the 3rd direction.

        Examples
        --------
        - Example #1: Slice the variable in the 3 directions

            >>> slices(var, x1=0, x2=0, x3=0)

        - Example #2: Slice the variable in the diagonal

            >>> slices(var, diag=True)

        - Example #3: Slice the variable in the opposite diagonal

            >>> slices(var, diag="min")

        """
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
        self,
        var: np.ndarray,
        dirs: str | list = "l",
        xax: np.ndarray | None = None,
        yax: np.ndarray | None = None,
    ) -> list[np.ndarray]:
        """Mirror the variable in the specified directions.

        Multiple directions can be specified.

        Returns
        -------
        - newvar: np.ndarray
            The mirrored variable.
        - xax: np.ndarray
            The mirrored x-axis.
        - yax: np.ndarray
            The mirrored y-axis.

        Parameters
        ----------
        - dirs: str | list, default 'l'
            The directions to mirror the variable. Can be 'l', 'r', 't', 'b' or
            a list or combination of them.
        - var: np.ndarray
            The variable to mirror.
        - xax: np.ndarray | None, default None
            The x-axis to mirror.
        - yax: np.ndarray | None, default None
            The y-axis to mirror.

        Examples
        --------
        - Example #1: Mirror the variable in the left direction

            >>> mirror(var, dirs="l")

        - Example #2: Mirror the variable in the right direction with axis

            >>> mirror(var, dirs="r", xax=xax)

        - Example #3: Mirror the variable in the top and left directions

            >>> mirror(var, dirs=["t", "l"])

        - Example #4: Mirror the variable in the top and left directions (no
            list)

            >>> mirror(var, dirs="tl")

        - Example #5: Mirror the variable in the left direction three times

            >>> mirror(var, dirs="lll")

        """
        spp = [*dirs] if not isinstance(dirs, list) else dirs
        newvar = np.copy(var)
        axx = np.copy(xax) if xax is not None else None
        axy = np.copy(yax) if yax is not None else None
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
            if axx is not None and direction in {"l", "r"}:
                axx = np.pad(
                    axx,
                    choices[direction][0],
                    mode="reflect",
                    reflect_type="odd",
                )
            if axy is not None and direction in {"t", "b"}:
                axy = np.pad(
                    axy,
                    choices[direction][0],
                    mode="reflect",
                    reflect_type="odd",
                )
        if axx is not None:
            nax.append(axx)
        if axy is not None:
            nax.append(axy)
        if len(nax) > 1:
            return [newvar, *nax]
        if len(nax) > 0:
            return [newvar, nax[0]]
        return [newvar]

    def repeat(
        self,
        var: np.ndarray,
        dirs: str | list,
        xax: np.ndarray | None = None,
        yax: np.ndarray | None = None,
    ) -> np.ndarray:
        """Repeat a variable in one or more directions."""
        raise NotImplementedError("Function repeat not implemented yet")

    @track_kwargs
    def cartesian_vector(
        self,
        var: str | None = None,
        _check: bool = True,
        **kwargs: Unpack[CartesianVectorKwargs],
    ) -> tuple[np.ndarray, ...]:
        """Convert a vector from spherical or polar components to cartesian.

        Returns
        -------
        - newvar: tuple(np.ndarray)
            The converted vector components.

        Parameters
        ----------
        - fullout: bool, default False
            If True, all vector components are returned.
        - transpose: True/False, default False
            Transposes the variable matrix. Use is not recommended if not
            really necessary (e.g. in case of highly customized variables and
            plots).
        - var: np.ndarray
            The variable to convert.
        - var1: np.ndarray
            The first variable to convert if var is not used.
        - var2: np.ndarray
            The second variable to convert if var is not used.
        - var3: np.ndarray
            The third variable to convert if var is not used.
        - x1: int
            The first index of the variable.
        - x2: int
            The second index of the variable.

        Examples
        --------
        - Example #1: Convert the vector from spherical to cartesian components

            >>> Bx, By, Bz = cartesian_vector(var="B")

        - Example #2: Convert the vector from polar to cartesian components

            >>> Bx, By = cartesian_vector(var1=D.Bx1, var2=D.Bx2)

        """
        vecvars = {
            "B": ["Bx1", "Bx2", "Bx3"],
            "E": ["Ex1", "Ex2", "Ex3"],
            "v": ["vx1", "vx2", "vx3"],
        }
        threed = 3

        if var is not None:
            var_0 = [
                self.LoadToolsManager.check_var(
                    v,
                    kwargs.get("transpose", False),
                )
                for v in vecvars[var]
            ]
        elif "var1" in kwargs and "var2" in kwargs:
            var_0 = [
                self.LoadToolsManager.check_var(
                    kwargs["var1"],
                    kwargs.get("transpose", False),
                ),
                self.LoadToolsManager.check_var(
                    kwargs["var2"],
                    kwargs.get("transpose", False),
                ),
            ]
        else:
            raise ValueError("Either var or var1 and var2 must be specified.")

        if "var3" in kwargs:
            var_0.append(
                self.LoadToolsManager.check_var(
                    kwargs["var3"],
                    kwargs.get("transpose", False),
                ),
            )

        x2 = kwargs.get("x2", self.x2)
        x3 = kwargs.get("x3", self.x3)

        if self.geom == "SPHERICAL":
            varr = var_0[0] * np.sin(x2) + var_0[1] * np.cos(x2)
            varz = var_0[0] * np.cos(x2) - var_0[1] * np.sin(x2)
            if self.dim == threed:
                varx = varr * np.cos(x3) - var_0[2] * np.sin(x3)
                vary = varr * np.sin(x3) + var_0[2] * np.cos(x3)
                if kwargs.get("fullout", False):
                    return varx, vary, varz, varr
                return varx, vary, varz
            return varr, varz

        if self.geom == "POLAR":
            varx = var_0[0] * np.cos(x2) - var_0[1] * np.sin(x2)
            vary = var_0[0] * np.sin(x2) + var_0[1] * np.cos(x2)
            return varx, vary
        raise ValueError(f"Geometry {self.geom} not supported")

    @track_kwargs
    def reshape_cartesian(
        self,
        var1: np.ndarray,
        var2: np.ndarray | None = None,
        var3: np.ndarray | None = None,
        _check: bool = True,
        **kwargs: Unpack[ReshapeKwargs],
    ) -> tuple[np.ndarray, ...]:
        """Reshape a variable into a cartesian grid.

        Zones not covered by the original domain (e.g. the very inner radial
        regions) are also interpolated. At the current stage, the transformation
        is only in 2D.

        Returns
        -------
        - newvar: tuple(np.ndarray)
            The converted variable.

        Parameters
        ----------
        - nx1: int, default len(x1)
            The number of grid points in the first direction.
        - nx2: int, default len(x2)
            The number of grid points in the second direction.
        - transpose: True/False, default False
            Transposes the variable matrix. Use is not recommended if not
            really necessary (e.g. in case of highly customized variables and
            plots).
        - var1 (not optional): np.ndarray
            The first variable to convert.
        - var2: np.ndarray | None, default None
            The second variable to convert.
        - var3: np.ndarray | None, default None
            The third variable to convert.
        - x1: np.ndarray, default self.x1
            The first grid coordinate.
        - x2: np.ndarray, default self.x2
            The second grid coordinate.

        Examples
        --------
        - Example #1: Reshape a single variable into a cartesian grid

            >>> xc, yc, rho = reshape_cartesian(D.rho)

        - Example #2: Reshape two variables into a cartesian grid

            >>> xc, yc, Bx, Bz = reshape_cartesian(Bx, Bz, nx1=500)

        """
        newv: list[np.ndarray] = []
        var = [
            self.LoadToolsManager.check_var(v, kwargs.get("transpose", False))
            for v in (var1, var2, var3)
            if v is not None
        ]

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

        # Forward the (possibly defaulted) grid coordinates to reshape_uniform
        kwargs["x1"], kwargs["x2"] = x1, x2
        x1, x2, var = self.reshape_uniform(*var, **kwargs)

        ww, nn = self._convert2cartgrid(xc, yc, x1, x2)

        xcong = self.LoadToolsManager.congrid(xc, (nx1, nx2), method="linear")
        ycong = self.LoadToolsManager.congrid(yc, (nx1, nx2), method="linear")

        for i, singlevar in enumerate(var):
            newv.append(
                np.sum(
                    [ww[j] * singlevar.flat[nn[j]] for j in range(4)],
                    axis=0,
                ),
            )
            newv[i] = self.LoadToolsManager.congrid(
                newv[i],
                (nx1, nx2),
                method="linear",
            )

        if self.geom == "SPHERICAL":
            return ycong[:, 0], xcong[0], *newv
        return xcong[:, 0], ycong[0], *newv

    @track_kwargs
    def reshape_uniform(
        self,
        var1: np.ndarray,
        var2: np.ndarray | None = None,
        var3: np.ndarray | None = None,
        *,
        _check: bool = True,
        **kwargs: Unpack[ReshapeKwargs],
    ) -> tuple[np.ndarray, np.ndarray, list[np.ndarray]]:
        """Reshape a non-uniform (cartesian) 2D grid into a uniform grid.

        Returns
        -------
        tuple: A tuple containing the reshaped x1, x2 and the variables.

        Parameters
        ----------
        - nx1: int, default len(x1)
            The number of grid points in the first direction.
        - nx2: int, default len(x2)
            The number of grid points in the second direction.
        - transpose: True/False, default False
            Transposes the variable matrix. Use is not recommended if not
            really necessary (e.g. in case of highly customized variables and
            plots).
        - var1 (not optional): np.ndarray
            The first variable to reshape.
        - var2: np.ndarray | None, default None
            The second variable to reshape.
        - var3: np.ndarray | None, default None
            The third variable to reshape.
        - x1: np.ndarray, default self.x1
            The first grid coordinate.
        - x2: np.ndarray, default self.x2
            The second grid coordinate.

        Examples
        --------
        - Example #1: Reshape the grid into a uniform grid

            >>> x1new, x2new, varx = reshape_uniform(var, x1=x1, x2=x2)

        """
        x1 = kwargs.get("x1", self.x1)
        x2 = kwargs.get("x2", self.x2)

        args = [v for v in (var1, var2, var3) if v is not None]

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
            newvars = list(args)

        return x1new, x2new, newvars

    def _convert2cartgrid(
        self,
        R: np.ndarray,
        Z: np.ndarray,
        new_r: np.ndarray,
        new_t: np.ndarray,
    ) -> tuple[list[np.ndarray], list[np.ndarray]]:
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
