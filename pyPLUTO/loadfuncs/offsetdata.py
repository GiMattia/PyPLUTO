"""Docstring for pyPLUTO.loadfuncs.offsetdata."""

import mmap

from pyPLUTO.baseloadmixin import BaseLoadMixin
from pyPLUTO.baseloadstate import BaseLoadState
from pyPLUTO.loadfuncs.offsetfluid import OffsetFluid
from pyPLUTO.loadfuncs.readgridfile import GridFileManager
from pyPLUTO.loadfuncs.readtab import ReadtabManager
from pyPLUTO.loadstate import LoadState


class OffsetData(BaseLoadMixin[BaseLoadState]):
    """Class that computes the offset of variables in single_file format."""

    def __init__(self, state: BaseLoadState) -> None:
        self.state = state
        if isinstance(state, LoadState):
            self.GridFileManager = GridFileManager(state)
            self.Offsetclass = OffsetFluid(state)
            self.ReadtabManager = ReadtabManager(state)

    def compute_offset(
        self,
        i: int,
        exout: int,
        varname: str | None,
        mm: mmap.mmap,
    ) -> None:
        """Compute the offset and shape of the variable in single_file format.

        The function computes the offset and shape of the variable in
        single_file format. The offset is computed based on the variable name,
        output index, and file index. The shape is computed based on the
        variable characteristics and the grid information.

        Returns
        -------
        - None

        Parameters
        ----------
        - i (not optional): int
            The index of the file to be loaded.
        - exout (not optional): int
            The index of the output to be loaded.
        - varname (not optional): str | None
            The name of the variable to be loaded. If None, all variables are
            considered.

        ----

        Examples
        --------
        - Example #1: Compute offset for a specific variable

            >>> _compute_offset(0, 0, "rho")

        - Example #2: Compute offset for all variables

            >>> _compute_offset(0, 0, None)
        """
        if (
            self.alone is not True
            and isinstance(self.state, LoadState)
            and self.infogrid is True
        ):
            self.GridFileManager.read_gridfile()
            self.infogrid = False

        fmt = "h5" if self.format in {"dbl.h5", "flt.h5"} else self.format
        fmt = "bin" if fmt in {"dbl", "flt"} else fmt

        if isinstance(self.state, LoadState):
            handlers = {
                "tab": self.ReadtabManager.read_tab,
                "bin": self.Offsetclass.offset_bin,
                "vtk": self.Offsetclass.offset_vtk,
                "h5": self.Offsetclass.offset_h5,
                #  "hdf5": None,
            }
        else:
            raise TypeError(
                "OffsetData requires LoadState for now "
                "(particles still not implemented)."
            )
        handlers.get(fmt, self.Offsetclass.offset_bin)(i, varname, exout, mm)
