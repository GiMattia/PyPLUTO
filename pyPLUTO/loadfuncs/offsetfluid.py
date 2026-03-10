"""Docstring for pyPLUTO.loadfuncs.offsetfluid module."""

import mmap
import struct
import warnings

import h5py
import numpy as np

from pyPLUTO.loadfuncs.readgridalone import GridManager
from pyPLUTO.loadmixin import LoadMixin
from pyPLUTO.loadstate import LoadState


class OffsetFluid(LoadMixin):
    """Class that computes the fluid offsets in single_file format."""

    def __init__(self, state: LoadState) -> None:
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
        self, i: int, _var: str | None, exout: int, _mm: mmap.mmap
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
        h5file = h5py.File(str(self.filepath), "r")

        # Selects the binformat
        self.d_info["binformat"][exout] = (
            "d" if self.format == "dbl.h5" else "f"
        )

        # Safely access the timestep group and its sub-items to avoid
        # treating an h5py.Datatype as a subscriptable object.
        timestep_key = f"Timestep_{exout}"
        timestep = h5file.get(timestep_key, None)

        if isinstance(timestep, h5py.Group):
            timeattr = timestep.attrs["Time"]
            idx = np.searchsorted(self.outlist, exout)
            self.timelist[idx] = float(timeattr)
            idx = np.searchsorted(self.noutlist, exout)
            self.ntimelist[idx] = float(timeattr)
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

        if self.alone is True and self.infogrid is True:
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
        self, i: int, var: str | None, exout: int, mm: mmap.mmap
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
        dir_map: dict[str, str] = {}

        self.d_info["endianess"][exout] = (
            ">" if self.endian is None else self.d_info["endianess"][exout]
        )
        if self.d_info["endianess"][exout] is None:
            raise ValueError("Error: Wrong endianess in vtk file.")

        if self.alone is True:
            self.d_info["binformat"][exout] = (
                f"{self.d_info['endianess'][exout]}f{self.charsize}"
            )
        search_pos = 0
        while True:
            line_end = mm.find(b"\n", search_pos)
            if line_end == -1:
                break  # No more occurrences found
            line = mm[search_pos:line_end]

            if line.startswith(b"SCALARS"):
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
                    line_end + self.gridsize * 4
                )  # Continue searching after the current line
            elif line.startswith(b"VECTORS"):
                # Handle VECTORS data
                warnings.warn(
                    "Warning: VECTORS data is not supported.",
                    UserWarning,
                    stacklevel=2,
                )
                search_pos = line_end + 1
            elif line.startswith(b"DIMENSIONS") and self.infogrid is True:
                self.nx1, self.nx2, self.nx3 = [
                    max(int(i) - 1, 1) for i in line.split()[1:4]
                ]
                if self.nx3 == 1 and self.nx2 == 1:
                    self.dim = 1
                    self.nshp = self.nx1
                    self.gridsize = self.nx1
                    nshp_grid = self.nx1 + 1
                    gridvars = ["x1r", "x2", "x3"]
                elif self.nx3 == 1:
                    self.dim = 2
                    self.nshp = (self.nx2, self.nx1)
                    self.gridsize = self.nx1 * self.nx2
                    nshp_grid = (self.nx2 + 1, self.nx1 + 1)
                    gridvars = ["x1r", "x2r", "x3"]
                else:
                    self.dim = 3
                    self.nshp = (self.nx3, self.nx2, self.nx1)
                    self.gridsize = self.nx1 * self.nx2 * self.nx3
                    nshp_grid = (self.nx3 + 1, self.nx2 + 1, self.nx1 + 1)
                    gridvars = ["x1r", "x2r", "x3r"]
                dir_map = {"X": gridvars[0], "Y": gridvars[1], "Z": gridvars[2]}
                search_pos = line_end + 1
            elif line.startswith(b"TIME") and self.alone is True:
                try:
                    parts = line.split()
                    binf = 8 if parts[3].decode() == "double" else 4
                    raw = mm[line_end + 1 : line_end + 1 + binf]
                    self.timelist[exout] = struct.unpack(
                        self.d_info["endianess"][exout] + "d", raw
                    )[0]
                except Exception:
                    binf = 0
                search_pos = line_end + 1 + binf

            elif line[1:].startswith(b"_COORDINATES") and self.infogrid is True:
                self.geom = "CARTESIAN"
                linesplit = line.split()
                var_sel = linesplit[0].decode()[0]
                binf = (
                    self.d_info["endianess"][exout] + "d"
                    if linesplit[2].decode() == "double"
                    else self.d_info["endianess"][exout] + "f"
                )
                scrh = np.ndarray(
                    shape=int(linesplit[1]),
                    dtype=binf,
                    buffer=mm,
                    offset=line_end + 1,
                    order="C",
                ).T
                setattr(self, dir_map[var_sel], scrh)
                search_pos = line_end + 1
            else:
                search_pos = line_end + 1

        if (
            self.d_info["typefile"][exout] == "single_file"
            and self.alone is True
        ):
            self.d_info["varslist"][exout] = np.array(
                list(self.varoffset.keys())
            )
        if self.infogrid is True:
            self.GridAloneManager.readgridvtk(gridvars)
            self.infogrid = False
