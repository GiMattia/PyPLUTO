from pathlib import Path
from typing import Any, Literal, overload

import numpy as np
from numpy.typing import NDArray

from pyPLUTO.loadmixin import LoadMixin
from pyPLUTO.loadstate import LoadState

class Load(LoadMixin):
    state: LoadState
    text: bool | None
    class_name: str
    full3D: bool
    level: int

    def __init__(
        self,
        nout: int | str | list[int | str] | None = ...,
        check: bool = ...,
        **kwargs: Any,
    ) -> None: ...
    @overload
    def __getattr__(
        self,
        name: Literal[
            "x1",
            "x2",
            "x3",
            "x1r",
            "x2r",
            "x3r",
            "x1c",
            "x2c",
            "x1rc",
            "x2rc",
            "dx1",
            "dx2",
            "dx3",
            "outlist",
            "timelist",
            "noutlist",
            "ntimelist",
            "ntime",
            "nout",
        ],
    ) -> NDArray[Any]: ...
    @overload
    def __getattr__(
        self, name: Literal["nx1", "nx2", "nx3", "gridsize"]
    ) -> int: ...
    @overload
    def __getattr__(
        self,
        name: Literal[
            "geom",
            "datatype",
            "format",
            "code",
            "class_name",
        ],
    ) -> str: ...
    @overload
    def __getattr__(self, name: Literal["pathdir"]) -> str | Path: ...
    @overload
    def __getattr__(self, name: Literal["text"]) -> bool | None: ...
    @overload
    def __getattr__(self, name: str) -> NDArray[Any]: ...
    def find_fieldlines(
        self,
        var1: str | np.ndarray,
        var2: str | np.ndarray,
        x0: list | float | None = ...,
        y0: list | float | None = ...,
        text: bool = ...,
        check: bool = ...,
        **kwargs: Any,
    ) -> list: ...
    def find_contour(
        self, var: str | np.ndarray, check: bool = ..., **kwargs: Any
    ) -> list: ...
    def __setattr__(self, name: str, value: object) -> None: ...
