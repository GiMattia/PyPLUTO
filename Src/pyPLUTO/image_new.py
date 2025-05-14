# image_new.py
from typing import Any

from matplotlib.figure import Figure

from .delegator import delegator
from .figure_new import FigureManager
from .imagestate import ImageState
from .inspect_kwargs import track_kwargs


@delegator("state")
class Image_new:

    @track_kwargs
    def __init__(
        self,
        LaTeX: bool | str = True,
        fig: Figure | None = None,
        style: str = "default",
        text: bool = False,
        check: bool = True,
        **kwargs: Any,
    ) -> None:

        kwargs.pop("check", check)

        self.state: ImageState = ImageState(
            style=style, LaTeX=LaTeX, fig=fig or Figure()
        )
        self.figure_manager: FigureManager = FigureManager(self.state, **kwargs)

        if text:
            print(
                "Image class created at nwin..."
            )  # NEED TO FINISH THE SENTENCE
