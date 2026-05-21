"""Particle post-processing helpers for LoadPart."""

from __future__ import annotations

from typing import Any

import numpy as np

from pyPLUTO.baseloadmixin import BaseLoadMixin
from pyPLUTO.baseloadstate import BaseLoadState


class StorePart(BaseLoadMixin):
    """Normalize particle variables after raw loading."""

    def __init__(self, state: BaseLoadState) -> None:
        self.state = state

    def finalize(self) -> None:
        """Apply particle-specific storage and type normalization."""
        if self.state.datatype == "vtk":
            self._store_vtk_particles()
        else:
            self._store_bin_particles()

        self._normalize_id()

    def _store_bin_particles(self) -> None:
        """Split packed ``tot`` particle arrays into named variables."""
        if "tot" not in self.state.d_vars:
            return

        # varskeys is sparse and indexed by output number.
        var_keys_map = self.state.d_info.get("varskeys", [])

        tot_data = self.state.d_vars["tot"]
        out_to_tot_chunks: dict[int, list[np.ndarray]]

        if isinstance(tot_data, dict):
            out_to_tot_chunks = {}
            for out, arr in tot_data.items():
                out_i = int(out)
                if isinstance(arr, list | tuple):
                    out_to_tot_chunks[out_i] = [a for a in arr]
                else:
                    out_to_tot_chunks[out_i] = [arr]
        else:
            # Single-output layout: `nout` may be assigned after finalize().
            if hasattr(self.state, "noutlist"):
                out = int(np.atleast_1d(self.state.noutlist)[0])
            elif hasattr(self.state, "nout"):
                out = int(np.atleast_1d(self.state.nout)[0])
            else:
                raise AttributeError(
                    "Cannot infer output index: neither 'noutlist' nor 'nout' "
                    "is available in state."
                )
            if isinstance(tot_data, list | tuple):
                out_to_tot_chunks = {out: [a for a in tot_data]}
            else:
                out_to_tot_chunks = {out: [tot_data]}

        for out, chunks in out_to_tot_chunks.items():
            if out >= len(var_keys_map):
                continue

            var_keys = list(var_keys_map[out])
            if not var_keys:
                continue

            ncol = 0
            for var in var_keys:
                # Infer number of components from the source offset/shape.
                vshape = self.state.varshape.get(var)
                ncomp = (
                    int(vshape[1])
                    if isinstance(vshape, tuple) and len(vshape) > 1
                    else 1
                )

                slc = ncol if ncomp == 1 else slice(ncol, ncol + ncomp)
                if len(chunks) == 1:
                    # Single chunk: mmap-backed view, zero copy.
                    part = chunks[0][slc]
                else:
                    # Multiple chunks: keep as a list of mmap-backed views.
                    # Concatenation is deferred to first attribute access in
                    # LoadPart.__getattr__ so no file pages are faulted here.
                    part = [chunk[slc] for chunk in chunks]

                if self.state.lennout != 1:
                    if var not in self.state.d_vars or not isinstance(
                        self.state.d_vars[var], dict
                    ):
                        self.state.d_vars[var] = {}
                    self.state.d_vars[var][out] = part
                else:
                    self.state.d_vars[var] = part

                ncol += ncomp

        del self.state.d_vars["tot"]

    def _store_vtk_particles(self) -> None:
        """Rename/split vtk particle arrays into canonical variable names."""
        vardict = {
            "points": ["x1", "x2", "x3"],
            "Velocity": ["vx1", "vx2", "vx3"],
            "Four-Velocity": ["ux1", "ux2", "ux3"],
        }

        for src, dest_names in vardict.items():
            if src not in self.state.d_vars:
                continue

            src_data = self.state.d_vars[src]
            if isinstance(src_data, dict):
                for out, arr in src_data.items():
                    arr_np = np.asarray(arr)
                    for idx, dest in enumerate(dest_names):
                        if dest not in self.state.d_vars or not isinstance(
                            self.state.d_vars[dest], dict
                        ):
                            self.state.d_vars[dest] = {}
                        self.state.d_vars[dest][int(out)] = arr_np[idx]
            else:
                arr_np = np.asarray(src_data)
                for idx, dest in enumerate(dest_names):
                    self.state.d_vars[dest] = arr_np[idx]

            del self.state.d_vars[src]

        if "Identity" in self.state.d_vars:
            self.state.d_vars["id"] = self.state.d_vars.pop("Identity")

    def _normalize_id(self) -> None:
        """Cast particle ids consistently across formats and output modes."""
        if "id" not in self.state.d_vars:
            return

        id_data = self.state.d_vars["id"]

        def _cast(arr: Any) -> np.ndarray:
            arr_np = np.asarray(arr)
            if self.state.datatype == "vtk":
                # VTK stores id as int32 bits inside a float-typed field;
                # view() reinterprets the bytes in-place — zero copy, no fault.
                return arr_np.view(">i4")
            # Binary: id is a float field whose VALUES are integer IDs (1.0,
            # 2.0, …).  astype() would stride through every interleaved row and
            # fault the entire file into RSS at load time.  Return the
            # mmap-backed view as-is; callers can astype(int) on demand.
            return arr_np

        def _is_pending(val: object) -> bool:
            return (
                isinstance(val, list)
                and bool(val)
                and isinstance(val[0], np.ndarray)
            )

        if isinstance(id_data, dict):
            self.state.d_vars["id"] = {
                int(out): arr if _is_pending(arr) else _cast(arr)
                for out, arr in id_data.items()
            }
        elif _is_pending(id_data):
            # Multi-chunk binary: list of mmap views — leave for lazy concat.
            pass
        else:
            self.state.d_vars["id"] = _cast(id_data)
