"""Descriptor management utilities for reading PLUTO descriptor files."""

from pathlib import Path
from typing import Any

import numpy as np
import pandas as pd

from ..loadmixin import LoadMixin
from ..loadstate import LoadState
from .baseloadtools import BaseLoadTools


class DescriptorManager(LoadMixin):
    """Class that manages the descriptor files for loading data."""

    def __init__(self, state: LoadState, **kwargs: Any) -> None:
        """Initialize the DescriptorManager class."""
        self.state = state
        self.LoadToolManager = BaseLoadTools(self.state)

        self.load_descriptor(**kwargs)

    def load_descriptor(self, **kwargs: Any) -> None:
        """Read the datatype.out file and stores the information.

        Such information are the time array, the output variables, the file type
        (single or multiples), the endianess, the simulation path and the bin
        format. All these information are relevant in order to open the output
        files and access the data.

        Returns
        -------
        - None

        Parameters
        ----------
        - endian (not optional): str
            The endianess of the files.
        - nout (not optional): int
            The output file to be opened. If default ('last'), the code assumes
            the last file should be opened. Other options available are 'last'
            (all the files should be opened) and -1 (same as 'last').

        ----

        Examples
        --------
        - Example #1: Read the 'filetype'.out file

            >>> _read_outfile(0, "big")

        """
        if self.format is None:
            raise ValueError("Format not defined. Cannot read descriptor file.")
        # Open and read the 'filetype'.out file
        pathdata = self.pathdir / Path(self.format + ".out")
        vfp = pd.read_csv(
            str(pathdata), sep=r"\s+", header=None, engine="python"
        )

        # Store the output and the time full list
        self.outlist = np.array(vfp.iloc[:, 0], dtype="int")
        self.timelist = np.array(vfp.iloc[:, 1])

        # Check the output lines
        self.LoadToolManager.check_nout(kwargs.get("nout", "last"))
        self.ntime = self.timelist[self.noutlist]
        self._lennout = len(self.noutlist)

        # Initialize the info dictionary
        self._d_info = {
            "typefile": np.array(vfp.iloc[self.noutlist, 4]),
            "endianess": np.where(
                vfp.iloc[self.noutlist, 5] == "big", ">", "<"
            ),
        }

        # Compute the endianess (vtk have always big endianess).
        # If endian is given, it is used instead of the one in the file.
        self._d_info["endianess"][:] = (
            ">" if self.format == "vtk" else self._d_info["endianess"]
        )
        self._d_info["endianess"][:] = (
            self._d_end[self.endian]
            if self.endian is not None
            else self._d_info["endianess"]
        )

        # Store the variables list
        if self.format not in {"dbl.h5", "flt.h5"}:
            self._d_info["varslist"] = np.array(vfp.iloc[self.noutlist, 6:])
        else:
            self.varsh5 = np.array(vfp.iloc[self.nout, 6:])[0]
            self._d_info["varslist"] = [[] for _ in range(self._lennout)]

        # Compute binformat and endpath
        self._d_info["binformat"] = np.char.add(
            self._d_info["endianess"], "f" + str(self._charsize)
        )
        format_string = f".%04d.{self.format}"
        self._d_info["endpath"] = np.char.mod(format_string, self.noutlist)
