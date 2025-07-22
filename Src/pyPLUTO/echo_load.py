import h5py


def echo_load(self, nout, path, vars):
    """Method to load the data from the output files of the ECHO code.
    The data are loaded only from h5 files and only a single output is
    possible. Note that binary files produced by ECHO are not supported
    by this method. The data are loaded in the PLUTO format, so the
    variables are renamed to match the PLUTO naming convention.

    Returns
    -------
    - None

    Parameters
    ----------
    - nout: int | str | list | None, default 0
        The output number to be loaded.
    - path: str, default './'
        The path to the folder containing the data files.
    - vars: str | list[str] | bool | None, default True
        The variables to be loaded. If 'True', all the variables are loaded.

    """
    # Check the path and convert it to a Path object
    self._check_pathformat(path)

    # Geometry is set to CARTESIAN by default
    self.geom = "CARTESIAN"

    # DIctionary to convert the keys from ECHO to PLUTO
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

    # Opwn te grid file and load the grid data
    grid = h5py.File(self.pathdir / "grid.h5", "r")
    for key in grid.keys():
        # Check if the key is in the dictionary and convert it
        if key in conv_dict:
            setattr(self, conv_dict[key], grid[key][:])

        # If the key is not in the dictionary, simply store the data
        else:
            setattr(self, key, grid[key][:])

    # Close the grid file
    grid.close()

    # Set the number of grid points in each direction (nx1, nx2, nx3)
    for dim in ["x1", "x2", "x3"]:
        # Check if the variable exists and store the number of grid points
        if hasattr(self, dim) is True:
            setattr(self, f"n{dim}", len(getattr(self, dim)))

        # If the variable does not exist, set the number of grid points to 1
        else:
            setattr(self, f"n{dim}", 1)

    # Compute the dimensios and the grid size
    self.dim = (self.nx1 > 1) + (self.nx2 > 1) + (self.nx3 > 1)
    self.gridsize = self.nx1 * self.nx2 * self.nx3

    # Set the number of grid points in each direction (nx1, nx2, nx3)
    dim_dict = {
        1: self.nx1,
        2: (self.nx1, self.nx2),
        3: (self.nx1, self.nx2, self.nx3),
    }

    # Set the grid shape
    self.nshp = dim_dict[self.dim]

    # Find the output file number and compute the full path to the file
    self.nout = nout if nout != "last" else 0
    file = self.pathdir / f"out{self.nout:03d}.h5"

    # Open the output file
    tmp = h5py.File(file, "r")

    # Set the time (in PLUTO format)
    self.ntime = tmp["time"][...][0]

    # Check if only selected vars should be loaded or the entire file
    vars = list(tmp.keys()) if vars is True else vars

    # Loop on the vars to load
    for key in vars:
        # Skip the time variable
        if key == "time":
            continue

        # Check if the variable has been requested in ECHO or PLUTO format
        valkey = next((k for k, v in conv_dict.items() if v == key), None)
        valkey = key if valkey is None else valkey

        # Load the variable and resize it to the grid shape
        var = tmp[valkey][:]
        [var := var[0] for dim in [self.nx3, self.nx2, self.nx1] if dim == 1]

        # Check if the variable is in the dictionary and convert it
        if valkey in conv_dict:
            setattr(self, conv_dict[valkey], var.T)

        # If the variable is not in the dictionary, simply store the data
        elif valkey in tmp.keys():
            setattr(self, valkey, var.T)

        # Delete the temporary variable
        del var

    # Close the output file
    tmp.close()

    # End of the function
