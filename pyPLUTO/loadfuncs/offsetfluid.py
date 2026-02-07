"""Docstring for pyPLUTO.loadfuncs.offsetfluid module."""

import mmap
import warnings

import h5py
import numpy as np

from ..loadmixin import LoadMixin
from ..loadstate import LoadState
from .readgridalone import GridManager


class OffsetFluid(LoadMixin):
    """Class that computes the fluid offsets in single_file format."""

    def __init__(self, state: LoadState):
        self.state = state
        self.varoffset, self.varshape = ({}, {})
        self.GridAloneManager = GridManager(state)

    def offset_bin(
        self, _i: int, var: str | None, exout: int, _mm: mmap.mmap
    ) -> None:
        """Compute the offset and shape of the variables to be loaded.

        The routine, knowing the grid shape, computes the offset and stores the
        shape dependng on wether the variable is staggered or not.

        Returns
        -------
        - None

        Parameters
        ----------
        - i (not optional): int
            The index of the file to be loaded.
        - var (not optional): str
            The variable to be loaded.

        ----

        Examples
        --------
        - Example #1: Load all the variables

            >>> _offset_bin(0, True)

        """
        off_start = 0

        grid_sizes: dict[str, tuple[int | tuple[int, ...] | None, int]] = {
            "Bx1s": (self.nshp_st1, self.gridsize_st1),
            "Ex1s": (self.nshp_st1, self.gridsize_st1),
            "Bx2s": (self.nshp_st2, self.gridsize_st2),
            "Ex2s": (self.nshp_st2, self.gridsize_st2),
            "Bx3s": (self.nshp_st3, self.gridsize_st3),
            "Ex3s": (self.nshp_st3, self.gridsize_st3),
        }

        # Loop over the variables to be loaded (None for single files)
        varloop = self.d_info["varslist"][exout] if var is None else [var]

        for eachvar in varloop:
            # Get the grid shape and size (centered or staggered)
            grid_size = grid_sizes.get(eachvar, [self.nshp, self.gridsize])
            self.varshape[eachvar] = grid_size[0]
            # Assign the offset
            self.varoffset[eachvar] = off_start
            # Move to next variable
            if isinstance(grid_size[1], int):
                off_start += grid_size[1] * self.charsize
            else:
                raise ValueError("Grid size must be an integer.")

        # End of function

    def offset_h5(
        self, i: int, var: str | None, exout: int, mm: mmap.mmap
    ) -> None:
        """Compute the offset and shape of the variable in hdf5 format.

        The routine, knowing the grid shape, computes the offset and stores the
        shape dependng on wether the variable is staggered or not.

        Returns
        -------
        - None

        Parameters
        ----------
        - i (not optional): int
            The index of the file to be loaded.
        - var (not optional): str
            The variable to be loaded.

        ----

        Examples
        --------
        - Example #1: Load all the variables

            >>> _offset_h5(0, True)

        """
        # Open the file with the h5py library
        h5file = h5py.File(self.filepath, "r")

        # Selects the binformat
        self.d_info["binformat"][i] = "d" if self.format == "dbl.h5" else "f"

        # Safely access the timestep group and its sub-items to avoid
        # treating an h5py.Datatype as a subscriptable object.
        timestep_key = f"Timestep_{exout}"
        timestep = h5file.get(timestep_key, None)
        if isinstance(timestep, h5py.Group):
            cellvs = timestep.get("vars", {})
            stagvs = timestep.get("stag_vars", {})
            cellvs = (
                {}
                if cellvs is None or isinstance(cellvs, h5py.Datatype)
                else cellvs
            )

            stagvs = (
                {}
                if stagvs is None or isinstance(stagvs, h5py.Datatype)
                else stagvs
            )
        else:
            # Timestep group not present or not a group; treat as empty
            cellvs = {}
            stagvs = {}

        # If standalone file, finds the variables to be loaded, else
        # remove variables in the .out file that are not present in the actual
        # file
        if (
            self.alone is True
            and isinstance(cellvs, h5py.Group | dict)
            and isinstance(stagvs, h5py.Group | dict)
        ):
            self.d_info["varslist"][exout] = set(cellvs.keys()) | set(
                stagvs.keys()
            )
        elif not isinstance(cellvs, h5py.Group | dict) or not isinstance(
            stagvs, h5py.Group | dict
        ):
            raise ValueError(
                "Error: Variables group not found in the HDF5 file."
            )

        # Loop over the variables and store the offset and shape
        for j in self.d_info["varslist"][exout]:
            if j in cellvs:
                obj = cellvs[j]
            elif j in stagvs:
                obj = stagvs[j]
            else:
                obj = None
                warnings.warn(
                    f"Warning: Variable {j} not found in the HDF5 file.",
                    UserWarning,
                    stacklevel=2,
                )
            # Only Dataset objects provide shape and a file offset
            if isinstance(obj, h5py.Dataset):
                self.varoffset[j] = obj.id.get_offset()
                self.varshape[j] = obj.shape
            elif obj is not None:
                raise ValueError(
                    f"Error: Variable {j} in the HDF5 file is not a dataset."
                )

        if (
            self.alone is True
            and isinstance(self.state, LoadState)
            and self.infogrid is True
        ):
            self.x1 = h5file["cell_coords"]["X"][:]
            self.x2 = h5file["cell_coords"]["Y"][:]
            self.x3 = h5file["cell_coords"]["Z"][:]
            self.x1r = h5file["node_coords"]["X"][:]
            self.x2r = h5file["node_coords"]["Y"][:]
            self.x3r = h5file["node_coords"]["Z"][:]
            self.GridAloneManager.readgridh5()
            self.infogrid = False

        # Close the file
        h5file.close()

    def offset_vtk(
        self, i: int, var: str | None, _exout: int, mm: mmap.mmap
    ) -> None:
        """Compute the offset and shape of the variables to be loaded.

        The routine, knowing the grid shape, computes the offset and stores the
        shape dependng on wether the variable is staggered or not.

        Returns
        -------
        - None

        Parameters
        ----------
        - i (not optional): int
            The index of the file to be loaded.
        - var (not optional): str
            The variable to be loaded.

        ----

        Examples
        --------
        - Example #1: Load all the variables

            >>> _offset_vtk(0, True)

        """
        self.d_info["endianess"][i] = (
            ">" if self.endian is None else self.d_info["endianess"][i]
        )
        if self.d_info["endianess"][i] is None:
            raise ValueError("Error: Wrong endianess in vtk file.")

        if self.alone is True:
            self.d_info["binformat"][
                i
            ] = f"{self.d_info['endianess'][i]}f{self.charsize}"
        search_pos = 0
        while True:
            scalars_pos = mm.find(b"SCALARS", search_pos)
            if scalars_pos == -1:
                break  # No more occurrences found

            # Move to the end of the 'SCALARS' line
            line_end = mm.find(b"\n", scalars_pos)
            line = mm[scalars_pos:line_end]
            parts = line.split()
            namevar = parts[1].decode()

            # Move to the start of the scalar data
            lookup_table_pos = mm.find(b"LOOKUP_TABLE default", line_end)
            offset = mm.find(b"\n", lookup_table_pos) + 1

            self.varoffset[namevar] = offset
            self.varshape[namevar] = self.nshp
            if var is not None:
                break

            search_pos = (
                line_end + 1 + self.gridsize * 4
            )  # Continue searching after the current line

        if self.d_info["typefile"][i] == "single_file" and self.alone is True:
            self.d_info["varslist"][i] = np.array(list(self.varoffset.keys()))
