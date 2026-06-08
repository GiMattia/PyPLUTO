"""Module for grid management when reading files without descriptor."""

from __future__ import annotations

import warnings

import numpy as np

from pyPLUTO.loadmixin import LoadMixin
from pyPLUTO.loadstate import LoadState


class GridManager(LoadMixin):
    """Docstring for BaseLoadTools class."""

    def __init__(self, state: LoadState) -> None:
        """Initialize the BaseLoadTools class."""
        self.state: LoadState = state

    def readgridvtk(self, gridvars: list[str]) -> None:
        """Read the grid from a .vtk file.

        Parameters
        ----------
        - gridvars (not optional): list[str]
            The list of grid variables.

        Returns
        -------
        - None

        Examples
        --------
        - Example #1: Read the grid from a vtk file

            >>> _read_grid_vtk(["self.x1r", "self.x2r", "self.x3r"])

        """
        # - RECTILINEAR GRID
        #   Variables that we already have: x1r x2r x3r nshp dim nx1 nx2 nx3
        #   Variables that we need: x1 x2 x3 dx1 dx2 dx3  gridsize

        self.state.gridsize = self.state.nx1 * self.state.nx2 * self.state.nx3
        twod = 2

        if self.state.geom == "UNKNOWN":
            if gridvars[0] == "x1r":
                self.state.x1 = 0.5 * (self.state.x1r[1:] + self.state.x1r[:-1])
                self.state.x1 = (
                    0.5 * (self.state.x1[:, 1:] + self.state.x1[:, :-1])
                    if self.state.dim > 1
                    else self.state.x1
                )
                self.state.x1 = (
                    0.5 * (self.state.x1[:, :, 1:] + self.state.x1[:, :, :-1])
                    if self.state.dim > twod
                    else self.state.x1
                )

                """
                self.state.dx1 = self.state.x1r[1:] - self.state.x1r[:-1]
                self.state.dx1 = (
                    0.5 * (self.state.dx1[:, 1:] + self.state.dx1[:, :-1])
                    if self.state.dim > 1
                    else self.state.dx1
                )
                self.state.dx1 = (
                    0.5 * (self.state.dx1[:, :, 1:] + self.state.dx1[:, :, :-1])
                    if self.state.dim > twod
                    else self.state.dx1
                )
                """

            if gridvars[1] == "x2r":
                self.state.x2 = 0.5 * (self.state.x2r[1:] + self.state.x2r[:-1])
                self.state.x2 = 0.5 * (
                    self.state.x2[:, 1:] + self.state.x2[:, :-1]
                )
                self.state.x2 = (
                    0.5 * (self.state.x2[:, :, 1:] + self.state.x2[:, :, :-1])
                    if self.state.dim > twod
                    else self.state.x2
                )

                """
                self.state.dx2 = self.state.x2r[1:] - self.state.x2r[:-1]
                self.state.dx2 = 0.5 * (
                    self.state.dx2[:, 1:] + self.state.dx2[:, :-1]
                )
                self.state.dx2 = (
                    0.5 * (self.state.dx2[:, :, 1:] + self.state.dx2[:, :, :-1])
                    if self.state.dim > twod
                    else self.state.dx2
                )
                """

            if gridvars[2] == "x3r":
                self.state.x3 = 0.5 * (self.state.x3r[1:] + self.state.x3r[:-1])
                self.state.x3 = 0.5 * (
                    self.state.x3[:, 1:] + self.state.x3[:, :-1]
                )
                self.state.x3 = 0.5 * (
                    self.state.x3[:, :, 1:] + self.state.x3[:, :, :-1]
                )

                """
                self.state.dx3 = self.state.x3r[1:] - self.state.x3r[:-1]
                self.state.dx3 = 0.5*(
                    self.state.dx3[:, 1:] + self.state.dx3[:, :-1]
                )
                self.state.dx3 = 0.5*(
                    self.state.dx3[:, :, 1:] + self.state.dx3[:, :, :-1]
                )
                """

            warn = (
                "The geometry is unknown, therefore the grid spacing has not "
                "been computed. \nFor a more accurate grid analysis, the "
                "loading with the .out file is recommended.\n"
            )
            warnings.warn(warn, UserWarning, stacklevel=2)

            return

        if gridvars[0] == "x1r":
            self.state.x1 = 0.5 * (self.state.x1r[:-1] + self.state.x1r[1:])
            self.state.dx1 = self.state.x1r[1:] - self.state.x1r[:-1]
        if gridvars[1] == "x2r":
            self.state.x2 = 0.5 * (self.state.x2r[:-1] + self.state.x2r[1:])
            self.state.dx2 = self.state.x2r[1:] - self.state.x2r[:-1]
        if gridvars[2] == "x3r":
            self.state.x3 = 0.5 * (self.state.x3r[:-1] + self.state.x3r[1:])
            self.state.dx3 = self.state.x3r[1:] - self.state.x3r[:-1]

        return

    def readgridh5(self) -> None:
        """Read the grid from a .h5 file.

        Parameters
        ----------
        - None

        Returns
        -------
        - None

        Examples
        --------
        - Example #1: Read the grid from a .h5 file

            >>> _read_grid_h5()

        """
        # Variables that we already have: x1 x2 x3 x1r x2r x3r
        # Variables that we need: nx1 nx2 nx3 nshp nx1s nx2s nx3s dim
        #                        nshp_st1 nshp_st2 nshp_st3
        #                        gridsize gridsize_st1 gridsize_st2 gridsize_st3
        nshp = np.shape(self.state.x1)
        if isinstance(nshp, int):
            nshp = (nshp,)

        self.state.nshp = nshp
        self.state.dim = len(nshp)
        self.state.geom = "UNKNOWN"
        nx_vals = (*nshp, 1, 1, 1)
        self.state.nx1 = int(nx_vals[0])
        self.state.nx2 = int(nx_vals[1])
        self.state.nx3 = int(nx_vals[2])
        nx1s, nx2s, nx3s = (
            self.state.nx1 + 1,
            self.state.nx2 + 1,
            self.state.nx3 + 1,
        )

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
        (self.state.nshp_st1, self.state.nshp_st2, self.state.nshp_st3) = (
            GRID_SHAPES[self.state.dim](
                self.state.nx1,
                self.state.nx2,
                self.state.nx3,
            )
        )

        # Grid spacing has been temporarily removed from the .h5 file
        """
        self.state.dx1 = self.state.x1r[1:] - self.state.x1r[:-1]
        self.state.dx1 = (
            0.5 * (self.state.dx1[:, 1:] + self.state.dx1[:, :-1])
            if self.state.dim > 1
            else self.state.dx1
        )
        self.state.dx1 = (
            0.5 * (self.state.dx1[:, :, 1:] + self.state.dx1[:, :, :-1])
            if self.state.dim > 2
            else self.state.dx1
        )

        self.state.dx2 = self.state.x2r[1:] - self.state.x2r[:-1]
        self.state.dx2 = (
            0.5 * (self.state.dx2[:, 1:] + self.state.dx2[:, :-1])
            if self.state.dim > 1
            else self.state.dx2
        )
        self.state.dx2 = (
            0.5 * (self.state.dx2[:, :, 1:] + self.state.dx2[:, :, :-1])
            if self.state.dim > 2
            else self.state.dx2
        )

        self.state.dx3 = self.state.x3r[1:] - self.state.x3r[:-1]
        self.state.dx3 = (
            0.5 * (self.state.dx3[:, 1:] + self.state.dx3[:, :-1])
            if self.state.dim > 1
            else self.state.dx3
        )
        self.state.dx3 = (
            0.5 * (self.state.dx3[:, :, 1:] + self.state.dx3[:, :, :-1])
            if self.state.dim > 2
            else self.state.dx3
        )
        """

        # Compute the gridsize both centered and staggered
        self.state.gridsize = self.state.nx1 * self.state.nx2 * self.state.nx3
        self.state.gridsize_st1 = nx1s * self.state.nx2 * self.state.nx3
        self.state.gridsize_st2 = self.state.nx1 * nx2s * self.state.nx3
        self.state.gridsize_st3 = self.state.nx1 * self.state.nx2 * nx3s

        warn = (
            "The geometry is unknown, therefore the grid spacing has not been "
            "computed. \nFor a more accurate grid analysis, the loading with "
            "the .out file is recommended.\n"
        )
        warnings.warn(warn, UserWarning, stacklevel=2)
