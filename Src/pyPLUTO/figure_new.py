# figure_new.py
import warnings
from typing import Any

import matplotlib.pyplot as plt

from .delegator import delegator
from .imagestate import ImageState
from .inspect_kwargs import track_kwargs


@delegator("state")
class FigureManager:

    @track_kwargs
    def __init__(self, state: ImageState, **kwargs: Any) -> None:
        self.state = state
        self._setup_style()

    def _setup_style(self) -> None:
        try:
            plt.style.use(self.state.style)
        except OSError:
            warn = f"Warning: Style '{self.state.style}' not found. \
                Switching to 'default'"
            warnings.warn(warn, UserWarning)
            self.state.style = "default"

    def _choose_colorlines(self) -> None:
        pass

    def _assign_LaTeX(self) -> None:
        pass
