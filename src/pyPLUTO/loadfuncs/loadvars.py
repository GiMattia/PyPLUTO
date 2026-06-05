"""Docstring for pyPLUTO.loadfuncs.loadvars module."""

import mmap
import warnings
from pathlib import Path

import numpy as np

from pyPLUTO.baseloadmixin import BaseLoadMixin
from pyPLUTO.baseloadstate import BaseLoadState
from pyPLUTO.loadfuncs.offsetdata import OffsetData


class LoadVariables(BaseLoadMixin[BaseLoadState]):
    """Class that handles the loading of variables from PLUTO output files."""

    def __init__(
        self,
        state: BaseLoadState,
        variables: str | list[str] | bool | None,
        index: int,
        exout: int,
    ) -> None:
        """Initialize the LoadVariables class."""
        self.state = state
        self.offsetdata = OffsetData(state)
        self.load_variables(variables, index, exout)

    def load_variables(
        self, variables: str | list[str] | bool | None, i: int, exout: int
    ) -> None:
        """Load the variables in the class.

        The function checks if the variables to be loaded are valid and then
        loads them. If the variables are not valid, an error is raised. If the
        variables are valid, the function loads them in the class through memory
        mapping. The offset and shape of each variable is computed depenging on
        the format and typefile characteristics. In case the files are
        standalone, the relevand time and grid information is loaded.

        Parameters
        ----------
        - endian (not optional): bool
            The endianess of the files. If True the endianess is big, otherwise
            it is little.
        - exout (not optional): int
            The index of the output to be loaded.
        - i (not optional): int
            The index of the file to be loaded.
        - variables (not optional): str | list[str] | bool | None, default True
            If True all the variables are loaded, otherwise just a selection is
            loaded.

        Returns
        -------
        - None

        ----

        Examples
        --------
        - Example #1: Load all the variables

            >>> _load_variables(True, 0, 0, True)

        - Example #2: Load only the selected variables

            >>> _load_variables(["rho", "vx1"], 0, 0, True)

        - Example #3: Load all the variables (little endian)

            >>> _load_variables(True, 0, 0, False)

        - Example #4: Load all the variables from a specific output file

            >>> _load_variables(True, 0, 1, True)

        """
        # Initialize mm variable to None to avoid uninitialized variable error
        mm = None
        endpath = f".{int(exout):04d}.{self.state.datatype}"

        self.find_pathclass(endpath)

        # If files in single_file format, inspect the file
        # or compute the offset and shape

        if self.state.d_info["typefile"][exout] == "single_file":
            with open(self.state.filepath, "rb") as fd:
                kwargs = {"access": mmap.ACCESS_READ}
                # if sys.version_info >= (3, 13):
                #    kwargs["trackfd"] = False
                mm = mmap.mmap(fd.fileno(), 0, **kwargs)
            self._track_mm(mm)
            self.offsetdata.compute_offset(i, exout, None, mm)
            if self.state.datatype in ("hdf5", "tab"):
                return None

        # Check if only specific variables should be loaded
        is_chunked_particles = (
            self.state.class_name == "LoadPart"
            and self.state.d_info["typefile"][exout] == "multiple_files"
            and "chnklist" in self.state.d_info
        )
        if is_chunked_particles:
            # Chunked particle binary layout: load one file per chunk id.
            load_vars = self.state.d_info["chnklist"][exout]
        elif variables is True:
            # If all the variables are to be loaded, the load_vars
            # is set to the variables list
            load_vars = self.state.d_info["varslist"][exout]
        elif isinstance(variables, list | str):
            # If only specific variables are to be loaded, the load_vars
            # becomes the list of the selected variables
            load_vars = (
                variables if isinstance(variables, list) else [variables]
            )
        else:
            # If no variables are to be loaded, return None (WIP)
            return None

        for j in load_vars:
            offvar = j
            offind = j

            if is_chunked_particles:
                format_string = (
                    f".{int(exout):04d}_ch{int(j):02d}.{self.datatype}"
                )
                self.state.filepath = Path(self.state.pathdir) / (
                    "particles" + format_string
                )
                offvar = None
                offind = "tot"
            elif self.state.d_info["typefile"][exout] == "multiple_files":
                self.state.filepath = Path(self.state.pathdir) / (j + endpath)
            if self.state.d_info["typefile"][exout] == "multiple_files":
                try:
                    with open(self.state.filepath, "rb") as fd:
                        kwargs = {"access": mmap.ACCESS_READ}
                        # if sys.version_info >= (3, 13):
                        #    kwargs["trackfd"] = False
                        mm = mmap.mmap(fd.fileno(), 0, **kwargs)
                    self._track_mm(mm)
                except (OSError, ValueError) as e:
                    warnings.warn(
                        f"AttributeError: Unable to open {self.state.filepath}."
                        f"\n{e}\nSkipping variable {j}.",
                        UserWarning,
                        stacklevel=2,
                    )
                    continue
                self.offsetdata.compute_offset(i, exout, offvar, mm)

            if self.state.lennout != 1:
                self.init_vardict(j)

            dtype = np.dtype(self.state.d_info["binformat"][exout])
            shape = self.state.varshape[offind]
            offset = self.state.varoffset[offind]

            scrh = np.ndarray(
                shape=shape,
                dtype=dtype,
                buffer=mm,
                offset=offset,
                order="C",
            ).T

            self.assign_var(
                exout,
                offind,
                scrh,
                int(j) if is_chunked_particles and offind == "tot" else None,
            )

    def find_pathclass(self, endpath: str) -> None:
        """Set the data filepath based on the loader class and file suffix.

        Parameters
        ----------
        - endpath (not optional): str
            The file suffix.

        Returns
        -------
        - None
        """
        # Find the class name and find the single_file filepath
        if self.state.class_name == "Load":
            # If the class name is Load (single file), the filepath is data
            self.state.filepath = Path(self.state.pathdir) / ("data" + endpath)
        elif self.state.class_name == "LoadPart":
            # If the class name is LoadPart, the filepath is particles
            self.state.filepath = Path(self.state.pathdir) / (
                "particles" + endpath
            )
        else:
            # If the class name is not recognized, raise an error
            raise NameError("Invalid class name.")

    def assign_var(
        self,
        time: int,
        var: str,
        scrh: np.ndarray,
        chunk_id: int | None = None,
    ) -> None:
        """Assign the variable data to the class variable.

        The function assigns the data to the class variable. The variable name
        is constructed based on the variable name and the output index.

        Parameters
        ----------
        - data (not optional): np.ndarray
            The data to be assigned to the variable.
        - chunk_id: int | None
            The ID of the chunk to which the variable belongs.
        - exout (not optional): int
            The index of the output to be loaded.
        - scrh (not optional): np.ndarray
            The data to be assigned to the variable.
        - var (not optional): str
            The variable name.



        Returns
        -------
        - None

        ----

        Examples
        --------
        - Example #1: Assign data to a variable

            >>> _assign_var(0, "rho", data)

        """
        # Chunked LP particle files: keep all `tot` pieces for later merge.
        if var == "tot" and chunk_id is not None:
            if self.state.lennout != 1:
                if var not in self.state.d_vars or not isinstance(
                    self.state.d_vars[var], dict
                ):
                    self.state.d_vars[var] = {}
                if time not in self.state.d_vars[var] or not isinstance(
                    self.state.d_vars[var][time], list
                ):
                    self.state.d_vars[var][time] = []
                self.state.d_vars[var][time].append(scrh)
            else:
                if var not in self.state.d_vars or not isinstance(
                    self.state.d_vars[var], list
                ):
                    self.state.d_vars[var] = []
                self.state.d_vars[var].append(scrh)
            return

        # Assign the memmap object to the dictionary
        if self.state.lennout != 1:
            # If the number of outputs is not 1, the variable is stored at the
            # corresponding output
            self.state.d_vars[var][time] = scrh
        else:
            # If the number of outputs is 1, the variable is stored directly
            self.state.d_vars[var] = scrh

        # End of the function

    def _track_mm(self, mm: mmap.mmap) -> None:
        """Store mmap reference on state so compact() can evict its pages.

        Parameters
        ----------
        - mm: mmap.mmap
            The memory-mapped file to be tracked.
        """
        if self.state.class_name != "LoadPart":
            return
        self.state.mmaps.append(mm)

    def init_vardict(self, var: str) -> None:
        """If not initialized, a new dictionary is created to store the vars.

        The dictionary is stored in the class. The shape of the dictionary is
        computed depending on the number of outputs and the variable shape.

        Parameters
        ----------
        - var (not optional): str
            The variable to be loaded.

        Returns
        -------
        - None

        ----

        Examples
        --------
        - Example #1: Initialize the dictionary of a non-initialized variable

            >>> _init_vardict("rho")

        """
        # If the variable is not initialized, create a new dictionary
        if var not in self.state.d_vars:
            self.state.d_vars[var] = {}
