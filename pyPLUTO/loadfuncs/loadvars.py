"""Docstring for pyPLUTO.loadfuncs.loadvars module."""

import mmap
import warnings

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

        Returns
        -------
        - None

        Parameters
        ----------
        - endian (not optional): bool
            The endianess of the files. If True the endianess is big, otherwise
            it is little.
        - exout (not optional): int
            The index of the output to be loaded.
        - i (not optional): int
            The index of the file to be loaded.
        - vars (not optional): str | list[str] | bool | None, default True
            If True all the variables are loaded, otherwise just a selection is
            loaded.

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

        # Find the class name and find the single_file filepath
        if self.class_name == "Load":
            # If the class name is Load (single file), the filepath is data
            self.filepath = self.pathdir / (
                "data" + self.d_info["endpath"][exout]
            )
        elif self.class_name == "LoadPart":
            # If the class name is LoadPart, the filepath is particles
            self.filepath = self.pathdir / (
                "particles" + self.d_info["endpath"][exout]
            )
        else:
            # If the class name is not recognized, raise an error
            raise NameError("Invalid class name.")

        # If files in single_file format, inspect the file
        # or compute the offset and shape

        if self.d_info["typefile"][exout] == "single_file":
            with open(self.filepath, "rb") as fd:
                kwargs = {"access": mmap.ACCESS_READ}
                # if sys.version_info >= (3, 13):
                #    kwargs["trackfd"] = False
                mm = mmap.mmap(fd.fileno(), 0, **kwargs)
            self.offsetdata.compute_offset(i, exout, None, mm)
            if self.format in ("hdf5", "tab"):
                return None

        # Check if only specific variables should be loaded
        if variables is True:
            # If all the variables are to be loaded, the load_vars
            # is set to the variables list
            load_vars = self.d_info["varslist"][exout]
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
            if self.d_info["typefile"][exout] == "multiple_files":
                self.filepath = self.pathdir / (
                    j + self.d_info["endpath"][exout]
                )
                try:
                    with open(self.filepath, "rb") as fd:
                        kwargs = {"access": mmap.ACCESS_READ}
                        # if sys.version_info >= (3, 13):
                        #    kwargs["trackfd"] = False
                        mm = mmap.mmap(fd.fileno(), 0, **kwargs)
                except (OSError, ValueError) as e:
                    warnings.warn(
                        f"AttributeError: Unable to open {self.filepath}.\n"
                        f"{e}\nSkipping variable {j}.",
                        UserWarning,
                        stacklevel=2,
                    )
                    continue
                self.offsetdata.compute_offset(i, exout, j, mm)

            if self.lennout != 1:
                self.init_vardict(j)

            if mm is None:
                raise RuntimeError("memmap object not initialized")

            dtype = np.dtype(self.d_info["binformat"][exout])
            shape = self.varshape[j]
            offset = self.varoffset[j]
            scrh = np.ndarray(
                shape=shape,
                dtype=dtype,
                buffer=mm,
                offset=offset,
                order="C",
            )

            # Transpose the array if necessary (not dbl.h5 / flt.h5)
            if (
                self.format not in {"dbl.h5", "flt.h5"}
                or self.alone is not True
            ):
                scrh = scrh.T

            self.assign_var(exout, j, scrh)

        # ... then after the variable loop ...

    def assign_var(self, time: int, var: str, scrh: np.ndarray) -> None:
        """Assign the variable data to the class variable.

        The function assigns the data to the class variable. The variable name
        is constructed based on the variable name and the output index.

        Returns
        -------
        - None

        Parameters
        ----------
        - exout (not optional): int
            The index of the output to be loaded.
        - var (not optional): str
            The variable name.
        - data (not optional): np.ndarray
            The data to be assigned to the variable.

        ----

        Examples
        --------
        - Example #1: Assign data to a variable

            >>> _assign_var(0, "rho", data)

        """
        # Assign the memmap object to the dictionary
        if self.lennout != 1:
            # If the number of outputs is not 1, the variable is stored at the
            # corresponding output
            self.d_vars[var][time] = scrh
        else:
            # If the number of outputs is 1, the variable is stored directly
            self.d_vars[var] = scrh

        # End of the function

    def init_vardict(self, var: str) -> None:
        """If not initialized, a new dictionary is created to store the vars.

        The dictionary is stored in the class. The shape of the dictionary is
        computed depending on the number of outputs and the variable shape.

        Returns
        -------
        - None

        Parameters
        ----------
        - var (not optional): str
            The variable to be loaded.

        ----

        Examples
        --------
        - Example #1: Initialize the dictionary of a non-initialized variable

            >>> _init_vardict("rho")

        """
        # If the variable is not initialized, create a new dictionary
        if var not in self.d_vars:
            self.d_vars[var] = {}
