"""Module for reading different types of external files."""

from __future__ import annotations

import warnings
from pathlib import Path
from typing import Any

import h5py
import numpy as np

from pyPLUTO.loadmixin import LoadMixin
from pyPLUTO.loadstate import LoadState
from pyPLUTO.utils.inspector import track_kwargs


class ReadFilesManager(LoadMixin):
    """Class that manages reading external files."""

    def __init__(self, state: LoadState) -> None:
        """Initialize the file-reading manager with the given load state.

        Parameters
        ----------
        - state: LoadState
            The load state object providing the working directory path.

        Returns
        -------
        - None

        """
        self.state = state

    @track_kwargs
    def _read_vtk(
        self, filename: str, _check: bool = True, **kwargs: Any
    ) -> None:
        """Read data from a VTK file."""
        raise NotImplementedError("read_vtk() is not yet implemented.")

    @track_kwargs
    def _read_h5(
        self, filename: str, _check: bool = True, **kwargs: Any
    ) -> dict[str, Any]:
        """Read data from an HDF5 file."""
        try:
            pathh5 = self.state.pathdir / Path(filename)
        except FileNotFoundError:
            pathh5 = filename

        data_dict: dict[str, Any] = {}
        with h5py.File(str(pathh5), "r") as f:
            for key in f:
                data_dict[key] = f[key][()]

        return data_dict

    @track_kwargs
    def _read_tab(
        self, filename: str, _check: bool = True, **kwargs: Any
    ) -> None:
        """Read data from a tab file."""
        raise NotImplementedError("read_tab() is not yet implemented.")

    @track_kwargs
    def _read_bin(
        self, filename: str, _check: bool = True, **kwargs: Any
    ) -> None:
        """Read data from a binary file."""
        raise NotImplementedError("read_bin() is not yet implemented.")

    @track_kwargs
    def _read_dat(
        self, filename: str, _check: bool = True, **kwargs: Any
    ) -> dict[str, Any]:
        """Read data from a dat file."""
        try:
            pathh5 = self.state.pathdir / Path(filename)
        except FileNotFoundError:
            pathh5 = Path(filename)

        names = kwargs.get("names", True)
        skip = kwargs.get("skip", 0)

        data = np.genfromtxt(str(pathh5), names=names, skip_header=skip)
        if names:
            loop = data.dtype.names
            if loop is None:
                return {}
            analysis = {name: data[name] for name in loop}
        else:
            loop = range(data.shape[1])
            analysis = {f"col_{i}": data[:, i] for i in loop}

        return analysis

    @track_kwargs
    def read_file(
        self,
        filename: str,
        datatype: str | None = None,
        _check: bool = True,
        **kwargs: Any,
    ) -> Any:
        """Read data from output files."""
        if datatype is None:
            datatype = filename.rsplit(".", maxsplit=1)[-1]

        readers = {
            "h5": self._read_h5,
            "dat": self._read_dat,
            "vtk": self._read_vtk,
            "tab": self._read_tab,
            "dbl": self._read_bin,
            "flt": self._read_bin,
        }
        reader = readers.get(datatype)

        if reader is None:
            warn = f"Invalid datatype: {datatype}. Resetting to 'h5'"
            warnings.warn(warn, UserWarning, stacklevel=2)
            return self._read_h5(filename, _check=False, **kwargs)

        if datatype in {"h5", "dat"}:
            return reader(filename, _check=False, **kwargs)

        warn = (
            f"Invalid datatype: {datatype}, not implemented yet! "
            "Resetting to 'h5'"
        )
        warnings.warn(warn, UserWarning, stacklevel=2)
        return self._read_h5(filename, _check=False, **kwargs)
