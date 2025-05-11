from typing import Any

from matplotlib.axes import Axes

from .h_pypluto import check_par


def savefig(
    self, filename: str = "img.png", bbox: str | None = "tight", dpi: int = 300
) -> None:
    """Creation of a .png image file of the figure created with the Image
    class.

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
    self.fig.savefig(filename, bbox_inches=bbox, dpi=dpi)


def show(
    self,
) -> None:
    raise NotImplementedError(
        "Image show is deprecated, \
                              please use pp.show instead"
    )


def text(
    self,
    text: str,
    x: float = 0.85,
    y: float = 0.85,
    ax: Axes | None = None,
    check: bool = True,
    **kwargs: Any,
) -> None:
    """Insertion of a text box inside the figure created with Image class.

    Returns
    -------
    - None

    Parameters
    ----------
    - ax: axis object, default None
        The axis where to insert the text box. If None, the last considered axis
        will be used.
    - c: str, default 'k'
        Determines the text color.
    - horalign: str, default 'left'
        The horizontal alignment. Possible values are 'left', 'center', 'right'.
    - text (not optional): str
        The text that will appear on the text box
    - textsize: float, default fontsize
        Sets the text fontsize. The default value corresponds to the value of
        the actual fontsize in the figure.
    - veralign: str, default 'baseline'
        The vertical alignment. Possible values are 'baseline', 'bottom',
        'center', 'center_baseline', 'top'.
    - x: float, default 0.85
        The horizontal starting position of the text box, in units of figure
        size.
    - xycoords: str, default 'fraction'
        The coordinate system used. Possible values are 'figure fraction',
        which sets the position as a fraction of the axis (inside the axis lie
        values between 0 and 1), 'points', which sets the position in units of
        the x/y coordinate system, and 'figure', which sets the position as a
        fraction of the figure.
    - y: float, default 0.85
        The vertical starting position of the text box, in units of figure size.

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

    - Example #4: Insert text inside the last axis with a specific fontsize and
        a specific color

        >>> I.text('text', x = 0.5, y = 0.5, textsize = 20, c = 'r')

    - Example #5: Insert text inside the last axis with a points position

        >>> I.text('text', x = 0.5, y = 0.5, xycoords = 'points')

    """
    # Check parameters
    param = {"c", "horalign", "textsize", "veralign", "xycoords"}
    if check is True:
        check_par(param, "text", **kwargs)

    # Find figure and number of the axis
    ax, nax = self._assign_ax(ax, **kwargs)

    # Dictionary with the possible 'xycoords' values
    coordinates = {
        "fraction": ax.transAxes,
        "points": ax.transData,
        "figure": self.fig.transFigure,
    }

    # Set the 'xycoords' keyword
    xycoord = kwargs.get("xycoords", "fraction")

    # If the text is inside a specific axis, hide the text of the create_axes
    # function
    if xycoord != "figure":
        self._hide_text(nax, ax.texts)

    # Set the 'xycoords' value
    coord = coordinates[xycoord]

    # Set the 'veralign' and 'horalign' values
    hortx = kwargs.get("horalign", "left")
    vertx = kwargs.get("veralign", "baseline")

    # Insert the text
    ax.text(
        x,
        y,
        text,
        c=kwargs.get("c", "k"),
        transform=coord,
        fontsize=kwargs.get("textsize", self.fontsize),
        horizontalalignment=hortx,
        verticalalignment=vertx,
    )

    # End of the function
