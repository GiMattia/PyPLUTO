"""Module for grid management when reading files without descriptor."""

from ..loadmixin import LoadMixin
from ..loadstate import LoadState


class GridManager(LoadMixin):
    """Docstring for BaseLoadTools class."""

    def __init__(self, state: LoadState) -> None:
        """Initialize the BaseLoadTools class."""
        self.state: LoadState = state

    def readgridvtk(self, gridvars: list[str]) -> None:
        """Read the grid information from VTK files without descriptor.

        Such information are the dimensions, the geometry, the center and edges
        of each cell, the grid shape and size and, in case of non cartesian
        coordinates, the transformed cartesian coordinates (only 2D for now).
        The full non-cartesian 3D transformations have not been implemented yet.

        Returns
        -------
        - None

        Parameters
        ----------
        - gridvars (list[str]): List of grid variables to read.

        ----

        Examples
        --------
        - Example #1: read the grid from VTK files without descriptor

            >>> _read_gridvtk()

        """
        if gridvars[0] == "x1r":
            self.x1 = 0.5 * (self.x1r[:-1] + self.x1r[1:])
            self.dx1 = self.x1r[1:] - self.x1r[:-1]
        if gridvars[1] == "x2r":
            self.x2 = 0.5 * (self.x2r[:-1] + self.x2r[1:])
            self.dx2 = self.x2r[1:] - self.x2r[:-1]
        if gridvars[2] == "x3r":
            self.x3 = 0.5 * (self.x3r[:-1] + self.x3r[1:])
            self.dx3 = self.x3r[1:] - self.x3r[:-1]

    def readgridh5(self):
        """Read the grid information from HDF5 files without descriptor.

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
        - Example #1: read the grid from HDF5 files without descriptor

            >>> _read_gridh5()

        """
        pass
        # raise NotImplementedError("Function not implemented yet.")
