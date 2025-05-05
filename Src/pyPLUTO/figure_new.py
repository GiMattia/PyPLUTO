# figure_new.py
import matplotlib.pyplot as plt

from .imagestate import ImageState, ImageStateComponent


class FigureManager(ImageStateComponent):
    def __init__(self, state: ImageState) -> None:
        super().__init__(state)
        self._setup_style()

    def _setup_style(self):
        try:
            plt.style.use(self.style)
        except OSError:
            print(
                f"Warning: Style '{self.style}' not found. Switching to 'default'"
            )
            self.style = "default"
