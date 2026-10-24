"""Type annotations for accepted **kwargs in the PyPLUTO Image class.

Each table names the keywords one method accepts, and is attached to it as
`**kwargs: Unpack[SomethingKwargs]`. That is what lets an editor complete
`I.plot(ls=...)` and pyright reject a misspelled keyword before it runs.
All are `total=False`, so every key is optional.

The inheritance mirrors the call chain, not a classification: `plot()`
forwards its keywords to the legend and axis code, so PlotKwargs inherits
from LegendKwargs and SetAxisKwargs and accepts everything they do. A few
tables are attached to no method at all and exist only to be inherited.

This is the static half of the keyword checking; `track_kwargs` in
`utils/inspector.py` is the runtime half, warning about a keyword that is
accepted here but read nowhere.
"""

from __future__ import annotations

from collections.abc import Callable, Sequence
from typing import Any, Literal, TypedDict

import numpy as np
from matplotlib.axes import Axes
from matplotlib.colors import Colormap
from matplotlib.figure import Figure
from matplotlib.typing import (
    ColorType,
    LegendLocType,
    LineStyleType,
    MarkerType,
)
from numpy.typing import ArrayLike, NDArray


class ImageKwargs(TypedDict, total=False):
    """Figure keywords that create_axes and set_axis read too."""

    figsize: Sequence[float]
    fontsize: float | int
    suptitle: str | None
    tight: bool


class FigureKwargs(ImageKwargs, total=False):
    """Keyword arguments for creating figures."""

    close: bool  # deprecated, use "replace"
    fig: Figure | None
    fontweight: str
    LaTeX: bool | str
    numcolors: int
    nwin: int
    replace: bool
    style: str
    suptitlesize: int | str
    withblack: bool
    withwhite: bool


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
    sharex: bool | int | Literal["all", "row", "col"] | Axes | None
    sharexaxes: (
        bool | int | Literal["all", "row", "col"] | Axes | None
    )  # deprecated, use "sharex"
    sharey: bool | int | Literal["all", "row", "col"] | Axes | None
    shareyaxes: (
        bool | int | Literal["all", "row", "col"] | Axes | None
    )  # deprecated, use "sharey"
    top: float
    wratio: Sequence[float] | float
    wspace: Sequence[float] | float


class TextKwargs(CreateAxesKwargs, total=False):
    """Keyword arguments for setting text."""

    bbox: dict[str, object] | None
    horalign: str
    textsize: float
    veralign: str
    xycoords: Literal["fraction", "points", "figure"]


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
    MinorTicksKwargs,
    SetTitleKwargs,
    CheckRangeKwargs,
    SetScalesKwargs,
    total=False,
):
    """Keyword argument for set axis."""

    aspect: float | Literal["auto", "equal"]
    axalpha: float
    grid: Literal["x", "y", "both"] | bool
    ticksdir: str
    tickssize: float
    xticks: list[float] | bool | None
    xtickslabels: str | list[str] | bool | None
    yticks: list[float] | bool | None
    ytickslabels: str | list[str] | bool | None


class LegendKwargs(CreateAxesKwargs, total=False):
    """Keyword arguments for setting legends."""

    # Not ArrayLike: from Python 3.13, ty drops str from a union holding it
    c: (
        ColorType
        | Sequence[ColorType]
        | Sequence[Sequence[float]]
        | NDArray[Any]
        | None
    )
    edgecolor: str | Sequence[str]
    legpad: float
    fillstyle: str | Sequence[str]
    label: str | Sequence[str] | None
    legalpha: float
    legcols: int
    legpos: LegendLocType | None
    legsize: float
    legspace: float
    ls: str | Sequence[str | LineStyleType] | LineStyleType
    lw: float | Sequence[float]
    marker: str | list[str | MarkerType] | MarkerType
    ms: float | Sequence[float]
    mscale: float | Sequence[float]


class PlotKwargs(LegendKwargs, SetAxisKwargs, total=False):
    """Keyword arguments for plotting."""

    alpha: float


class ShowGridKwargs(PlotKwargs, total=False):
    """Keyword arguments for showing grid lines."""

    everyx: int
    everyy: int


class ColorbarKwargs(CreateAxesKwargs, total=False):
    """Keyword arguments for setting colorbars."""

    clabel: str
    cpad: float
    cpos: str
    cticks: list[float] | bool | None
    ctickslabels: str | list[str] | bool | None
    extend: str
    extendrect: bool


class ColorScaleKwargs(ColorbarKwargs, SetAxisKwargs, total=False):
    """Keyword arguments for the colour scale of a plot coloured by a value."""

    alpha: float
    cmap: str | Colormap
    cscale: str
    tresh: float
    vmin: float
    vmax: float


class Base2DplotKwargs(ColorScaleKwargs, total=False):
    """Keyword arguments for base 2D plots, drawn on a grid."""

    transpose: bool
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


class ScatterKwargs(ColorScaleKwargs, LegendKwargs, total=False):
    """Keyword arguments for creating scatter plots."""

    edgecolors: str | Sequence[str]


class VolumeKwargs(Base2DplotKwargs, total=False):
    """Keyword arguments for volume rendering of a 3D Cartesian field."""

    x3: np.ndarray
    opacity: str | tuple | Callable[[np.ndarray], np.ndarray]
    opacity_scale: float
    mode: Literal["composite", "mip", "average"]
    samples: int
    resolution: int | tuple[int, int]
    preview_resolution: int
    preview_samples: int
    background: str | tuple[float, float, float, float] | None
    gamma: float
    lut_size: int
    margin: float
    interactive: bool
    triad: bool
    colorbar: bool
    show_grid: bool
    set_orthographic: bool
    elev: float
    azim: float
    roll: float


class SetLocKwargs(TypedDict, total=False):
    """Keyword arguments for setting location."""

    left: float
    bottom: float
    right: float
    top: float
    width: float
    height: float


class ZoomKwargs(DisplayKwargs, total=False):
    """Keyword arguments for base zoom functionality."""

    height: float
    pos: list[float]
    var: ArrayLike
    width: float
    zoomcolor: str
    zoomlines: bool
