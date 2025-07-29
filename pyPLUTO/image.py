# image_new.py
from typing import Any

from matplotlib.figure import Figure

from .amr import oplotbox
from .imagefuncs.colorbar import ColorbarManager
from .imagefuncs.contour import ContourManager
from .imagefuncs.create_axes import CreateAxesManager
from .imagefuncs.display import DisplayManager
from .imagefuncs.figure import FigureManager
from .imagefuncs.imagetools import ImageToolsManager
from .imagefuncs.interactive import InteractiveManager
from .imagefuncs.legend import LegendManager
from .imagefuncs.plot import PlotManager
from .imagefuncs.scatter import ScatterManager
from .imagefuncs.set_axis import AxisManager
from .imagefuncs.streamplot import StreamplotManager
from .imagefuncs.zoom import ZoomManager
from .imagemixin import ImageMixin
from .imagestate import ImageState
from .utils.inspector import track_kwargs


class Image(ImageMixin):
    """Image class. It plots the data. The Image class is a facade for the
    different managers that handle the various aspects of plotting, such as
    creating axes, displaying data, adding colorbars, and more. It provides a
    unified interface for creating and managing plots in a figure.
    The attributes are handled through the `ImageState` class, which is a
    dataclass that stores the state of the image, such as the figure, axes,
    and other properties. The `Image` class uses a mediator pattern to manage
    the interactions between the different managers and the state."""

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

        ----

        Examples
        --------
        - Example #1: create an empty image

            >>> import pyPLUTO as pp
            >>> I = pp.Image()

        - Example #2: create an image with the pgf backend

            >>> import pyPLUTO as pp
            >>> I = pp.Image(LaTeX="pgf")

        - Example #3: create an image with the LaTeX option True

            >>> import pyPLUTO as pp
            >>> I = pp.Image(LaTeX=True)

        - Example #4: create an image with fixed size

            >>> import pyPLUTO as pp
            >>> I = pp.Image(figsize=[5, 5])

        - Example #5: create an image with a title

            >>> import pyPLUTO as pp
            >>> I = pp.Image(suptitle="Title")

        """
        kwargs.pop("check", check)

        self.state = ImageState(style=style, LaTeX=LaTeX, fig=fig)

        self._figure_manager = FigureManager(self.state, **kwargs)

        # Initialize managers
        self.AxisManager = AxisManager(self.state)
        self.ColorbarManager = ColorbarManager(self.state)
        self.ContourManager = ContourManager(self.state)
        self.CreateAxesManager = CreateAxesManager(self.state)
        self.DisplayManager = DisplayManager(self.state)
        self.ImageToolsManager = ImageToolsManager(self.state)
        self.InteractiveManager = InteractiveManager(self.state)
        self.LegendManager = LegendManager(self.state)
        self.PlotManager = PlotManager(self.state)
        self.ScatterManager = ScatterManager(self.state)
        self.StreamplotManager = StreamplotManager(self.state)
        self.ZoomManager = ZoomManager(self.state)

        if text:
            print(f"Image class created at nwin {self.nwin}")

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

    def __setattr__(self, name, value):
        if name == "state" or not hasattr(self, "state"):
            # Initialization step: allow everything until state exists
            super().__setattr__(name, value)
        elif hasattr(type(self), name) or name in self.__dict__:
            # Allow normal attributes and managers
            super().__setattr__(name, value)
        elif hasattr(self.state, name):
            # Write-through to state if attr already defined
            setattr(self.state, name, value)
        else:
            # Set the attribute on the state
            setattr(self.state, name, value)

    def __getattr__(self, name):
        # Called only if attribute not found in usual places
        if hasattr(self.state, name):
            return getattr(self.state, name)
        # elif hasattr(type(self), name):
        #    return getattr(type(self), name)
        # elif hasattr(self, name):
        #    return getattr(self, name)
        else:
            raise AttributeError(f"'Image' object has no attribute '{name}'")

    @property
    def animate(self):
        return self.InteractiveManager.animate

    @property
    def colorbar(self):
        return self.ColorbarManager.colorbar

    @property
    def contour(self):
        return self.ContourManager.contour

    @property
    def create_axes(self):
        return self.CreateAxesManager.create_axes

    @property
    def display(self):
        return self.DisplayManager.display

    @property
    def interactive(self):
        return self.InteractiveManager.interactive

    @property
    def legend(self):
        return self.LegendManager.legend

    @property
    def plot(self):
        return self.PlotManager.plot

    @property
    def savefig(self):
        return self.ImageToolsManager.savefig

    @property
    def scatter(self):
        return self.ScatterManager.scatter

    @property
    def set_axis(self):
        return self.AxisManager.set_axis

    @property
    def show(self):
        return self.ImageToolsManager.show

    @property
    def text(self):
        return self.ImageToolsManager.text

    @property
    def streamplot(self):
        return self.StreamplotManager.streamplot

    @property
    def zoom(self):
        return self.ZoomManager.zoom

    def oplotbox(self, *args: Any, **kwargs: Any) -> None:
        """Plots a box in the figure (AMR, WIP)"""
        oplotbox(self, *args, **kwargs)
