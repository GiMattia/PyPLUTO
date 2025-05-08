# figure_new.py
import matplotlib.pyplot as plt

from .delegator import delegator
from .imagestate import ImageState


@delegator("state")
class FigureManager:
    def __init__(self, state: ImageState) -> None:
        self.state = state
        self._setup_style()

    def _setup_style(self):
        try:
            plt.style.use(self.style)
        except OSError:
            print(
                f"Warning: Style '{self.style}' not found. Switching to 'default'"
            )
            self.style = "default"
