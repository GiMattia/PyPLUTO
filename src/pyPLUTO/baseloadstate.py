"""Module that contains the LoadState class.

This module holds the state that Load and LoadPart have in common. LoadState
adds the grid on top of it, in loadstate.py, and LoadPart uses this class
directly since particles carry their positions as ordinary variables.

The class is deliberately behaviour-free: it stores, and the managers do the
work. One instance is created per load and handed to every manager by
reference, so anything one of them writes is immediately visible to all the
others and to the Load object the user holds.
"""

from __future__ import annotations

import mmap
from collections.abc import Sequence
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

    The fields come in two kinds. One with an ordinary default is a setting
    the user may choose. One written as `field(init=False, repr=False)` is a
    result: it has no meaning until the files are read, so it has no default
    and raises AttributeError until the loading code fills it in. `repr=False`
    is what lets `repr()` of a fresh state work rather than raise on the first
    such field.

    A mutable default must use `default_factory`, or every load would share
    one dict and a second dataset would overwrite the variables of the first.
    """

    # Whether the grid comes from a standalone file rather than the data
    alone: bool = field(init=False, repr=False)

    # Bytes per value: 8 for double precision, 4 for single
    charsize: int = field(init=False, repr=False)

    # Name of the owning class, for managers that differ between them
    class_name: str = field(init=False, repr=False)

    # Which chunk(s) of a particle output to read; None means all
    chnk: int | Sequence[int] | None = None

    # The simulation code that wrote the data, deciding which reader runs
    code: str = "gPLUTO"

    # Metadata per output: endianness, variable names, times
    d_info: dict[str, Any] = field(default_factory=dict)

    # The variables themselves, by name; this is what Data.rho reaches
    d_vars: dict[str, Any] = field(default_factory=dict)

    # The file format in use (dbl, flt, vtk, h5, tab)
    datatype: str = "Unknown"

    # Number of spatial dimensions of the simulation
    dim: int = field(init=False, repr=False)

    # Byte order of the data files, found by inspection unless given
    endian: str | None = None

    # The file currently being read
    filepath: Path = field(init=False, repr=False)

    # Whether the grid information sits alongside the data
    infogrid: bool = True

    # Number of outputs actually loaded
    lennout: int = field(init=False, repr=False)

    # Number of outputs available in the folder
    lennoutlist: int = field(init=False, repr=False)

    # The data files found in the folder, before any selection
    matching_files: list[str] | None = None

    # The open memory mappings, kept so they can be closed
    mmaps: list[mmap.mmap] = field(default_factory=list)

    # Whether each output is split across several files
    multiple: bool = False

    # The output number(s) loaded: an int for one, an array for several
    nout: int | np.ndarray = field(init=False, repr=False)

    # Every output number loaded, always as an array
    noutlist: np.ndarray = field(init=False, repr=False)

    # Number of particles for a particle load, grid shape for a fluid one
    nshp: int | tuple[int, ...] = field(init=False, repr=False)

    # The simulation time(s) of the loaded output(s), matching nout
    ntime: int | np.ndarray = field(init=False, repr=False)

    # The simulation times of every loaded output, matching noutlist
    ntimelist: np.ndarray = field(init=False, repr=False)

    # Every output number present in the folder; noutlist selects from it
    outlist: np.ndarray = field(init=False, repr=False)

    # The folder being read
    pathdir: str | Path = "./"

    # Verbosity: None prints the load line, False silences, True debugs
    text: bool | None = None

    # The simulation time of every output present in the folder
    timelist: np.ndarray = field(init=False, repr=False)

    # The variables currently carrying an astropy unit
    unit_attached: set[str] = field(default_factory=set)

    # The code units of the simulation
    unit_base: dict[str, float | str] = field(default_factory=dict)

    # The units the user overrode
    unit_userdef: dict[str, float] = field(default_factory=dict)

    # The full set of units in use
    units: dict[str, Any] = field(default_factory=dict)

    # Where each variable starts in its file, so it can be mapped alone
    varoffset: dict[str, Any] = field(default_factory=dict)

    # The shape each variable has in its file
    varshape: dict[str, Any] = field(default_factory=dict)
