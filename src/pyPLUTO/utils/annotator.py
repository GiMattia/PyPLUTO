"""Docstring for pyPLUTO.annotator."""

from typing import TypedDict

from matplotlib.figure import Figure


class AllKwargs(TypedDict, total=False):
    """Docstring for AllKwargs."""

    close: bool
    fig: Figure | None
    figsize: list[float]
    fontsize: int
    fontweight: str
    kwargscheck: bool
    LaTeX: bool | str
    numcolors: int
    nwin: int
    oldcolor: bool
    replace: bool
    style: str
    suptitle: str | None
    suptitlesize: int | str
    tight: bool
    withblack: bool
    withwhite: bool
