# imagestate.py

from dataclasses import dataclass, field
from typing import Any

from matplotlib.axes import Axes
from matplotlib.figure import Figure


@dataclass
class ImageState:
    """Class that stores the state of the Image class. It contains the
    following attributes:

    - LaTeX: bool | str (non optional)
    - style: str (non optional)
    - color: list[str]
    - dictcolor: dict[int, str]
    - fig: Figure | None
    - figsize: list[float]
    - fontsize: int
    - nwin: int
    - tight: bool
    ...
    """

    LaTeX: bool | str
    style: str
    ax: list[Axes] = field(default_factory=list)
    color: list[str] = field(default_factory=list)
    dictcol: dict[int, str] = field(default_factory=dict)
    fig: Figure | None = None
    figsize: list[float] = field(default_factory=lambda: [8.0, 5.0])
    fontsize: int = 17
    legpar: list[list[float]] = field(default_factory=list)
    legpos: list[int | str | None] = field(default_factory=list)
    ncol0: int = 0
    nline: list[int] = field(default_factory=list)
    nrow0: int = 0
    ntext: list[Any | None] = field(default_factory=list)
    nwin: int = 1
    setax: list[Any | int] = field(default_factory=list)
    setay: list[Any | int] = field(default_factory=list)
    set_size: bool = False
    shade: list[str] = field(default_factory=list)
    tickspar: list[Any | int] = field(default_factory=list)
    tight: bool = True
    vlims: list[list[float]] = field(default_factory=list)
    xscale: list[str] = field(default_factory=list)
    yscale: list[str] = field(default_factory=list)

    def __setattr__(self, name: str, value: object) -> None:
        super().__setattr__(name, value)
