"""Image class. It plots the data."""

# ruff: noqa: ANN201  # noqa: RUF100

from __future__ import annotations

import logging
from typing import Unpack

import numpy as np
from matplotlib.axes import Axes
from matplotlib.collections import LineCollection, PathCollection, QuadMesh
from matplotlib.contour import QuadContourSet
from numpy.typing import ArrayLike

from pyPLUTO.amr import oplotbox
from pyPLUTO.configure import set_text
from pyPLUTO.imagefuncs.colorbar import ColorbarManager
from pyPLUTO.imagefuncs.contour import ContourManager
from pyPLUTO.imagefuncs.create_axes import CreateAxesManager
from pyPLUTO.imagefuncs.display import DisplayManager
from pyPLUTO.imagefuncs.figure import FigureManager
from pyPLUTO.imagefuncs.imagetools import ImageToolsManager
from pyPLUTO.imagefuncs.interactive import InteractiveManager
from pyPLUTO.imagefuncs.legend import LegendManager
from pyPLUTO.imagefuncs.plot import PlotManager
from pyPLUTO.imagefuncs.range import RangeManager
from pyPLUTO.imagefuncs.scatter import ScatterManager
from pyPLUTO.imagefuncs.set_axis import AxisManager
from pyPLUTO.imagefuncs.streamplot import StreamplotManager
from pyPLUTO.imagefuncs.zoom import ZoomManager
from pyPLUTO.imagekwargs import (
    ColorbarKwargs,
    ContourKwargs,
    CreateAxesKwargs,
    DisplayKwargs,
    FigureKwargs,
    LegendKwargs,
    PlotKwargs,
    ScatterKwargs,
    SetAxisKwargs,
    StreamplotKwargs,
    TextKwargs,
    ZoomKwargs,
)
from pyPLUTO.imagemixin import ImageMixin
from pyPLUTO.imagestate import ImageState
from pyPLUTO.utils.inspector import track_kwargs
from pyPLUTO.utils.resolver import AttrResolver

logger = logging.getLogger(__name__)


class Image(ImageMixin):
    """Description of the Image class.

    The Image class is a facade for the different managers that handle the
    various aspects of plotting, such as creating axes, displaying data, adding
    legends, text, fieldlines, colorbars, and more. It provides a unified
    interface for creating and managing plots in a figure. The attributes are
    handled through the `ImageState` class, which is a dataclass that stores the
    state of the image, such as the figure, axes, and other properties. The
    `Image` class uses a mediator pattern to manage the interactions between the
    different managers and the state.

    """

    @track_kwargs
    def __init__(
        self,
        text: bool | None = None,
        _check: bool = True,
        **kwargs: Unpack[FigureKwargs],
    ) -> None:
        """Initialize the Image class.

        Ihat creates a new figure and sets the LaTeX conditions, as well as the
        matplotlib style. Every Image is associated to a figure object and only
        one in order to avoid confusion between images and figures. If you want
        to create multiple figures, you have to create multiple Image objects.

        Parameters
        ----------
        - close: bool, default True
            If True, the existing figure with the same window number is closed.
        - fig: Figure | None, default None
            The figure instance. If not None, the figure is used (only
            if we need to associate an Image to an existing figure).
        - figsize: list[float], default varies
            Sets the figure size. The default is [6*sqrt(ncol), 5*sqrt(nrow)],
            computed from the number of rows and columns (or [8,5] for a single
            plot).
        - fontsize: float, default 17.0
            Sets the fontsize for all the axis components.
        - fontweight: str, default 'normal'
            The font weight for all the axis components.
        - LaTeX: bool | str, default False
            The LaTeX option. Is True is selected, the default LaTeX font
            is used. If 'pgf' is selected, the pgf backend is used to save pdf
            figures with minimal file size. If XeLaTeX is not installed and the
            'pgf' option is selected, the LaTeX option True is used as backup
            strategy.
        - numcolors: int, default 10
            The number of colors in the colorscheme. The default number is 10,
            but the full list contains 24 colors (+ black or white).
        - nwin: int, default 1
            The window number.
        - replace: bool, default False
            If True, the existing figure with the same window is replaced.
        - style: str, default 'default'
            The style of the figure. Possible values are: 'seaborn', 'ggplot',
            'fivethirtyeight', 'bmh', 'grayscale', 'dark_background', 'classic',
            etc.
        - suptitle: str, default None
            Creates a figure title over all the subplots.
        - suptitlesize: str | int, default 'large'
            The figure title size.
        - tight: bool, default True
            Enables/disables tight layout options for the figure. In case of a
            highly customized plot (e.g. ratios or space between rows and
            columns) the option is set by default to False since that option
            would not be available for standard matplotlib functions.
        - text: bool | None, default None
            Controls output verbosity. None (default) logs the window number at
            INFO level. False silences all output. True enables full DEBUG
            logging.
        - withblack: bool, default False
            If True, the black color is used as first color.
        - withwhite: bool, default False
            If True, the white color is used as first color.

        Returns
        -------
        - None

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
        self.state = ImageState()
        set_text(text)

        self.FigureManager = FigureManager(self.state, **kwargs)

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
        self.RangeManager = RangeManager(self.state)
        self.ScatterManager = ScatterManager(self.state)
        self.StreamplotManager = StreamplotManager(self.state)
        self.ZoomManager = ZoomManager(self.state)

        if text is not False:
            logger.info("Image class created at nwin %s", self.nwin)

    def __repr__(self) -> str:
        """Return the repr of the Image class."""
        return f"Image(nwin={self.nwin!r}, figsize={self.figsize!r})"

    def __str__(self) -> str:
        """Print the Image class."""
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

    def __getattr__(self, name: str) -> object:
        """Get the attribute of the Image class."""
        val = getattr(self.state, name)
        return AttrResolver.resolve(self.state, name, val)

    def __setattr__(self, name: str, value: object) -> None:
        """Set the attribute of the Image class."""
        if name == "state" or not hasattr(self, "state"):
            return super().__setattr__(name, value)
        return setattr(self.state, name, value)

    @property
    def animate(self):
        """Return the animate method."""
        return self.InteractiveManager.animate

    def colorbar(
        self,
        pcm: QuadMesh
        | PathCollection
        | LineCollection
        | QuadContourSet
        | None = None,
        axs: Axes | int | None = None,
        cax: Axes | int | None = None,
        _check: bool = True,
        **kwargs: Unpack[ColorbarKwargs],
    ):
        """Colorbar method."""
        return self.ColorbarManager.colorbar(
            pcm=pcm, axs=axs, cax=cax, _check=_check, **kwargs
        )

    colorbar.__doc__ = ColorbarManager.colorbar.__doc__

    def contour(
        self,
        var: ArrayLike,
        ax: Axes | list[Axes] | int | None = None,
        _check: bool = True,
        **kwargs: Unpack[ContourKwargs],
    ):
        """Contour method."""
        return self.ContourManager.contour(var, ax, _check=_check, **kwargs)

    contour.__doc__ = ContourManager.contour.__doc__

    def create_axes(
        self, _check: bool = True, **kwargs: Unpack[CreateAxesKwargs]
    ) -> Axes | list[Axes]:
        """Creation of a set of axes using add_subplot from matplotlib."""
        return self.CreateAxesManager.create_axes(_check=_check, **kwargs)

    create_axes.__doc__ = CreateAxesManager.create_axes.__doc__

    def display(
        self,
        var: ArrayLike,
        ax: Axes | list[Axes] | int | None = None,
        _check: bool = True,
        **kwargs: Unpack[DisplayKwargs],
    ):
        """Display method."""
        return self.DisplayManager.display(var, ax=ax, _check=_check, **kwargs)

    display.__doc__ = DisplayManager.display.__doc__

    def interactive(
        self,
        varx: dict[str, np.ndarray] | np.ndarray,
        vary: dict[str, np.ndarray] | None = None,
        _check: bool = True,
        limfix: bool = True,
        labslider: list[str | float] | None = None,
        **kwargs: Unpack[DisplayKwargs],
    ):
        """Interactive method."""
        return self.InteractiveManager.interactive(
            varx=varx,
            vary=vary,
            _check=_check,
            limfix=limfix,
            labslider=labslider,
            **kwargs,
        )

    interactive.__doc__ = InteractiveManager.interactive.__doc__

    def legend(
        self,
        ax: Axes | int | None = None,
        fromplot: bool = False,
        _check: bool = True,
        **kwargs: Unpack[LegendKwargs],
    ):
        """Legend method."""
        return self.LegendManager.legend(
            ax=ax, fromplot=fromplot, _check=_check, **kwargs
        )

    legend.__doc__ = LegendManager.legend.__doc__

    def plot(
        self,
        x: ArrayLike,
        y: ArrayLike | None = None,
        ax: Axes | list[Axes] | int | None = None,
        _check: bool = True,
        **kwargs: Unpack[PlotKwargs],
    ):
        """Plot method."""
        return self.PlotManager.plot(x, y, ax, _check=_check, **kwargs)

    plot.__doc__ = PlotManager.plot.__doc__

    @property
    def savefig(self):
        """Return the savefig method."""
        return self.ImageToolsManager.savefig

    def scatter(
        self,
        x: np.ndarray | list[float],
        y: np.ndarray | list[float],
        ax: Axes | list[Axes] | int | None = None,
        _check: bool = True,
        **kwargs: Unpack[ScatterKwargs],
    ):
        """Scatter method."""
        return self.ScatterManager.scatter(x, y, ax, _check=_check, **kwargs)

    scatter.__doc__ = ScatterManager.scatter.__doc__

    def set_axis(
        self,
        ax: Axes | list[Axes] | int | None = None,
        _check: bool = True,
        **kwargs: Unpack[SetAxisKwargs],
    ):
        """Set axis method."""
        return self.AxisManager.set_axis(ax=ax, _check=_check, **kwargs)

    set_axis.__doc__ = AxisManager.set_axis.__doc__

    def streamplot(
        self,
        var1: np.ndarray,
        var2: np.ndarray,
        ax: Axes | list[Axes] | int | None = None,
        _check: bool = True,
        **kwargs: Unpack[StreamplotKwargs],
    ):
        """Streamplot method."""
        return self.StreamplotManager.streamplot(
            var1, var2, ax, _check=_check, **kwargs
        )

    streamplot.__doc__ = StreamplotManager.streamplot.__doc__

    def text(
        self,
        text: str,
        x: float = 0.85,
        y: float = 0.85,
        ax: Axes | int | None = None,
        c: str = "k",
        _check: bool = True,
        **kwargs: Unpack[TextKwargs],
    ):
        """Text method."""
        return self.ImageToolsManager.text(
            text=text, x=x, y=y, ax=ax, c=c, _check=_check, **kwargs
        )

    text.__doc__ = ImageToolsManager.text.__doc__

    def zoom(
        self,
        ax: Axes | list[Axes] | int | None = None,
        _check: bool = True,
        **kwargs: Unpack[ZoomKwargs],
    ):
        """Zoom method."""
        return self.ZoomManager.zoom(ax=ax, _check=_check, **kwargs)

    zoom.__doc__ = ZoomManager.zoom.__doc__

    @track_kwargs
    def oplotbox(
        self, *args: object, _check: bool = True, **kwargs: object
    ) -> None:
        """Plot a box in the figure (AMR, WIP)."""
        oplotbox(self, *args, _check=False, **kwargs)
