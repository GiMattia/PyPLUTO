"""Docstring for pyPLUTO.annotator."""

from typing import TypedDict

from matplotlib.figure import Figure


class AllKwargs(TypedDict, total=False):
    """Docstring for AllKwargs."""

    close: bool
    fig: Figure | None
    figsize: list[float]
    fontsize: int
    LaTeX: bool | str
    numcolor: int
    nwin: int
    oldcolor: bool
    style: str
    suptitle: str | None
    suptitlesize: str | int
    tight: bool
    withblack: bool
    withwhite: bool
