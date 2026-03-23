"""Docstring for pyPLUTO.loadfuncs.readtab."""

import io
import mmap

import numpy as np

from pyPLUTO.loadmixin import LoadMixin
from pyPLUTO.loadstate import LoadState


class ReadtabManager(LoadMixin):
    """Class that manages the reading of tabular data."""

    def __init__(self, state: LoadState) -> None:
        self.state = state

    def read_tab(
        self, i: int, var: str | None, exout: int, mm: mmap.mmap
    ) -> None:
        """Read the data.****.tab file and stores the relevant information.

        Such information are the grid variables, the output variables and the
        output time.

        Returns
        -------
        - None

        Parameters
        ----------
        - i (not optional): int
            The index of the file to be loaded.

        ----

        Examples
        --------
        - Example #1: Read the data.0000.tab file

            >>> _read_tabfile(0)

        """
        Dict_tab = {}

        # Read entire mmap in one call
        mm.seek(0)
        raw = mm.read()

        # Count empty lines via C-level bytes.count — no Python loop needed
        # \n\n indicates a blank line between two newlines
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
                self.nx1 = empty_lines
                self.nx2 = num_rows // empty_lines
                self.dim = 2
                self.nshp = (self.nx1, self.nx2)
        elif not hasattr(self, "dim"):
            self.nx1 = num_rows
            self.nx2 = 1
            self.dim = 1
            self.nshp = self.nx1

        if self.infogrid is True:
            self.x1 = data[:, 1].reshape(self.nx1, self.nx2)
            self.x2 = data[:, 0].reshape(self.nx1, self.nx2)
            if self.nx2 == 1:
                self.x1 = self.x2[0]

        # Variable names
        if len(self.d_info["varslist"][exout]) == 0:
            self.d_info["varslist"][exout] = [
                f"var{k}" for k in range(num_cols - 2)
            ]
        self.load_vars = self.d_info["varslist"][exout]

        # Store variables — pure numpy column slices (views, zero-copy)
        num_cols_iter = num_cols
        for j in range(2, num_cols_iter):
            var = self.d_info["varslist"][exout][j - 2]
            col = data[:, j]
            if empty_lines > 0:
                col = col.reshape(self.nx1, self.nx2)
            Dict_tab[var] = col
            if var in self.load_vars:
                setattr(self.state, var, col)
