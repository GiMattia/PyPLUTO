"""Module that contains the LoadState class."""

from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, TypeVar

from numpy.typing import NDArray


@dataclass
class BaseLoadState:
    """Class that stores the state of the Load class.

    Its purpose is to keep track of the current state of the data loading,
    such as the file paths, data arrays, and other properties and update the
    key attributes through all the different classes that handle the data
    loading at runtime."""

    # pylint: disable=too-many-instance-attributes

    alone: bool = field(init=False)
    class_name: str = field(init=False)
    code: str = "gPLUTO"
    endian: str | None = None
    format: str | None = None
    multiple: bool = False
    noutlist: NDArray[Any] = field(init=False)
    outlist: NDArray[Any] = field(init=False)
    pathdir: str | Path = "./"


StateT = TypeVar("StateT", bound=BaseLoadState)
