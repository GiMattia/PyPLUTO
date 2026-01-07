"""Module to find the format of the PLUTO output files."""

import glob
from collections.abc import Callable
from pathlib import Path
from typing import Any

from ..baseloadmixin import BaseLoadMixin
from ..baseloadstate import BaseLoadState
from ..utils.inspector import track_kwargs


class FindFormat(BaseLoadMixin):
    """Class to find the format of the PLUTO output files."""

    @track_kwargs
    def __init__(self, state: BaseLoadState, **kwargs: Any) -> None:
        """Initialize the FindFormat class."""
        self.state = state

        datatype = kwargs.get("datatype")
        alone = kwargs.get("alone")
        self.check_format(datatype, alone)

    def check_format(
        self,
        datatype: str | None,
        alone: bool | None,
    ) -> None:
        """Find the format of the data files to load.

        This checks whether outputs are fluid or particles and searches for
        available filetypes in the target directory. Depending on the requested
        datatype and whether files are standalone, it probes formats in order
        and sets self.format, self._alone and self._charsize accordingly.
        Supported types are dbl, flt, vtk, dbl.h5 and flt.h5; hdf5 and tab are
        not implemented.

        Parameters
        ----------
        alone: bool | None
            If the output files are standalone or they require a .out
            file to be loaded. Only suggested for fluid files, .vtk
            format and standalone files, otherwise the code finds
            the alone property by itself.
        datatype: str | None
            The file format. If None the format is recovered between
            (in order) dbl, flt, vtk, dbl.h5 and flt.h5.
            Formats hdf5 (AMR) and tab have not been implemented yet.

        Returns
        -------
        None

        Examples
        --------
        - Example #1: Find the format of the fluid files

            >>> find_format("dbl", False)

        - Example #2: Find the format of the standalone files

            >>> find_format("vtk", True)

        - Example #3: Find the format of the fluid files (no format given)

            >>> find_format(None, False)

        - Example #4: Find the format of the particles files

            >>> find_format("dbl", True)        --------

        """
        # Initialization or declaration of variables
        dbl = {"dbl", "dbl.h5"}  # The set of double filetypes

        # Define the possible filetypes and set the keyword "alone" accordingly
        if self.class_name == "Load":
            # Divide the formats between standalone and not standalone
            type_out = ["dbl", "flt", "vtk", "dbl.h5", "flt.h5", "tab"]
            type_lon = ["vtk", "dbl.h5", "flt.h5", "tab", "hdf5"]
            # If datatype is dbl or flt the files are not standalone
            if datatype in {"dbl", "flt"}:
                alone = False
        elif self.class_name == "LoadPart":
            # Particle files are always standalone
            alone = True
            type_out = []
            type_lon = ["dbl", "flt", "vtk"]
        else:
            # If the class name is not recognized, raise an error
            raise NameError("Invalid class name.")

        # Check if the given datatype is valid, if not raise an error
        if datatype not in type_out + type_lon + [None]:
            if self.class_name == "Load":
                err = (
                    f"Invalid datatype {datatype}.\n"
                    f"Possible formats are: dbl, flt, vtk, dbl.h5, flt.h5, tab"
                )
            elif self.class_name == "LoadPart":
                err = (
                    f"Invalid datatype {datatype}.\n"
                    f"Possible formats are: dbl, flt, vtk"
                )
            raise ValueError(err)

        # Create the list of types to iterate over. If the datatype is None
        # then the list is the full list of types, otherwise the list is the
        # datatype itself.
        typeout0, typelon0 = (
            ([], []) if datatype is not None else (type_out, type_lon)
        )
        type_out = [datatype] if datatype in type_out else typeout0
        type_lon = [datatype] if datatype in type_lon else typelon0

        # Create the list of functions to be called (.out or alone)
        funcf: list[Callable[[list[str]], None]] = []
        funcf += (
            [self.check_typeout]
            if len(type_out) > 0 and alone is not True
            else []
        )
        funcf += (
            [self.check_typelon]
            if len(type_lon) > 0 and alone is not False
            else []
        )

        # Define the dictionary for the function argument
        dict_func = {"check_typeout": type_out, "check_typelon": type_lon}

        # Iterate over the functions to be called
        for do_check in funcf:
            do_check(dict_func[do_check.__name__])

            # Check if the format has been found
            if self.format != "Unknown":
                # Store the charsize depending on the format
                self.charsize = 8 if self.format in dbl else 4

                # If the format is found, end the function
                return None

        # No file has been found, so raise an error depending on the case.
        # If the datatype is None, raise a general error, otherwise raise
        # an error for the specific datatype.
        scrh = f"No available type has been found in {self.pathdir}."

        if datatype is not None:
            scrh = f"Type {datatype} not found."
        raise FileNotFoundError(scrh)

    def check_typeout(self, type_out: list[str]) -> None:
        """Loop over possible formats in order to findthe descriptor files.

        If the datatype.out file is found, the file format is selected and the
        flag alone is set to False.

        Returns
        -------
        - None

        Parameters
        ----------
        - type_out (not optional): list[str]
            The list of possible formats for the output file.

        ----

        Examples
        --------
        - Example #1: Check the format of the output files

            >>> _check_typeout(["dbl", "flt", "vtk", "dbl.h5", "flt.h5", "tab"])

        - Example #2: Check the format of the output files (no format given)

            >>> _check_typeout([])

        """
        # Loop over the possible formats
        for try_type in type_out:
            # Create the path to the grid.out and datatype.out files
            pathgrid = self.pathdir / Path("grid.out")
            pathdata = self.pathdir / Path(try_type + ".out")

            # Check if the datatype.out file is present
            if pathdata.is_file() and pathgrid.is_file():
                # Store the format and set the flag alone to False
                self.format = try_type
                self.alone = False
                # Format is found, break the loop
                break

        # End of the function

    def check_typelon(self, type_lon: list[str]) -> None:
        """Loop over possible formats in order to find the datatype.

        If the file is found, the file format is selected and the flag alone is
        set to True.

        Returns
        -------
        - None

        Parameters
        ----------
        - type_lon (not optional): list[str]
            The list of possible formats for the output file.

        ----

        Examples
        --------
        - Example #1: Check the format of the output files

            >>> _check_typelon(["dbl", "flt", "vtk"])

        - Example #2: Check the format of the output files (no format given)

            >>> _check_typelon([])

        """
        # Loop over the possible formats
        for try_type in type_lon:
            # Create the pattern to be searched
            pattern = self.pathdir / Path("*.*." + try_type)

            # Find the files matching the pattern
            self.matching_files = glob.glob(str(pattern))

            # Check if the file is present
            if self.matching_files:
                # Store the format and set the flag alone to True
                self.format = try_type
                self.alone = True
                self.infogrid = False
                # Format is found, break the loop
                break

        # End of the function
