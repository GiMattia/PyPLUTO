"""Module to load the data from the output files of the ECHO code."""

import warnings
from typing import cast

import h5py


def echo_load(
    self,
    nout: int | str | list | None,
    path: str,
    vars: str | list[str] | bool | None = True,
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
    # Check the path and convert it to a Path object
    self._check_pathformat(path)

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

    self._echo_load_grid(conv_dict)
    self._echo_set_grid_dims()

    self.nout = nout if nout != "last" else 0
    file = self.pathdir / f"out{self.nout:03d}.h5"

    with h5py.File(file, "r") as tmp:
        self.ntime = cast(h5py.Dataset, tmp["time"])[()][0]
        vars = list(tmp.keys()) if vars is True else vars or []
        self._echo_load_vars(tmp, conv_dict, vars)


def _echo_load_grid(self, conv_dict: dict[str, str]) -> None:
    """Load grid.h5 and set attributes."""
    with h5py.File(self.pathdir / "grid.h5", "r") as grid:
        for key, obj in grid.items():
            if not isinstance(obj, h5py.Dataset):
                continue
            data = obj[()]
            name = conv_dict.get(key, key)
            if name is not None:
                setattr(self, name, data)


def _echo_set_grid_dims(self) -> None:
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


def _echo_load_vars(
    self, tmp: h5py.File, conv_dict: dict[str, str], vars: list[str]
) -> None:
    """Load variables from output file."""
    for key in vars:
        if key == "time":
            continue
        valkey = next((k for k, v in conv_dict.items() if v == key), key)
        obj = tmp.get(valkey)
        if not isinstance(obj, h5py.Dataset):
            warnings.warn(
                f"'{valkey}' not a dataset (found {type(obj)})", stacklevel=2
            )
            continue
        var = obj[()]
        for dim in [self.nx3, self.nx2, self.nx1]:
            if dim == 1:
                var = var[0]
        setattr(self, conv_dict.get(valkey, valkey), var.T)
