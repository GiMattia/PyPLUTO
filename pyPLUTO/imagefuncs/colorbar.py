import warnings
from typing import Any

from matplotlib.axes import Axes
from matplotlib.collections import LineCollection, PathCollection, QuadMesh
from matplotlib.contour import QuadContourSet
from mpl_toolkits.axes_grid1 import make_axes_locatable

from ..imagemixin import ImageMixin
from ..imagestate import ImageState
from ..utils.inspector import track_kwargs
from .imagetools import ImageToolsManager


class ColorbarManager(ImageMixin):
    """Class to manage the colorbar in the image.

    This class provides methods to create and manage colorbars in the image
    class. It allows for customization of the colorbar's position, size,
    ticks, labels, and other properties."""

    exposed_methods = ("colorbar",)

    def __init__(self, state: ImageState):
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
        check: bool = True,
        **kwargs: Any,
    ) -> None:
        """Method to display a colorbar in a selected position. If the
        keyword cax is enabled the colorbar is located in a specific
        axis, otherwise an axis will be shrunk in order to place the
        colorbar.

        Returns
        -------
        - None

        Parameters
        ----------
        - axs: axis object, default None
            The axes where the display that will be used for the colorbar is
            located. If None, the last considered axis will be used.
        - cax: axis object, default None
            The axes where the colorbar should be placed. If None, the colorbar
            will be placed next to the axis axs.
        - clabel: str, default None
            Sets the label of the colorbar.
        - cpad: float, default 0.07
            Fraction of original axes between colorbar and the axes (in case cax
            is not defined).
        - cpos: {'top','bottom','left','right'}, default 'right'
            Sets the position of the colorbar.
        - cticks: {[float], None}, default None
            If enabled (and different from None), sets manually ticks on the
            colorbar.
        - ctickslabels: str, default None
            If enabled, sets manually ticks labels on the colorbar.
        - extend: {'neither','both','min','max'}, default 'neither'
            Sets the extension of the triangular colorbar extension.
        - extendrect: bool, default False
            If True, the colorbar extension will be rectangular.
        - pcm: QuadMesh | PathCollection | None, default None
            The collection to be used for the colorbar. If None, the axs will be
            used. If both pcm and axs are not None, pcm will be used.

        ----

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
        kwargs.pop("check", check)

        # If pcm and a source axes are selected, raise a warning and use pcm
        if pcm is not None and axs is not None:
            warn = "Both pcm and axs are not None, pcm will be used"
            warnings.warn(warn, UserWarning)

        # Standard check on the figure
        if self.fig is None:
            raise ValueError(
                "No figure is present. Please create a figure first."
            )

        # Select the source axis
        if pcm is not None:
            # If the pcm is not none, use it and find the corresponding axes
            if not isinstance(pcm.axes, Axes):
                raise TypeError("Expected an Axes instance.")
            axs = pcm.axes
        elif axs is None:
            # If axs is None, use the current axes
            gca = self.fig.gca()
            if not isinstance(gca, Axes):
                raise TypeError("gca() did not return an Axes instance.")
            axs = gca
        axs, _ = self.ImageToolsManager.assign_ax(axs, **kwargs)

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
            cax, naxc = self.ImageToolsManager.assign_ax(cax, **kwargs)
            self.ImageToolsManager.hide_text(naxc, cax.texts)

        # Check if the cax is an Axes instance
        if not isinstance(cax, Axes):
            raise TypeError("cax must be an Axes instance.")

        # Place the colorbar
        cbar = self.fig.colorbar(
            pcm,
            cax=cax,
            label=kwargs.get("clabel", ""),
            ticks=kwargs.get("cticks"),
            orientation=ccor,
            extend=kwargs.get("extend", "neither"),
            extendrect=kwargs.get("extendrect", False),
        )

        # Set the tickslabels
        ctkc = kwargs.get("ctickslabels", "Default")
        if ctkc != "Default":
            cbar.ax.set_yticklabels(ctkc)

        # Ensure, if needed, the tight layout
        if self.tight:
            self.fig.tight_layout()

        # End of function
