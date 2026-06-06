"""Module providing colorbar management functionalities for image displays."""

from __future__ import annotations

import warnings
from typing import Unpack

from matplotlib.axes import Axes
from matplotlib.collections import LineCollection, PathCollection, QuadMesh
from matplotlib.contour import QuadContourSet
from matplotlib.ticker import FixedFormatter, FixedLocator
from mpl_toolkits.axes_grid1 import make_axes_locatable

from pyPLUTO.imagefuncs.imagetools import ImageToolsManager
from pyPLUTO.imagekwargs import ColorbarKwargs
from pyPLUTO.imagemixin import ImageMixin
from pyPLUTO.imagestate import ImageState
from pyPLUTO.utils.inspector import track_kwargs


class ColorbarManager(ImageMixin):
    """Class to manage the colorbar in the image.

    This class provides methods to create and manage colorbars in the image
    class. It allows for customization of the colorbar's position, size,
    ticks, labels, and other properties.
    """

    def __init__(self, state: ImageState) -> None:
        """Initialize the ColorbarManager with the given state."""
        self.state = state
        self.ImageToolsManager = ImageToolsManager(state)

    @track_kwargs
    def colorbar(
        self,
        pcm: (
            QuadMesh | PathCollection | LineCollection | QuadContourSet | None
        ) = None,
        axs: Axes | int | None = None,
        cax: Axes | int | None = None,
        _check: bool = True,
        **kwargs: Unpack[ColorbarKwargs],
    ) -> None:
        """Display a colorbar in a selected position.

        The colorbar will be placed next to the axis axs. If the keyword cax is
        enabled the colorbar is located in a specific axis, otherwise an axis
        will be shrunk in order to place the colorbar.

        Parameters
        ----------
        - axs: axis object, default None
            The axes where the display that will be used for the colorbar is
            located. If None, the last considered axis will be used.
        - bottom: float, default varies
            The bottom limit of the axis / axes set. For the figure layout it
            is the space from the bottom border to the plot (default 0.1); for
            an inset zoom it is the bottom position of the inset (default 0.6 +
            height).
        - cax: axis object, default None
            The axes where the colorbar should be placed. If None, the colorbar
            will be placed next to the axis axs.
        - clabel: str, default None
            Sets the label of the colorbar.
        - cpad: float, default 0.07
            Fraction of original axes between colorbar and the axes (in axes
            units).
        - cpos: {'top','bottom','left','right'}, default None
            Enables the colorbar and sets its position. If not defined, no
            colorbar is shown.
        - cticks: {[float], None}, default None
            If enabled (and different from None), sets manually the ticks on
            the colorbar.
        - ctickslabels: str, default None
            If enabled, sets manually ticks labels on the colorbar.
        - extend: {'neither','both','min','max'}, default 'neither'
            Sets the extension of the triangular colorbar extension.
        - extendrect: bool, default False
            If True, the colorbar extension will be triangular.
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
        - pcm: QuadMesh | PathCollection | None, default None
            The collection to be used for the colorbar. If None, the axs will be
            used. If both pcm and axs are not None, pcm will be used.
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
        - None

        Examples
        --------
        - Example #1: create a standard colorbar on the right

            >>> import pyPLUTO as pp
            >>> I = pp.Image()
            >>> I.display(var)
            >>> I.colorbar()

        - Example #2: create a colorbar in a different axis

            >>> import pyPLUTO as pp
            >>> I = pp.Image()
            >>> ax = I.create_axes(ncol=2)
            >>> I.display(var, ax=ax[0])
            >>> I.colorbar(axs=ax[0], cax=ax[1])

        - Example #3: create a set of 3 displays with a colorbar on the bottom.
            Another colorbar is shown on the right of the topmost display

            >>> import pyPLUTO as pp
            >>> I = pp.Image()
            >>> ax = I.create_axes(nrow=4)
            >>> I.display(var1, ax=ax[0])
            >>> I.colorbar(axs=ax[0])
            >>> I.display(var2, ax=ax[1])
            >>> I.display(var3, ax=ax[2])
            >>> I.colorbar(axs=ax[2], cax=ax[3])

        """
        # Check parameters
        if not isinstance(_check, bool):
            raise TypeError("_check must be a boolean value.")

        # If pcm and a source axes are selected, raise a warning and use pcm
        if pcm is not None and axs is not None:
            warn = "Both pcm and axs are not None, pcm will be used"
            warnings.warn(warn, UserWarning, stacklevel=2)

        # Standard check on the figure
        if self.state.fig is None:
            raise ValueError(
                "No figure is present. Please create a figure first."
            )

        # Assign the source axis
        axs = self._find_ax(pcm, axs)

        # Select the keywords to position the colorbar
        if pcm is None:
            collection = axs.collections[0]
            if not isinstance(collection, QuadMesh):
                raise TypeError("First collection is not a QuadMesh")
            pcm = collection
        cpad = kwargs.get("cpad", 0.07)
        cpos = kwargs.get("cpos", "right")
        ccor = "vertical" if cpos in ["left", "right"] else "horizontal"

        # Assign the colorbar axis, if cax is None create a new one
        if cax is None:
            divider = make_axes_locatable(axs)
            cax = divider.append_axes(cpos, size="7%", pad=cpad)
        else:
            cax, naxc = self.ImageToolsManager.assign_ax(
                cax, _check=False, **kwargs
            )
            self.ImageToolsManager.hide_text(naxc, cax.texts)

        # Check if the cax is an Axes instance
        if not isinstance(cax, Axes):
            raise TypeError("cax must be an Axes instance.")

        # Place the colorbar
        cbar = self.state.fig.colorbar(
            pcm,
            cax=cax,
            label=kwargs.get("clabel", ""),
            ticks=kwargs.get("cticks"),
            orientation=ccor,
            extend=kwargs.get("extend", "neither"),
            extendrect=kwargs.get("extendrect", False),
        )

        # Set the tickslabels
        if isinstance(
            (ctkc := kwargs.get("ctickslabels", "Default")), (list, tuple)
        ):
            axis = cbar.ax.yaxis if ccor == "vertical" else cbar.ax.xaxis
            ticks = kwargs.get("cticks") or list(cbar.get_ticks())
            axis.set_major_locator(FixedLocator(ticks))
            axis.set_major_formatter(FixedFormatter(list(ctkc)))

        # Ensure, if needed, the tight layout
        if self.state.tight:
            self.state.fig.tight_layout()

        # End of function

    @track_kwargs
    def _find_ax(
        self,
        pcm: (
            QuadMesh | PathCollection | LineCollection | QuadContourSet | None
        ) = None,
        axs: Axes | int | None = None,
    ) -> Axes:
        """Find and return the appropriate axis based on the input.

        Parameters
        ----------
        - axs: Axes | int | None, default None
            The axis or index of the axis to find. If None, the last used axis
            will be returned.
        - pcm: matplotlib collection or None, default None
            The collection for which to find the corresponding axis.
            Accepted types: QuadMesh, PathCollection, LineCollection,
            QuadContourSet.

        Returns
        -------
        - Axes

        Raises
        ------
        - ValueError
            If no figure is present or if the specified axis index is invalid.
        - TypeError
            If the provided axs parameter is not of type Axes or int.

        """
        # Standard check on the figure
        if self.state.fig is None:
            raise ValueError(
                "No figure is present. Please create a figure first."
            )
        # Standard check on the figure
        # Select the source axis
        if pcm is not None:
            # If the pcm is not none, use it and find the corresponding axes
            if not isinstance(pcm.axes, Axes):
                raise TypeError("Expected an Axes instance.")
            axs = pcm.axes
        elif axs is None:
            # If axs is None, use the current axes
            gca = self.state.fig.gca()
            if not isinstance(gca, Axes):
                raise TypeError("gca() did not return an Axes instance.")
            axs = gca
        axs, _ = self.ImageToolsManager.assign_ax(
            axs,
            _check=False,
        )
        if self.state.fig is None:
            raise ValueError(
                "No figure is present. Please create a figure first."
            )

        return axs
