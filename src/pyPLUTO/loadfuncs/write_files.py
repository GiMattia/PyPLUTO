"""Module for writing external files."""

import warnings
from pathlib import Path
from typing import Any

import h5py
import numpy as np

from pyPLUTO.loadmixin import LoadMixin
from pyPLUTO.loadstate import LoadState
from pyPLUTO.utils.inspector import track_kwargs


class WriteFilesManager(LoadMixin):
    """Class that manages writing data to external files."""

    def __init__(self, state: LoadState) -> None:
        """Initialize the file-writing manager with the given load state."""
        self.state = state

    @track_kwargs
    def _write_h5(
        self,
        data: np.ndarray | dict,
        filename: str,
        dataname: str | None = None,
        grid: bool = False,
        **kwargs: Any,
    ) -> None:
        """Write data to an HDF5 file.

        Parameters
        ----------
        - data: np.ndarray | dict
            The data to write.
        - dx1: np.ndarray
            The grid spacing in the x1 direction
        - dx2: np.ndarray
            The grid spacing in the x2 direction
        - dx3: np.ndarray
            The grid spacing in the x3 direction
        - filename: str
            The name of the file to write to.
        - dataname: str | None
            The name of the dataset to create.
        - grid: bool
            Whether to write grid data.
        - nx1: int
            The number of points in the x1 direction.
        - nx2: int
            The number of points in the x2 direction.
        - nx3: int
            The number of points in the x3 direction.
        - x1: np.ndarray
            The x1 grid points.
        - x2: np.ndarray
            The x2 grid points.
        - x3: np.ndarray
            The x3 grid points.

        Returns
        -------
        - None
        """
        path_h5 = self.state.pathdir / Path(filename)
        if not filename.endswith(".h5"):
            path_h5 = f"{path_h5}.h5"

        with h5py.File(str(path_h5), "w") as f:
            if isinstance(data, dict):
                for key in data:
                    f.create_dataset(key, data=data[key])
            else:
                dataname = "data" if dataname is None else dataname
                f.create_dataset(dataname, data=data)

            if grid is True:
                f.create_dataset("nx1", data=kwargs.get("nx1", self.state.nx1))
                f.create_dataset("nx2", data=kwargs.get("nx2", self.state.nx2))
                f.create_dataset("nx3", data=kwargs.get("nx3", self.state.nx3))
                f.create_dataset("x1", data=kwargs.get("x1", self.state.x1))
                f.create_dataset("x2", data=kwargs.get("x2", self.state.x2))
                f.create_dataset("x3", data=kwargs.get("x3", self.state.x3))
                f.create_dataset("dx1", data=kwargs.get("dx1", self.state.dx1))
                f.create_dataset("dx2", data=kwargs.get("dx2", self.state.dx2))
                f.create_dataset("dx3", data=kwargs.get("dx3", self.state.dx3))

    @track_kwargs
    def _write_vtk(
        self,
        data: np.ndarray | dict,
        filename: str,
        dataname: str | None = None,
        grid: bool = False,
        **kwargs: Any,
    ) -> None:
        """Write data to a VTK file."""
        raise NotImplementedError("write_vtk() is not yet implemented.")

    @track_kwargs
    def _write_tab(
        self,
        data: np.ndarray | dict,
        filename: str,
        dataname: str | None = None,
        grid: bool = False,
        **kwargs: Any,
    ) -> None:
        """Write data to a tab-separated file."""
        raise NotImplementedError("write_tab() is not yet implemented.")

    @track_kwargs
    def _write_bin(
        self,
        data: np.ndarray | dict,
        filename: str,
        dataname: str | None = None,
        grid: bool = False,
        **kwargs: Any,
    ) -> None:
        """Write data to a binary file."""
        raise NotImplementedError("write_bin() is not yet implemented.")

    @track_kwargs
    def write_file(
        self,
        data: np.ndarray | dict,
        filename: str,
        datatype: str | None = None,
        dataname: str | None = None,
        grid: bool = False,
        **kwargs: Any,
    ) -> None:
        """Write the input data to a file."""
        if datatype is None:
            datatype = filename.rsplit(".", maxsplit=1)[-1]
        writers = {
            "h5": self._write_h5,
            "vtk": self._write_vtk,
            "tab": self._write_tab,
            "dbl": self._write_bin,
            "flt": self._write_bin,
        }
        writer = writers.get(datatype)

        if writer is None:
            warn = f"Invalid datatype: {datatype}. Resetting to 'h5'"
            warnings.warn(warn, UserWarning, stacklevel=2)
            self._write_h5(data, filename, dataname, grid, **kwargs)
            return

        if datatype != "h5":
            warn = (
                f"Invalid datatype: {datatype}, not implemented yet! "
                "Resetting to 'h5'"
            )
            warnings.warn(warn, UserWarning, stacklevel=2)
            self._write_h5(data, filename, dataname, grid, **kwargs)
            return

        writer(data, filename, dataname, grid, **kwargs)
