"""Module for grid management when reading files without descriptor."""

from ..loadmixin import LoadMixin
from ..loadstate import LoadState


class GridManager(LoadMixin):
    """Docstring for BaseLoadTools class."""

    def __init__(self, state: LoadState) -> None:
        """Initialize the BaseLoadTools class."""
        self.state: LoadState = state

    def readgridvtk(self):
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
        - None

        ----

        Examples
        --------
        - Example #1: read the grid from VTK files without descriptor

            >>> _read_gridvtk()

        """
        raise NotImplementedError("Function not implemented yet.")

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
        raise NotImplementedError("Function not implemented yet.")
