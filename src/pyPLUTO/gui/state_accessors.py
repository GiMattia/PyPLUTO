"""State accessor mixin for ``PyPLUTOApp``."""

from __future__ import annotations

from typing import Any

import numpy as np

from pyPLUTO.gui.app_state import AppState
from pyPLUTO.image import Image as ImageType
from pyPLUTO.load import Load


class StateAccessorsMixin:
    """Expose :class:`AppState` values as window properties."""

    state: AppState

    @property
    def frozen_lines(self) -> list[dict[str, Any]]:
        """Saved line snapshots that are not updated by the slider."""
        return self.state.frozen_lines

    @property
    def live_specs(self) -> list[dict[str, Any]]:
        """Plot specs for lines that follow the time slider."""
        return self.state.live_specs

    @property
    def Data(self) -> Load:
        """Current loaded data object."""
        return self.state.Data

    @Data.setter
    def Data(self, value: Load) -> None:
        self.state.Data = value

    @property
    def data_loaded(self) -> bool:
        """Whether a dataset is currently loaded."""
        return self.state.data_loaded

    @data_loaded.setter
    def data_loaded(self, value: bool) -> None:
        self.state.data_loaded = value

    @property
    def datadict(self) -> dict[str, Any]:
        """Plot keyword arguments assembled from current GUI controls."""
        return self.state.datadict

    @datadict.setter
    def datadict(self, value: dict[str, Any]) -> None:
        self.state.datadict = value

    @property
    def datatype(self) -> str | None:
        """Detected or selected data format."""
        return self.state.datatype

    @datatype.setter
    def datatype(self, value: str | None) -> None:
        self.state.datatype = value

    @property
    def firstplot(self) -> bool:
        """Whether the next plot is the first one on the active canvas."""
        return self.state.firstplot

    @firstplot.setter
    def firstplot(self, value: bool) -> None:
        self.state.firstplot = value

    @property
    def folder_path(self) -> str | None:
        """Selected data folder path."""
        return self.state.folder_path

    @folder_path.setter
    def folder_path(self, value: str | None) -> None:
        self.state.folder_path = value

    @property
    def Image(self) -> ImageType:
        """Current ``pyPLUTO.Image`` plotting helper instance."""
        return self.state.Image

    @Image.setter
    def Image(self, value: ImageType) -> None:
        self.state.Image = value

    @property
    def nout(self) -> int | str:
        """Current output index (or ``'last'``)."""
        return self.state.nout

    @nout.setter
    def nout(self, value: int | str) -> None:
        self.state.nout = value

    @property
    def numlines(self) -> int:
        """Number of overplotted 1D lines on the active axes."""
        return self.state.numlines

    @numlines.setter
    def numlines(self, value: int) -> None:
        self.state.numlines = value

    @property
    def var(self) -> np.ndarray | None:
        """Current selected variable array after optional slicing."""
        return self.state.var

    @var.setter
    def var(self, value: np.ndarray | None) -> None:
        self.state.var = value

    @property
    def vardim(self) -> int:
        """Dimensionality of the currently selected variable view."""
        return self.state.vardim

    @vardim.setter
    def vardim(self, value: int) -> None:
        self.state.vardim = value

    @property
    def xmax(self) -> float:
        """Tracked global x-axis maximum for the current figure."""
        return self.state.xmax

    @xmax.setter
    def xmax(self, value: float) -> None:
        self.state.xmax = value

    @property
    def xmin(self) -> float:
        """Tracked global x-axis minimum for the current figure."""
        return self.state.xmin

    @xmin.setter
    def xmin(self, value: float) -> None:
        self.state.xmin = value

    @property
    def ymax(self) -> float:
        """Tracked global y-axis maximum for the current figure."""
        return self.state.ymax

    @ymax.setter
    def ymax(self, value: float) -> None:
        self.state.ymax = value

    @property
    def ymin(self) -> float:
        """Tracked global y-axis minimum for the current figure."""
        return self.state.ymin

    @ymin.setter
    def ymin(self, value: float) -> None:
        self.state.ymin = value
