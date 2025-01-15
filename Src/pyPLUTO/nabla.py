from .libraries import *


def _is_number(value: Any) -> bool:
    """
    Checks if value is a number.

    Returns
    -------

    - bool
        True if value is a number, False otherwise.

    Parameters
    ----------

    - value (not optional): Any
        The value to check.

    Notes
    -----

    - Probably this function will be moved elsewhere

    ----

    Examples
    ========

    - Example #1: Check if 1 is a number

        >>> _is_number(1)
        True

    - Example #2: Check if '1' is a number

        >>> _is_number('1')
        False

    """

    return isinstance(value, (int, float))


def _islice_imin_imax(xvalue, xgrid) -> list[int]:
    """
    Returns i, imin, imax for xgrid such that xgrid[i] <= xvalue <= xgrid[i+1]
    with a stencil of 3 cells. If the grid is too small, imin and imax are
    set to 0 and N, respectively.

    Returns
    -------

    - i: int
        The central index of the stencil, counting from the minimum.
    - imin: int
        The minimum index of the stencil.
    - imax: int
        The maximum index of the stencil.

    Parameters
    ----------

    - xvalue (not optional): float
        The value to check.
    - xgrid (not optional): numpy.ndarray
        The grid to check.

    Notes
    -----

    - None

    ----

    Examples
    ========

    - Example # 1: Compute the indices for the stencil of 3 cells

        >>> _islice_imin_imax(0.5, np.linspace(0,1,11))

    """

    # Compute the grid length and the index of the closest grid point
    N = len(xgrid)
    i = np.argmin(abs(xgrid - xvalue))

    # Compute the limits of the stencil
    i_min = max(0, i - 1)
    i_max = min(N, i + 2)

    # If the grid is too small, set imin and imax to 0 and N
    if N < 3:
        i_min, i_max = 0, N

    # If imin or imax are outside the grid, set them to 0 and/or N
    else:
        i_min = N - 3 if i_max == N else i_min
        i_max = 3 if i_min == 0 else i_max

    # Return i, imin, imax
    return i - i_min, i_min, i_max


def _get_slice_indices(slice_val, grid, grid_size):
    """
    Function to get the slice indices from the slice value.

    Returns
    -------

    - idx (not optional): int
        The index of the slice.
    - idx_min (not optional): int
        The minimum index of the slice.
    - idx_max (not optional): int
        The maximum index of the slice.

    Parameters
    ----------

    - slice_val: float
        The value of the slice.
    - grid: np.ndarray
        The grid of the data.
    - grid_size: int
        The size of the grid.

    Notes
    -----

    - None

    ----

    Examples
    ========

    - Example # 1: Get the slice indices

        >>> _get_slice_indices(0.5, np.linspace(0,1,11), 11)

    """

    # If the slice value is a number return the index and the slice
    if _is_number(slice_val):
        # Get the slice indices
        idx, idx_min, idx_max = _islice_imin_imax(slice_val, grid)

        # Return the indices and the slice
        return idx, slice(idx_min, idx_max)

    # If the slice value is a list return the indices and the slice
    else:

        # Return the indices and the slice
        return slice(0, grid_size), slice(0, grid_size)


def _warning_cylindrical():
    warning_message = """"""
    # CYLINDRICAL geometry has been deprecated since PLUTO v4.4.
    # POLAR may be used instead by excluding the phi-direction
    # (simply set INCLUDE_JDIR to NO in definitions.h).
    # """
    warnings.warn(warning_message, DeprecationWarning, stacklevel=3)


def gradient(
    self,
    var: np.ndarray,
    x1slice: float | int | None = None,
    x2slice: float | int | None = None,
    x3slice: float | int | None = None,
    edge_order: int = 2,
) -> np.ndarray:
    """
    Computes the gradient of a specified field 'var' in all available directions
    using second-order accurate central differences via the NumPy gradient()
    function. The first index of the resulting array represents the N gradient
    components. If 'x1slice', 'x2slice', or 'x3slice' are specified, the
    gradient is only computed at the corresponding x1, x2, or x3 values. N
    corresponds to the number of employed dimensions unless a slice is taken.

    Returns
    -------

    - np.ndarray
        Gradient of the input field 'var'. The shape of the array depends on the
        number of used spatial dimensions. E.g.:
        3D: (3, self.nx1, self.nx2, self.nx3)
        3D, INCLUDE_JDIR == NO: (2, self.nx1, self.nx3)
        3D, x2slice = constant: (3, self.nx1, self.nx3)

    Parameters
    ----------

    - edge_order: int | None, default 2
        The order of accuracy of derivatives at the domain boundaries.
    - var (not optional): np.ndarray
        The field whose gradient is calculated (e.g., 'rho', 'vx1'). Must have
        the same shape as self.rho.
    - x1slice: float | None, default None
        If not None, specifies the constant value for the x1 axis.
    - x2slice: float | None, default None
        If not None, specifies the constant value for the x2 axis.
    - x3slice: float | None, default None
        If not None, specifies the constant value for the x3 axis.

    Notes
    -----

    - A more efficient implementation based on the axes will be added in the
      future.

    ----

    Examples
    ========

    - Example # 1: Compute the gradient of the density field

        >>> import pyPLUTO as pp
        >>> D = pp.Load(0)
        >>> D.gradient(D.rho)

    """

    # If the geometry is not defined raise an error
    if self.geom == "UNKNOWN":
        raise ValueError("Unknown geometry nabla cannot be computed!")

    # if self.geom == 'CYLINDRICAL':
    #    _warning_cylindrical()

    # Unpack the slice values and grids into tuples
    slices = [
        (x1slice, self.x1, self.nx1),
        (x2slice, self.x2, self.nx2),
        (x3slice, self.x3, self.nx3),
    ]

    # Process each slice and store the results
    indices, ranges = zip(*[_get_slice_indices(s, g, size) for s, g, size in slices])

    # Unpack the results back into individual variables
    i, j, k = indices
    irange, jrange, krange = ranges

    if self.dim == 1:
        grad = np.gradient(var[irange], self.x1[irange], edge_order=edge_order)
        return np.asarray(grad)[i]

    elif self.dim == 2:
        grad = np.gradient(
            var[irange, jrange],
            self.x1[irange],
            self.x2[jrange],
            edge_order=edge_order,
        )

        if self.geom in ["SPHERICAL", "POLAR"]:
            rr, _ = np.meshgrid(self.x1[irange], self.x2[jrange], indexing="ij")
            grad[1] /= rr

        return np.asarray(grad)[:, i, j]

    elif self.dim == 3:
        if self.nx2 == 1:
            grad = np.gradient(
                var[irange, 0, krange],
                self.x1[irange],
                self.x3[krange],
                edge_order=edge_order,
            )

            if self.geom == "SPHERICAL":
                rr, _ = np.meshgrid(self.x1[irange], self.x3[krange], indexing="ij")
                grad[1] /= rr * np.sin(self.x2[0])

            return np.asarray(grad)[:, i, k]

        else:
            grad = np.gradient(
                var[irange, jrange, krange],
                self.x1[irange],
                self.x2[jrange],
                self.x3[krange],
                edge_order=edge_order,
            )

            if self.geom != "CARTESIAN":
                xx1, xx2, _ = np.meshgrid(
                    self.x1[irange],
                    self.x2[jrange],
                    self.x3[krange],
                    indexing="ij",
                )
                grad[1] /= xx1
                if self.geom == "SPHERICAL":
                    grad[2] /= xx1 * np.sin(xx2)

            return np.asarray(grad)[:, i, j, k]


def divergence(
    self,
    v1: np.ndarray | None = None,
    v2: np.ndarray | None = None,
    v3: np.ndarray | None = None,
    x1slice: float | int | None = None,
    x2slice: float | int | None = None,
    x3slice: float | int | None = None,
    edge_order: int = 2,
) -> np.ndarray:
    """
    Calculates the divergence of a vector field specified by its components v1,
    v2, and v3 using second-order accurate central differences via the NumPy
    gradient() function.
    If 'x1slice', 'x2slice', or 'x3slice' are specified, the divergence is only
    computed at the corresponding x1, x2, or x3 values.

    Returns
    -------

    - np.ndarray
        Array corresponding to the divergence of the input vector field. In 3D,
        e.g., its shape is (self.nx1, self.nx2, self.nx3), while if
        INCLUDE_JDIR == NO (or if x2slice = constant), its shape is
        (self.nx1, self.nx3).

    Parameters
    ----------

    - edge_order: int, default 2
        The order of accuracy of derivatives at the domain boundaries.
    - v1: np.ndarray | None
        Field corresponding to the x1 vector component. Must have the same shape
        as self.rho. Can only be None is a given direction is not used.
    - v2: np.ndarray | None
        Field corresponding to the x2 vector component. Must have the same shape
        as self.rho. Can only be None is a given direction is not used.
    - v3: np.ndarray | None
        Field corresponding to the x3 vector component. Must have the same shape
        as self.rho. Can only be None is a given direction is not used.
    - x1slice: float | None
        If not None, specifies the constant value for the x1 axis.
    - x2slice: float | None
        If not None, specifies the constant value for the x2 axis.
    - x3slice: float | None
        If not None, specifies the constant value for the x3 axis.

    Notes
    -----

    - A more efficient implementation based on the axes will be added in the
      future.

    ----

    Examples
    ========

    - Example #1: Calculate the divergence of a vector field

        >>> import pyPLUTO as pp
        >>> D = pp.Load()
        >>> D.divergence(D.vx1, D.vx2, D.vx3)

    """

    if self.geom == "CYLINDRICAL":
        _warning_cylindrical()

    if _is_number(x1slice):
        i, imin, imax = _islice_imin_imax(x1slice, self.x1)
        irange = slice(imin, imax)
    else:
        i = slice(0, self.nx1)
        irange = i

    if _is_number(x2slice):
        j, jmin, jmax = _islice_imin_imax(x2slice, self.x2)
        jrange = slice(jmin, jmax)
    else:
        j = slice(0, self.nx2)
        jrange = j

    if _is_number(x3slice):
        k, kmin, kmax = _islice_imin_imax(x3slice, self.x3)
        krange = slice(kmin, kmax)
    else:
        k = slice(0, self.nx3)
        krange = k

    if self.dim == 1:
        var1 = np.copy(v1[irange])

        rr = self.x1[irange]

        if self.geom in ["POLAR", "CYLINDRICAL"]:
            var1 *= rr
        elif self.geom == "SPHERICAL":
            var1 *= rr**2

        div1 = np.gradient(var1, rr, edge_order=edge_order)

        if self.geom in ["POLAR", "CYLINDRICAL"]:
            div1 /= rr
        elif self.geom == "SPHERICAL":
            div1 /= rr**2

        return div1[i]

    elif self.dim == 2:
        var1 = np.copy(v1[irange, jrange])
        var2 = np.copy(v2[irange, jrange])

        if self.geom != "CARTESIAN":
            rr, tt = np.meshgrid(self.x1[irange], self.x2[jrange], indexing="ij")

            if self.geom in ["POLAR", "CYLINDRICAL"]:
                var1 *= rr
            elif self.geom == "SPHERICAL":
                var1 *= rr**2
                var2 *= np.sin(tt)

        div1 = np.gradient(var1, self.x1[irange], axis=0, edge_order=edge_order)
        div2 = np.gradient(var2, self.x2[jrange], axis=1, edge_order=edge_order)

        if self.geom in ["POLAR", "CYLINDRICAL"]:
            div1 /= rr
            if self.geom == "POLAR":
                div2 /= rr
        elif self.geom == "SPHERICAL":
            div1 /= rr**2
            div2 /= rr * np.sin(tt)

        return div1[i, j] + div2[i, j]

    elif self.dim == 3:

        if self.nx2 == 1:
            var1 = np.copy(v1[irange, 0, krange])
            var3 = np.copy(v3[irange, 0, krange])

            if self.geom != "CARTESIAN":
                rr, _ = np.meshgrid(self.x1[irange], self.x3[krange], indexing="ij")

                if self.geom == "POLAR":
                    var1 *= rr
                elif self.geom == "SPHERICAL":
                    var1 *= rr**2

            div1 = np.gradient(var1, self.x1[irange], axis=0, edge_order=edge_order)
            div3 = np.gradient(var3, self.x3[krange], axis=1, edge_order=edge_order)

            if self.geom == "POLAR":
                div1 /= rr
            elif self.geom == "SPHERICAL":
                div1 /= rr**2
                div3 /= rr * np.sin(self.x2[0])

            return div1[i, k] + div3[i, k]

        else:
            var1 = np.copy(v1[irange, jrange, krange])
            var2 = np.copy(v2[irange, jrange, krange])
            var3 = np.copy(v3[irange, jrange, krange])

            if self.geom != "CARTESIAN":
                rr, tt, _ = np.meshgrid(
                    self.x1[irange],
                    self.x2[jrange],
                    self.x3[krange],
                    indexing="ij",
                )

                if self.geom == "POLAR":
                    var1 *= rr
                elif self.geom == "SPHERICAL":
                    var1 *= rr**2
                    var2 *= np.sin(tt)

            div1 = np.gradient(var1, self.x1[irange], axis=0, edge_order=edge_order)
            div2 = np.gradient(var2, self.x2[jrange], axis=1, edge_order=edge_order)
            div3 = np.gradient(var3, self.x3[krange], axis=2, edge_order=edge_order)

            if self.geom == "POLAR":
                div1 /= rr
                div2 /= rr
            elif self.geom == "SPHERICAL":
                div1 /= rr**2
                div2 /= rr * np.sin(tt)
                div3 /= rr * np.sin(tt)

            return div1[i, j, k] + div2[i, j, k] + div3[i, j, k]


def curl(
    self,
    v1: np.ndarray | None = None,
    v2: np.ndarray | None = None,
    v3: np.ndarray | None = None,
    x1slice: float | int | None = None,
    x2slice: float | int | None = None,
    x3slice: float | int | None = None,
    edge_order: int = 2,
) -> np.ndarray:
    """
    Calculates the curl of a specified vector field (v1, v2, v3) using
    second-order accurate central differences via the NumPy gradient() function.
    Unlike in divergence(), all three vector components must be specified.
    The resulting array has its first index representing the 3 curl components,
    while the remaining indices correspond to the grid location. If 'x1slice',
    'x2slice', or 'x3slice' are specified, the curl is only computed at the
    corresponding x1, x2, or x3 values.

    Returns
    -------

    - np.ndarray
        Curl of the specified vector field (v1, v2, v3). In 3D, e.g., its shape
        is (3, self.nx1, self.nx2, self.nx3), while if INCLUDE_JDIR == NO (or if
        x2slice = constant), its shape is (3, self.nx1, self.nx3).

    Parameters
    ----------

    - edge_order: int, default 2
        The order of accuracy of derivatives at the domain boundaries.
    - v1: np.ndarray | None
        Field corresponding to the x1 vector component. Must have the same shape
        as self.rho.
    - v2: np.ndarray | None
        Field corresponding to the x2 vector component. Must have the same shape
        as self.rho.
    - v3: np.ndarray | None
        Field corresponding to the x3 vector component. Must have the same shape
        as self.rho.
    - x1slice: float | None
        If not None, specifies the constant value for the x1 axis.
    - x2slice: float | None
        If not None, specifies the constant value for the x2 axis.
    - x3slice: float | None
        If not None, specifies the constant value for the x3 axis.

    Notes
    -----

    - A more efficient implementation based on the axes will be added in the
      future.

    ----

    Examples
    ========

    - Example #1: Calculate the curl of a vector field

        >>> import pyPLUTO as pp
        >>> D = pp.Load()
        >>> D.curl(D.vx1, D.vx2, D.vx3)

    """

    if self.geom == "CYLINDRICAL":
        _warning_cylindrical()

    if _is_number(x1slice):
        i, imin, imax = _islice_imin_imax(x1slice, self.x1)
        irange = slice(imin, imax)
    else:
        i = slice(0, self.nx1)
        irange = i

    if _is_number(x2slice):
        j, jmin, jmax = _islice_imin_imax(x2slice, self.x2)
        jrange = slice(jmin, jmax)
    else:
        j = slice(0, self.nx2)
        jrange = j

    if _is_number(x3slice):
        k, kmin, kmax = _islice_imin_imax(x3slice, self.x3)
        krange = slice(kmin, kmax)
    else:
        k = slice(0, self.nx3)
        krange = k

    if self.dim == 1:
        raise ValueError("curl() requires DIMENSION >= 2")

    elif self.dim == 2:
        var1 = np.copy(v1[irange, jrange])
        var2 = np.copy(v2[irange, jrange])
        var3 = np.copy(v3[irange, jrange])

        if self.geom != "CARTESIAN":
            rr, tt = np.meshgrid(self.x1[irange], self.x2[jrange], indexing="ij")

            if self.geom == "POLAR":
                var2 *= rr
            elif self.geom in "CYLINDRICAL":
                var3 *= rr
            elif self.geom == "SPHERICAL":
                var2 *= rr
                var3 *= rr * np.sin(tt)

        dv1_dx2 = np.gradient(var1, self.x2, axis=1, edge_order=edge_order)
        dv2_dx1 = np.gradient(var2, self.x1, axis=0, edge_order=edge_order)
        dv3_dx1, dv3_dx2 = np.gradient(var3, self.x1, self.x2, edge_order=edge_order)

        curl1 = dv3_dx2
        curl2 = -dv3_dx1
        curl3 = dv2_dx1 - dv1_dx2
        if self.geom == "CYLINDRICAL":
            curl1 *= -1
            curl2 *= -1
            curl3 *= -1

        if self.geom == "POLAR":
            curl1 /= rr
            curl3 /= rr
        elif self.geom == "CYLINDRICAL":
            curl1 /= rr
            curl2 /= rr
        elif self.geom == "SPHERICAL":
            curl1 /= rr**2 * np.sin(tt)
            curl2 /= rr * np.sin(tt)
            curl3 /= rr

        return np.asarray([curl1[i, j], curl2[i, j], curl3[i, j]])

    elif self.dim == 3:

        if self.nx2 == 1:
            var1 = np.copy(v1[irange, 0, krange])
            var2 = np.copy(v2[irange, 0, krange])
            var3 = np.copy(v3[irange, 0, krange])

            if self.geom != "CARTESIAN":
                rr, _ = np.meshgrid(self.x1[irange], self.x3[krange], indexing="ij")

                if self.geom == "POLAR":
                    var2 *= rr
                elif self.geom == "SPHERICAL":
                    var2 *= rr
                    var3 *= rr * np.sin(self.x2[0])

            dv1_dx3 = np.gradient(var1, self.x3, axis=1, edge_order=edge_order)
            dv2_dx1, dv2_dx3 = np.gradient(
                var2, self.x1, self.x3, edge_order=edge_order
            )
            dv3_dx1 = np.gradient(var3, self.x1, axis=0, edge_order=edge_order)

            curl1 = -dv2_dx3
            curl2 = dv1_dx3 - dv3_dx1
            curl3 = dv2_dx1

            if self.geom == "POLAR":
                curl1 /= rr
                curl3 /= rr
            elif self.geom == "SPHERICAL":
                curl1 /= rr**2 * np.sin(self.x2[0])
                curl2 /= rr * np.sin(self.x2[0])
                curl3 /= rr

            return np.asarray([curl1[i, k], curl2[i, k], curl3[i, k]])

        else:
            var1 = np.copy(v1[irange, jrange, krange])
            var2 = np.copy(v2[irange, jrange, krange])
            var3 = np.copy(v3[irange, jrange, krange])

            if self.geom != "CARTESIAN":
                rr, tt, _ = np.meshgrid(
                    self.x1[irange],
                    self.x2[jrange],
                    self.x3[krange],
                    indexing="ij",
                )

                if self.geom == "POLAR":
                    var2 *= rr
                elif self.geom == "SPHERICAL":
                    var2 *= rr
                    var3 *= rr * np.sin(tt)

            dv1_dx2, dv1_dx3 = np.gradient(
                var1, self.x2, self.x3, axis=[1, 2], edge_order=edge_order
            )
            dv2_dx1, dv2_dx3 = np.gradient(
                var2, self.x1, self.x3, axis=[0, 2], edge_order=edge_order
            )
            dv3_dx1, dv3_dx2 = np.gradient(
                var3, self.x1, self.x2, axis=[0, 1], edge_order=edge_order
            )

            curl1 = dv3_dx2 - dv2_dx3
            curl2 = dv1_dx3 - dv3_dx1
            curl3 = dv2_dx1 - dv1_dx2

            if self.geom == "POLAR":
                curl1 /= rr
                curl3 /= rr
            elif self.geom == "SPHERICAL":
                curl1 /= rr**2 * np.sin(tt)
                curl2 /= rr * np.sin(tt)
                curl3 /= rr

            return np.asarray([curl1[i, j, k], curl2[i, j, k], curl3[i, j, k]])
