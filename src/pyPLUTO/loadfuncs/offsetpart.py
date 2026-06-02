"""Docstring for pyPLUTO.loadfuncs.offsetfluid module."""

import mmap
import warnings

import numpy as np

from pyPLUTO.baseloadmixin import BaseLoadMixin
from pyPLUTO.baseloadstate import BaseLoadState


class OffsetPart(BaseLoadMixin):
    """Class that computes the fluid offsets in single_file format."""

    def __init__(self, state: BaseLoadState) -> None:
        """Initialize the particle offset manager with the given load state.

        Parameters
        ----------
        - state: BaseLoadState
            The load state object carrying particle metadata and file information.

        Returns
        -------
        - None

        """
        self.state = state

    def offset_bin(
        self, _i: int, var: str | None, exout: int, mm: mmap.mmap
    ) -> None:
        """Compute the offset and shape of the variables to be loaded.

        The routine, knowing the grid shape, computes the offset and stores the
        shape dependng on wether the variable is staggered or not.

        Parameters
        ----------
        - i (not optional): int
            The index of the file to be loaded.
        - var (not optional): str
            The variable to be loaded.

        Returns
        -------
        - None

        ----

        Examples
        --------
        - Example #1: Load all the variables

            >>> _offset_bin(0, True)

        """
        # Binary particle files have an ASCII header and then one packed
        # payload matrix. We read header metadata to locate the `tot` block
        # and derive per-variable slices from `field_dim`.

        vardim: list[int] = []
        field_names: list[str] = []

        search_pos = 0
        while True:
            line_end = mm.find(b"\n", search_pos)
            if line_end == -1:
                break
            raw_line = mm[search_pos:line_end]
            search_pos = line_end + 1

            parts = raw_line.split()
            if len(parts) < 3:
                continue
            key = parts[1]

            if key == b"endianity":
                # Keep descriptor endian unless user override provided.
                if self.state.endian is not None:
                    self.state.d_info["endianess"][exout] = self.state.endian
                if self.state.d_info["endianess"][exout] is None:
                    raise ValueError(
                        "Error: Wrong endianess in particle binary file."
                    )
                self.state.d_info["binformat"][exout] = (
                    f"{self.state.d_info['endianess'][exout]}f"
                    f"{self.state.charsize}"
                )

            elif key == b"nparticles":
                self.state.nshp = int(parts[2])
                self.state.dim = int(parts[2])

            elif key == b"field_names":
                field_names = [elem.decode() for elem in parts[2:]]
                self.state.d_info["varskeys"][exout] = field_names
                self.state.d_info["varslist"][exout] = ["tot"]

            elif key == b"field_dim":
                vardim = [int(elem.decode()) for elem in parts[2:]]
                total_cols = int(np.sum(vardim))
                self.state.varoffset["tot"] = search_pos
                self.state.varshape["tot"] = (self.state.nshp, total_cols)
                break

        if not field_names or not vardim:
            return

        # Binary particle data are packed row-wise (particle by particle).
        # Only `tot` is contiguous and directly loadable from file.
        # Per-variable offsets would be strided/non-contiguous, so we only keep
        # logical per-variable shapes for the post-processing split step.
        for var_name, ncomp in zip(field_names, vardim, strict=True):
            self.state.varshape[var_name] = (
                self.state.nshp if ncomp == 1 else (self.state.nshp, ncomp)
            )

        # End of function

    def offset_vtk(
        self, i: int, var: str | None, exout: int, mm: mmap.mmap
    ) -> None:
        """Compute the offset and shape of the variables to be loaded.

        The routine, knowing the grid shape, computes the offset and stores the
        shape dependng on wether the variable is staggered or not.

        Parameters
        ----------
        - i (not optional): int
            The index of the file to be loaded.
        - var (not optional): str
            The variable to be loaded.

        Returns
        -------
        - None

        ----

        Examples
        --------
        - Example #1: Load all the variables

            >>> _offset_vtk(0, True)

        """
        self.state.d_info["endianess"][exout] = (
            ">"
            if self.state.endian is None
            else self.state.d_info["endianess"][exout]
        )
        if self.state.d_info["endianess"][exout] is None:
            raise ValueError("Error: Wrong endianess in vtk file.")

        self.state.d_info["binformat"][exout] = (
            f"{self.state.d_info['endianess'][exout]}f{self.state.charsize}"
        )

        # Particle vtk files store point coordinates first. Use this section to
        # infer the particle count and point-data offsets.
        search_pos = 0
        while True:
            points_pos = mm.find(b"POINTS", search_pos)
            if points_pos == -1:
                break
            line_end = mm.find(b"\n", points_pos)
            if line_end == -1:
                break

            line = mm[points_pos:line_end]
            parts = line.split()
            if len(parts) < 2:
                break

            self.state.dim = int(parts[1])
            self.state.nshp = self.state.dim
            self.state.varoffset["points"] = line_end + 1
            self.state.varshape["points"] = (self.state.dim, 3)

            # Move after point payload (3 coordinates for each particle).
            search_pos = line_end + 1 + 3 * self.state.charsize * self.state.dim
            break

        while True:
            scalars_pos = mm.find(b"SCALARS", search_pos)
            if scalars_pos == -1:
                break

            line_end = mm.find(b"\n", scalars_pos)
            if line_end == -1:
                break
            line = mm[scalars_pos:line_end]
            parts = line.split()
            if len(parts) < 2:
                break
            namevar = parts[1].decode()

            lookup_table_pos = mm.find(b"LOOKUP_TABLE default", line_end)
            if lookup_table_pos == -1:
                break
            offset = mm.find(b"\n", lookup_table_pos)
            if offset == -1:
                break
            offset += 1

            self.state.varoffset[namevar] = offset
            self.state.varshape[namevar] = self.state.nshp

            if var is not None and namevar == var:
                break

            search_pos = offset + self.state.dim * self.state.charsize

        while True:
            vectors_pos = mm.find(b"VECTORS", search_pos)
            if vectors_pos == -1:
                break

            line_end = mm.find(b"\n", vectors_pos)
            if line_end == -1:
                break
            line = mm[vectors_pos:line_end]
            parts = line.split()
            if len(parts) < 4:
                warnings.warn(
                    "Warning: malformed VECTORS entry in vtk particle file.",
                    UserWarning,
                    stacklevel=2,
                )
                break
            namevar = parts[1].decode()
            ncomp = int(parts[3])

            self.state.varoffset[namevar] = line_end + 1
            self.state.varshape[namevar] = (self.state.dim, ncomp)

            if var is not None and namevar == var:
                break

            search_pos = (
                line_end + 1 + self.state.dim * ncomp * self.state.charsize
            )

        self.state.d_info["varslist"][exout] = list(self.state.varoffset.keys())
