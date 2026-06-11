"""Central runtime state for the PyPLUTO GUI."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any

import numpy as np


@dataclass(slots=True)
class AppState:
    """Mutable application state shared across GUI controllers."""

    # Load/session state
    folder_path: str | None = None
    datatype: str | None = None
    nout: int | str = 0
    data_loaded: bool = False

    # Plot/session state
    firstplot: bool = True
    vardim: int = 0
    numlines: int = 0
    xmin: float = 0.0
    xmax: float = 0.0
    ymin: float = 0.0
    ymax: float = 0.0
    datadict: dict[str, Any] = field(default_factory=dict)

    # Line-lock / slider replay state
    frozen_lines: list[dict[str, Any]] = field(default_factory=list)
    live_specs: list[dict[str, Any]] = field(default_factory=list)

    # Runtime objects/data
    Data: Any = None
    Image: Any = None
    var: np.ndarray | None = None
