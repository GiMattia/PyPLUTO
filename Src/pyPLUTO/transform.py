from typing import Any

import numpy as np
from numpy.typing import NDArray
from scipy.interpolate import RectBivariateSpline, RegularGridInterpolator
from scipy.ndimage import map_coordinates

from .h_pypluto import check_par


def slices(
    self,
    var: NDArray,
    check: bool = True,
    diag: bool | None = None,
    x1: int | list | None = None,
    x2: int | list | None = None,
    x3: int | list | None = None,
    **kwargs: Any,
) -> np.ndarray:
    """Function that slices the variable in the 3 directions.
    Also, it can slice the diagonal of the variable.

    Returns
    -------
    - newvar: NDArray
        The sliced variable.

    Parameters
    ----------
    - axis1: int | None, default None
        Axis to be used as the first axis of the 2-D sub-arrays from which the
        diagonals should be taken. Defaults to first axis (0).
    - axis2: int | None, default None
        Axis to be used as the second axis of the 2-D sub-arrays from which the
        diagonals should be taken. Defaults to second axis (1).
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

    Notes
    -----
    - None

    ----

    Examples
    --------
    - Example #1: Slice the variable in the 3 directions

        >>> slices(var, x1 = 0, x2 = 0, x3 = 0)

    - Example #2: Slice the variable in the diagonal

        >>> slices(var, diag = True)

    - Example #3: Slice the variable in the opposite diagonal

        >>> slices(var, diag = 'min')

    """
    # Check the kwargs parameters
    param = {"axis1", "axis2", "offset"}
    if check is True:
        check_par(param, "slice", **kwargs)

    # Make a copy to not modify the variable
    newvar = np.copy(var)

    # Slice the diagonal
    if diag is not None:
        if diag == "min":
            newvar = np.diagonal(np.flipud(newvar), **kwargs)
        else:
            newvar = np.diagonal(newvar, **kwargs)

    # Slice 3rd direction
    if x3 is not None:
        newvar = newvar[:, :, x3]

    # Slice 2nd direction
    if x2 is not None:
        newvar = newvar[:, x2]

    # Slice 1st direction
    if x1 is not None:
        newvar = newvar[x1]

    # End of the function, return the sliced array
    return newvar


def mirror(
    self, var: NDArray, dirs="l", xax=None, yax=None
) -> list[np.ndarray]:
    """Function that mirrors the variable in the specified directions.
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
        The directions to mirror the variable. Can be 'l', 'r', 't', 'b' or a
        list or combination of them.
    - var: np.ndarray
        The variable to mirror.
    - xax: np.ndarray | None, default None
        The x-axis to mirror.
    - yax: np.ndarray | None, default None
        The y-axis to mirror.

    Notes
    -----
    - None

    ----

    Examples
    --------
    - Example #1: Mirror the variable in the left direction

        >>> mirror(var, dirs = 'l')

    - Example #2: Mirror the variable in the right direction with axis

        >>> mirror(var, dirs = 'r', xax = xax)

    - Example #3: Mirror the variable in the top and left directions

        >>> mirror(var, dirs = ['t','l'])

    - Example #4: Mirror the variable in the top and left directions (no list)

        >>> mirror(var, dirs = 'tl')

    - Example #5: Mirror the variable in the left direction three times

        >>> mirror(var, dirs = 'lll')

    """
    spp = [*dirs] if not isinstance(dirs, list) else dirs
    newvar, axx, axy = np.copy(var), np.copy(xax), np.copy(yax)
    dim = np.ndim(var) - 1
    if dim > 1:
        raise ValueError("Mirror function does not works for 3D arrays")
    nax = []
    for dir in spp:
        lvx = len(newvar[:, 0]) if dim == 1 else len(var)
        lvy = len(newvar[0, :]) if dim == 1 else len(var)
        choices = {
            "l": [(lvx, 0), ((lvx, 0), (0, 0))],
            "r": [(0, lvx), ((0, lvx), (0, 0))],
            "t": [(0, lvy), ((0, 0), (0, lvy))],
            "b": [(lvy, 0), ((0, 0), (lvy, 0))],
        }
        newvar = np.pad(newvar, choices[dir][dim], "symmetric")
        if xax is not None and dir in {"l", "r"}:
            axx = np.pad(axx, choices[dir][0], "reflect", reflect_type="odd")
        if yax is not None and dir in {"t", "b"}:
            axy = np.pad(axy, choices[dir][0], "reflect", reflect_type="odd")
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
    """Function that repeats the variable in the specified directions.
    Multiple directions can be specified.

    Returns
    -------
    - newvar: np.ndarray
        The repeated variable.

    Parameters
    ----------
    - dirs: str | list
        The directions to repeat the variable. Can be 'l', 'r', 't', 'b' or a
        list or combination of them.
    - var: np.ndarray
        The variable to repeat.
    - xax: np.ndarray | None, default None
        The x-axis to repeat.
    - yax: np.ndarray | None, default None
        The y-axis to repeat.

    Notes
    -----
    - None

    ----

    Examples
    --------
    - Example #1: Repeat the variable in the left direction

        >>> repeat(var, dirs = 'l')

    - Example #2: Repeat the variable in the right direction with axis

        >>> repeat(var, dirs = 'r', xax = xax)

    - Example #3: Repeat the variable in the top and left directions

        >>> repeat(var, dirs = ['t','l'])

    - Example #4: Repeat the variable in the top and left directions (no list)

        >>> repeat(var, dirs = 'tl')

    """
    raise NotImplementedError("Function repeat not implemented yet")

    spp = [*dirs] if not isinstance(dirs, list) else dirs
    newvar, axx, axy = np.copy(var), np.copy(xax), np.copy(yax)

    for dir in spp:
        lvx = len(newvar[:, 0])
        lvy = len(newvar[0, :])
        choices = {
            "l": [(lvx, 0), ((lvx, 0), (0, 0))],
            "r": [(0, lvx), ((0, lvx), (0, 0))],
            "t": [(0, lvy), ((0, 0), (0, lvy))],
            "b": [(lvy, 0), ((0, 0), (lvy, 0))],
        }
        newvar = np.pad(newvar, choices[dir][1], "wrap")
        if xax is not None and dir in {"l", "r"}:
            axx = np.pad(axx, choices[dir][0], "wrap")
        if yax is not None and dir in {"t", "b"}:
            axy = np.pad(axy, choices[dir][0], "wrap")

    if xax is not None and yax is not None:
        return newvar, axx, axy
    elif xax is not None:
        return newvar, axx
    elif yax is not None:
        return newvar, axy
    else:
        return newvar


def cartesian_vector(
    self, var: str | None = None, **kwargs: Any
) -> tuple[NDArray, ...]:
    """Function that converts a vector from spherical or polar components to
    cartesian components.

    Returns
    -------
    - newvar: tuple(np.ndarray)
        The converted vector components.

    Parameters
    ----------
    - transpose: bool, default False
        If True, the variable is transposed.
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

    Notes
    -----
    - None

    ----

    Examples
    --------
    - Example #1: Convert the vector from spherical to cartesian components

        >>> Bx, By, Bz = cartesian_vector(var = 'B')

    - Example #2: Convert the vector from polar to cartesian components

        >>> Bx, By = cartesian_vector(var1 = D.Bx1, var2 = D.Bx2)

    """
    vars = {
        "B": ["Bx1", "Bx2", "Bx3"],
        "E": ["Ex1", "Ex2", "Ex3"],
        "v": ["vx1", "vx2", "vx3"],
    }

    if var is not None:
        var_0 = [
            self.check_var(v, kwargs.get("transpose", False)) for v in vars[var]
        ]
    elif "var1" in kwargs and "var2" in kwargs:
        var_0 = [
            self.check_var(kwargs["var1"], kwargs.get("transpose", False)),
            self.check_var(kwargs["var2"], kwargs.get("transpose", False)),
        ]
    else:
        raise ValueError("Either var or var1 and var2 must be specified.")

    if "var3" in kwargs:
        var_0.append(
            self.check_var(kwargs["var3"], kwargs.get("transpose", False))
        )

    # x1 = kwargs.get("x1", self.x1)
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


def reshape_cartesian(self, *args: Any, **kwargs: Any) -> tuple[NDArray, ...]:
    """Function that reshapes a variable from a cylindrical or spherical grid into
    a cartesian grid. Zones not covered by the original domain (e.g. the very
    inner radial regions) are also interpolated.

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
    - transpose: bool, default False
        If True, the variable is transposed.
    - var: np.ndarray
        The variable to convert.
    - x1: int
        The first index of the variable.
    - x2: int
        The second index of the variable.

    Notes
    -----
    - For now only some methods are available
    - The transformation is only in 2D for now

    ----

    Examples
    --------
    - Example #1: Convert the vector from spherical to cartesian components

        >>> Bx, By, Bz = cartesian_vector(var = 'B')

    - Example #2: Convert the vector from polar to cartesian components

        >>> Bx, By = cartesian_vector(var1 = D.Bx1, var2 = D.Bx2)

    """
    # Get the variable, if it is a string, get the variable from the dataset.
    # The .T is used to transpose the variable to the correct shape.
    vars = []
    newv = []
    for i in args:
        vars.append(self._check_var(i, kwargs.get("transpose", False)))

    # Get the grid information
    x1 = kwargs.pop("x1", self.x1)
    x2 = kwargs.pop("x2", self.x2)

    # Get the grid limits
    xx = x1[:, np.newaxis] * np.cos(x2)
    yy = x1[:, np.newaxis] * np.sin(x2)

    xmin, xmax = xx.min(), xx.max()
    ymin, ymax = yy.min(), yy.max()

    del xx, yy

    # Get the number of grid points of the new grid
    nx1 = int(kwargs.get("nx1", len(x1)))
    nx2 = int(kwargs.get("nx2", nx1 * (ymax - ymin) / (xmax - xmin)))
    # nx2 = int(kwargs.get('nx2', nx1*(ymax-ymin)//(xmax-xmin)))

    # Get the cartesian grid

    if self.geom == "SPHERICAL":
        xc0 = np.linspace(xmin, xmax, nx2)
        yc0 = np.linspace(ymin, ymax, nx1)
        xc, yc = np.meshgrid(xc0, yc0, indexing="xy")
    else:
        xc0 = np.linspace(xmin, xmax, nx1)
        yc0 = np.linspace(ymin, ymax, nx2)
        xc, yc = np.meshgrid(xc0, yc0, indexing="ij")

    # Create the new grid
    x1, x2, vars = self.reshape_uniform(x1, x2, *vars, **kwargs)

    # Convert grid
    ww, nn = _convert2cartgrid(xc, yc, x1, x2)

    xcong = self._congrid(xc, (nx1, nx2), method="linear")
    ycong = self._congrid(yc, (nx1, nx2), method="linear")

    for i, var in enumerate(vars):
        newv.append(np.sum([ww[j] * var.flat[nn[j]] for j in range(4)], axis=0))
        newv[i] = self._congrid(newv[i], (nx1, nx2), method="linear")

    if self.geom == "SPHERICAL":
        return ycong[:, 0], xcong[0], *newv
    else:
        return xcong[:, 0], ycong[0], *newv


def reshape_uniform(self, x1, x2, *args, **kwargs):
    """Reshapes a non-uniform (cartesian) grid into a uniform grid.

    Returns
    -------
    tuple: A tuple containing the reshaped x1, x2, varx, and vary.

    Parameters
    ----------
    - nx1: int, default len(x1)
        The number of grid points in the first direction.
    - nx2: int, default len(x2)
        The number of grid points in the second direction.
    - transpose: bool, default False
        If True, the variable is transposed.
    - var: np.ndarray
        The variable to convert.
    - x1: int
        The first index of the variable.
    - x2: int
        The second index of the variable.

    Notes
    -----
    - For now only some methods are available
    - The transformation is only in 2D for now

    ----

    Examples
    --------
    - Example #1: Reshape the grid into a uniform grid

        >>> x1new, x2new, varx = reshape_uniform(x1, x2, var)

    """
    uniform_x = all(np.diff(x1) == np.diff(x1)[0])
    uniform_y = all(np.diff(x2) == np.diff(x2)[0])

    nx1new = kwargs.get("nx1", len(x1))
    nx2new = kwargs.get("nx2", len(x2))

    uniform_x = False if nx1new != len(x1) else uniform_x
    uniform_y = False if nx2new != len(x2) else uniform_y

    newvars = []

    if not uniform_x or not uniform_y:

        x1new = np.linspace(x1.min(), x1.max(), nx1new) if not uniform_x else x1
        x2new = np.linspace(x2.min(), x2.max(), nx2new) if not uniform_y else x2

        for i in args:
            interp = RectBivariateSpline(x2, x1, i.T)
            newvars.append(interp(x2new, x1new))

    else:
        x1new = x1
        x2new = x2
        newvars = [arg for arg in args]

    return x1new, x2new, newvars


def _convert2cartgrid(R, Z, new_r, new_t):
    """Function that converts a grid from spherical to cartesian coordinates.

    Returns
    -------
    - newvar: tuple(np.ndarray)
        The new grid.

    Parameters
    ----------
    - R: np.ndarray
        The radial grid.
    - Z: np.ndarray
        The vertical grid.
    - new_r: np.ndarray
        The new radial grid.
    - new_t: np.ndarray
        The new vertical grid.

    Notes
    -----
    - For now only some methods are available
    - The transformation is only in 2D for now

    ----

    Examples
    --------
    - Example #1: Convert the grid from spherical to cartesian coordinates

        >>> new_r, new_t, newvar = _convert2cartgrid(R, Z, new_r, new_t)

    """
    # Convert Cartesian coordinates (R, Z) to polar (Rs, Th)
    Rs = np.sqrt(R**2 + Z**2)

    Th = np.arctan2(Z, R)
    Th = np.where(Th < 0, Th + 2 * np.pi, Th)  # Ensure Th is in [0, 2pi]

    # Clip Rs and Th to the range of the new grid
    Rs_clipped = np.clip(Rs, new_r[0], new_r[-1])
    Th_clipped = np.clip(Th, new_t[0], new_t[-1])

    # Normalize Rs and Th to the new grid indices
    ra = (len(new_r) - 1) * (Rs_clipped - new_r[0]) / (new_r[-1] - new_r[0])
    tha = (len(new_t) - 1) * (Th_clipped - new_t[0]) / (new_t[-1] - new_t[0])

    # Get the integer and fractional parts of the grid indices
    rn, dra = np.divmod(ra, 1)
    thn, dtha = np.divmod(tha, 1)
    rn, thn = rn.astype(int), thn.astype(int)

    # Ensure indices are within bounds
    rn = np.clip(rn, 0, len(new_r) - 2)
    thn = np.clip(thn, 0, len(new_t) - 2)

    # Bilinear interpolation
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


def _congrid(self, a, newdims, method="linear", center=False, minusone=False):
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

    Notes
    -----
    - For now only some methods are available
    - The transformation is only in 2D for now

    ----

    Examples
    --------
    - Example #1: Resample the grid

        >>> newvar = _congrid(newvar, (10, 10))

    """
    # Based on IDL's congrid routine
    # Ensure input is a floating-point array for interpolation
    a = a.astype(float, copy=False)

    olddims = np.array(a.shape)
    newdims = np.asarray(newdims, dtype=int)

    if olddims.size != newdims.size:
        raise ValueError(
            "Dimension mismatch: newdims must have the same number \
                          of dimensions as the input array."
        )

    m1 = int(minusone)
    ofs = 0.5 if center else 0.0

    # Generate the original grid
    old_grid = [np.arange(n) for n in olddims]

    # Generate the new grid, scaled to match the new dimensions
    new_grid = np.meshgrid(
        *[
            np.linspace(ofs, olddims[i] - 1 - ofs, num=newdims[i])
            for i in range(len(olddims))
        ],
        indexing="ij",
    )

    # Stack the coordinates for RegularGridInterpolator
    new_coords = np.stack(new_grid, axis=-1)

    if method == "spline":
        # Use spline interpolation with map_coordinates
        scale = (olddims - m1) / (newdims - m1)
        coords = np.array(new_grid) * scale[:, None, None]
        return map_coordinates(a, coords, order=3, mode="nearest")

    else:
        # Use RegularGridInterpolator for 'linear' and 'nearest' methods
        interpolator = RegularGridInterpolator(
            old_grid, a, method=method, bounds_error=False, fill_value=None
        )
        return interpolator(new_coords)
