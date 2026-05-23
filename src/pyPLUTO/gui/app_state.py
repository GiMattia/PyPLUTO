"""Central runtime state for the PyPLUTO GUI."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any

import numpy as np
from numpy.typing import NDArray


@dataclass(slots=True)
class AppState:
    """Mutable application state shared across GUI controllers."""

    # Load/session state
    folder_path: str | None = None
    datatype: str | None = None
    nout: int | str = "last"
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

    # Runtime objects/data
    Data: Any = None
    Image: Any = None
    var: NDArray[np.floating[Any]] | NDArray[np.integer[Any]] | None = None
