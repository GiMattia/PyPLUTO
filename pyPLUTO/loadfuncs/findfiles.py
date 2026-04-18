"""Docstring for findfiles.py."""

from pathlib import Path
from typing import Any

import numpy as np

from pyPLUTO.baseloadmixin import BaseLoadMixin
from pyPLUTO.baseloadstate import BaseLoadState
from pyPLUTO.loadfuncs.baseloadtools import BaseLoadTools


class FindFilesManager(BaseLoadMixin[BaseLoadState]):
    """Class that manages file finding operations."""

    def __init__(
        self,
        state: BaseLoadState,
        nout: int | str | list[int | str],
        **kwargs: Any,
    ) -> None:
        """Initialize the FindFilesManager class."""
        self.state = state
        self.LoadToolManager = BaseLoadTools(self.state)
        self.find_files(nout, **kwargs)

    def find_files(
        self, nout: int | str | list[int | str], **kwargs: Any
    ) -> None:
        """Find the files to be loaded.

        If nout is a list, the function loops over the list and finds the
        corresponding files. If nout is an integer, the function finds the
        corresponding file. If nout is 'last', the function finds the last file.
        If nout is 'all', the function finds all the files. Then, the function
        stores the relevant information in a dictionary d_info.

        Returns
        -------
        - None

        Parameters
        ----------
        - nout (not optional): int | str | list[int|str]
            The output file to be loaded

        ----

        Examples
        --------
        - Example #1: Load the last file

            >>> _findfiles("last")

        - Example #2: Load the first file

            >>> _findfiles(0)

        - Example #3: Load all the files

            >>> _findfiles("all")

        - Example #4: Load multiple specific files

            >>> _findfiles([0, 1, 2, 3])

        """
        # Initialization or declaration of variables
        set_vars: set[str] = set()
        set_outs: set[str] = set()
        self.d_info = {}

        if self.matching_files is None:
            raise ValueError("No files are found! Cannot proceed.")
        # Find the files to be loaded
        for elem in self.matching_files:
            self.varsout(elem, set_vars, set_outs)

        # Check if the files are present
        if len(set_vars) == 0 or len(set_outs) == 0:
            raise FileNotFoundError(f"No files found in {self.pathdir}!")

        self.outlist = np.array(sorted(set_outs))
        self.lennoutlist = len(self.outlist)
        self.LoadToolManager.check_nout(nout)
        self.lennout = len(self.noutlist)
        self.ntimelist = np.full(self.lennout, np.nan)
        self.timelist = np.full(len(self.outlist), np.nan)

        # Find the max size of the output numbers to allow for loading if some
        # files are missing
        d_info_size = int(np.max(self.outlist)) + 1

        # Initialize the info dictionary and initialize some relevant variables
        self.d_info["typefile"] = np.empty(d_info_size, dtype="U20")
        self.d_info["endianess"] = np.empty(d_info_size, dtype="U20")
        self.d_info["binformat"] = np.empty(d_info_size, dtype="U20")
        if self.class_name == "LoadPart":
            raise NotImplementedError(
                "FindFilesManager for LoadPart is not implemented yet."
            )
        elif self.class_name == "Load":
            # Check if the fluid files are present as multiple files
            if "data" not in set_vars or self.multiple is True:
                # If the files are multiple, the typefile is set accordingly
                self.d_info["typefile"][:] = "multiple_files"
                self.d_info["varslist"] = [[] for _ in range(d_info_size)]
                for elem in self.matching_files:
                    raw_str = Path(elem).name.split(".")
                    self.d_info["varslist"][int(raw_str[1])].append(raw_str[0])
            else:
                # If the files are single, the typefile is set to 'single_file'
                self.d_info["typefile"][:] = "single_file"
                self.d_info["varslist"] = [[] for _ in range(d_info_size)]
        else:
            raise ValueError(f"Unknown class name: {self.class_name}")

        # Sparse map indexed by output number
        endpath = np.empty(d_info_size, dtype=f"<U{len(self.format) + 6}")
        endpath[:] = ""
        for out in self.outlist:
            endpath[int(out)] = f".{int(out):04d}.{self.format}"
        self.d_info["endpath"] = endpath

    def varsout(
        self,
        elem: str,
        set_vars: set,
        set_outs: set,
    ) -> None:
        """Find the variables and the outputs for the fluid and particles files.

        Returns
        -------
        - None

        Parameters
        ----------
        - class_name (not optional): str
            The name of the class. Supported classes are 'Load' or 'LoadPart'.
        - elem (not optional): str
            The matching file.

        ----

        Examples
        --------
        - Example #1: Find the outputs (particles, non LP)

            >>> _varsouts_p("particles.0000.dbl")

        - Example #2: Find the outputs (fluid)

            >>> _varsouts_f("rho.0000.dbl")

        - Example #3: Find the outputs (LP)

            >>> _varsouts_lp("particles.0000_ch_00.dbl")

        """
        # Splits the matching filename (variable/data and output number)
        raw_str = Path(elem).name.split(".")
        var = raw_str[0]
        out = raw_str[1]

        # Set the conditions if the file is fluid or particles
        isfluid = var != "particles" and self.class_name == "Load"
        ispart = var == "particles" and self.class_name == "LoadPart"

        if isfluid or (ispart and "_" not in out):
            # Control variable set to True
            outc = True
        elif ispart and "_" in out:
            pass
        else:
            # Control variable set to False
            outc = False

            # Add the variables and the outputs
        if outc is True:
            set_vars.add(var)
            set_outs.add(int(out))
