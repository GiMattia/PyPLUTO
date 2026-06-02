"""Docstring for pyPLUTO.loadfuncs.offsetdata."""

import mmap

from pyPLUTO.baseloadmixin import BaseLoadMixin
from pyPLUTO.baseloadstate import BaseLoadState
from pyPLUTO.loadfuncs.offsetfluid import OffsetFluid
from pyPLUTO.loadfuncs.offsetpart import OffsetPart
from pyPLUTO.loadfuncs.readgridfile import GridFileManager
from pyPLUTO.loadfuncs.readtab import ReadtabManager
from pyPLUTO.loadstate import LoadState


class OffsetData(BaseLoadMixin[BaseLoadState]):
    """Class that computes the offset of variables in single_file format."""

    def __init__(self, state: BaseLoadState) -> None:
        """Initialize the offset manager and delegate sub-managers by state type.

        Parameters
        ----------
        - state: BaseLoadState
            The load state object carrying grid metadata and file information.

        Returns
        -------
        - None

        """
        self.state = state
        if isinstance(state, LoadState):
            self.GridFileManager = GridFileManager(state)
            self.FluidOffsetclass = OffsetFluid(state)
            self.ReadtabManager = ReadtabManager(state)
        else:
            self.PartOffsetclass = OffsetPart(state)

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

        Parameters
        ----------
        - i (not optional): int
            The index of the file to be loaded.
        - exout (not optional): int
            The index of the output to be loaded.
        - varname (not optional): str | None
            The name of the variable to be loaded. If None, all variables are
            considered.

        Returns
        -------
        - None

        ----

        Examples
        --------
        - Example #1: Compute offset for a specific variable

            >>> _compute_offset(0, 0, "rho")

        - Example #2: Compute offset for all variables

            >>> _compute_offset(0, 0, None)
        """
        if (
            self.state.alone is not True
            and isinstance(self.state, LoadState)
            and self.state.infogrid is True
        ):
            self.GridFileManager.read_gridfile()
            self.state.infogrid = False

        fmt = (
            "h5"
            if self.state.datatype in {"dbl.h5", "flt.h5"}
            else self.state.datatype
        )
        fmt = "bin" if fmt in {"dbl", "flt"} else fmt

        cls = (
            self.FluidOffsetclass
            if isinstance(self.state, LoadState)
            else self.PartOffsetclass
        )

        if fmt == "tab":
            self.ReadtabManager.read_tab(i, varname, exout, mm)
        else:
            getattr(cls, f"offset_{fmt}", cls.offset_bin)(i, varname, exout, mm)
