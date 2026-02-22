"""Module that contains the LoadState class."""

from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

from numpy.typing import NDArray


@dataclass(slots=True)
class BaseLoadState:
    """Class that stores the state of the Load class.

    Its purpose is to keep track of the current state of the data loading,
    such as the file paths, data arrays, and other properties and update the
    key attributes through all the different classes that handle the data
    loading at runtime.
    """

    # pylint: disable=too-many-instance-attributes

    alone: bool = field(init=False)
    charsize: int = field(init=False)
    class_name: str = field(init=False)
    code: str = "gPLUTO"
    d_info: dict[str, Any] = field(init=False)
    d_vars: dict[str, Any] = field(default_factory=dict)
    endian: str | None = None
    filepath: Path = field(init=False)
    format: str = "Unknown"
    infogrid: bool = True
    lennout: int = field(init=False)
    lennoutlist: int = field(init=False)
    matching_files: list[str] | None = None
    multiple: bool = False
    nout: int | NDArray[Any] = field(init=False)
    noutlist: NDArray[Any] = field(init=False)
    ntime: int | NDArray[Any] = field(init=False)
    ntimelist: NDArray[Any] = field(init=False)
    outlist: NDArray[Any] = field(init=False)
    pathdir: str | Path = "./"
    timelist: NDArray[Any] = field(init=False)
    varoffset: dict[str, Any] = field(init=False)
    varshape: dict[str, Any] = field(init=False)
