"""Mixin class for base load functionality."""

from pathlib import Path
from typing import Any, TypeVar

from numpy.typing import NDArray

from pyPLUTO.baseloadstate import BaseLoadState

S = TypeVar("S", bound=BaseLoadState)


class BaseLoadMixin[S: BaseLoadState]:
    """Mixin class that provides base functionality for load state."""

    # pylint: disable=too-many-public-methods

    state: S

    @property
    def alone(self) -> bool:
        """Get the alone attribute of the load state."""
        return self.state.alone

    @alone.setter
    def alone(self, value: bool) -> None:
        """Set the alone attribute of the load state."""
        self.state.alone = value

    @property
    def charsize(self) -> int:
        """Get the charsize attribute of the load state."""
        return self.state.charsize

    @charsize.setter
    def charsize(self, value: int) -> None:
        """Set the charsize attribute of the load state."""
        self.state.charsize = value

    @property
    def class_name(self) -> str:
        """Get the class_name attribute of the load state."""
        return self.state.class_name

    @class_name.setter
    def class_name(self, value: str) -> None:
        """Set the class_name attribute of the load state."""
        self.state.class_name = value

    @property
    def code(self) -> str:
        """Get the code attribute of the load state."""
        return self.state.code

    @code.setter
    def code(self, value: str) -> None:
        """Set the code attribute of the load state."""
        self.state.code = value

    @property
    def d_info(self) -> dict[str, Any]:
        """Get the d_info attribute of the load state."""
        return self.state.d_info

    @d_info.setter
    def d_info(self, value: dict[str, Any]) -> None:
        """Set the d_info attribute of the load state."""
        self.state.d_info = value

    @property
    def d_vars(self) -> dict[str, Any]:
        """Get the d_vars attribute of the load state."""
        return self.state.d_vars

    @d_vars.setter
    def d_vars(self, value: dict[str, Any]) -> None:
        """Set the d_vars attribute of the load state."""
        self.state.d_vars = value

    @property
    def endian(self) -> str | None:
        """Get the endian attribute of the load state."""
        return self.state.endian

    @endian.setter
    def endian(self, value: str | None) -> None:
        """Set the endian attribute of the load state."""
        self.state.endian = value

    @property
    def filepath(self) -> Path:
        """Get the filepath attribute of the load state."""
        return self.state.filepath

    @filepath.setter
    def filepath(self, value: Path) -> None:
        """Set the filepath attribute of the load state."""
        self.state.filepath = value

    @property
    def format(self) -> str:
        """Get the format attribute of the load state."""
        return self.state.format

    @format.setter
    def format(self, value: str) -> None:
        """Set the format attribute of the load state."""
        self.state.format = value

    @property
    def infogrid(self) -> bool:
        """Get the infogrid attribute of the load state."""
        return self.state.infogrid

    @infogrid.setter
    def infogrid(self, value: bool) -> None:
        """Set the infogrid attribute of the load state."""
        self.state.infogrid = value

    @property
    def lennout(self) -> int:
        """Get the lennout attribute of the load state."""
        return self.state.lennout

    @lennout.setter
    def lennout(self, value: int) -> None:
        """Set the lennout attribute of the load state."""
        self.state.lennout = value

    @property
    def lennoutlist(self) -> int:
        """Get the lenoutlist attribute of the load state."""
        return self.state.lennoutlist

    @lennoutlist.setter
    def lennoutlist(self, value: int) -> None:
        """Set the lennoutlist attribute of the load state."""
        self.state.lennoutlist = value

    @property
    def matching_files(self) -> list[str] | None:
        """Get the matching_files attribute of the load state."""
        return self.state.matching_files

    @matching_files.setter
    def matching_files(self, value: list[str] | None) -> None:
        """Set the matching_files attribute of the load state."""
        self.state.matching_files = value

    @property
    def multiple(self) -> bool:
        """Get the multiple attribute of the load state."""
        return self.state.multiple

    @multiple.setter
    def multiple(self, value: bool) -> None:
        """Set the multiple attribute of the load state."""
        self.state.multiple = value

    @property
    def nout(self) -> int | NDArray[Any]:
        """Get the nout attribute of the load state."""
        return self.state.nout

    @nout.setter
    def nout(self, value: int | NDArray[Any]) -> None:
        """Set the nout attribute of the load state."""
        self.state.nout = value

    @property
    def noutlist(self) -> NDArray[Any]:
        """Get the nout attribute of the load state."""
        return self.state.noutlist

    @noutlist.setter
    def noutlist(self, value: NDArray[Any]) -> None:
        """Set the nout attribute of the load state."""
        self.state.noutlist = value

    @property
    def ntime(self) -> int | NDArray[Any]:
        """Get the ntime attribute of the load state."""
        return self.state.ntime

    @ntime.setter
    def ntime(self, value: int | NDArray[Any]) -> None:
        """Set the ntime attribute of the load state."""
        self.state.ntime = value

    @property
    def ntimelist(self) -> NDArray[Any]:
        """Get the ntime attribute of the load state."""
        return self.state.ntimelist

    @ntimelist.setter
    def ntimelist(self, value: NDArray[Any]) -> None:
        """Set the ntime attribute of the load state."""
        self.state.ntimelist = value

    @property
    def outlist(self) -> NDArray[Any]:
        """Get the outlist attribute of the load state."""
        return self.state.outlist

    @outlist.setter
    def outlist(self, value: NDArray[Any]) -> None:
        """Set the outlist attribute of the load state."""
        self.state.outlist = value

    @property
    def pathdir(self) -> str | Path:
        """Get the pathdir attribute of the load state."""
        return self.state.pathdir

    @pathdir.setter
    def pathdir(self, value: str | Path) -> None:
        """Set the pathdir attribute of the load state."""
        self.state.pathdir = value

    @property
    def timelist(self) -> NDArray[Any]:
        """Get the timelist attribute of the load state."""
        return self.state.timelist

    @timelist.setter
    def timelist(self, value: NDArray[Any]) -> None:
        """Set the timelist attribute of the load state."""
        self.state.timelist = value

    @property
    def varoffset(self) -> dict[str, Any]:
        """Get the varoffset attribute of the load state."""
        return self.state.varoffset

    @varoffset.setter
    def varoffset(self, value: dict[str, Any]) -> None:
        """Set the varoffset attribute of the load state."""
        self.state.varoffset = value

    @property
    def varshape(self) -> dict[str, Any]:
        """Get the varshape attribute of the load state."""
        return self.state.varshape

    @varshape.setter
    def varshape(self, value: dict[str, Any]) -> None:
        """Set the varshape attribute of the load state."""
        self.state.varshape = value
