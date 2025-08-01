import warnings
from pathlib import Path

import numpy as np

from .h_pypluto import makelist


def _load_variables(
    self,
    vars: str | list[str] | bool | None,
    i: int,
    exout: int,
    endian: str | None,
) -> None:
    """Loads the variables in the class. The function checks if the
    variables to be loaded are valid and then loads them. If the
    variables are not valid, an error is raised. If the variables are
    valid, the function loads them in the class through memory mapping.
    The offset and shape of each variable is computed depenging on the
    format and typefile characteristics. In case the files are
    standalone, the relevand time and grid information is loaded.

    Returns
    -------
    - None

    Parameters
    ----------
    - endian (not optional): bool
        The endianess of the files. If True the endianess is big, otherwise it
        is little.
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
    # Find the class name and find the single_file filepath
    class_name: str = self.__class__.__name__
    if class_name == "Load":
        # If the class name is Load (single file), the filepath is data
        self._filepath = self.pathdir / ("data" + self._d_info["endpath"][i])
    elif class_name == "LoadPart":
        # If the class name is LoadPart, the filepath is particles
        self._filepath = self.pathdir / (
            "particles" + self._d_info["endpath"][i]
        )
    else:
        # If the class name is not recognized, raise an error
        raise NameError("Invalid class name.")

    # If files in single_file format, inspect the file
    # or compute the offset and shape
    if self._d_info["typefile"][i] == "single_file":
        self._compute_offset(i, endian, exout, None)
    if self.format == "hdf5":
        return None

    # Check if only specific variables should be loaded
    if vars is True:
        # If all the variables are to be loaded, the load_vars
        # is set to the variables list
        self._load_vars = self._d_info["varslist"][i]
    elif vars is not None:
        # If only specific variables are to be loaded, the load_vars
        # becomes the list of the selected variables
        self._load_vars = makelist(vars)
    else:
        # If no variables are to be loaded, return None (WIP)
        return None

    # If the format is tab, the data have been already loaded, so
    # the function returns None
    if self.format == "tab":
        return None

    # ERROR: TOO MANY OPEN FILES!!!
    # This chunk of code is here simply to show how the variables were loaded
    # in a preliminary version of the memory mapping procedure.
    """
    # Loop over the variables to be loaded
    for j in self._load_vars:

        # Change filepath, offset and shape in case of multiple_files
        if self._d_info['typefile'][i] == 'multiple_files':
            # If the files are multiple, the filepath is changed for each
            # variable and the offset and shape are computed
            self._filepath = self.pathdir / (j + self._d_info['endpath'][i])
            self._compute_offset(i, endian, exout, j)

        # Initialize the variables dictionary
        self._init_vardict(j) if self._lennout != 1 else None

        # Load the variable through memory mapping and store them in the class
        scrh = np.memmap(self._filepath,self._d_info['binformat'][i],mode="r+",
                         offset=self._offset[j], shape = self._shape[j]).T
        self._assign_var(exout, j, scrh)

    """

    # Compute the byte range for all variables in the current loop
    if self._d_info["typefile"][i] == "single_file" and class_name == "Load":
        start_byte = min(self._offset[j] for j in self._load_vars)
        end_byte = max(
            self._offset[j]
            + np.prod(self._shape[j])
            * np.dtype(self._d_info["binformat"][i]).itemsize
            for j in self._load_vars
        )

        # Create a single memmap spanning the required byte range
        # This is the original code that was used to load the variables

        # file_memmap = np.memmap(
        #    self._filepath,
        #    dtype=self._d_info["binformat"][i],
        #    mode="r+",
        #    offset=start_byte,
        #    shape=(end_byte - start_byte),
        # )

        file_memmap = np.memmap(
            self._filepath,
            dtype="uint8",  # Raw byte access for all data types
            mode="r+",
            offset=start_byte,
            shape=(end_byte - start_byte),
        )

    # Loop over the variables to extract slices
    for j in self._load_vars:
        if self._d_info["typefile"][i] == "multiple_files":
            self._filepath = self.pathdir / (j + self._d_info["endpath"][i])
            self._compute_offset(i, endian, exout, j)
            start_byte = self._offset[j]
            # Reload memmap for the new file
            file_memmap = np.memmap(
                self._filepath,
                self._d_info["binformat"][i],
                mode="r+",
                offset=self._offset[j],
                shape=self._shape[j],
            )

        # Initialize the variables dictionary
        self._init_vardict(j) if self._lennout != 1 else None

        # Extract the relevant slice and reshape
        if class_name == "Load":
            # Calculate the relative start and end for this variable
            rel_start = (
                self._offset[j] - start_byte
            )  # Offset relative to the memory-mapped file
            rel_end = (
                rel_start
                + np.prod(self._shape[j])
                * np.dtype(self._d_info["binformat"][i]).itemsize
            )

            # Step 3: Extract the raw data slice from the memory map
            raw_data = file_memmap[rel_start:rel_end]

            # View the slice with the desired dtype and reshape
            scrh = np.ndarray(
                shape=self._shape[j],
                dtype=self._d_info["binformat"][i],
                buffer=raw_data,
            ).T

            # Calculate the relative offset within the mapped range
            # rel_start = (self._offset[j] - start_byte) // file_memmap.itemsize
            # rel_end = rel_start + np.prod(self._shape[j])
            # scrh = file_memmap[rel_start:rel_end].reshape(self._shape[j]).T

        elif class_name == "LoadPart":
            scrh = np.memmap(
                self._filepath,
                self._d_info["binformat"][i],
                mode="r+",
                offset=self._offset[j],
                shape=self._shape[j],
            ).T

        # Assign the variable
        self._assign_var(exout, j, scrh)

    # End of function
    return None


def _check_nout(self, nout: int | str | list[int | str]) -> None:
    """Finds the number of datafile to be loaded. If nout is a list, the
    function checks if the list contains the keyword 'last' or -1. If
    so, the keyword is replaced with the last file number. If nout is a
    string, the function checks if the string contains the keyword
    'last' or -1. If so, the keyword is replaced with the last file
    number. If nout is an integer, the function returns a list
    containing the integer. If nout is 'all', the function returns a
    list containing all the file numbers.

    Returns
    -------
    - None

    Parameters
    ----------
    - nout (not optional): int | str | list[int|str]
        The output file to be loaded.

    ----

    Examples
    --------
    - Example #1: Load the last file

        >>> _check_nout("last")

    - Example #2: Load the first file

        >>> _check_nout(0)

    - Example #3: Load all the files

        >>> _check_nout("all")

    - Example #4: Load multiple specific files

        >>> _check_nout([0, 1, 2, 3])

    """
    # Assign the last possible output file
    last: int = self.outlist.tolist()[-1]

    # Check if nout is a list and change the keywords
    if not isinstance(nout, list):
        # If nout is a string, get the keywords
        Dnout = {nout: nout, "last": last, -1: last, "all": self.outlist}[nout]
    else:
        # If nout is a list, replace the keywords
        Dnout = [last if i in {"last", -1} else i for i in nout]

    # Sort the list, compute the corresponding time and store its length
    self.nout = np.sort(np.unique(np.atleast_1d(Dnout)))

    # Check if the output files are in the list
    if np.any(~np.isin(self.nout, self.outlist)):
        raise ValueError(
            f"Error: Wrong output file(s) {self.nout} \
                         in path {self.pathdir}."
        )

    # End of the function


def _findfiles(self, nout: int | str | list[int | str]) -> None:
    """Finds the files to be loaded. If nout is a list, the function
    loops over the list and finds the corresponding files. If nout is an
    integer, the function finds the corresponding file. If nout is
    'last', the function finds the last file. If nout is 'all', the
    function finds all the files. Then, the function stores the relevant
    information in a dictionary _d_info.

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
    class_name = self.__class__.__name__  # The class name
    self.set_vars = set()
    self.set_outs = set()

    # Loop over the matching files and call the functions
    for elem in self._matching_files:
        # varsouts[condition](self, elem)
        _varsouts(self, elem, class_name)

    # Check if the files are present
    if len(self.set_vars) == 0:
        raise FileNotFoundError(f"No files found in {self.pathdir}!")

    # Sort the outputs in an array and check the number of outputs
    self.outlist = np.array(sorted(self.set_outs))
    self._check_nout(nout)

    # Store the number of outputs and the time
    self._lennout = len(self.nout)
    self.ntime = np.empty(self._lennout)

    # Initialize the info dictionary and initialize some relevant variables
    self._d_info = {}
    self._d_info["typefile"] = np.empty(self._lennout, dtype="U20")
    self._d_info["endianess"] = np.empty(self._lennout, dtype="U20")
    self._d_info["binformat"] = np.empty(self._lennout, dtype="U20")

    if class_name == "LoadPart":
        # Check if the particles file is present
        if "particles" not in self.set_vars:
            raise FileNotFoundError(
                f"file particles.*.{self.format} \
                                    not found!"
            )

        # Particles are always 'single_file', initialize additional variables
        self._d_info["typefile"][:] = "single_file"
        self._d_info["varslist"] = [[] for _ in range(self._lennout)]
        self._d_info["varskeys"] = [[] for _ in range(self._lennout)]

        # Check if we are loading a single file (to be fixed)
        if self._lennout != 1:
            # Particles can be read only at a single fixed time
            raise NotImplementedError("multiple loading not implemented yet")

    elif class_name == "Load":
        # Check if the fluid files are present as multiple files
        if "data" not in self.set_vars or self._multiple is True:
            # If the files are multiple, the typefile is set to 'multiple_files'
            self._d_info["typefile"][:] = "multiple_files"
            self._d_info["varslist"] = np.empty(
                (self._lennout, len(self.set_vars)), dtype="U20"
            )
            self._d_info["varslist"][:] = list(self.set_vars)
        else:
            # If the files are single, the typefile is set to 'single_file'
            self._d_info["typefile"][:] = "single_file"
            self._d_info["varslist"] = [[] for _ in range(self._lennout)]

    else:
        # If the class name is not recognized, raise an error
        raise NameError("Invalid class name.")

    # Compute the endpath
    if self.nfile_lp is None:
        # If the number of LP files is not given, the format is standard
        format_string = f".%04d.{self.format}"
    else:
        # If the number of LP files is given, the format is different
        format_string = f".%04d_ch{self.nfile_lp:02d}.{self.format}"
    self._d_info["endpath"] = np.char.mod(format_string, self.nout)

    # End of the function


def _init_vardict(self, var: str) -> None:
    """If not initialized, a new dictionary is created to store the
    variables. The dictionary is stored in the class. The shape of the
    dictionary is computed depending on the number of outputs and the
    shape of the variable.

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
    if var not in self._d_vars.keys():
        self._d_vars[var] = {}
        """
        if isinstance(self._shape[var], tuple):
            # If the shape is a tuple, the shape is reversed
            sh_type = self._shape[var][::-1]
        else:
            # If the shape is not a tuple, the shape is converted to a tuple
            sh_type = (self._shape[var],)

        if self.__class__.__name__ == 'LoadPart':
            varsh = self._dictdim[var]
            # If the particles have multidimensional vars, the shape is changed
            shape = (varsh,) + sh_type if varsh != 1 else sh_type
        else:
            # If multiple fluid files are loaded, the shape is changed
            shape = (self._lennout,) + sh_type if self._lennout != 1 \
                else sh_type

        # Create a temporary file to store the data
        with tempfile.NamedTemporaryFile() as temp_file:
            # Create the dictionary key and fill the values with nan
            self._d_vars[var] = np.memmap(temp_file, \
                                          mode='w+', \
                                          dtype=np.float32, \
                                          shape = shape)
            self._d_vars[var][:] = np.nan
        """

    # End of the function


def _assign_var(self, time: int, var: str, scrh: np.memmap) -> None:
    """Assigns the memmap object to the dictionary. If the number of
    outputs is 1, the variable is stored directly in the dictionary,
    otherwise the variable is stored in the dictionary at the
    corresponding output.

    Returns
    -------
    - None

    Parameters
    ----------
    - scrh (not optional): np.memmap
        The memmap object containing the data to be stored.
    - time (not optional): int
        The output file to be loaded
    - var (not optional): str
        The variable to be loaded.

    ----

    Examples
    --------
    - Example #1: Assign the variable to the dictionary (single output time)

        >>> _assign_var(3, "rho", scrh)

    - Example #2: Assign the variable to the dictionary (multiple output times)

        >>> _assign_var(1, "rho", scrh)

    """
    # Assign the memmap object to the dictionary
    if self._lennout != 1:
        # If the number of outputs is not 1, the variable is stored at the
        # corresponding output
        self._d_vars[var][time] = scrh
    else:
        # If the number of outputs is 1, the variable is stored directly
        self._d_vars[var] = scrh

    # End of the function


def _varsouts(self, elem: str, class_name: str) -> None:
    """From the matching files finds the variables and the outputs for
    the fluid and particles files (variables are to be intended here as
    the first part of the output filename, they are the effective
    variables only in case of multiple fluid files).

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
    vars = raw_str[0]
    outs = raw_str[1]

    # Set the conditions if the file is fluid or particles
    isfluid = vars != "particles" and class_name == "Load"
    ispart = vars == "particles" and class_name == "LoadPart"

    if isfluid or (ispart and "_" not in outs):
        # File is fluid or particles, but not LP
        if self.nfile_lp is not None:
            # If the file is not LP, but nfile_lp is not None, raise a warning
            warn = f"nfile_lp is not None, but the file {elem} is not LP."
            warnings.warn(warn, UserWarning)
        # Control variable set to True
        outc = True

    elif ispart and "_" in outs:
        # File is LP
        if self.nfile_lp is None:
            # If the file is LP, but nfile_lp is None, raise a warning
            self.nfile_lp = 0
            warn = f"nfile_lp is None, but the file {elem} is LP, set to 0."
            warnings.warn(warn, UserWarning)

        # Control variable set to the number of LP files
        scrh = outs.split("_")
        outs = int(scrh[0])
        outc = int(scrh[1][2:])
    else:
        # Control variable set to False
        outc = False

    # Add the variables and the outputs
    if outc is True or outc == self.nfile_lp:
        self.set_vars.add(vars)
        self.set_outs.add(int(outs))

    # End of the function
