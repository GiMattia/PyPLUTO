"""Module that contains the LoadState class."""

from __future__ import annotations

import mmap
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

import numpy as np


@dataclass
class BaseLoadState:
    """Class that stores the state of the Load class.

    Its purpose is to keep track of the current state of the data loading,
    such as the file paths, data arrays, and other properties and update the
    key attributes through all the different classes that handle the data
    loading at runtime.
    """

    alone: bool = field(init=False)
    charsize: int = field(init=False)
    class_name: str = field(init=False)
    code: str = "gPLUTO"
    d_info: dict[str, Any] = field(default_factory=dict)
    d_vars: dict[str, Any] = field(default_factory=dict)
    datatype: str = "Unknown"
    dim: int = field(init=False)
    endian: str | None = None
    filepath: Path = field(init=False)
    infogrid: bool = True
    lennout: int = field(init=False)
    lennoutlist: int = field(init=False)
    matching_files: list[str] | None = None
    mmaps: list[mmap.mmap] = field(default_factory=list)
    multiple: bool = False
    nout: int | np.ndarray = field(init=False, repr=False)
    noutlist: np.ndarray = field(init=False)
    nshp: int | tuple[int, ...] = field(init=False)
    ntime: int | np.ndarray = field(init=False, repr=False)
    ntimelist: np.ndarray = field(init=False)
    outlist: np.ndarray = field(init=False)
    pathdir: str | Path = "./"
    text: bool | None = None
    timelist: np.ndarray = field(init=False)
    unit_attached: set[str] = field(default_factory=set)
    unit_base: dict[str, float | str] = field(default_factory=dict)
    unit_userdef: dict[str, float] = field(default_factory=dict)
    units: dict[str, Any] = field(default_factory=dict)
    varoffset: dict[str, Any] = field(default_factory=dict)
    varshape: dict[str, Any] = field(default_factory=dict)
