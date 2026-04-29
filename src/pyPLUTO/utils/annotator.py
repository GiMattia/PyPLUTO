"""Docstring for the pyPLUTO.annotator.

The aim is to provide a comprehensive annotation system for the pyPLUTO library,
based on the absence of duplicate keywords across the entire module.
"""

from typing import TypedDict

from matplotlib.figure import Figure


class AllKwargs(TypedDict, total=False):
    """Class for AllKwargs of PyPLUTO, properly annotated."""

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
