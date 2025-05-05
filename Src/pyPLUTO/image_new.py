# image_new.py
from typing import Any

from matplotlib.figure import Figure

from .figure_new import FigureManager
from .imagestate import ImageState


class Image_new:
    def __init__(
        self,
        LaTeX: bool | str = True,
        fig: Figure | None = None,
        style: str = "default",
        text: bool = False,
        check: bool = True,
        **kwargs: Any,
    ) -> None:
        self.state: ImageState = ImageState(style=style, fig=fig or Figure())
        self.figure_manager: FigureManager = FigureManager(self.state)

    def __getattr__(self, name: str):
        try:
            return getattr(self.state, name)
        except AttributeError:
            raise AttributeError(
                f"'Image_new' object has no attribute '{name}'"
            )

    def __setattr__(self, name: str, value):
        if name in {"state", "figure_manager"}:
            object.__setattr__(self, name, value)
        else:
            setattr(self.state, name, value)
