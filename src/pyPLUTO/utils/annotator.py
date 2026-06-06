"""Type annotations for all accepted **kwargs in pyPLUTO.

AllKwargs is a TypedDict covering every keyword argument accepted anywhere
in the public API.  Functions annotate their **kwargs parameter as
``Unpack[AllKwargs]`` to get full static type-checking support.
"""

from __future__ import annotations

from collections.abc import Sequence
from pathlib import Path as FilePath
from typing import TypedDict

import numpy as np
from matplotlib.axes import Axes
from matplotlib.figure import Figure


class AllKwargs(TypedDict, total=False):
    """All keyword arguments accepted by pyPLUTO public methods."""

    # --- Figure / window ---
    close: bool
    fig: Figure | None
    figsize: Sequence[float]
    fontsize: float | int
    fontweight: str
    kwargscheck: bool
    LaTeX: bool | str
    numcolors: int
    nwin: int
    proj: str | None
    replace: bool
    style: str
    suptitle: str | None
    suptitlesize: int | str
    tight: bool
    withblack: bool
    withwhite: bool

    # --- Axes grid layout ---
    bottom: float
    height: float
    hratio: list[float]
    hspace: list[float]
    left: float
    ncol: int
    nrow: int
    pos: list[float] | None
    right: float
    sharex: bool | str | Axes
    sharey: bool | str | Axes
    top: float
    width: float
    wratio: list[float]
    wspace: list[float]

    # --- Axis styling ---
    alpha: float
    aspect: str | float
    ax: Axes | int | None
    grid: bool | str
    labelsize: float
    minorticks: str | None
    ticksdir: str
    tickssize: float | bool
    title: str | None
    titlepad: float | str
    titlesize: float
    transpose: bool
    xticks: list[float] | None | bool
    xtickslabels: list[str] | None | bool
    xtitle: str | None
    xlabelpad: float
    xrange: list[float]
    xscale: str
    xtresh: float | None
    yticks: list[float] | None | bool
    ytickslabels: list[str] | None | bool
    ytitle: str | None
    ylabelpad: float
    yrange: list[float]
    yscale: str
    ytresh: float | None

    # --- Color / colormap ---
    c: str
    clabel: str | None
    cmap: str | None
    cpad: float
    cpos: str | None
    cscale: str
    cticks: list[float] | None
    ctickslabels: str | None
    edgecolor: list[str | None]
    edgecolors: str | None
    extend: str
    extendrect: bool
    shading: str
    tresh: float
    vmax: float | None
    vmin: float | None

    # --- Plot / line styling ---
    fillstyle: str
    label: str | None
    ls: str
    lw: float
    marker: str
    ms: float
    mscale: float

    # --- Legend ---
    legalpha: float
    legcols: int
    legpad: float
    legpos: int | str | None
    legsize: float
    legspace: float

    # --- Contour / display ---
    fullout: bool | None
    levels: np.ndarray
    levelscale: str
    lint: bool | None
    x1: np.ndarray
    x2: np.ndarray

    # --- Streamplot ---
    arrowsize: float
    arrowstyle: str
    brokenlines: bool
    density: float
    integration_direction: str
    maxlength: float
    minlength: float
    start_points: np.ndarray | None

    # --- Zoom / inset ---
    zoomcolor: str
    zoomlines: bool

    # --- Text box ---
    horalign: str
    textsize: float
    veralign: str
    xycoords: str

    # --- Data loading ---
    datatype: str | None
    full3D: bool
    path: str | FilePath
    vars: str | list[str] | bool | None  # to be deprecated

    # --- Spectrum ---
    nbins: int

    # --- Write file ---
    dx1: float
    dx2: float
    dx3: float
    nx1: int
    nx2: int
    nx3: int
    x3: np.ndarray

    # --- Fourier ---
    dx: float
    dy: float
    dz: float

    # --- Slices / transform ---
    axis1: int
    axis2: int
    offset: int
