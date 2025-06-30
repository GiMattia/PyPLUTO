# image_new.py
from typing import Any

from matplotlib.figure import Figure

from .colorbar import ColorbarManager
from .contour import ContourManager
from .create_axes import CreateAxesManager
from .delegator import delegator
from .display import DisplayManager
from .figure_new import FigureManager
from .imagestate import ImageState
from .imagetools_new import ImageToolsManager
from .inspector import track_kwargs
from .interactive import InteractiveManager
from .legend import LegendManager
from .mediator import Mediator
from .plot_new import PlotManager
from .scatter import ScatterManager
from .set_axis import AxisManager
from .streamplot import StreamplotManager
from .zoom import ZoomManager

manager_classes = (
    AxisManager,
    ColorbarManager,
    ContourManager,
    CreateAxesManager,
    DisplayManager,
    ImageToolsManager,
    InteractiveManager,
    LegendManager,
    PlotManager,
    ScatterManager,
    StreamplotManager,
    ZoomManager,
)


@delegator("state", "mediator")
class Image_new:
    """Image class. It plots the data.

    Image properties:
    - Figure size        (figsize)
    - Window number      (nwin)
    - Number of subplots (nrow0 x ncol0)
    - Global fontsize    (fontsize)

    Public methods available:

    WIP...

    Public attributes available:

    - color: the colora available
    - dictcolor: the color dictionary
    - fig: the figure associated to the image
    - figsize: the figure size
    - fontsize: the fontsize
    - LaTeX: the LaTeX option
    - nwin: the window number
    - style: the plotting style
    - tight: the tight layout option

    WIP...

    """

    @track_kwargs
    def __init__(
        self,
        LaTeX: bool | str = True,
        fig: Figure | None = None,
        style: str = "default",
        text: bool = True,
        check: bool = True,
        **kwargs: Any,
    ) -> None:
        """Initialization of the Image class that creates a new figure and sets
        the LaTeX conditions, as well as the matplotlib style. Every Image is
        associated to a figure object and only one in order to avoid confusion
        between images and figures. If you want to create multiple figures, you
        have to create multiple Image objects.

        Returns
        -------
        - None

        Parameters
        ----------
        - close: bool, default True
            If True, the existing figure with the same window number is closed.
        - fig: Figure | None, default None
            The the figure instance. If not None, the figure is used (only
            if we need to associate an Image to an existing figure).
        - figsize: list[float], default [8,5]
            The figure size.
        - fontsize: int, default 17
            The font size.
        - LaTeX: bool | str, default False
            The LaTeX option. Is True is selected, the default LaTeX font
            is used. If 'pgf' is selected, the pgf backend is used to save pdf
            figures with minimal file size. If XeLaTeX is not installed and the
            'pgf' option is selected, the LaTeX option True is used as backup
            strategy.
        - numcolor: int, default 10
            The number of colors in the colorscheme. The default number is 10,
            but the full list contains 24 colors (+ black or white).
        - nwin: int, default 1
            The window number.
        - oldcolor: bool, default False
            if True, the old colors are used
        - style: str, default 'default'
            The style of the figure. Possible values are: 'seaborn', 'ggplot',
            'fivethirtyeight', 'bmh', 'grayscale', 'dark_background', 'classic',
            etc.
        - suptitle: str, default None
            The super title of the figure.
        - suptitlesize: str | int, default 'large'
            The figure title size.
        - tight: bool, default True
            If True, the tight layout is used.
        - withblack: bool, default False
            If True, the black color is used as first color.
        - withwhite: bool, default False
            If True, the white color is used as first color.

        Notes
        -----
        - None

        ----

        Examples
        --------
        - Example #1: create an empty image

            >>> import pyPLUTO as pp
            >>> I = pp.Image()

        - Example #2: create an image with the pgf backend

            >>> import pyPLUTO as pp
            >>> I = pp.Image(LaTeX = 'pgf')

        - Example #3: create an image with the LaTeX option True

            >>> import pyPLUTO as pp
            >>> I = pp.Image(LaTeX = True)

        - Example #4: create an image with fixed size

            >>> import pyPLUTO as pp
            >>> I = pp.Image(figsize = [5,5])

        - Example #5: create an image with a title

            >>> import pyPLUTO as pp
            >>> I = pp.Image(suptitle = 'Title')

        """
        kwargs.pop("check", check)

        self.state = ImageState(style=style, LaTeX=LaTeX, fig=fig)
        self.mediator = Mediator(self.state, manager_classes)

        self._figure_manager = FigureManager(self.state, **kwargs)

        if text:
            print(f"Image class created at nwin {self.state.nwin}")

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
