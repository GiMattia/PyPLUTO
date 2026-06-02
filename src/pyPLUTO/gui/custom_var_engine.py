"""Pure custom-variable engine (no Qt dependencies)."""

import contextlib
import os
import re
import tempfile
from typing import Any, cast

import numexpr as ne
import numpy as np

from pyPLUTO.load import Load

# Strip common object-access prefixes so the user can write "D.rho",
# "Data.rho", "np.sqrt", or "numpy.sqrt" interchangeably with bare names.
_NORM_PATTERNS = [
    (re.compile(r"\bD\."), ""),
    (re.compile(r"\bData\."), ""),
    (re.compile(r"\bnp\."), ""),
    (re.compile(r"\bnumpy\."), ""),
]


def normalize_expr(expr: str) -> str:
    """Strip common prefixes from a user-supplied expression string.

    Transforms prefixed attribute access (D.rho, Data.rho) and NumPy
    namespace references (np.sqrt, numpy.sqrt) into bare identifiers so
    that numexpr can handle them directly.

    Parameters
    ----------
    - expr: str
        Raw expression string entered by the user.

    Returns
    -------
    - str

    """
    s = expr.strip()
    for pat, repl in _NORM_PATTERNS:
        s = pat.sub(repl, s)
    return s


def frozen_var_names(Data: Load) -> set[str]:
    """Return the set of variable names that must not be redefined.

    The frozen set includes:

    - Every variable originally loaded from disk (from Data.state.d_vars).
    - The canonical grid coordinates x1, x2, x3.
    - Geometry-specific coordinate aliases: x, y, z for Cartesian;
      R, phi, z, x, y, xr, yr for Polar; r, theta, phi, R, z, rt, zt
      for Spherical.

    Parameters
    ----------
    - Data: Load
        Active Load object whose geometry and loaded variables determine the
        protected set.

    Returns
    -------
    - set[str]

    """
    names = set(map(str, getattr(Data.state, "d_vars", [])))
    names.update({"x1", "x2", "x3"})
    g = (getattr(Data.state, "geom", "") or "").upper()
    if g == "CARTESIAN":
        names.update({"x", "y", "z"})
    elif g == "POLAR":
        names.update({"R", "phi", "z", "x", "y", "xr", "yr"})
    elif g == "SPHERICAL":
        names.update({"r", "theta", "phi", "R", "z", "rt", "zt"})
    return names


def build_locals(Data: Load) -> dict[str, float | np.ndarray]:
    """Build the variable namespace used when evaluating user expressions.

    The namespace is populated in four passes:

    1. Mathematical constants pi and e.
    2. All public, non-callable attributes of Data (from __dict__), making
       fluid variables such as rho, vx1, bx2, etc. directly available.
    3. All public, non-callable attributes of Data.state, exposing grid
       metadata (geom, nshp, nx1, ...) by their short names.
    4. Explicit grid coordinates x1/x2/x3, cell spacings dx1/dx2/dx3, and
       cell counts nx1/nx2/nx3, fetched via getattr so they are present even
       when the grid mixin exposes them only as properties.

    Parameters
    ----------
    - Data: Load
        Active Load object providing the variable namespace.

    Returns
    -------
    - dict[str, float | np.ndarray]

    """
    local: dict[str, float | np.ndarray] = {
        "pi": float(np.pi),
        "e": float(np.e),
    }

    # Populate from Data's own instance dictionary.
    for k, v in Data.__dict__.items():
        if not k.startswith("_") and not callable(v):
            local[k] = v

    # Merge the state sub-object when present (avoids shadowing Data attrs).
    if (state := getattr(Data, "state", None)) is not None:
        for k, v in state.__dict__.items():
            if not k.startswith("_") and not callable(v):
                local[k] = v

    # Ensure grid coordinates are present even when exposed only as properties.
    for k in ("x1", "x2", "x3", "dx1", "dx2", "dx3", "nx1", "nx2", "nx3"):
        if k in local:
            continue
        try:
            v = getattr(Data, k)
        except Exception:
            continue
        if not callable(v):
            local[k] = v
    return local


def apply_grid_shaping(
    local: dict[str, float | np.ndarray], Data: Load
) -> None:
    """Reshape 1-D grid arrays for broadcasting and expose geometry aliases.

    Each x1/x2/x3 axis vector is reshaped into an N-D array whose size is 1
    along every axis except its own so that it broadcasts correctly against
    the full data arrays (e.g. shape (nx1, 1, 1) for the x1 axis in 3-D).

    Geometry-specific coordinate aliases are then added to local:

    - Cartesian: x = x1, y = x2, z = x3.
    - Polar: R = x1, phi = x2, z = x3; x and y from the 2-D/3-D
      Cartesian projections stored in Data.x1c and Data.x2c.
    - Spherical: r = x1, theta = x2, phi = x3; R and z from the
      poloidal-plane projections in Data.x1p and Data.x2p; rt and zt
      from the azimuthal projections Data.x1t and Data.x3t (3-D only).

    Parameters
    ----------
    - local: dict[str, float | np.ndarray]
        Evaluation namespace built by build_locals. Modified in place.
    - Data: Load
        Active Load object supplying geometry and projection arrays.

    Returns
    -------
    - None

    """
    nshp = (
        Data.state.nshp
        if isinstance(Data.state.nshp, tuple)
        else (Data.state.nshp,)
    )
    threed = 3  # named constant so the dim == 3 comparisons below read clearly

    # Reshape each axis vector to (1, ..., N_axis, ..., 1) for broadcasting.
    for axis, name in enumerate(("x1", "x2", "x3")[: Data.state.dim]):
        v = local.get(name)
        if (
            isinstance(v, np.ndarray)
            and v.ndim == 1
            and v.shape[0] == nshp[axis]
        ):
            try:
                pattern = [1] * Data.state.dim
                pattern[axis] = v.shape[0]
                local[name] = np.broadcast_to(
                    cast(np.ndarray, v).reshape(pattern), nshp
                )
            except Exception:
                pass  # leave the original 1-D array if reshape fails

    # Expose coordinate aliases for each supported geometry.
    if Data.geom == "CARTESIAN":
        local["x"], local["y"], local["z"] = (
            local["x1"],
            local["x2"],
            local["x3"],
        )
    elif Data.geom == "POLAR":
        local["R"], local["phi"], local["z"] = (
            local["x1"],
            local["x2"],
            local["x3"],
        )

        # x1c/x2c hold the Cartesian projections of the polar mesh.
        local["x"] = (
            Data.x1c.T[:, :, None] if Data.dim == threed else Data.x1c.T
        )
        local["y"] = (
            Data.x2c.T[:, :, None] if Data.dim == threed else Data.x2c.T
        )
    elif Data.geom == "SPHERICAL":
        local["r"], local["theta"], local["phi"] = (
            local["x1"],
            local["x2"],
            local["x3"],
        )
        local["R"] = (
            Data.x1p.T[:, :, None] if Data.dim == threed else Data.x1p.T
        )
        local["z"] = (
            Data.x2p.T[:, :, None] if Data.dim == threed else Data.x2p.T
        )
        if Data.dim == threed:
            local["rt"] = Data.x1t.T[:, None, :]
            local["zt"] = Data.x3t.T[:, None, :]


def _evaluate_array_expr(
    expr: str,
    local: dict[str, Any],
    name: str,
    arrs: list[np.ndarray],
    out_dtype: np.dtype,
) -> np.ndarray:
    """Evaluate expr into a memory-mapped temporary file.

    Broadcasts the shapes of all array operands to compute the output shape,
    then writes the result directly into a .dat memmap file so the output
    array is never held in RAM alongside the input arrays.
    The temporary file is removed on failure to avoid leaking disk space.

    Parameters
    ----------
    - expr: str
        Normalised expression string ready for numexpr.
    - local: dict[str, Any]
        Full evaluation namespace (arrays + scalars).
    - name: str
        Used as the prefix of the temporary file name for easier debugging.
    - arrs: list[np.ndarray]
        Array operands extracted from local; used to compute out_shape.
    - out_dtype: np.dtype
        Dtype of the output array, inferred from a prior tiny evaluation.

    Returns
    -------
    - np.ndarray

    """
    out_shape = np.broadcast(*[np.empty(a.shape, dtype=[]) for a in arrs]).shape

    with tempfile.NamedTemporaryFile(
        prefix=f"{name}_", suffix=".dat", delete=False
    ) as tmp:
        tmp_path = tmp.name

    try:
        out = np.memmap(tmp_path, mode="w+", dtype=out_dtype, shape=out_shape)
        ne.evaluate(expr, local_dict=local, global_dict={}, out=out)
    except Exception as err:
        with contextlib.suppress(OSError):
            os.remove(tmp_path)
        raise ValueError(f"evaluate error: {err}") from err

    return out


def evaluate_custom_var(
    Data: Load, name: str, expr: str, *, assign: bool = True
) -> np.ndarray | int | float:
    """Evaluate a user-defined expression and optionally store the result.

    Three-step process:

    1. Compile via numexpr.NumExpr to catch syntax errors before touching data.
    2. Validate on 1-element array slices to detect unknown names and type
       mismatches cheaply, regardless of dataset size.
    3. Evaluate in full: scalar results are unwrapped to Python scalars; array
       results are written to a memory-mapped file to avoid doubling RAM usage.

    Parameters
    ----------
    - Data: Load
        Supplies the variable namespace; receives the result when assign
        is True.
    - name: str
        Attribute name under which the result is stored on Data. Must not
        collide with any protected name returned by frozen_var_names.
    - expr: str
        Expression string. Prefixes D., Data., np., numpy. are stripped
        automatically before compilation.
    - assign: bool, default True
        When True, calls setattr(Data, name, result) so subsequent expressions
        and the GUI var selector can reference the new variable.

    Returns
    -------
    - np.ndarray | int | float

    Raises
    ------
    - ValueError
        If name is protected, the expression fails to compile, an unknown
        variable is referenced, or evaluation raises an error.

    """
    expr = normalize_expr(expr)
    if name in frozen_var_names(Data):
        raise ValueError(f"protected name: {name}")

    local = build_locals(Data)
    apply_grid_shaping(local, Data)

    try:
        compiled = ne.NumExpr(expr)
    except Exception as err:
        raise ValueError(f"compile error: {err}") from err

    # Build tiny namespace: 1-element slices for arrays, scalars unchanged.
    names: list[str] = compiled.input_names
    tiny: dict[str, Any] = {}
    for n in names:
        v = local.get(n)
        if v is None:
            raise ValueError(f"unknown name: {n}")
        if isinstance(v, np.ndarray):
            arr: np.ndarray = v
            tiny[n] = arr.reshape(-1)[:1]
        else:
            tiny[n] = v

    try:
        tiny_res: np.ndarray = ne.evaluate(
            expr, local_dict=tiny, global_dict={}
        )
    except Exception as err:
        raise ValueError(f"validation error: {err}") from err

    # Collect the array operands to decide between scalar and array paths.
    arrs: list[np.ndarray] = [
        a for n in names if isinstance(a := local[n], np.ndarray)
    ]

    if not arrs:
        # Scalar expression: evaluate directly and unwrap 0-D arrays.
        try:
            res: np.ndarray = ne.evaluate(
                expr, local_dict=local, global_dict={}
            )
        except Exception as err:
            raise ValueError(f"evaluate error: {err}") from err
        scalar_result: np.ndarray | int | float = (
            res.item() if res.shape == () else res
        )
        if assign:
            setattr(Data, name, scalar_result)
        return scalar_result

    # Infer dtype from the tiny result; fall back to the first array's dtype.
    out_dtype: np.dtype = (
        tiny_res.dtype if isinstance(tiny_res, np.ndarray) else arrs[0].dtype
    )
    # Array expression: write into a memmap to avoid doubling RAM usage.
    array_result = _evaluate_array_expr(expr, local, name, arrs, out_dtype)
    if assign:
        setattr(Data, name, array_result)
    return array_result


def validate_lines_sequential(Data: Load, pairs: list[tuple[str, str]]) -> None:
    """Validate a sequence of name = expr pairs in declaration order.

    Builds a tiny namespace where every array is collapsed to a 1-element
    slice, then evaluates each expression in sequence. Grid shaping is not
    applied here (unlike evaluate_custom_var) because spatial broadcasting
    is not required for cheap type and name checking.

    Definitions are accumulated sequentially: a variable defined in an
    earlier pair is available to all subsequent expressions in the same batch.

    Parameters
    ----------
    - Data: Load
        Active Load object supplying the base variable namespace.
    - pairs: list[tuple[str, str]]
        Ordered list of (name, expression) pairs to validate.

    Returns
    -------
    - None

    Raises
    ------
    - ValueError
        If any expression references an unknown variable, targets a protected
        name, or produces an error on the tiny namespace.

    """
    base = build_locals(Data)
    # Collapse every array to a 1-element view; keep scalars as-is.
    tiny: dict[str, Any] = {}
    for k, v in base.items():
        if isinstance(v, np.ndarray):
            arr: np.ndarray = v
            tiny[k] = arr.reshape(-1)[:1]
        else:
            tiny[k] = v
    # Re-add constants explicitly in case they were shadowed by a Data attr.
    tiny["pi"], tiny["e"] = float(np.pi), float(np.e)
    for name, expr in pairs:
        s = normalize_expr(expr)
        compiled = ne.NumExpr(s)
        names = compiled.input_names
        # Build a minimal env from the accumulated tiny namespace.
        env: dict[str, Any] = {}
        for n in names:
            if n not in tiny:
                raise ValueError(f"unknown name: {n}")
            env[n] = tiny[n]
        if name in frozen_var_names(Data):
            raise ValueError(f"'{name}' is protected and cannot be redefined")
        try:
            res = ne.evaluate(s, local_dict=env, global_dict={})
        except Exception as err:
            raise ValueError(f"error in '{name} = {expr}': {err}") from err
        # Accumulate the result so later expressions in the batch can use it.
        tiny[name] = res
