"""Docstring for pyPLUTO.loadfuncs.readmetricfile."""

from __future__ import annotations

import io
import mmap

import numpy as np

from pyPLUTO.loadmixin import LoadMixin
from pyPLUTO.loadstate import LoadState

# Fixed variable names from the metric.out header, after the 3 coordinate columns
METRIC_VARS = [
    "lapse",
    "shift1",
    "shift2",
    "shift3",
    "gcov11",
    "gcov22",
    "gcov33",
    "gcov12",
    "gcov13",
    "gcov23",
]

METRIC_NCOLS_COORD = 3  # x1, x2, x3


class ReadMetricManager(LoadMixin):
    """Class that manages the reading of the metric.out file."""

    def __init__(self, state: LoadState) -> None:
        """Initialize the metric-data reading manager with the given state."""
        self.state = state

    def read_metric(self, filepath: str) -> None:
        """Read the metric.out file and store fields on the state object.

        Reads the lapse function, the 3 components of the shift vector,
        and the 6 independent coefficients of the spatial metric tensor
        (lower-index, gcov).  Coordinate arrays x1 and x2 are also stored.

        Parameters
        ----------
        filepath : str
            Absolute path to the metric.out file.

        Returns
        -------
        None

        Examples
        --------
        >>> ReadMetricManager(state).read_metric("/path/to/metric.out")
        """
        with open(filepath, "rb") as fd:
            mm = mmap.mmap(fd.fileno(), 0, access=mmap.ACCESS_READ)
            mm.seek(0)
            raw = mm.read()
            mm.close()

        # Normalize line endings (cross-platform safety)
        raw = raw.replace(b"\r\n", b"\n").replace(b"\r", b"\n")

        # Count blank-line block separators (each \n\n = one x2 block boundary)
        n_blank = raw.count(b"\n\n")

        # np.loadtxt skips #-comments and blank lines natively
        data = np.loadtxt(io.BytesIO(raw), comments=b"#", dtype=np.float64)

        if data.size == 0:
            return

        if data.ndim == 1:
            data = data[np.newaxis, :]

        num_rows, num_cols = data.shape

        # Grid dimensions.
        # blank lines separate x2 slices, so n_blank == nx2.
        # Each slice has nx1 = num_rows // nx2 rows.
        if n_blank > 0:
            nx2 = n_blank
            nx1 = num_rows // nx2
            self.state.nx1 = nx1
            self.state.nx2 = nx2
            self.state.dim = 2
            self.state.nshp = (nx1, nx2)
        else:
            self.state.nx1 = num_rows
            self.state.nx2 = 1
            self.state.dim = 1
            self.state.nshp = num_rows

        # Coordinate arrays — reshape to (nx1, nx2)
        shp = (self.state.nx1, self.state.nx2) if n_blank > 0 else (num_rows,)
        self.state.x1 = data[:, 0].reshape(shp)
        self.state.x2 = data[:, 1].reshape(shp)
        self.state.x3 = data[:, 2].reshape(shp)

        # Metric fields — cols 3 onwards, names from METRIC_VARS
        expected_data_cols = num_cols - METRIC_NCOLS_COORD
        for k, varname in enumerate(METRIC_VARS[:expected_data_cols]):
            col = data[:, METRIC_NCOLS_COORD + k].reshape(shp)
            setattr(self.state, varname, col)
