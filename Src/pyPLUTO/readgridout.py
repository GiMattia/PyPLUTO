import warnings

import numpy as np
import pandas as pd


def _read_grid_h5(self) -> None:
    """Read the grid from a .h5 file.

    Returns
    -------
    - None

    Parameters
    ----------
    - None

    ----

    Examples
    --------
    - Example #1: Read the grid from a .h5 file

        >>> _read_grid_h5()

    """
    #  Variables that we already have: x1 x2 x3 x1r x2r x3r
    #  Variables that we need: nx1 nx2 nx3 nshp nx1s nx2s nx3s dim
    #                          nshp_st1 nshp_st2 nshp_st3
    #                          gridsize gridsize_st1 gridsize_st2 gridsize_st3
    self.nshp = np.shape(self.x1)
    self.dim = len(self.nshp)
    self.geom = "UNKNOWN"
    self.nx1, self.nx2, self.nx3 = (self.nshp + (1, 1, 1))[:3]
    nx1s, nx2s, nx3s = self.nx1 + 1, self.nx2 + 1, self.nx3 + 1

    GRID_SHAPES = {
        1: lambda nx1, _, __: (nx1s, None, None),
        2: lambda nx1, nx2, _: ((nx2, nx1s), (nx2s, nx1), None),
        3: lambda nx1, nx2, nx3: (
            (nx3, nx2, nx1s),
            (nx3, nx2s, nx1),
            (nx3s, nx2, nx1),
        ),
    }

    # Determine grid shape based on dimension
    (self._nshp_st1, self._nshp_st2, self._nshp_st3) = GRID_SHAPES[self.dim](
        self.nx1, self.nx2, self.nx3
    )

    # Grid spacing has been removed from the .h5 file
    """
    self.dx1 = self.x1r[1:] - self.x1r[:-1]
    self.dx1 = 0.5*(self.dx1[:, 1:] + self.dx1[:, :-1]) if self.dim > 1 else self.dx1
    self.dx1 = 0.5*(self.dx1[:, :, 1:] + self.dx1[:, :, :-1]) if self.dim > 2 else self.dx1

    self.dx2 = self.x2r[1:] - self.x2r[:-1]
    self.dx2 = 0.5*(self.dx2[:, 1:] + self.dx2[:, :-1]) if self.dim > 1 else self.dx2
    self.dx2 = 0.5*(self.dx2[:, :, 1:] + self.dx2[:, :, :-1]) if self.dim > 2 else self.dx2

    self.dx3 = self.x3r[1:] - self.x3r[:-1]
    self.dx3 = 0.5*(self.dx3[:, 1:] + self.dx3[:, :-1]) if self.dim > 1 else self.dx3
    self.dx3 = 0.5*(self.dx3[:, :, 1:] + self.dx3[:, :, :-1]) if self.dim > 2 else self.dx3
    """

    # Compute the gridsize both centered and staggered
    self.gridsize = self.nx1 * self.nx2 * self.nx3
    self._gridsize_st1 = nx1s * self.nx2 * self.nx3
    self._gridsize_st2 = self.nx1 * nx2s * self.nx3
    self._gridsize_st3 = self.nx1 * self.nx2 * nx3s

    warn = (
        "The geometry is unknown, therefore the grid spacing has not been "
        "computed. \nFor a more accurate grid analysis, the loading with "
        "the .out file is recommended.\n"
    )
    warnings.warn(warn, UserWarning)


def _read_grid_vtk(self, gridvars) -> None:
    """Read the grid from a .vtk file.

    Returns
    -------
    - None

    Parameters
    ----------
    - gridvars (not optional): list[str]
        The list of grid variables.

    ----

    Examples
    --------
    - Example #1: Read the grid from a vtk file

        >>> _read_grid_vtk(['self.x1r', 'self.x2r', 'self.x3r'])

    """
    # - RECTILINEAR GRID
    #   Variables that we already have: x1r x2r x3r nshp dim nx1 nx2 nx3
    #   Variables that we need: x1 x2 x3 dx1 dx2 dx3  gridsize

    self.gridsize = self.nx1 * self.nx2 * self.nx3

    if self.geom == "UNKNOWN":

        if gridvars[0] == "self.x1r":
            self.x1 = 0.5 * (self.x1r[1:] + self.x1r[:-1])
            self.x1 = (
                0.5 * (self.x1[:, 1:] + self.x1[:, :-1])
                if self.dim > 1
                else self.x1
            )
            self.x1 = (
                0.5 * (self.x1[:, :, 1:] + self.x1[:, :, :-1])
                if self.dim > 2
                else self.x1
            )

            # self.dx1 = self.x1r[1:] - self.x1r[:-1]
            # self.dx1 = 0.5*(self.dx1[:, 1:] + self.dx1[:, :-1]) if self.dim > 1 else self.dx1
            # self.dx1 = 0.5*(self.dx1[:, :, 1:] + self.dx1[:, :, :-1]) if self.dim > 2 else self.dx1

        if gridvars[1] == "self.x2r":
            self.x2 = 0.5 * (self.x2r[1:] + self.x2r[:-1])
            self.x2 = 0.5 * (self.x2[:, 1:] + self.x2[:, :-1])
            self.x2 = (
                0.5 * (self.x2[:, :, 1:] + self.x2[:, :, :-1])
                if self.dim > 2
                else self.x2
            )

            # self.dx2 = self.x2r[1:] - self.x2r[:-1]
            # self.dx2 = 0.5*(self.dx2[:, 1:] + self.dx2[:, :-1])
            # self.dx2 = 0.5*(self.dx2[:, :, 1:] + self.dx2[:, :, :-1]) if self.dim > 2 else self.dx2

        if gridvars[2] == "self.x3r":
            self.x3 = 0.5 * (self.x3r[1:] + self.x3r[:-1])
            self.x3 = 0.5 * (self.x3[:, 1:] + self.x3[:, :-1])
            self.x3 = 0.5 * (self.x3[:, :, 1:] + self.x3[:, :, :-1])

            # self.dx3 = self.x3r[1:] - self.x3r[:-1]
            # self.dx3 = 0.5*(self.dx3[:, 1:] + self.dx3[:, :-1])
            # self.dx3 = 0.5*(self.dx3[:, :, 1:] + self.dx3[:, :, :-1])

        warn = (
            "The geometry is unknown, therefore the grid spacing has not been "
            "computed. \nFor a more accurate grid analysis, the loading with "
            "the .out file is recommended.\n"
        )
        warnings.warn(warn, UserWarning)

        return None

    if gridvars[0] == "self.x1r":
        self.x1 = 0.5 * (self.x1r[:-1] + self.x1r[1:])
        self.dx1 = self.x1r[1:] - self.x1r[:-1]
    if gridvars[1] == "self.x2r":
        self.x2 = 0.5 * (self.x2r[:-1] + self.x2r[1:])
        self.dx2 = self.x2r[1:] - self.x2r[:-1]
    if gridvars[2] == "self.x3r":
        self.x3 = 0.5 * (self.x3r[:-1] + self.x3r[1:])
        self.dx3 = self.x3r[1:] - self.x3r[:-1]

    return None


def _read_gridfile(self) -> None:
    """The file grid.out is read and all the grid information are stored
    in the Load class. Such information are the dimensions, the
    geometry, the center and edges of each cell, the grid shape and size
    and, in case of non cartesian coordinates, the transformed cartesian
    coordinates (only 2D for now).bThe full non-cartesian 3D
    transformations have not been implemented yet.

    Returns
    -------
    - None

    Parameters
    ----------
    - None

    ----

    Examples
    --------
    - Example #1: read the grid file

        >>> _read_gridfile()

    """
    # Initialize relevant lists
    nmax, xL, xR = [], [], []

    # Open and read the gridfile
    with open(self._pathgrid) as gfp:
        for i in gfp.readlines():
            self._split_gridfile(i, xL, xR, nmax)

    # Compute nx1, nx2, nx3
    self.nx1, self.nx2, self.nx3 = nmax
    nx1p2 = self.nx1 + self.nx2
    nx1p3 = self.nx1 + self.nx2 + self.nx3

    # Define grid shapes based on dimensions
    nx1s, nx2s, nx3s = self.nx1 + 1, self.nx2 + 1, self.nx3 + 1
    GRID_SHAPES = {
        1: lambda nx1, _, __: (nx1, nx1s, None, None),
        2: lambda nx1, nx2, _: ((nx2, nx1), (nx2, nx1s), (nx2s, nx1), None),
        3: lambda nx1, nx2, nx3: (
            (nx3, nx2, nx1),
            (nx3, nx2, nx1s),
            (nx3, nx2s, nx1),
            (nx3s, nx2, nx1),
        ),
    }

    # Determine grid shape based on dimension
    (self.nshp, self._nshp_st1, self._nshp_st2, self._nshp_st3) = GRID_SHAPES[
        self.dim
    ](self.nx1, self.nx2, self.nx3)

    # Compute the centered and staggered grid values
    self.x1r = np.array(xL[0 : self.nx1] + [xR[self.nx1 - 1]])
    self.x1 = 0.5 * (self.x1r[:-1] + self.x1r[1:])
    self.dx1 = self.x1r[1:] - self.x1r[:-1]

    self.x2r = np.array(xL[self.nx1 : nx1p2] + [xR[nx1p2 - 1]])
    self.x2 = 0.5 * (self.x2r[:-1] + self.x2r[1:])
    self.dx2 = self.x2r[1:] - self.x2r[:-1]

    self.x3r = np.array(xL[nx1p2:nx1p3] + [xR[nx1p3 - 1]])
    self.x3 = 0.5 * (self.x3r[:-1] + self.x3r[1:])
    self.dx3 = self.x3r[1:] - self.x3r[:-1]

    # Compute the cartesian grid coordinates (non-cartesian geometry)

    if self.geom == "POLAR":

        x1_2D, x2_2D = np.meshgrid(self.x1, self.x2, indexing="ij")
        x1r_2D, x2r_2D = np.meshgrid(self.x1r, self.x2r, indexing="ij")

        self.x1c = (np.cos(x2_2D) * x1_2D).T
        self.x2c = (np.sin(x2_2D) * x1_2D).T
        self.x1rc = (np.cos(x2r_2D) * x1r_2D).T
        self.x2rc = (np.sin(x2r_2D) * x1r_2D).T

        self.gridlist3 = ["x1c", "x2c", "x1rc", "x2rc"]
        del x1_2D, x2_2D, x1r_2D, x2r_2D
    elif self.geom == "SPHERICAL":
        x1_2D, x2_2D = np.meshgrid(self.x1, self.x2, indexing="ij")
        x1r_2D, x2r_2D = np.meshgrid(self.x1r, self.x2r, indexing="ij")

        self.x1p = (np.sin(x2_2D) * x1_2D).T
        self.x2p = (np.cos(x2_2D) * x1_2D).T
        self.x1rp = (np.sin(x2r_2D) * x1r_2D).T
        self.x2rp = (np.cos(x2r_2D) * x1r_2D).T

        x1_2D, x3_2D = np.meshgrid(self.x1, self.x3, indexing="ij")
        x1r_2D, x3r_2D = np.meshgrid(self.x1r, self.x3r, indexing="ij")

        self.x1t = (np.cos(x3_2D) * x1_2D).T
        self.x3t = (np.sin(x3_2D) * x1_2D).T
        self.x1rt = (np.cos(x3r_2D) * x1r_2D).T
        self.x3rt = (np.sin(x3r_2D) * x1r_2D).T

        self.gridlist3 = [
            "x1p",
            "x2p",
            "x1rp",
            "x2rp",
            "x1t",
            "x3t",
            "x1rt",
            "x3rt",
        ]

        del x1_2D, x2_2D, x1r_2D, x2r_2D, x3_2D, x3r_2D

        if self.dim == 3 and self._full3d is True:

            x1_3D, x2_3D, x3_3D = np.meshgrid(
                self.x1, self.x2, self.x3, indexing="ij"
            )
            x1r_3D, x2r_3D, x3r_3D = np.meshgrid(
                self.x1r, self.x2r, self.x3r, indexing="ij"
            )

            self.x1c = (np.sin(x2_3D) * np.cos(x3_3D) * x1_3D).T
            self.x2c = (np.sin(x2_3D) * np.sin(x3_3D) * x1_3D).T
            self.x3c = (np.cos(x2_3D) * x1_3D).T
            self.x1rc = (np.sin(x2r_3D) * np.cos(x3r_3D) * x1r_3D).T
            self.x2rc = (np.sin(x2r_3D) * np.sin(x3r_3D) * x1r_3D).T
            self.x3rc = (np.cos(x2r_3D) * x1r_3D).T

            del x1_3D, x2_3D, x3_3D, x1r_3D, x2r_3D, x3r_3D
        else:
            pass
            # self.x1c = np.zeros((self.nx1,self.nx2,self.nx3))
            # print(np.shape(self.x1c))
            # self.pippo = np.meshgrid(self.x2, self.x3, indexing='xy')
            # print(np.shape(self.pippo))

    # Compute the gridsize both centered and staggered
    self.gridsize = self.nx1 * self.nx2 * self.nx3
    self._gridsize_st1 = nx1s * self.nx2 * self.nx3
    self._gridsize_st2 = self.nx1 * nx2s * self.nx3
    self._gridsize_st3 = self.nx1 * self.nx2 * nx3s

    self._info = False


def _read_outfile(self, nout: int, endian: str) -> None:
    """Reads the datatype.out file and stores the relevant information
    within the class. Such information are the time array, the output
    variables, the file type (single or multiples), the endianess, the
    simulation path and the bin format. All these information are
    relevant in order to open the output files and access the data.

    Returns
    -------
    - None

    Parameters
    ----------
    - endian (not optional): str
        The endianess of the files.
    - nout (not optional): int
        The output file to be opened. If default ('last'), the code assumes the
        last file should be opened. Other options available are 'last' (all the
        files should be opened) and -1 (same as 'last').

    ----

    Examples
    --------
    - Example #1: Read the 'filetype'.out file

        >>> _read_outfile(0, 'big')

    """
    # Open and read the 'filetype'.out file
    vfp = pd.read_csv(str(self._pathdata), sep=r"\s+", header=None)

    # Store the output and the time full list
    self.outlist = np.array(vfp.iloc[:, 0], dtype="int")
    self.timelist = np.array(vfp.iloc[:, 1])

    # Check the output lines
    self._check_nout(nout)
    self.ntime = self.timelist[self.nout]
    self._lennout = len(self.nout)

    # Initialize the info dictionary
    self._d_info = {
        "typefile": np.array(vfp.iloc[self.nout, 4]),
        "endianess": np.where(vfp.iloc[self.nout, 5] == "big", ">", "<"),
    }

    # Compute the endianess (vtk have always big endianess).
    # If endian is given, it is used instead of the one in the file.
    self._d_info["endianess"][:] = (
        ">" if self.format == "vtk" else self._d_info["endianess"]
    )
    self._d_info["endianess"][:] = (
        self._d_end[endian] if endian is not None else self._d_info["endianess"]
    )

    # Store the variables list
    if self.format not in {"dbl.h5", "flt.h5"}:
        self._d_info["varslist"] = np.array(vfp.iloc[self.nout, 6:])
    else:
        self.varsh5 = np.array(vfp.iloc[self.nout, 6:])[0]
        self._d_info["varslist"] = [[] for _ in range(self._lennout)]

    # Compute binformat and endpath
    self._d_info["binformat"] = np.char.add(
        self._d_info["endianess"], "f" + str(self._charsize)
    )
    format_string = f".%04d.{self.format}"
    self._d_info["endpath"] = np.char.mod(format_string, self.nout)


def _split_gridfile(
    self, i: str, xL: list[float], xR: list[float], nmax: list[int]
) -> None:
    """Splits the gridfile, storing the information in the variables
    passed by the function. Dimensions and geometry are stored in the
    class.

    Return
    ------

    - None

    Parameters
    ----------
    - i (not optional): str
        The line of the gridfile.
    - nmax (not optional): list[int]
        The number of the cells in the grid.
    - xL (not optional): list[float]
        The list of the left cell boundaries values.
    - xR (not optional): list[float]
        The list of the right cell boundaries values.

    ----

    Examples
    --------
    - Example #1: Split the gridfile

        >>> _split_gridfile(i, xL, xR, nmax)

    """
    # If the splitted line has only one string, try to convert it
    # to an integer (number of cells in a dimension).
    if len(i.split()) == 1:
        try:
            nmax.append(int(i.split()[0]))
        except ValueError:
            pass

    # Check if the splitted line has three strings
    if len(i.split()) == 3:
        # Try to convert the first string to an int (cell number in a dimension)
        # and the other two to floats (left and right cell boundaries)
        try:
            int(i.split()[0])
            xL.append(float(i.split()[1]))
            xR.append(float(i.split()[2]))

        # Check if the keyword is geometry or dimensions and
        # store the information in the class
        except ValueError:
            if i.split()[1] == "GEOMETRY:":
                self.geom = i.split()[2]
            if i.split()[1] == "DIMENSIONS:":
                self.dim = int(i.split()[2])
