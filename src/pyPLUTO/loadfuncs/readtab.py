"""Docstring for pyPLUTO.loadfuncs.readtab."""

from __future__ import annotations

import io
import mmap

import numpy as np

from pyPLUTO.loadmixin import LoadMixin
from pyPLUTO.loadstate import LoadState


class ReadtabManager(LoadMixin):
    """Class that manages the reading of tabular data."""

    def __init__(self, state: LoadState) -> None:
        """Initialize the tabular-data reading manager with the given state."""
        self.state = state

    def read_tab(
        self,
        i: int,
        var: str | None,
        exout: int,
        mm: mmap.mmap,
    ) -> None:
        """Read the data.****.tab file and stores the relevant information.

        Such information are the grid variables, the output variables and the
        output time.

        Parameters
        ----------
        - i (not optional): int
            The index of the file to be loaded.
        - exout (not optional): int
            The index of the output file to be loaded.
        - mm (not optional): mmap.mmap
            The memory-mapped file object.
        - var (not optional): str
            The variable to be loaded.

        Returns
        -------
        - None

        Examples
        --------
        - Example #1: Read the data.0000.tab file

            >>> _read_tabfile(0)

        """
        # Read entire mmap in one call
        mm.seek(0)
        raw = mm.read()

        # Normalize line endings so grid detection is consistent across OSes.
        # On Windows checkouts, lines can be CRLF and blank rows are \r\n\r\n.
        raw = raw.replace(b"\r\n", b"\n").replace(b"\r", b"\n")

        # Count empty lines via C-level bytes.count — no Python loop needed.
        # \n\n indicates a blank line between two newlines.
        empty_lines = raw.count(b"\n\n")

        # np.loadtxt skips blank lines natively and parses entirely in C
        data = np.loadtxt(io.BytesIO(raw), dtype=np.float64)

        if data.size == 0:
            return

        # Ensure 2D even for single-row files
        if data.ndim == 1:
            data = data[np.newaxis, :]

        num_rows, num_cols = data.shape

        # Grid detection
        if empty_lines > 0:
            if not hasattr(self, "dim"):
                self.state.nx1 = empty_lines
                self.state.nx2 = num_rows // empty_lines
                self.state.dim = 2
                self.state.nshp = (self.state.nx1, self.state.nx2)
        elif not hasattr(self, "dim"):
            self.state.nx1 = num_rows
            self.state.nx2 = 1
            self.state.dim = 1
            self.state.nshp = self.state.nx1

        if self.state.infogrid is True:
            self.state.x1 = data[:, 1].reshape(self.state.nx1, self.state.nx2)
            self.state.x2 = data[:, 0].reshape(self.state.nx1, self.state.nx2)
            # if self.state.nx2 == 1:
            #    self.state.x1 = self.state.x2[0]

        # Variable names
        if len(self.state.d_info["varslist"][exout]) == 0:
            self.state.d_info["varslist"][exout] = [
                f"var{k + 1}" for k in range(num_cols - 2)
            ]
        self.load_vars = self.state.d_info["varslist"][exout]

        # Store variables — pure numpy column slices (views, zero-copy)
        num_cols_iter = num_cols
        for j in range(2, num_cols_iter):
            var = self.state.d_info["varslist"][exout][j - 2]
            col = data[:, j]
            if empty_lines > 0:
                col = col.reshape(self.state.nx1, self.state.nx2)
            if var is not None and var in self.load_vars:
                setattr(self.state, var, col)
