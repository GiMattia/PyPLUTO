import warnings
from typing import Any

import h5py
import numpy as np


def read_vtk(self) -> None:
    """Read the data from a VTK file.

    Returns
    -------
    - None

    Parameters
    ----------
    - None

    ----

    Examples
    --------
    - Example #1: Read the data from a VTK file

        >>> read_vtk()

    """
    raise NotImplementedError("read_vtk() is not yet implemented.")


def _read_h5(self, filename: str, **kwargs: Any) -> None:
    """Read the data from a HDF5 file.

    Returns
    -------
    - the data in a dictionary

    Parameters
    ----------
    - filename: str
        The name of the file to be read.
    - kwargs: Any
        Any additional arguments.

    ----

    Examples
    --------
    - Example #1: Read the data from a HDF5 file

        >>> read_h5("filename.h5")

    """
    # Create the path to the HDF5 file
    try:
        self._pathh5 = self.pathdir / filename
    except FileNotFoundError:
        self._pathh5 = filename

    # Open the HDF5 file
    data_dict = {}
    with h5py.File(self._pathh5, "r") as f:
        for key in f.keys():
            data_dict[key] = f[key][()]  # Store data in the dictionary

    return data_dict  # Return the dictionary


def read_tab(self) -> None:
    """Read the data from a tab file.

    Returns
    -------
    - None

    Parameters
    ----------
    - None

    ----

    Examples
    --------
    - Example #1: Read the data from a tab file

        >>> read_tab()

    """
    raise NotImplementedError("read_tab() is not yet implemented.")


def read_bin(self) -> None:
    """Read the data from a binary file.

    Returns
    -------
    - None

    Parameters
    ----------
    - None

    ----

    Examples
    --------
    - Example #1: Read the data from a binary file

        >>> read_bin()

    """
    raise NotImplementedError("read_bin() is not yet implemented.")


def _read_dat(self, filename: str, **kwargs: Any) -> None:
    """Read the data from a dat file.

    Returns
    -------
    - The file columns as a dicionary

    Parameters
    ----------
    - filename (not optional): str
        The name of the file to be read.
    - kwargs: Any
        Any additional arguments.
    - names: bool, default True
        If True, checks for column names in the file.
    - skip: int, default 0
        The number of rows to skip.

    ----

    Examples
    --------
    - Example #1: Read the data from a dat file

        >>> read_dat("filename.dat")

    """
    print("Reading dat file...")
    print("Reading dat file...")
    print("Reading dat file...")
    print("Reading dat file...")
    print("Reading dat file...")
    print("Reading dat file...")
    # Create the path to the HDF5 file
    try:
        self._pathh5 = self.pathdir / filename
    except FileNotFoundError:
        self._pathh5 = filename

    names = kwargs.get("names", True)
    skip = kwargs.get("skip", 0)

    # Open the dat file with np.genfromtext
    data = np.genfromtxt(self._pathh5, names=names, skip_header=skip)
    if names:
        loop = data.dtype.names
        analysis = {name: data[name] for name in loop}
    else:
        loop = range(data.shape[1])
        analysis = {f"col_{i}": data[:, i] for i in loop}

    return analysis


def read_file(
    self, filename: str, datatype: str | None = None, **kwargs: Any
) -> Any:
    """Read the data from the output files.

    Returns
    -------
    - the data as a dicionary

    Parameters
    ----------
    - filename (not optional): str
        The name of the file to be read.
    - datatype: str
        The type of the file.
    - **kwargs: Any
        Any additional arguments.

    ----

    Examples
    --------
    - Example #1: Read the data from the output files

        >>> read_files()

    """
    # Check the datatype of the input data
    if datatype is None:
        datatype = filename.split(".")[-1]
    poss_types = {"dbl", "flt", "vtk", "h5", "tab", "dat"}
    if datatype not in poss_types:
        warn = f"Invalid datatype: {datatype}. Resetting to 'h5'"
        warnings.warn(warn)
        datatype = "h5"

    # Check the format of the output files
    if datatype == "h5":
        res = _read_h5(self, filename, **kwargs)
    elif datatype == "dat":
        res = _read_dat(self, filename, **kwargs)
    else:
        warn = (
            f"Invalid datatype: {datatype}, not implemented yet! "
            "Resetting to 'h5'"
        )
        warnings.warn(warn)
        pass

    # End of the function
    return res
