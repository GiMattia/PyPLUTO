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

        self.state: ImageState = ImageState(style=style, LaTeX=LaTeX, fig=fig)
        self.figure_manager: FigureManager = FigureManager(self.state, **kwargs)

        if text:
            print("Image class created at nwin...")

    def __str__(self) -> str:
        return r"""
        Image class.
        It plots the data.

        Image properties:
        - Figure size        (figsize)
        - Window number      (nwin)
        - Number of subplots (nrow0 x ncol0)
        - Global fontsize    (fontsize)

        Public methods available:

        - create_axes
            Adds a set of [nrow,ncol] subplots to the figure.
        - colorbar
            Places a colorbar in a subplot or next to a subplot.
        - contour
            Plots a contour plot in a subplot.
        - display
            Plots a 2D quantity in a subplot.
        - interactive
            Creates an interactive plot with a slider to change the data.
        - legend
            Places one legend in a subplot.
        - set_axis
            Changes the parameter of a specific subplot.
        - plot
            Plots one line in a subplot.
        - savefig
            Saves the figure in a file.
        - scatter
            Plots a scatter plot in a subplot.
        - streamplot
            Plots a stream plot in a subplot.
        - text
            Places the text in the figure or in a subplot.
        - zoom
            Creates an inset zoom region of a subplot.

        Public attributes available:

        - ax:
            The list of relevant axes in the figure.
        - fig
            The figure associated to the image.
        - fontsize
            The fontsize in the figure.
        - fontweight
            The fontweight in the figure.
        - nwin
            The window number.
        - tg
            The tight layout of the figure.

        Please do not use 'private' methods and attributes if not absolutely
        necessary.
        """
