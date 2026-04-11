"""Module for grid management when reading files without descriptor."""

import warnings

import numpy as np

from ..loadmixin import LoadMixin
from ..loadstate import LoadState


class GridManager(LoadMixin):
    """Docstring for BaseLoadTools class."""

    def __init__(self, state: LoadState) -> None:
        """Initialize the BaseLoadTools class."""
        self.state: LoadState = state

    def readgridvtk(self, gridvars: list[str]) -> None:
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

            >>> _read_grid_vtk(["self.x1r", "self.x2r", "self.x3r"])

        """
        # - RECTILINEAR GRID
        #   Variables that we already have: x1r x2r x3r nshp dim nx1 nx2 nx3
        #   Variables that we need: x1 x2 x3 dx1 dx2 dx3  gridsize

        self.gridsize = self.nx1 * self.nx2 * self.nx3
        twod = 2

        if self.geom == "UNKNOWN":
            if gridvars[0] == "x1r":
                self.x1 = 0.5 * (self.x1r[1:] + self.x1r[:-1])
                self.x1 = (
                    0.5 * (self.x1[:, 1:] + self.x1[:, :-1])
                    if self.dim > 1
                    else self.x1
                )
                self.x1 = (
                    0.5 * (self.x1[:, :, 1:] + self.x1[:, :, :-1])
                    if self.dim > twod
                    else self.x1
                )

                """
                self.dx1 = self.x1r[1:] - self.x1r[:-1]
                self.dx1 = (
                    0.5 * (self.dx1[:, 1:] + self.dx1[:, :-1])
                    if self.dim > 1
                    else self.dx1
                )
                self.dx1 = (
                    0.5 * (self.dx1[:, :, 1:] + self.dx1[:, :, :-1])
                    if self.dim > twod
                    else self.dx1
                )
                """

            if gridvars[1] == "x2r":
                self.x2 = 0.5 * (self.x2r[1:] + self.x2r[:-1])
                self.x2 = 0.5 * (self.x2[:, 1:] + self.x2[:, :-1])
                self.x2 = (
                    0.5 * (self.x2[:, :, 1:] + self.x2[:, :, :-1])
                    if self.dim > twod
                    else self.x2
                )

                """
                self.dx2 = self.x2r[1:] - self.x2r[:-1]
                self.dx2 = 0.5 * (self.dx2[:, 1:] + self.dx2[:, :-1])
                self.dx2 = (
                    0.5 * (self.dx2[:, :, 1:] + self.dx2[:, :, :-1])
                    if self.dim > twod
                    else self.dx2
                )
                """

            if gridvars[2] == "x3r":
                self.x3 = 0.5 * (self.x3r[1:] + self.x3r[:-1])
                self.x3 = 0.5 * (self.x3[:, 1:] + self.x3[:, :-1])
                self.x3 = 0.5 * (self.x3[:, :, 1:] + self.x3[:, :, :-1])

                """
                self.dx3 = self.x3r[1:] - self.x3r[:-1]
                self.dx3 = 0.5*(self.dx3[:, 1:] + self.dx3[:, :-1])
                self.dx3 = 0.5*(self.dx3[:, :, 1:] + self.dx3[:, :, :-1])
                """

            warn = (
                "The geometry is unknown, therefore the grid spacing has not "
                "been computed. \nFor a more accurate grid analysis, the "
                "loading with the .out file is recommended.\n"
            )
            warnings.warn(warn, UserWarning, stacklevel=2)

            return None

        if gridvars[0] == "x1r":
            self.x1 = 0.5 * (self.x1r[:-1] + self.x1r[1:])
            self.dx1 = self.x1r[1:] - self.x1r[:-1]
        if gridvars[1] == "x2r":
            self.x2 = 0.5 * (self.x2r[:-1] + self.x2r[1:])
            self.dx2 = self.x2r[1:] - self.x2r[:-1]
        if gridvars[2] == "x3r":
            self.x3 = 0.5 * (self.x3r[:-1] + self.x3r[1:])
            self.dx3 = self.x3r[1:] - self.x3r[:-1]

        return None

    def readgridh5(self) -> None:
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
        # Variables that we already have: x1 x2 x3 x1r x2r x3r
        # Variables that we need: nx1 nx2 nx3 nshp nx1s nx2s nx3s dim
        #                        nshp_st1 nshp_st2 nshp_st3
        #                        gridsize gridsize_st1 gridsize_st2 gridsize_st3
        nshp = np.shape(self.x1)
        if isinstance(nshp, int):
            nshp = (nshp,)

        self.nshp = nshp
        self.dim = len(nshp)
        self.geom = "UNKNOWN"
        self.nx1, self.nx2, self.nx3 = ((*nshp, 1, 1, 1))[:3]
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
        (self._nshp_st1, self._nshp_st2, self._nshp_st3) = GRID_SHAPES[
            self.dim
        ](self.nx1, self.nx2, self.nx3)

        # Grid spacing has been temporarily removed from the .h5 file
        """
        self.dx1 = self.x1r[1:] - self.x1r[:-1]
        self.dx1 = (
            0.5 * (self.dx1[:, 1:] + self.dx1[:, :-1])
            if self.dim > 1
            else self.dx1
        )
        self.dx1 = (
            0.5 * (self.dx1[:, :, 1:] + self.dx1[:, :, :-1])
            if self.dim > 2
            else self.dx1
        )

        self.dx2 = self.x2r[1:] - self.x2r[:-1]
        self.dx2 = (
            0.5 * (self.dx2[:, 1:] + self.dx2[:, :-1])
            if self.dim > 1
            else self.dx2
        )
        self.dx2 = (
            0.5 * (self.dx2[:, :, 1:] + self.dx2[:, :, :-1])
            if self.dim > 2
            else self.dx2
        )

        self.dx3 = self.x3r[1:] - self.x3r[:-1]
        self.dx3 = (
            0.5 * (self.dx3[:, 1:] + self.dx3[:, :-1])
            if self.dim > 1
            else self.dx3
        )
        self.dx3 = (
            0.5 * (self.dx3[:, :, 1:] + self.dx3[:, :, :-1])
            if self.dim > 2
            else self.dx3
        )
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
        warnings.warn(warn, UserWarning, stacklevel=2)
