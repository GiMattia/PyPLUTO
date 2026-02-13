"""Module that contains the LoadState class."""

from dataclasses import dataclass, field
from typing import Any

from numpy.typing import NDArray

from .baseloadstate import BaseLoadState


@dataclass
class LoadState(BaseLoadState):
    """Class that stores the state of the Load class.

    Its purpose is to keep track of the current state of the data loading,
    such as the file paths, data arrays, and other properties and update the
    key attributes through all the different classes that handle the data
    loading at runtime.
    """

    # pylint: disable=too-many-instance-attributes

    dim: int = field(init=False)
    dx1: NDArray[Any] = field(init=False)
    dx2: NDArray[Any] = field(init=False)
    dx3: NDArray[Any] = field(init=False)
    full3D: bool = False
    geom: str = field(init=False)

    gridsize: int = field(init=False)
    gridsize_st1: int = field(init=False)
    gridsize_st2: int = field(init=False)
    gridsize_st3: int = field(init=False)

    nshp: int | tuple[int, ...] = field(init=False)
    nshp_st1: int | tuple[int, ...] | None = field(init=False)
    nshp_st2: tuple[int, ...] | None = field(init=False)
    nshp_st3: tuple[int, ...] | None = field(init=False)
    nx1: int = field(init=False)
    nx2: int = field(init=False)
    nx3: int = field(init=False)

    x1: NDArray[Any] = field(init=False)
    x1c: NDArray[Any] = field(init=False, repr=False)
    x1p: NDArray[Any] = field(init=False, repr=False)
    x1r: NDArray[Any] = field(init=False)
    x1rc: NDArray[Any] = field(init=False, repr=False)
    x1rp: NDArray[Any] = field(init=False, repr=False)
    x1rt: NDArray[Any] = field(init=False, repr=False)
    x1t: NDArray[Any] = field(init=False, repr=False)

    x2: NDArray[Any] = field(init=False)
    x2c: NDArray[Any] = field(init=False, repr=False)
    x2p: NDArray[Any] = field(init=False, repr=False)
    x2r: NDArray[Any] = field(init=False)
    x2rc: NDArray[Any] = field(init=False, repr=False)
    x2rp: NDArray[Any] = field(init=False, repr=False)

    x3: NDArray[Any] = field(init=False)
    x3c: NDArray[Any] = field(init=False, repr=False)
    x3r: NDArray[Any] = field(init=False)
    x3rc: NDArray[Any] = field(init=False, repr=False)
    x3rt: NDArray[Any] = field(init=False, repr=False)
    x3t: NDArray[Any] = field(init=False, repr=False)
