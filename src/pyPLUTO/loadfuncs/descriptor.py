"""Descriptor management utilities for reading PLUTO descriptor files."""

from pathlib import Path
from typing import Any

import numpy as np

from pyPLUTO.loadfuncs.baseloadtools import BaseLoadTools
from pyPLUTO.loadmixin import LoadMixin
from pyPLUTO.loadstate import LoadState


class DescriptorManager(LoadMixin):
    """Class that manages the descriptor files for loading data."""

    def __init__(
        self,
        state: LoadState,
        nout: int | str | list[int | str],
        **kwargs: Any,
    ) -> None:
        """Initialize the DescriptorManager class."""
        self.state = state
        self.LoadToolManager = BaseLoadTools(self.state)
        self.load_descriptor(nout, **kwargs)

    def load_descriptor(
        self, nout: int | str | list[int | str], **kwargs: Any
    ) -> None:
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
        # Read and parse the 'filetype'.out file — pure Python split, no Pandas
        pathdata = self.state.pathdir / Path(self.state.datatype + ".out")
        rows = [
            line.split()
            for line in pathdata.read_text().splitlines()
            if line.strip()
        ]

        # Store the output and the time full list
        self.state.outlist = np.array([r[0] for r in rows], dtype=np.int32)
        self.state.timelist = np.array([r[1] for r in rows], dtype=np.float64)
        self.state.lennoutlist = len(self.state.outlist)

        # Check the output lines
        self.LoadToolManager.check_nout(nout)
        self.state.ntimelist = self.state.timelist[self.state.noutlist]
        self.state.lennout = len(self.state.noutlist)

        # Initialize the info dictionary
        self.state.d_info = {
            "typefile": np.array([rows[k][4] for k in self.state.outlist]),
            "endianess": np.array(
                [
                    ">" if rows[k][5] == "big" else "<"
                    for k in self.state.outlist
                ]
            ),
        }

        # Compute the endianess (vtk always big endian).
        # If endian is given, it is used instead of the one in the file.
        self.state.d_info["endianess"][:] = (
            ">"
            if self.state.datatype == "vtk"
            else self.state.d_info["endianess"]
        )
        self.state.d_info["endianess"][:] = (
            self.state.endian
            if self.state.endian is not None
            else self.state.d_info["endianess"]
        )
        self.state.d_info["varslist"] = [
            rows[k][6:] for k in self.state.outlist
        ]

        self.state.d_info["binformat"] = np.char.add(
            self.state.d_info["endianess"], "f" + str(self.state.charsize)
        )
