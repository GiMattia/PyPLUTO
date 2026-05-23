"""Pure custom-variable engine (no Qt dependencies)."""

from __future__ import annotations

import os
import re
import tempfile
from typing import Any

import numexpr as ne
import numpy as np

_NORM_PATTERNS = [
    (re.compile(r"\bD\."), ""),
    (re.compile(r"\bData\."), ""),
    (re.compile(r"\bnp\."), ""),
    (re.compile(r"\bnumpy\."), ""),
]


def normalize_expr(expr: str) -> str:
    """Normalize expression syntax for evaluation."""
    s = expr.strip()
    for pat, repl in _NORM_PATTERNS:
        s = pat.sub(repl, s)
    return s


def frozen_var_names(Data: Any) -> set[str]:
    """Names that must never be overridden by custom vars."""
    names = set(map(str, getattr(Data, "_load_vars", [])))
    names.update({"x1", "x2", "x3"})
    g = (getattr(Data, "geom", "") or "").upper()
    if g == "CARTESIAN":
        names.update({"x", "y", "z"})
    elif g == "POLAR":
        names.update({"R", "phi", "z", "x", "y", "xr", "yr"})
    elif g == "SPHERICAL":
        names.update({"r", "theta", "phi", "R", "z", "rt", "zt"})
    return names


def build_locals(Data: Any) -> dict[str, Any]:
    """Build local evaluation namespace from load object and state."""
    local: dict[str, Any] = {"pi": float(np.pi), "e": float(np.e)}
    for k, v in Data.__dict__.items():
        if not k.startswith("_") and not callable(v):
            local[k] = v
    if (state := getattr(Data, "state", None)) is not None:
        for k, v in state.__dict__.items():
            if not k.startswith("_") and not callable(v):
                local[k] = v
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


def apply_grid_shaping(local: dict[str, Any], Data: Any) -> None:
    """Reshape x1/x2/x3 for broadcasting with Data.nshp and expose geom aliases."""
    nshp = Data.nshp if isinstance(Data.nshp, tuple) else tuple(Data.nshp)
    for axis, name in enumerate(("x1", "x2", "x3")[: Data.dim]):
        v = local.get(name)
        if (
            isinstance(v, np.ndarray)
            and v.ndim == 1
            and v.shape[0] == nshp[axis]
        ):
            try:
                pattern = [1] * Data.dim
                pattern[axis] = v.shape[0]
                local[name] = np.broadcast_to(v.reshape(tuple(pattern)), nshp)
            except Exception:
                pass

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
        local["x"] = Data.x1c.T[:, :, None] if Data.dim == 3 else Data.x1c.T
        local["y"] = Data.x2c.T[:, :, None] if Data.dim == 3 else Data.x2c.T
    elif Data.geom == "SPHERICAL":
        local["r"], local["theta"], local["phi"] = (
            local["x1"],
            local["x2"],
            local["x3"],
        )
        local["R"] = Data.x1p.T[:, :, None] if Data.dim == 3 else Data.x1p.T
        local["z"] = Data.x2p.T[:, :, None] if Data.dim == 3 else Data.x2p.T
        if Data.dim == 3:
            local["rt"] = Data.x1t.T[:, None, :]
            local["zt"] = Data.x3t.T[:, None, :]


def evaluate_custom_var(
    Data: Any, name: str, expr: str, *, assign: bool = True
):
    """Evaluate and optionally assign a custom variable."""
    expr = normalize_expr(expr)
    if name in frozen_var_names(Data):
        raise ValueError(f"protected name: {name}")

    local = build_locals(Data)
    apply_grid_shaping(local, Data)

    try:
        compiled = ne.NumExpr(expr)
    except Exception as e:
        raise ValueError(f"compile error: {e}")

    names = compiled.input_names
    tiny: dict[str, Any] = {}
    for n in names:
        v = local.get(n)
        if v is None:
            raise ValueError(f"unknown name: {n}")
        tiny[n] = v.reshape(-1)[:1] if isinstance(v, np.ndarray) else v
    try:
        tiny_res = ne.evaluate(expr, local_dict=tiny, global_dict={})
    except Exception as e:
        raise ValueError(f"validation error: {e}")

    arrs = [local[n] for n in names if isinstance(local[n], np.ndarray)]
    if not arrs:
        try:
            res = ne.evaluate(expr, local_dict=local, global_dict={})
        except Exception as e:
            raise ValueError(f"evaluate error: {e}")
        if isinstance(res, np.ndarray) and res.shape == ():
            res = res.item()
    else:
        out_shape = np.broadcast(
            *[np.empty(a.shape, dtype=[]) for a in arrs]
        ).shape
        out_dtype = getattr(tiny_res, "dtype", arrs[0].dtype)
        tmp = tempfile.NamedTemporaryFile(
            prefix=f"{name}_", suffix=".dat", delete=False
        )
        tmp_path = tmp.name
        tmp.close()
        try:
            out = np.memmap(
                tmp_path, mode="w+", dtype=out_dtype, shape=out_shape
            )
            ne.evaluate(expr, local_dict=local, global_dict={}, out=out)
            res = out
        except Exception as e:
            try:
                if "out" in locals():
                    del out
                if os.path.exists(tmp_path):
                    os.remove(tmp_path)
            except Exception:
                pass
            raise ValueError(f"evaluate error: {e}")

    if assign:
        setattr(Data, name, res)
    return res


def validate_lines_sequential(Data: Any, pairs: list[tuple[str, str]]) -> None:
    """Cheap sequential validation using 1-element array views."""
    base = build_locals(Data)
    apply_grid_shaping(base, Data)
    tiny = {
        k: (v.reshape(-1)[:1] if isinstance(v, np.ndarray) else v)
        for k, v in base.items()
    }
    tiny["pi"], tiny["e"] = float(np.pi), float(np.e)
    for name, expr in pairs:
        s = normalize_expr(expr)
        compiled = ne.NumExpr(s)
        names = compiled.input_names
        env: dict[str, Any] = {}
        for n in names:
            if n not in tiny:
                raise ValueError(f"unknown name: {n}")
            env[n] = tiny[n]
        if name in frozen_var_names(Data):
            raise ValueError(f"'{name}' is protected and cannot be redefined")
        try:
            res = ne.evaluate(s, local_dict=env, global_dict={})
        except Exception as e:
            raise ValueError(f"error in '{name} = {expr}': {e}")
        tiny[name] = res
