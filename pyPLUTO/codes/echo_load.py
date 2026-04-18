"""Module to load the data from the output files of the ECHO code."""

import warnings
from pathlib import Path
from typing import Any, cast

import h5py

from pyPLUTO.loadmixin import LoadMixin
from pyPLUTO.loadstate import LoadState
from pyPLUTO.utils.inspector import track_kwargs


@track_kwargs
class EchoLoadManager(LoadMixin):
    """Manager for the loading of the ECHO code data."""

    @track_kwargs
    def __init__(self, state: LoadState) -> None:
        """Initialize the EchoLoadManager."""
        self.state = state

    def load_echo(
        self, nout: int | str | list[int | str] | None, **kwargs: Any
    ) -> None:
        """Load the data from the output files of the ECHO code.

        The data are loaded only from h5 files and only a single output is
        possible. Note that binary files produced by ECHO are not supported
        by this method. The data are loaded in the PLUTO format, so the
        variables are renamed to match the PLUTO naming convention.

        Parameters
        ----------
        - nout: int | str | list | None, default 0
            The output number to be loaded.
        - path: str, default './'
            The path to the folder containing the data files.
        - vars: str | list[str] | bool | None, default True
            The variables to be loaded. If 'True', all the variables are loaded.

        Returns
        -------
        - None

        Examples
        --------
        Example 1: Load all the variables from the last output in the current
        folder.

        >>> NOT IMPLEMENTED YET

        """
        print("load, echo")

        # Geometry is set to CARTESIAN by default
        self.geom = "CARTESIAN"

        # Dictionary to convert the keys from ECHO to PLUTO
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

        self.echo_load_grid(conv_dict)
        self.echo_set_grid_dims()

        if isinstance(nout, str) or nout is None:
            warnings.warn(
                "Please specify the output or it will be set to 0.",
                stacklevel=2,
            )
            self.nout = 0
        elif isinstance(nout, list):
            if isinstance(nout[0], int):
                self.nout = nout[0]
            else:
                warnings.warn(
                    "Please specify the output or it will be set to 0.",
                    stacklevel=2,
                )
                self.nout = 0
        else:
            self.nout = nout

        file = self.pathdir / Path(f"out{self.nout:03d}.h5")

        loadvars = True
        if kwargs.get("vars") is not None:
            warnings.warn(
                "'vars' argument is deprecated. Use 'var' instead.",
                DeprecationWarning,
                stacklevel=2,
            )
            loadvars = kwargs.get("vars", loadvars)
        loadvars = kwargs.get("var", loadvars)

        with h5py.File(str(file), "r") as tmp:
            self.ntime = cast(h5py.Dataset, tmp["time"])[()][0]
            var = list(tmp.keys()) if loadvars is True else loadvars or []
            self.echo_load_vars(tmp, conv_dict, var)

    def echo_load_grid(self, conv_dict: dict[str, str]) -> None:
        """Load grid.h5 and set attributes."""
        with h5py.File(str(self.pathdir / Path("grid.h5")), "r") as grid:
            for key, obj in grid.items():
                if not isinstance(obj, h5py.Dataset):
                    continue
                data = obj[()]
                name = conv_dict.get(key, key)
                if name is not None:
                    setattr(self, name, data)

    def echo_set_grid_dims(self) -> None:
        """Compute nx1, nx2, nx3, dim, gridsize, nshp."""
        for dim in ["x1", "x2", "x3"]:
            n = len(getattr(self, dim)) if hasattr(self, dim) else 1
            setattr(self, f"n{dim}", n)

        self.dim = (self.nx1 > 1) + (self.nx2 > 1) + (self.nx3 > 1)
        self.gridsize = self.nx1 * self.nx2 * self.nx3
        dim_dict = {
            1: self.nx1,
            2: (self.nx1, self.nx2),
            3: (self.nx1, self.nx2, self.nx3),
        }
        self.nshp = dim_dict[self.dim]

    def echo_load_vars(
        self, tmp: h5py.File, conv_dict: dict[str, str], var: list[str]
    ) -> None:
        """Load variables from output file."""
        for key in var:
            if key == "time":
                continue
            valkey = next((k for k, v in conv_dict.items() if v == key), key)
            obj = tmp.get(valkey)
            if not isinstance(obj, h5py.Dataset):
                warnings.warn(
                    f"'{valkey}' not a dataset (found {type(obj)})",
                    stacklevel=2,
                )
                continue
            loadvar = obj[()]
            for dim in [self.nx3, self.nx2, self.nx1]:
                if dim == 1:
                    loadvar = loadvar[0]
            setattr(self.state, conv_dict.get(valkey, valkey), loadvar.T)
