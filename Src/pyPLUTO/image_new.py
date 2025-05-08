# image_new.py
from typing import Any

from matplotlib.figure import Figure

from .delegator import delegator
from .figure_new import FigureManager
from .imagestate import ImageState


@delegator("state")
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
