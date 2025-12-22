"""Mixin class for base load functionality."""

from pathlib import Path
from typing import Any

from numpy.typing import NDArray

from .baseloadstate import BaseLoadState


class BaseLoadMixin:
    """Mixin class that provides base functionality for load state."""

    # pylint: disable=too-many-public-methods

    state: BaseLoadState

    @property
    def alone(self) -> bool:
        """Get the alone attribute of the load state."""
        return self.state.alone

    @alone.setter
    def alone(self, value: bool) -> None:
        """Set the alone attribute of the load state."""
        self.state.alone = value

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
    def endian(self) -> str | None:
        """Get the endian attribute of the load state."""
        return self.state.endian

    @endian.setter
    def endian(self, value: str | None) -> None:
        """Set the endian attribute of the load state."""
        self.state.endian = value

    @property
    def format(self) -> str | None:
        """Get the format attribute of the load state."""
        return self.state.format

    @format.setter
    def format(self, value: str | None) -> None:
        """Set the format attribute of the load state."""
        self.state.format = value

    @property
    def multiple(self) -> bool:
        """Get the multiple attribute of the load state."""
        return self.state.multiple

    @multiple.setter
    def multiple(self, value: bool) -> None:
        """Set the multiple attribute of the load state."""
        self.state.multiple = value

    @property
    def noutlist(self) -> NDArray[Any]:
        """Get the nout attribute of the load state."""
        return self.state.noutlist

    @noutlist.setter
    def noutlist(self, value: NDArray[Any]) -> None:
        """Set the nout attribute of the load state."""
        self.state.noutlist = value

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
