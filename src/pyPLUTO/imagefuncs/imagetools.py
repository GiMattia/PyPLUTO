"""Module providing image tools for saving figures and adding text."""

from __future__ import annotations

import importlib
import inspect
import warnings
from collections.abc import Sequence
from pathlib import Path
from typing import Unpack, cast

import matplotlib.colors as mcol
import matplotlib.pyplot as plt
from matplotlib.axes import Axes
from matplotlib.colors import Normalize
from matplotlib.text import Text

from pyPLUTO.imagefuncs.create_axes import CreateAxesManager
from pyPLUTO.imagekwargs import CreateAxesKwargs, TextKwargs
from pyPLUTO.imagemixin import ImageMixin
from pyPLUTO.imagestate import ImageState
from pyPLUTO.utils.inspector import track_kwargs

try:
    _pm = importlib.import_module("pastamarkers")
    salsa = getattr(_pm, "salsa", None)
except (ImportError, ModuleNotFoundError, AttributeError):
    salsa = None


class ImageToolsManager(ImageMixin):
    """ImageToolsManager class.

    It provides methods to save figures, add text.
    """

    def __init__(self, state: ImageState) -> None:
        """Initialize the ImageToolsManager with the given state."""
        self.state = state
        self.CreateAxesManager = CreateAxesManager(state)

    def savefig(
        self,
        filename: str = "img.png",
        bbox: str | None = "tight",
        dpi: int = 300,
        script_relative: bool = False,
    ) -> None:
        """Create a .png image file of the figure created with the Image class.

        Parameters
        ----------
        - bbox: {'tight', None}, default 'tight'
            Crops the white borders of the Image to create a more balanced image
            file.
        - filename: str, default 'img.png'
            The name of the saved image file.
        - script_relative: bool, default False
            If True, the image is saved in the same directory as the script
            calling this method. If False, the image is saved in the current
            working directory.
        - dpi: int, default 300
            The resolution of the saved image in dots per inch (DPI).

        Returns
        -------
        - None

        Examples
        --------
        - Example #1: save an empty image

            >>> import pyPLUTO as pp
            >>> I = pp.Image()
            >>> I.savefig("namefile.png")

        """
        if not self.state.fig:
            raise ValueError("No figure to save. Please create a figure first.")
        out_path = Path(filename)

        if script_relative and not out_path.is_absolute():
            # Find the path of the script calling this method
            caller_file = Path(inspect.stack()[1].filename).resolve()
            base_dir = caller_file.parent
            out_path = base_dir / out_path

        self.state.fig.savefig(out_path, bbox_inches=bbox, dpi=dpi)

    @track_kwargs
    def text(
        self,
        text: str,
        x: float = 0.85,
        y: float = 0.85,
        ax: Axes | int | None = None,
        c: str = "k",
        _check: bool = True,
        **kwargs: Unpack[TextKwargs],
    ) -> None:
        """Insert a text box inside the figure created with Image class.

        Parameters
        ----------
        - ax: axis object, default None
            The axis where to insert the text box. If None, the last considered
            axis will be used.
        - bbox: str | None, default None
            The bounding box for the text.
        - bottom: float, default varies
            The bottom limit of the axis / axes set. For the figure layout it
            is the space from the bottom border to the plot (default 0.1); for
            an inset zoom it is the bottom position of the inset (default 0.6 +
            height).
        - c: str, default 'k'
            The text color.
        - figsize: list[float], default varies
            Sets the figure size. The default is [6*sqrt(ncol), 5*sqrt(nrow)],
            computed from the number of rows and columns (or [8,5] for a single
            plot).
        - fontsize: float, default 17.0
            Sets the fontsize for all the axis components.
        - horalign: str, default 'left'
            The horizontal alignment. Possible values are 'left', 'center',
            'right'.
        - hratio: [float], default [1.0]
            Ratio between the rows of the plot. The default is that every plot
            row has the same height.
        - hspace: [float], default []
            The space between plot rows (in figure units). If not enough or too
            many spaces are considered, the program will remove the excess and
            fill the lacks with [0.1].
        - left: float, default varies
            The left limit of the axis / axes set. For the figure layout it is
            the space from the left border to the plot (default 0.125); for an
            inset zoom it is the left position of the inset (default 0.6).
        - ncol: int, default 1
            The number of columns of subplots.
        - nrow: int, default 1
            The number of rows of subplots.
        - proj: str, default None
            Custom projection for the plot (e.g. 3D). Recommended only if
            needed. WARNING: pyPLUTO does not support 3D plotting for now, only
            3D axes. The 3D plot feature will be available in future releases.
        - right: float, default varies
            The right limit of the axis / axes set. For the figure layout it is
            the space from the right border to the plot (default 0.9); for an
            inset zoom it is the right position of the inset (default left +
            0.15).
        - sharex: bool | str | Matplotlib axis, default False
            Enables/disables the sharing of the x-axis between the subplots.
        - sharey: bool | str | Matplotlib axis, default False
            Enables/disables the sharing of the y-axis between the subplots.
        - suptitle: str, default None
            Creates a figure title over all the subplots.
        - text (not optional): str
            The text that will appear on the text box
        - textsize: float, default fontsize
            Sets the text fontsize. The default value corresponds to the value
            of the actual fontsize in the figure.
        - tight: bool, default True
            Enables/disables tight layout options for the figure. In case of a
            highly customized plot (e.g. ratios or space between rows and
            columns) the option is set by default to False since that option
            would not be available for standard matplotlib functions.
        - top: float, default varies
            The top limit of the axis / axes set. For the figure layout it is
            the space from the top border to the plot (default 0.9); for an
            inset zoom it is the top position of the inset (default bottom +
            height).
        - veralign: str, default 'baseline'
            The vertical alignment. Possible values are 'baseline', 'bottom',
            'center', 'center_baseline', 'top'.
        - x: float, default 0.85
            The horizontal starting position of the text box, in units of figure
            size.
        - wratio: [float], default [1.0]
            Ratio between the columns of the plot. The default is that every
            plot column has the same width.
        - wspace: [float], default []
            The space between plot columns (in figure units). If not enough or
            too many spaces are considered, the program will remove the excess
            and fill the lacks with [0.1].
        - xycoords: str, default 'fraction'
            The coordinate system used. Possible values are 'figure fraction',
            which sets the position as a fraction of the axis (inside the axis
            lie values between 0 and 1), 'points', which sets the position in
            units of the x/y coordinate system, and 'figure', which sets the
            position as a fraction of the figure.
        - y: float, default 0.85
            The vertical starting position of the text box, in units of figure
            size.

        Returns
        -------
        - None

        Examples
        --------
        - Example #1: Insert text inside a specific axis

            >>> I.text("text", x=0.5, y=0.5, ax=ax)

        - Example #2: Insert text inside the last axis

            >>> I.text("text", x=0.5, y=0.5)

        - Example #3: Insert text inside the last axis with a specific fontsize

            >>> I.text("text", x=0.5, y=0.5, textsize=20)

        - Example #4: Insert text inside the last axis with a specific fontsize
            and a specific color

            >>> I.text("text", x=0.5, y=0.5, textsize=20, c="r")

        - Example #5: Insert text inside the last axis with a points position

            >>> I.text("text", x=0.5, y=0.5, xycoords="points")

        """
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
            c=c,
            transform=coord,
            fontsize=kwargs.get("textsize", self.state.fontsize),
            horizontalalignment=hortx,
            verticalalignment=vertx,
            bbox=kwargs.get("bbox", bbox),
        )

    # End of the function

    @track_kwargs
    def assign_ax(
        self,
        ax: Axes | list[Axes] | int | None,
        _check: bool = True,
        **kwargs: Unpack[CreateAxesKwargs],
    ) -> tuple[Axes, int]:
        """Set the axes of the figure where the plot/feature should go.

         If no axis is present, an axis is created. If the axis is
         present but no axis is seletced, the last axis is selected.

        Parameters
        ----------
        - ax (not optional): ax | int | list[ax] | None
            The selected set of axes.
        - bottom: float, default varies
            The bottom limit of the axis / axes set. For the figure layout it
            is the space from the bottom border to the plot (default 0.1); for
            an inset zoom it is the bottom position of the inset (default 0.6 +
            height).
        - figsize: list[float], default varies
            Sets the figure size. The default is [6*sqrt(ncol), 5*sqrt(nrow)],
            computed from the number of rows and columns (or [8,5] for a single
            plot).
        - fontsize: float, default 17.0
            Sets the fontsize for all the axis components.
        - hratio: [float], default [1.0]
            Ratio between the rows of the plot. The default is that every plot
            row has the same height.
        - hspace: [float], default []
            The space between plot rows (in figure units). If not enough or too
            many spaces are considered, the program will remove the excess and
            fill the lacks with [0.1].
        - left: float, default varies
            The left limit of the axis / axes set. For the figure layout it is
            the space from the left border to the plot (default 0.125); for an
            inset zoom it is the left position of the inset (default 0.6).
        - ncol: int, default 1
            The number of columns of subplots.
        - nrow: int, default 1
            The number of rows of subplots.
        - proj: str, default None
            Custom projection for the plot (e.g. 3D). Recommended only if
            needed. WARNING: pyPLUTO does not support 3D plotting for now, only
            3D axes. The 3D plot feature will be available in future releases.
        - right: float, default varies
            The right limit of the axis / axes set. For the figure layout it is
            the space from the right border to the plot (default 0.9); for an
            inset zoom it is the right position of the inset (default left +
            0.15).
        - sharex: bool | str | Matplotlib axis, default False
            Enables/disables the sharing of the x-axis between the subplots.
        - sharey: bool | str | Matplotlib axis, default False
            Enables/disables the sharing of the y-axis between the subplots.
        - suptitle: str, default None
            Creates a figure title over all the subplots.
        - tight: bool, default True
            Enables/disables tight layout options for the figure. In case of a
            highly customized plot (e.g. ratios or space between rows and
            columns) the option is set by default to False since that option
            would not be available for standard matplotlib functions.
        - top: float, default varies
            The top limit of the axis / axes set. For the figure layout it is
            the space from the top border to the plot (default 0.9); for an
            inset zoom it is the top position of the inset (default bottom +
            height).
        - wratio: [float], default [1.0]
            Ratio between the columns of the plot. The default is that every
            plot column has the same width.
        - wspace: [float], default []
            The space between plot columns (in figure units). If not enough or
            too many spaces are considered, the program will remove the excess
            and fill the lacks with [0.1].

        Returns
        -------
        - tuple[Axes, int]

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
            kwargs["ncol"] = 1
            kwargs["nrow"] = 1
            ax = self.CreateAxesManager.create_axes(_check=False, **kwargs)

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
        elif isinstance(ax, list) and isinstance(ax[0], Axes):
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
        """Hide the text placed when an axis is created (the axis index).

        Parameters
        ----------
        - nax (not optional): int
            The number of the selected set of axes.
        - txts (not optional): str | None
            The text of the selected set of axes.

        Returns
        -------
        - None

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

    def set_cscale(
        self,
        cscale: str,
        vmin: float,
        vmax: float,
        tresh: float,
    ) -> Normalize:
        """Set the color scale and limits of a pcolormesh given the scale.

        Parameters
        ----------
        - cscale : {'linear','log','symlog','twoslope'}, default 'linear'
            Sets the colorbar scale. Default is the linear ('norm') scale.
        - tresh (not optional): float
            Sets the threshold for the colormap. If not defined, the threshold
            will be set to 1% of the maximum absolute value of the variable.
            The default cases are the following:
            - twoslope colorscale: sets the limit between the two linear
            regimes.
            - symlog: sets the limit between the logaitrhmic and the linear
            regime.
        - vmax (not optional): float
            The maximum value of the variable to be computed / plotted.
        - vmin (not optional): float
            The minimum value of the variable to be computed / plotted.

        Returns
        -------
        - Normalize

        Examples
        --------
        - Example #1: set a linear colormap between 0 and 1

            >>> _set_cscale("linear", 0.0, 1.0)

        - Example #2: set a logarithmic colormap between 0.1 and 1

            >>> _set_cscale("log", 0.1, 1.0)

        - Example #3: set a twoslope colormap between -1 and 1 with threshold
            0.1

            >>> _set_cscale("twoslope", -1.0, 1.0, 0.1)

        """
        norm: Normalize

        if cscale == "log":
            norm = mcol.LogNorm(vmin=vmin, vmax=vmax)
        elif cscale == "symlog":
            norm = mcol.SymLogNorm(tresh, vmin=vmin, vmax=vmax)
        elif cscale in ("twoslope", "2slope"):
            norm = mcol.TwoSlopeNorm(vmin=vmin, vmax=vmax, vcenter=tresh)
        elif cscale == "power":
            norm = mcol.PowerNorm(gamma=tresh, vmin=vmin, vmax=vmax)
        elif cscale == "asinh":
            norm = mcol.AsinhNorm(tresh, vmin, vmax)
        else:
            norm = mcol.Normalize(vmin=vmin, vmax=vmax)

        return norm

    def find_cmap(
        self, name: str | mcol.Colormap | None
    ) -> mcol.Colormap | None:
        """Find a colormap by name.

        Parameters
        ----------
        - name (not optional): str | Colormap | None
            The name of the colormap.

        Returns
        -------
        - Colormap | None

        Examples
        --------
        - Example #1: find a colormap by name

            >>> _find_cmap("viridis")

        - Example #2: find a colormap by name

            >>> _find_cmap("viridis_r")

        """
        # Find a colormap by name or return a default one if not found.
        if isinstance(name, mcol.Colormap) or name is None:
            return name

        # First, try matplotlib colormap
        try:
            return plt.get_cmap(name)
        except ValueError:
            pass  # Not a matplotlib colormap

        if salsa is None:
            warn = (
                "salsa is not installed, cannot find colormap. "
                "Defaulting to 'plasma'."
            )
            warnings.warn(warn, UserWarning, stacklevel=2)
            return plt.get_cmap("plasma")

        # Try salsa colormap
        reverse = False
        base_name = name
        if name.endswith("_r"):
            base_name = name[:-2]
            reverse = True

        if (cmap := getattr(salsa, base_name, None)) is not None:
            if reverse:
                # Prefer .reversed() method if available
                rev = getattr(cmap, "reversed", None)
                if callable(rev):
                    return cast(mcol.Colormap, rev())
            return cast(mcol.Colormap, cmap)

        # Gigantic warning!
        warn = (
            f"Colormap '{name}' not found in matplotlib or salsa! "
            "Defaulting to 'plasma'."
        )
        warnings.warn(warn, UserWarning, stacklevel=2)
        return plt.get_cmap("plasma")
