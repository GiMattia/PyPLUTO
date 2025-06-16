from collections.abc import Sequence
from typing import Any

from matplotlib.axes import Axes
from matplotlib.text import Text

from .create_axes import CreateAxesManager
from .delegator import delegator
from .imagestate import ImageState
from .inspector import track_kwargs


@delegator("state")
class ImageToolsManager:

    exposed_methods = (
        "savefig",
        "text",
        "show",
    )

    def __init__(self, state: ImageState):
        """Initialize the ImageToolsManager with the given state."""
        self.state = state
        self.AxesManager = CreateAxesManager(state)

    def savefig(
        self,
        filename: str = "img.png",
        bbox: str | None = "tight",
        dpi: int = 300,
    ) -> None:
        """Creation of a .png image file of the figure created with the
        Image class.

        Returns
        -------
        - None

        Parameters
        ----------
        - bbox: {'tight', None}, default 'tight'
            Crops the white borders of the Image to create a more balanced image
            file.
        - filename: str, default 'img.png'
            The name of the saved image file.

        Notes
        -----
        - None

        ----

        Examples
        --------
        - Example #1: save an empty image

            >>> import pyPLUTO as pp
            >>> I = pp.Image()
            >>> I.savefig('namefile.png')

        """
        if not self.state.fig:
            raise ValueError("No figure to save. Please create a figure first.")
        self.state.fig.savefig(filename, bbox_inches=bbox, dpi=dpi)

    def show(
        self,
    ) -> None:
        raise NotImplementedError(
            "Image show is deprecated, please use pp.show instead"
        )

    @track_kwargs
    def text(
        self,
        text: str,
        x: float = 0.85,
        y: float = 0.85,
        ax: Axes | None = None,
        check: bool = True,
        **kwargs: Any,
    ) -> None:
        """Insertion of a text box inside the figure created with Image
        class.

        Returns
        -------
        - None

        Parameters
        ----------
        - ax: axis object, default None
            The axis where to insert the text box. If None, the last considered
            axis will be used.
        - c: str, default 'k'
            Determines the text color.
        - horalign: str, default 'left'
            The horizontal alignment. Possible values are 'left', 'center',
            'right'.
        - text (not optional): str
            The text that will appear on the text box
        - textsize: float, default fontsize
            Sets the text fontsize. The default value corresponds to the value
            of the actual fontsize in the figure.
        - veralign: str, default 'baseline'
            The vertical alignment. Possible values are 'baseline', 'bottom',
            'center', 'center_baseline', 'top'.
        - x: float, default 0.85
            The horizontal starting position of the text box, in units of figure
            size.
        - xycoords: str, default 'fraction'
            The coordinate system used. Possible values are 'figure fraction',
            which sets the position as a fraction of the axis (inside the axis
            lie values between 0 and 1), 'points', which sets the position in
            units of the x/y coordinate system, and 'figure', which sets the
            position as a fraction of the figure.
        - y: float, default 0.85
            The vertical starting position of the text box, in units of figure
            size.

        Notes
        -----
        - None

        ----

        Examples
        --------
        - Example #1: Insert text inside a specific axis

            >>> I.text('text', x = 0.5, y = 0.5, ax = ax)

        - Example #2: Insert text inside the last axis

            >>> I.text('text', x = 0.5, y = 0.5)

        - Example #3: Insert text inside the last axis with a specific fontsize

            >>> I.text('text', x = 0.5, y = 0.5, textsize = 20)

        - Example #4: Insert text inside the last axis with a specific fontsize
            and a specific color

            >>> I.text('text', x = 0.5, y = 0.5, textsize = 20, c = 'r')

        - Example #5: Insert text inside the last axis with a points position

            >>> I.text('text', x = 0.5, y = 0.5, xycoords = 'points')

        """
        kwargs.pop("check", check)

        # Find figure and number of the axis
        ax, nax = self.assign_ax(ax, **kwargs)

        if self.state.fig is None:
            raise ValueError(
                "No figure is present. Please create a figure first."
            )

        # Dictionary with the possible 'xycoords' values
        coordinates = {
            "fraction": ax.transAxes,
            "points": ax.transData,
            "figure": self.state.fig.transFigure,
        }

        # Set the 'xycoords' keyword
        xycoord = kwargs.get("xycoords", "fraction")

        # If the text is inside a specific axis, hide the text of the
        # create_axes function
        if xycoord != "figure":
            self.hide_text(nax, ax.texts)

        # Set the 'xycoords' value
        coord = coordinates[xycoord]

        # Set the 'veralign' and 'horalign' values
        hortx = kwargs.get("horalign", "left")
        vertx = kwargs.get("veralign", "baseline")

        bbox = kwargs.get("bbox")

        # Insert the text
        ax.text(
            x,
            y,
            text,
            c=kwargs.get("c", "k"),
            transform=coord,
            fontsize=kwargs.get("textsize", self.state.fontsize),
            horizontalalignment=hortx,
            verticalalignment=vertx,
            bbox=kwargs.get("bbox", bbox),
        )

    # End of the function

    def assign_ax(
        self, ax: Axes | list[Axes] | None, **kwargs: Any
    ) -> tuple[Axes, int]:
        """Sets the axes of the figure where the plot/feature should go.
        If no axis is present, an axis is created. If the axis is
        present but no axis is seletced, the last axis is selected.

        Returns
        -------
        - ax: ax | list[ax] | int | None
            The selected set of axes.
        - nax: int
            The number of the selected set of axes.

        Parameters
        ----------
        - ax (not optional): ax | int | list[ax] | None
            The selected set of axes.
        - **kwargs: Any
            The keyword arguments to be passed to the create_axes function
            (not written here since is not public method).

        Notes
        -----
        - None

        ----

        Examples
        --------
        - Example #1: Set the axes of the figure

            >>> _assign_ax(ax, **kwargs)

        - Example #2: Set the axes of the figure (no axis selected)

            >>> _assign_ax(None, **kwargs)

        - Example #3: Set the axes of the figure (axis is a list)

            >>> _assign_ax([ax], **kwargs)

        """
        if self.state.fig is None:
            raise ValueError(
                "No figure is present. Please create a figure first."
            )
        # Check if the axis is None and no axis is present (and create one)
        if ax is None and len(self.state.ax) == 0:
            ax = self.AxesManager.create_axes(
                ncol=1, nrow=1, check=False, **kwargs
            )

        # Check if the axis is None and an axis is present (and select the last
        # one, the current axis if it belongs to the one saved in the figure or
        # the last one saved
        elif ax is None and len(self.state.ax) > 0:
            ax = (
                self.state.fig.gca()
                if self.state.fig.gca() in self.state.ax
                else self.state.ax[-1]
            )

        # Check if the axis is a list and select the first element
        elif isinstance(ax, list):
            ax = ax[0]

        # Check if the axis is an int, and select the corresponding axis from
        # the list of axes
        elif isinstance(ax, int):
            ax = self.state.ax[ax]

        # If none of the previous cases is satisfied assert that ax is an axis
        if not isinstance(ax, Axes):
            raise ValueError("The provided axis is not valid.")

        # Get the figure associated to the axes
        fig = ax.get_figure()

        # Check if the figure is the same as the one in the class
        if fig != self.state.fig:
            text = "The provided axis does not belong to the expected figure."
            raise ValueError(text)

        # Find the number of the axes and return it
        nax = self.state.ax.index(ax)

        # Return the axis and its index
        return ax, nax

    def hide_text(self, nax: int, txts: Sequence[Text] | None) -> None:
        """Hides the text placed when an axis is created (the axis
        index).

        Returns
        -------
        - None

        Parameters
        ----------
        - nax (not optional): int
            The number of the selected set of axes.
        - txts (not optional): str | None
            The text of the selected set of axes.

        Notes
        -----
        - None

        ----

        Examples
        --------
        - Example #1: Hide the text of the selected set of axes

            >>> _hide_text(nax, txts)

        """
        # Check if the text has already been removed
        if self.state.ntext[nax] is None and txts is not None:
            for txt in txts:
                txt.set_visible(False)

            # Set the text as removed
            self.state.ntext[nax] = 1

        # End of the function
