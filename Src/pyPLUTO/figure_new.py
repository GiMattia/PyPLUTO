# figure_new.py
import warnings

import matplotlib.pyplot as plt

from .delegator import delegator
from .imagestate import ImageState


@delegator("state")
class FigureManager:
    def __init__(self, state: ImageState) -> None:
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
