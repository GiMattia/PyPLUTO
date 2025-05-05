import glob
from pathlib import Path


def _check_pathformat(self, path: str | Path) -> None:
    """Check if the path is consistent, i.e. if the path is given through a
    non-empty string. If the path is consistent, it is converted to a Path
    object. Then, a check is performed to see if the path is a directory. The
    path is stored in the class as a Path object self.pathdir.

    Returns
    -------
    - None

    Parameters
    ----------
    - path (not optional): str | Path
        The path to the simulation directory.

    Notes
    -----
    - None

    ----

    Examples
    --------
    - Example #1: path is a string

        >>> _check_pathformat('path/to/simulation')

    - Example #2: path is not a string

        >>> _check_pathformat(1)
        TypeError: Invalid data type. 'path' must be a non-empty string.

    - Example #3: path is an empty string

        >>> _check_pathformat('')
        ValueError: 'path' cannot be an empty string.

    - Example #4: path is not a directory

        >>> _check_pathformat('path/to/simulation')
        NotADirectoryError: Directory path/to/simulation not found.

    """
    # Check if the path is a non-empty string.
    if not isinstance(path, str) and not isinstance(path, Path):
        error = TypeError("Invalid data type. 'path' must be path or string")
        raise TypeError(error)
    # Check if the path is not empty
    elif not isinstance(path, Path) and not path.strip():
        raise ValueError("'path' cannot be an empty string.")
    # Convert the path to a Path object and store it
    else:
        self.pathdir = Path(path)

    # Check that the path is a directory
    if not self.pathdir.is_dir():
        raise NotADirectoryError(f"Directory {self.pathdir} not found.")

    # End of the function


def _find_format(self, datatype: str | None, alone: bool | None) -> None:
    """Finds the format of the data files to load. At first, the code checks the
    filetype to be loaded (if fluid or particles). Then, depending on the
    filetype given, the code checks if the corresponding filetype is present
    Depending on the properties of the filetype and of the type of the output
    (if fluid or particles) different checks are performed.
    If no format is given or if the given format is not found, the code checks
    the presence other filetypes in the directory. If no file is found, an error
    is raised. CUrrent filetypes available are dbl, flt, vtk, dbl.h5 and flt.h5.

    Returns
    -------
    - None

    Parameters
    ----------
    - alone (not optional): bool | None, default False
        If the output files are standalone or they require a .out
        file to be loaded. Only suggested for fluid files, .vtk
        format and standalone files, otherwise the code finds
        the alone property by itself.
    - datatype (not optional): str | None, default None
        The file format. If None the format is recovered between
        (in order) dbl, flt, vtk, dbl.h5 and flt.h5.
        Formats hdf5 (AMR) and tab have not been implemented yet.

    Notes
    -----
    - None

    ----

    Examples
    --------
    - Example #1: Find the format of the fluid files

        >>> _find_format('dbl', False)

    - Example #2: Find the format of the standalone files

        >>> _find_format('vtk', True)

    - Example #3: Find the format of the fluid files (no format given)

        >>> _find_format(None, False)

    - Example #4: Find the format of the particles files

        >>> _find_format('dbl', True)

    """
    # Initialization or declaration of variables
    class_name = self.__class__.__name__  # The class name
    dbl = {"dbl", "dbl.h5"}  # The set of double filetypes

    # Define the possible filetypes and set the keyword "alone" accordingly
    if class_name == "Load":
        # Divide the formats between standalone and not standalone
        type_out = ["dbl", "flt", "vtk", "dbl.h5", "flt.h5", "tab"]
        type_lon = ["vtk", "dbl.h5", "flt.h5", "tab", "hdf5"]
        # If datatype is dbl or flt the files are not standalone
        if datatype in {"dbl", "flt"}:
            alone = False
    elif class_name == "LoadPart":
        # Particle files are always standalone
        alone = True
        type_out = []
        type_lon = ["dbl", "flt", "vtk"]
    else:
        # If the class name is not recognized, raise an error
        raise NameError("Invalid class name.")

    # Check if the given datatype is valid, if not raise an error
    if datatype not in type_out + type_lon + [None]:
        if class_name == "Load":
            err = (
                f"Invalid datatype {datatype}.\n"
                f"Possible formats are: dbl, flt, vtk, dbl.h5, flt.h5, tab"
            )
        elif class_name == "LoadPart":
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
    funcf = [_check_typeout] if len(type_out) > 0 and alone is not True else []
    funcf += (
        [_check_typelon] if len(type_lon) > 0 and alone is not False else []
    )

    # Define the dictionary for the function argument
    dict_func = {"_check_typeout": type_out, "_check_typelon": type_lon}

    # Iterate over the functions to be called
    for do_check in funcf:
        do_check(self, dict_func[do_check.__name__])

        # Check if the format has been found
        if self.format is not None:
            # Store the charsize depending on the format
            self._charsize = 8 if self.format in dbl else 4

            # If the format is found, end the function
            return None

    # No file has been found, so raise an error depending on the case.
    # If the datatype is None, raise a general error, otherwise raise
    # an error for the specific datatype.
    scrh = f"No available type has been found in {self.pathdir}."

    if datatype is not None:
        scrh = f"Type {datatype} not found."
    raise FileNotFoundError(scrh)

    # End of the function (never goes here, just for clarity)
    return None


def _check_typeout(self, type_out: list[str]) -> None:
    """Loops over possible formats in order to find, at first the grid.out file,
    then the datatype.out file. If the datatype.out file is found, the file
    format is selected and the flag alone is set to False.

    Returns
    -------
    - None

    Parameters
    ----------
    - type_out (not optional): list[str]
        The list of possible formats for the output file.

    Notes
    -----
    - None

    ----

    Examples
    --------
    - Example #1: Check the format of the output files

        >>> _check_typeout(['dbl','flt','vtk','dbl.h5','flt.h5','tab'])

    - Example #2: Check the format of the output files (no format given)

        >>> _check_typeout([])

    """
    # Loop over the possible formats
    for try_type in type_out:

        # Create the path to the grid.out and datatype.out files
        self._pathgrid = self.pathdir / "grid.out"
        self._pathdata = self.pathdir / (try_type + ".out")

        # Check if the datatype.out file is present
        if self._pathdata.is_file() and self._pathgrid.is_file():
            # Store the format and set the flag alone to False
            self.format = try_type
            self._alone = False
            # Format is found, break the loop
            break

    # End of the function


def _check_typelon(self, type_lon: list[str]) -> None:
    """Loops over posisble formats in order to find matching files with the
    datatype. If the file is found, the file format is selected and the flag
    alone is set to True.

    Returns
    -------
    - None

    Parameters
    ----------
    - type_lon (not optional): list[str]
        The list of possible formats for the output file.

    Notes
    -----
    - None

    ----

    Examples
    --------
    - Example #1: Check the format of the output files

        >>> _check_typelon(['dbl','flt','vtk'])

    - Example #2: Check the format of the output files (no format given)

        >>> _check_typelon([])

    """
    # Loop over the possible formats
    for try_type in type_lon:

        # Create the pattern to be searched
        pattern: Path = self.pathdir / ("*.*." + try_type)

        # Find the files matching the pattern
        self._matching_files = glob.glob(str(pattern))

        # Check if the file is present
        if self._matching_files:
            # Store the format and set the flag alone to True
            self.format = try_type
            self._alone = True
            # Format is found, break the loop
            break

    # End of the functionv
