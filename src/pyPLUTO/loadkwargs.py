"""Type annotations for accepted **kwargs in the PyPLUTO Loading classes.

The loading counterpart of imagekwargs.py: each table names the keywords one
method accepts, attached as `**kwargs: Unpack[SomethingKwargs]`, and all are
`total=False` so every key is optional.

Flatter than the image tables, since the loading methods rarely forward
keywords to one another: only LoadKwargs and LoadPartKwargs inherit, both
from BaseLoadKwargs, which holds what Load and LoadPart have in common.
"""

from __future__ import annotations

from collections.abc import Iterable, Sequence
from pathlib import Path
from typing import Literal, TypedDict

import numpy as np


class BaseLoadKwargs(TypedDict, total=False):
    """Base type for keyword arguments accepted by Loading classes."""

    alone: bool | None
    code: str | None
    endian: str | None
    multiple: bool
    path: str | Path
    text: bool | None
    units: str | Iterable[str] | bool | None
    skip_units: str | Iterable[str] | None
    user_units: dict[str, float]
    datatype: str | None


class LoadKwargs(BaseLoadKwargs, total=False):
    """Type for keyword arguments accepted by Load class."""

    defh: bool | str | None
    full3D: bool
    level: int
    plini: bool | str | None
    vars: str | list[str] | bool | None


class LoadPartKwargs(BaseLoadKwargs, total=False):
    """Type for keyword arguments accepted by LoadPart class."""

    chnk: int | None
    nfile_lp: int | None


class FourierKwargs(TypedDict, total=False):
    """Keyword arguments accepted by the fourier method."""

    dx: float | int | list | np.ndarray | None
    dy: float | int | list | np.ndarray | None
    dz: float | int | list | np.ndarray | None
    xdir: bool
    ydir: bool
    zdir: bool


class FindFieldlinesKwargs(TypedDict, total=False):
    """Keyword arguments accepted by the find_fieldlines method."""

    atol: float
    closed: bool
    ctol: float
    dense: bool
    maxstep: float
    minstep: float
    numsteps: int
    order: Literal["RK45", "RK23", "DOP853", "Radau", "BDF", "LSODA"]
    rtol: float
    step: float
    transpose: bool


class FindContourKwargs(TypedDict, total=False):
    """Keyword arguments accepted by the find_contour method."""

    levels: int | float | list[float] | np.ndarray
    levelscale: Literal["linear", "logarithmic"]
    line_cmap: str | None
    transpose: bool
    vmax: float
    vmin: float
    x1: np.ndarray
    x2: np.ndarray


class SlicesKwargs(TypedDict, total=False):
    """Keyword arguments accepted by the slices method."""

    axis1: int
    axis2: int
    offset: int


class CartesianVectorKwargs(TypedDict, total=False):
    """Keyword arguments accepted by the cartesian_vector method."""

    fullout: bool
    transpose: bool
    var1: str | np.ndarray
    var2: str | np.ndarray
    var3: str | np.ndarray
    x2: np.ndarray
    x3: np.ndarray


class ReshapeKwargs(TypedDict, total=False):
    """Keyword arguments accepted by the reshape_cartesian/uniform methods."""

    nx1: int
    nx2: int
    transpose: bool
    x1: np.ndarray
    x2: np.ndarray


class ReadFileKwargs(TypedDict, total=False):
    """Keyword arguments accepted by the read_file method."""

    names: bool | Sequence[str] | None
    skip: int


class WriteFileKwargs(TypedDict, total=False):
    """Keyword arguments accepted by the write_file method."""

    dx1: np.ndarray
    dx2: np.ndarray
    dx3: np.ndarray
    nx1: int
    nx2: int
    nx3: int
    x1: np.ndarray
    x2: np.ndarray
    x3: np.ndarray


class SpectrumKwargs(TypedDict, total=False):
    """Keyword arguments accepted by the spectrum method."""

    bins: int | np.ndarray
    density: bool
    nbins: int
    normalize: bool
