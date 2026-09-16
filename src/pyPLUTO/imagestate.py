"""Module that contains the ImageState class.

The plotting counterpart of BaseLoadState: one instance per Image, handed by
reference to each of the sixteen managers, so what one of them records is
immediately visible to the others and to the Image the user holds.
"""

from __future__ import annotations

from collections.abc import Sequence
from dataclasses import dataclass, field
from typing import Any

from matplotlib.axes import Axes
from matplotlib.figure import Figure
from matplotlib.typing import LegendLocType


@dataclass
class ImageState:
    """Class that stores the state of the Image class.

    Its purpose is to keep track of the current state of the image, such as the
    figure, axes, and other properties and update the key attributes through all
    the different classes that handle the plotting and display of the image at
    runtime.

    Unlike the load states, every field here has a default: an Image is usable
    the moment it is built, so there is nothing that only a later step can
    fill in.

    Most of the lists are *per axis*, indexed by the axis number that the
    managers call `nax`, and they grow as axes are created. So `nline[2]` is
    the number of lines drawn on the third axis, `vlims[2]` its colour limits,
    and so on. That is why so many defaults are an empty list rather than a
    value: there are no axes yet.

    Every mutable default uses `default_factory`, or all images would share
    one list and drawing on a second figure would disturb the first.
    """

    # The axes created so far; the index into every per-axis list below
    ax: list[Axes] = field(default_factory=list)

    # The colour cycle used for successive lines
    color: list[str] = field(default_factory=list)

    # The full colour palette, by index
    dictcol: dict[int, str] = field(default_factory=dict)

    # The matplotlib figure everything is drawn on
    fig: Figure | None = None

    # Figure size in inches
    figsize: Sequence[float] = field(default_factory=lambda: [8.0, 5.0])

    # Base font size for the figure
    fontsize: float = 17

    # Base font weight for the figure
    fontweight: str = "normal"

    # LaTeX rendering: True, False, or the name of a backend such as "pgf"
    LaTeX: bool | str = True

    # Per axis, the legend parameters: size, columns, spacing, pad and alpha
    legpar: list[list[float]] = field(default_factory=list)

    # Per axis, where the legend sits
    legpos: list[LegendLocType | None] = field(default_factory=list)

    # Number of columns already created, so a later create_axes continues on
    ncol0: int = 0

    # Per axis, how many lines have been drawn, which picks the next colour
    nline: list[int] = field(default_factory=list)

    # Number of rows already created, so a later create_axes continues on
    nrow0: int = 0

    # Per axis, whether a text has been placed on it
    ntext: list[Any | None] = field(default_factory=list)

    # Window number of the figure
    nwin: int = 1

    # Per axis, whether the x range was set and by whom
    setax: list[Any | int] = field(default_factory=list)

    # Per axis, whether the y range was set and by whom
    setay: list[Any | int] = field(default_factory=list)

    # Whether the user gave a figure size, which stops it being recomputed
    set_size: bool = False

    # Per axis, the shading mode used by the 2D plots
    shade: list[str] = field(default_factory=list)

    # The matplotlib style in use
    style: str = "default"

    # Per axis, whether the ticks have been configured
    tickspar: list[Any | int] = field(default_factory=list)

    # Whether the figure uses a tight layout
    tight: bool = True

    # Per axis, the colour limits of the last 2D plot
    vlims: list[list[float]] = field(default_factory=list)

    # The volume renderers created, kept so they can be updated and closed
    volumes: list[Any] = field(default_factory=list)

    # Per axis, the scale of the x axis
    xscale: list[str] = field(default_factory=list)

    # Per axis, the scale of the y axis
    yscale: list[str] = field(default_factory=list)
