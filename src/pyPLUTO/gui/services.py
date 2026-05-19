"""Pure (non-Qt) service helpers for the GUI layer."""

from __future__ import annotations

import os
import re
from typing import Any

import numpy as np


def parse_vars_text(text: str) -> bool | list[str]:
    """Parse GUI vars text into Load-compatible value."""
    if not text:
        return True
    vars_text = text.replace(" ", "").replace("-", ",")
    return vars_text.split(",")


def grid_shape_candidates(raw_nshp: Any) -> set[tuple[int, ...]]:
    """Build candidate grid-shape tuples (including reversed layout)."""
    if isinstance(raw_nshp, tuple):
        grid_shape = raw_nshp
    elif isinstance(raw_nshp, int):
        grid_shape = (raw_nshp,)
    else:
        try:
            grid_shape = tuple(raw_nshp)
        except TypeError:
            grid_shape = ()

    candidates = {grid_shape}
    if len(grid_shape) > 1:
        candidates.add(tuple(reversed(grid_shape)))
    return candidates


def filtered_loaded_vars(Data: Any) -> list[str]:
    """Return best-effort loaded vars that match full-grid arrays."""
    loaded_vars = getattr(Data, "load_vars", getattr(Data, "_load_vars", []))
    if not loaded_vars:
        loaded_vars = list(getattr(Data, "d_vars", {}).keys())

    candidates = grid_shape_candidates(getattr(Data, "nshp", ()))
    keep = []
    for v in map(str, loaded_vars):
        arr = getattr(Data, v, None)
        if isinstance(arr, np.ndarray) and arr.shape in candidates:
            keep.append(v)

    if keep:
        return keep

    return [
        v
        for v in map(str, loaded_vars)
        if isinstance(getattr(Data, v, None), np.ndarray)
    ]


def axis_labels_for_geom(geom: str) -> tuple[list[str], list[str]]:
    """Get x/y axis labels for the current geometry."""
    if geom == "POLAR":
        return ["R", "phi", "z", "x", "y"], ["phi", "z", "R", "x", "y"]
    if geom == "SPHERICAL":
        return ["r", "theta", "phi", "R", "z", "Rt", "zt"], [
            "theta",
            "phi",
            "r",
            "R",
            "z",
            "Rt",
            "zt",
        ]
    return ["x", "y", "z"], ["y", "z", "x"]


def loaded_step_repr(nout: Any) -> int | list[int]:
    """Normalize nout for GUI/info printing."""
    if isinstance(nout, (int, np.integer)):
        return int(nout)
    arr = np.atleast_1d(nout).astype(int).tolist()
    return arr[0] if len(arr) == 1 else arr


def custom_var_lines(defs: list[Any]) -> list[str]:
    """Render stored custom var tuples to info-box lines."""
    lines = []
    for tup in defs:
        if len(tup) == 3:
            name, _clean, disp = tup
            lines.append(f"{name} = {disp}")
        else:
            name, expr = tup
            lines.append(f"{name} = {expr}")
    return lines


def build_info_text(folder_path: str, Data: Any, defs: list[Any]) -> str:
    """Build multiline info text for GUI."""
    base = (
        f"Loaded folder: {folder_path}\n"
        f"Format file: {getattr(Data, 'datatype', 'Unknown')}\n"
        f"Geometry: {Data.geom}\n"
        f"Domain: {Data.nx1} x {Data.nx2} x {Data.nx3}\n"
        f"Loaded step = {loaded_step_repr(Data.nout)}\n"
        f"Present Time = {Data.ntime}\n"
        f"Variables: {', '.join(getattr(Data, '_load_vars', []))}"
    )
    if not defs:
        return base
    return f"{base}\n\nCustom variables:\n" + "\n".join(custom_var_lines(defs))


def parse_selected_file(file_path: str) -> tuple[str, str | None, int | str]:
    """Infer folder, datatype, and nout from selected file path."""
    folder_path = os.path.dirname(file_path)
    filename = os.path.basename(file_path)
    if filename.endswith(".dbl.h5"):
        datatype = "dbl.h5"
    elif filename.endswith(".flt.h5"):
        datatype = "flt.h5"
    else:
        parts = filename.rsplit(".", maxsplit=1)
        datatype = parts[-1] if len(parts) == 2 else None
    try:
        match = re.search(r"\.(\d+)\.", filename)
        nout = int(match.group(1)) if match else "last"
    except Exception:
        nout = "last"
    return folder_path, datatype, nout


def parse_slice_expr(text: str) -> int | slice | tuple | None:
    """Parse a numpy-like slice expression safely-ish for GUI behavior."""
    try:
        return eval(f"np.s_[{text}]", {"np": np})
    except Exception:
        return int(text) if text.isdigit() else None


def convert_axis_map(geom: str, vardim: int) -> dict[str, str]:
    """Map GUI axis labels to load-object coordinate arrays."""
    if geom == "POLAR":
        base = {"R": "x1", "phi": "x2", "z": "x3", "x": "x1c", "y": "x2c"}
    elif geom == "SPHERICAL":
        base = {
            "r": "x1",
            "theta": "x2",
            "phi": "x3",
            "R": "x1p",
            "z": "x2p",
            "rt": "x1t",
            "zt": "x3t",
        }
    else:
        base = {"x": "x1", "y": "x2", "z": "x3"}
    return {
        key: (val if vardim == 1 else val[:2] + "r" + val[2:])
        for key, val in base.items()
    }


def apply_slices(
    var: np.ndarray, xs: str, ys: str, zs: str
) -> tuple[
    np.ndarray,
    int | slice | tuple | None,
    int | slice | tuple | None,
    int | slice | tuple | None,
]:
    """Apply GUI x/y/z slicing strings to an array."""
    xslice = yslice = zslice = None
    if zs and np.ndim(var) == 3:
        zslice = parse_slice_expr(zs)
        var = var[:, :, zslice]
    if ys and np.ndim(var) > 1:
        yslice = parse_slice_expr(ys)
        var = var[:, yslice]
    if xs:
        xslice = parse_slice_expr(xs)
        var = var[xslice]
    return var, xslice, yslice, zslice
