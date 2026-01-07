"""Docstring for pyPLUTO.loadfuncs.baseloadtools module."""

import contextlib
from pathlib import Path

import numpy as np

from ..loadmixin import LoadMixin
from ..loadstate import LoadState


class GridManager(LoadMixin):
    """Docstring for BaseLoadTools class."""

    def __init__(self, state: LoadState) -> None:
        """Initialize the BaseLoadTools class."""
        self.state = state

    def read_gridfile(self) -> None:
        """Read the file grid.out is read and store all the grid information.

        Such information are the dimensions, the geometry, the center and edges
        of each cell, the grid shape and size and, in case of non cartesian
        coordinates, the transformed cartesian coordinates (only 2D for now).
        The full non-cartesian 3D transformations have not been implemented yet.

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
        nmax: list[int] = []
        xL: list[float] = []
        xR: list[float] = []

        # Open and read the gridfile
        with open(self.pathdir / Path("grid.out")) as gfp:
            for i in gfp.readlines():
                self.split_gridfile(i, xL, xR, nmax)

        # Compute nx1, nx2, nx3
        self.nx1, self.nx2, self.nx3 = nmax
        nx1p2 = self.nx1 + self.nx2
        nx1p3 = self.nx1 + self.nx2 + self.nx3

        # Define grid shapes based on dimensions
        """
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
        (self.nshp, self.nshp_st1, self.nshp_st2, self.nshp_st3) = GRID_SHAPES[
            self.dim
        ](self.nx1, self.nx2, self.nx3)
        """
        nx1s, nx2s, nx3s = self.nx1 + 1, self.nx2 + 1, self.nx3 + 1

        oned, twod, threed = 1, 2, 3
        if self.dim == oned:
            self.nshp = self.nx1
            self.nshp_st1 = nx1s
            self.nshp_st2 = None
            self.nshp_st3 = None

        elif self.dim == twod:
            self.nshp = (self.nx2, self.nx1)
            self.nshp_st1 = (self.nx2, nx1s)
            self.nshp_st2 = (nx2s, self.nx1)
            self.nshp_st3 = None

        elif self.dim == threed:
            self.nshp = (self.nx3, self.nx2, self.nx1)
            self.nshp_st1 = (self.nx3, self.nx2, nx1s)
            self.nshp_st2 = (self.nx3, nx2s, self.nx1)
            self.nshp_st3 = (nx3s, self.nx2, self.nx1)

        else:
            raise ValueError(f"dim must be 1..3, got {self.dim}")

        # Compute the centered and staggered grid values
        self.x1r = np.array([*xL[0 : self.nx1], xR[self.nx1 - 1]])
        self.x1 = 0.5 * (self.x1r[:-1] + self.x1r[1:])
        self.dx1 = self.x1r[1:] - self.x1r[:-1]

        self.x2r = np.array([*xL[self.nx1 : nx1p2], xR[nx1p2 - 1]])
        self.x2 = 0.5 * (self.x2r[:-1] + self.x2r[1:])
        self.dx2 = self.x2r[1:] - self.x2r[:-1]

        self.x3r = np.array([*xL[nx1p2:nx1p3], xR[nx1p3 - 1]])
        self.x3 = 0.5 * (self.x3r[:-1] + self.x3r[1:])
        self.dx3 = self.x3r[1:] - self.x3r[:-1]

        self.check_geometry()

        self.gridsize = self.nx1 * self.nx2 * self.nx3
        self.gridsize_st1 = nx1s * self.nx2 * self.nx3
        self.gridsize_st2 = self.nx1 * nx2s * self.nx3
        self.gridsize_st3 = self.nx1 * self.nx2 * nx3s

    def split_gridfile(
        self, i: str, xL: list[float], xR: list[float], nmax: list[int]
    ) -> None:
        """Split the gridfile, storing the info in the function variables.

        Dimensions and geometry are stored in the class.

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
        three_number = 3
        # If the splitted line has only one string, try to convert it
        # to an integer (number of cells in a dimension).
        if len(i.split()) == 1:
            with contextlib.suppress(ValueError):
                nmax.append(int(i.split()[0]))

        # Check if the splitted line has three strings
        if len(i.split()) == three_number:
            # Try to convert the first string to an int (cell number in a
            # dimension) and the other two to floats (left and right cell
            # boundaries)
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

    def check_geometry(self) -> None:
        """Check the geometry of the grid and set full3D attribute.

        The function checks the geometry of the grid and sets the full3D
        attribute accordingly. If the geometry is cartesian, full3D is set to
        True. If the geometry is cylindrical or spherical, full3D is set to
        False.

        Returns
        -------
        - None

        Parameters
        ----------
        - None

        ----

        Examples
        --------
        - Example #1: Check geometry for cartesian grid

            >>> _check_geometry()

        - Example #2: Check geometry for cylindrical grid

            >>> _check_geometry()

        """
        threed = 3
        if self.geom == "POLAR":
            x1_2D, x2_2D = np.meshgrid(self.x1, self.x2, indexing="ij")
            x1r_2D, x2r_2D = np.meshgrid(self.x1r, self.x2r, indexing="ij")

            self.x1c = (np.cos(x2_2D) * x1_2D).T
            self.x2c = (np.sin(x2_2D) * x1_2D).T
            self.x1rc = (np.cos(x2r_2D) * x1r_2D).T
            self.x2rc = (np.sin(x2r_2D) * x1r_2D).T
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

            del x1_2D, x2_2D, x1r_2D, x2r_2D, x3_2D, x3r_2D
            if self.dim == threed and self.full3D is True:
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
