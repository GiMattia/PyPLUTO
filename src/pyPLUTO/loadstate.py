"""Module that contains the LoadState class."""

from __future__ import annotations

from dataclasses import dataclass, field

import numpy as np

from pyPLUTO.baseloadstate import BaseLoadState


@dataclass
class LoadState(BaseLoadState):
    """Class that stores the state of the Load class.

    Its purpose is to keep track of the current state of the data loading,
    such as the file paths, data arrays, and other properties and update the
    key attributes through all the different classes that handle the data
    loading at runtime.
    """

    defh: dict = field(init=False, repr=False)
    dx1: np.ndarray = field(init=False)
    dx2: np.ndarray = field(init=False)
    dx3: np.ndarray = field(init=False)
    full3D: bool = False
    geom: str = field(init=False)

    gridsize: int = field(init=False)
    gridsize_st1: int = field(init=False)
    gridsize_st2: int = field(init=False)
    gridsize_st3: int = field(init=False)
    level: int = 0

    nshp_st1: int | tuple[int, ...] | None = field(init=False)
    nshp_st2: tuple[int, ...] | None = field(init=False)
    nshp_st3: tuple[int, ...] | None = field(init=False)
    nx1: int = field(init=False)
    nx2: int = field(init=False)
    nx3: int = field(init=False)

    plini: dict = field(init=False, repr=False)

    x1: np.ndarray = field(init=False)
    x1c: np.ndarray = field(init=False, repr=False)
    x1p: np.ndarray = field(init=False, repr=False)
    x1r: np.ndarray = field(init=False)
    x1rc: np.ndarray = field(init=False, repr=False)
    x1rp: np.ndarray = field(init=False, repr=False)
    x1rt: np.ndarray = field(init=False, repr=False)
    x1t: np.ndarray = field(init=False, repr=False)

    x2: np.ndarray = field(init=False)
    x2c: np.ndarray = field(init=False, repr=False)
    x2p: np.ndarray = field(init=False, repr=False)
    x2r: np.ndarray = field(init=False)
    x2rc: np.ndarray = field(init=False, repr=False)
    x2rp: np.ndarray = field(init=False, repr=False)

    x3: np.ndarray = field(init=False)
    x3c: np.ndarray = field(init=False, repr=False)
    x3r: np.ndarray = field(init=False)
    x3rc: np.ndarray = field(init=False, repr=False)
    x3rt: np.ndarray = field(init=False, repr=False)
    x3t: np.ndarray = field(init=False, repr=False)
