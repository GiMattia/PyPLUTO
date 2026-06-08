"""Module to load the data from the output files of the ECHO code."""

from __future__ import annotations

import warnings
from pathlib import Path
from typing import cast

import h5py

from pyPLUTO.loadmixin import LoadMixin
from pyPLUTO.loadstate import LoadState
from pyPLUTO.utils.inspector import track_kwargs


class EchoLoadManager(LoadMixin):
    """Manager for loading output data produced by the ECHO MHD code.

    Data are read exclusively from HDF5 files and variable names are
    remapped to the PLUTO naming convention (e.g. ``rh`` becomes ``rho``,
    ``bx`` becomes ``Bx1``).
    """

    def __init__(self, state: LoadState) -> None:
        """Initialize the EchoLoadManager with the given load state."""
        self.state = state

    @track_kwargs
    def load_echo(
        self,
        nout: int | str | list[int | str] | None,
        loadvars: str | list[str] | bool | None,
        _check: bool = True,
    ) -> None:
        """Load data from an ECHO HDF5 output file.

        Only HDF5 output is supported. Binary files produced by ECHO are
        not read by this method. A single output number is loaded at a time;
        if a list or string is given the first valid integer is used and a
        warning is raised otherwise.

        Parameters
        ----------
        - loadvars: str | list[str] | np.ndarray | bool | None, default True
            The variable to be loaded / plotted. When loading, it selects the
            variables (True loads all, or pass a string or list for a subset);
            when plotting, it is the array to display.
        - nout: int | list | None
            The output number to load. If a string or None is given the
            output defaults to 0 and a warning is raised.
        - vars: to be deprecated!

        Returns
        -------
        - None

        Examples
        --------
        - Example #1: Load all variables from output 3

            >>> EchoLoadManager = pp.EchoLoadManager(state)
            >>> EchoLoadManager.load_echo(nout=3, loadvars=True)

        """
        # ECHO always produces Cartesian geometry output
        self.state.geom = "CARTESIAN"

        # Mapping from ECHO field names to PLUTO naming convention
        conv_dict = {
            "x": "x1",
            "y": "x2",
            "z": "x3",
            "rh": "rho",
            "pg": "prs",
            "se": "ent",
            "vx": "vx1",
            "vy": "vx2",
            "vz": "vx3",
            "bx": "Bx1",
            "by": "Bx2",
            "bz": "Bx3",
            "ex": "Ex1",
            "ey": "Ex2",
            "ez": "Ex3",
        }

        # Load grid coordinates and derive dimension metadata
        self.echo_load_grid(conv_dict)
        self.echo_set_grid_dims()

        # Resolve the output number — fall back to 0 for invalid inputs
        if isinstance(nout, str) or nout is None:
            warnings.warn(
                "Please specify the output, it will now be set to 0.",
                stacklevel=2,
            )
            self.state.nout = 0
        elif isinstance(nout, list):
            if isinstance(nout[0], int):
                self.state.nout = nout[0]
            else:
                warnings.warn(
                    "Please specify the output or it will be set to 0.",
                    stacklevel=2,
                )
                self.state.nout = 0
        else:
            self.state.nout = nout

        # Construct the file path
        file = self.state.pathdir / Path(f"out{self.state.nout:03d}.h5")

        with h5py.File(str(file), "r") as tmp:
            # Read simulation time from the output file
            self.state.ntime = cast("h5py.Dataset", tmp["time"])[()][0]

            # Populate varslist: HDF5 keys except "time", mapped to PLUTO names
            all_vars = [conv_dict.get(k, k) for k in tmp if k != "time"]
            self.state.d_info["varslist"] = [all_vars]

            # Build the list of variable names to load
            if loadvars is True:
                var: list[str] = list(tmp.keys())
            elif isinstance(loadvars, str):
                var = [loadvars]
            elif isinstance(loadvars, list):
                var = [str(v) for v in loadvars]
            else:
                var = []

            self.echo_load_vars(tmp, conv_dict, var)

    def echo_load_grid(self, conv_dict: dict[str, str]) -> None:
        """Load the ECHO grid from ``grid.h5`` and set coordinate attributes.

        Each dataset in ``grid.h5`` is remapped through ``conv_dict`` and
        stored as an attribute on the manager (e.g. ``self.x1``, ``self.x2``).

        Parameters
        ----------
        - conv_dict: dict[str, str]
            Mapping from ECHO variable names to PLUTO variable names.

        Returns
        -------
        - None

        Examples
        --------
        - Example #1: Load grid coordinates

            >>> EchoLoadManager = pp.EchoLoadManager(state)
            >>> EchoLoadManager.echo_load_grid(conv_dict)

        """
        with h5py.File(str(self.state.pathdir / Path("grid.h5")), "r") as grid:
            # Load grid coordinates and map them to PLUTO naming convention
            for key, obj in grid.items():
                if not isinstance(obj, h5py.Dataset):
                    continue
                data = obj[()]
                name = conv_dict.get(key, key)
                if name is not None:
                    setattr(self, name, data)

    def echo_set_grid_dims(self) -> None:
        """Derive grid dimension attributes from the loaded coordinate arrays.

        Sets ``nx1``, ``nx2``, ``nx3`` (number of cells per direction),
        ``dim`` (number of active dimensions), ``gridsize`` (total cell count)
        and ``nshp`` (shape tuple used for array reshaping).


        Returns
        -------
        - None

        Examples
        --------
        - Example #1: Derive the grid dimensions

            >>> EchoLoadManager = pp.EchoLoadManager(state)
            >>> EchoLoadManager.echo_set_grid_dims()
        """
        # Count cells along each direction (1 if the coordinate is absent)
        for dim in ["x1", "x2", "x3"]:
            n = len(getattr(self, dim)) if hasattr(self, dim) else 1
            setattr(self, f"n{dim}", n)

        # Number of active spatial dimensions
        self.state.dim = (
            (self.state.nx1 > 1) + (self.state.nx2 > 1) + (self.state.nx3 > 1)
        )
        self.state.gridsize = self.state.nx1 * self.state.nx2 * self.state.nx3

        # Shape tuple depends on the number of active dimensions
        dim_dict = {
            1: self.state.nx1,
            2: (self.state.nx1, self.state.nx2),
            3: (self.state.nx1, self.state.nx2, self.state.nx3),
        }
        self.state.nshp = dim_dict[self.state.dim]

    def echo_load_vars(
        self,
        tmp: h5py.File,
        conv_dict: dict[str, str],
        var: list[str],
    ) -> None:
        """Load and store variables from an open ECHO HDF5 output file.

        Each requested variable is looked up in the file using the reverse
        of ``conv_dict``, squeezed along any unit-length dimension, transposed
        to Fortran (column-major) order and stored on ``self.state``.

        Parameters
        ----------
        - tmp: h5py.File
            Open HDF5 file handle for the output snapshot.
        - conv_dict: dict[str, str]
            Mapping from ECHO variable names to PLUTO variable names.
        - var: list[str]
            List of PLUTO variable names to load.

        Returns
        -------
        - None

        Examples
        --------
        - Example #1: Load variables

            >>> EchoLoadManager = pp.EchoLoadManager(state)
            >>> EchoLoadManager.echo_load_vars(tmp, conv_dict, var)
        """
        for key in var:
            if key == "time":
                continue

            # Reverse-look up the ECHO key for this PLUTO variable name
            valkey = next((k for k, v in conv_dict.items() if v == key), key)
            obj = tmp.get(valkey)

            # If the object is not a dataset, warn the user and create
            # an empty dataset
            if not isinstance(obj, h5py.Dataset):
                warnings.warn(
                    f"'{valkey}' not a dataset (found {type(obj)})",
                    stacklevel=2,
                )
                continue

            loadvar = obj[()]

            # Squeeze unit-length dimensions (innermost first)
            for dim in [self.state.nx3, self.state.nx2, self.state.nx1]:
                if dim == 1:
                    loadvar = loadvar[0]

            # Transpose to match PLUTO's column-major convention
            varname = conv_dict.get(valkey, valkey)
            setattr(self.state, varname, loadvar.T)
            self.state.d_vars[varname] = loadvar.T
