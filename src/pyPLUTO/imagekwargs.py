"""Type annotations for accepted **kwargs in the PyPLUTO Image class."""

from __future__ import annotations

from collections.abc import Sequence
from typing import Literal, TypedDict

import numpy as np
from matplotlib.axes import Axes
from matplotlib.colors import Colormap
from matplotlib.figure import Figure
from matplotlib.typing import ColorType, LineStyleType, MarkerType
from numpy.typing import ArrayLike


class ImageKwargs(TypedDict, total=False):
    """Base class for all keyword arguments accepted by pyPLUTOImage class."""

    figsize: Sequence[float]
    fontsize: float | int
    fontweight: str
    LaTeX: bool | str
    numcolors: int
    nwin: int
    replace: bool
    style: str
    suptitle: str | None
    suptitlesize: int | str
    tight: bool
    withblack: bool
    withwhite: bool


class FigureKwargs(ImageKwargs, total=False):
    """Keyword arguments for creating figures."""

    fig: Figure | None
    close: bool


class CreateAxesKwargs(ImageKwargs, total=False):
    """Keyword arguments for creating axes."""

    bottom: float
    hratio: Sequence[float] | float
    hspace: Sequence[float] | float
    left: float
    ncol: int
    nrow: int
    proj: str
    right: float
    sharexaxes: bool | str | Axes
    shareyaxes: bool | str | Axes
    top: float
    wratio: Sequence[float] | float
    wspace: Sequence[float] | float


class TextKwargs(CreateAxesKwargs, total=False):
    """Keyword arguments for setting text."""

    bbox: dict[str, object] | None
    horlign: str
    textsize: float
    veralign: str
    xycoords: str


class SetScalesKwargs(TypedDict, total=False):
    """Keyword arguments for setting scales."""

    xscale: str
    xtresh: float
    yscale: str
    ytresh: float


class CheckRangeKwargs(TypedDict, total=False):
    """Keyword arguments for checking ranges."""

    xrange: list[float]
    yrange: list[float]


class ShareAxesKwargs(TypedDict, total=False):
    """Keyword arguments for sharing axes."""

    sharex: Axes
    sharey: Axes


class MinorTicksKwargs(TypedDict, total=False):
    """Keyword arguments for setting minor ticks."""

    minorticks: str


class SetTitleKwargs(TypedDict, total=False):
    """Keyword arguments for setting titles."""

    labelsize: float
    title: str | None
    titlepad: float
    titlesize: float
    xlabelpad: float
    xtitle: str | None
    ylabelpad: float
    ytitle: str | None


class SetAxisKwargs(
    CreateAxesKwargs,
    ShareAxesKwargs,
    MinorTicksKwargs,
    SetTitleKwargs,
    CheckRangeKwargs,
    SetScalesKwargs,
    total=False,
):
    """Keyword argument for set axis."""

    alpha: float
    aspect: float | Literal["auto", "equal"]
    grid: Literal["x", "y"] | bool
    ticksdir: str
    tickssize: float
    xticks: list[float] | None | bool
    xtickslabels: list[str] | None | bool
    yticks: list[float] | None | bool
    ytickslabels: list[str] | None | bool


class LegendKwargs(CreateAxesKwargs, total=False):
    """Keyword arguments for setting legends."""

    c: str | Sequence[str | ColorType] | ArrayLike | ColorType
    edgecolor: str | Sequence[str]
    fillstyle: str | Sequence[str]
    label: str | Sequence[str] | None
    legalpha: float
    legcols: int
    legpos: str | int | None
    legsize: float
    legspace: float
    ls: str | Sequence[str | LineStyleType] | LineStyleType
    lw: float | Sequence[float]
    marker: str | list[str | MarkerType] | MarkerType
    ms: float | Sequence[float]
    mscale: float | Sequence[float]


class PlotKwargs(LegendKwargs, SetAxisKwargs, total=False):
    """Keyword arguments for plotting."""


class ColorbarKwargs(CreateAxesKwargs, total=False):
    """Keyword arguments for setting colorbars."""

    clabel: str
    cpad: float
    cpos: str
    cticks: list[float] | None
    ctickslabels: list[str] | None | bool
    extend: str
    extendrect: bool


class Base2DplotKwargs(ColorbarKwargs, SetAxisKwargs, total=False):
    """Keyword arguments for base 2D plots."""

    cmap: str | Colormap
    cscale: str
    transpose: bool
    tresh: float
    vmin: float
    vmax: float
    x1: np.ndarray
    x2: np.ndarray


class DisplayKwargs(Base2DplotKwargs, total=False):
    """Keyword arguments for displaying data."""

    shading: Literal["flat", "nearest", "gouraud", "auto"] | None


class ContourKwargs(Base2DplotKwargs, total=False):
    """Keyword arguments for creating contour plots."""

    c: str | Sequence[str]
    levels: ArrayLike | float
    lw: float | Sequence[float]


class StreamplotKwargs(Base2DplotKwargs, total=False):
    """Keyword arguments for creating stream plots."""

    arrowsize: float
    arrowstyle: str
    brokenlines: bool
    c: str | Sequence[str]
    density: float
    integration_direction: Literal["forward", "backward", "both"]
    lw: float | Sequence[float]
    maxlength: float
    minlength: float
    start_points: ArrayLike | None


class ScatterKwargs(Base2DplotKwargs, LegendKwargs, total=False):
    """Keyword arguments for creating scatter plots."""

    edgecolors: str | Sequence[str]


class ZoomKwargs(DisplayKwargs, total=False):
    """Keyword arguments for base zoom functionality."""

    pos: list[float]
    var: ArrayLike


class SetLocKwargs(TypedDict, total=False):
    """Keyword arguments for setting location."""

    left: float
    bottom: float
    right: float
    top: float
    width: float
    height: float
