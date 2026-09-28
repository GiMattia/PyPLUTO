"""Module providing colorbar management functionalities for image displays."""

from __future__ import annotations

import warnings
from typing import Unpack

from matplotlib.axes import Axes
from matplotlib.cm import ScalarMappable
from matplotlib.collections import LineCollection, PathCollection, QuadMesh
from matplotlib.colorbar import Colorbar
from matplotlib.contour import ContourSet, QuadContourSet
from mpl_toolkits.axes_grid1 import make_axes_locatable

from pyPLUTO.imagefuncs.imagetools import ImageToolsManager
from pyPLUTO.imagefuncs.set_axis import AxisManager
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
        self.AxisManager = AxisManager(state)
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
    ) -> Colorbar:
        """Display the colorbar of a drawn collection.

        The colorbar describes pcm, if given, otherwise the last collection of
        the axis axs that is colored by data: a map, contour lines, points or
        streamlines colored by a variable. Contour lines drawn in a single
        color are not colored by data and are skipped, so black lines over a
        map leave the colorbar to the map.

        The colorbar is placed in cax, if given; otherwise a new axis is cut
        from the side cpos of axs, which shrinks to make room for it. Contour
        lines get a continuous colorbar on their color scale, as a map does,
        instead of matplotlib's one block per level.

        Parameters
        ----------
        - axs: Axes | int, default None
            The axis whose collection the colorbar describes, and next to which
            it is placed. If None, the current axis of the figure is used when
            it is one of the image axes, otherwise the last of them.
        - bottom: float, default varies
            The bottom limit of the axis / axes set. For the figure layout it
            is the space from the bottom border to the plot (default 0.1); for
            an inset zoom it is the bottom position of the inset (default 0.6 +
            height).
        - cax: Axes | int, default None
            The axis where the colorbar should be placed. If None, a new axis
            is created next to the axis axs.
        - clabel: str, default None
            Sets the label of the colorbar.
        - cpad: float, default 0.07
            The space between the axis and the colorbar, in inches. Not used
            when cax is given.
        - cpos: {'top','bottom','left','right'}, default 'right'
            Enables the colorbar and sets its position. If not defined, no
            colorbar is shown.
        - cticks: list[float] | None | bool, default True
            If enabled (and different from True), sets manually the ticks on
            the colorbar. In order to completely remove the ticks the keyword
            should be used with None. The same rules as xticks.
        - ctickslabels: list[str] | None | bool, default True
            If enabled (and different from True), sets manually the ticks
            labels on the colorbar. In order to remove the labels, keeping the
            ticks, the keyword should be used with None. Fixed labels should
            always correspond to fixed ticks, as for xtickslabels.
        - extend: {'neither','both','min','max'}, default 'neither'
            Sets the extension of the triangular colorbar extension.
        - extendrect: bool, default False
            If True, the colorbar extensions are rectangular instead of
            triangular.
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
        - pcm: QuadMesh | PathCollection | LineCollection | QuadContourSet
            The collection the colorbar describes, as returned by display,
            scatter, streamplot or contour. If None, the last collection of axs
            colored by data is used. If both pcm and axs are given, pcm is used
            and a warning is raised.
        - proj: str, default None
            Custom projection for the plot (e.g. 3D). Recommended only if
            needed. WARNING: pyPLUTO does not support 3D plotting for now, only
            3D axes. The 3D plot feature will be available in future releases.
        - right: float, default varies
            The right limit of the axis / axes set. For the figure layout it is
            the space from the right border to the plot (default 0.9); for an
            inset zoom it is the right position of the inset (default left +
            0.15).
        - sharexaxes: bool | str | Matplotlib axis, default False
            Enables/disables the sharing of the x-axis between the subplots.
        - shareyaxes: bool | str | Matplotlib axis, default False
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
        - Colorbar

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

        - Example #4: a colorbar of contour lines, with no ticks

            >>> import pyPLUTO as pp
            >>> I = pp.Image()
            >>> I.contour(var, levels=8)
            >>> I.colorbar(cticks=None)

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
                "No figure is present. Please create a figure first.",
            )

        # Assign the source axis
        axs = self._find_ax(pcm, axs)

        # Without a collection, take the last one drawn on the axis that is
        # colored by data: a map, contour lines, streamlines by magnitude.
        # Contour lines keep their levels even when drawn in a fixed color
        mappable: ScalarMappable
        if pcm is None:
            drawn = [
                c
                for c in axs.collections
                if c.get_array() is not None
                and getattr(c, "colors", None) is None
            ]
            if len(drawn) == 0:
                raise ValueError(
                    "No collection colored by data is present on the axis.",
                )
            mappable = drawn[-1]
        else:
            mappable = pcm

        # Contour lines give matplotlib's colorbar one block per level; a
        # mappable with the same scale gives the continuous bar of a map
        if isinstance(mappable, ContourSet) and not mappable.filled:
            mappable = ScalarMappable(norm=mappable.norm, cmap=mappable.cmap)

        # Select the keywords to position the colorbar
        cpad = kwargs.get("cpad", 0.07)
        cpos = kwargs.get("cpos", "right")
        ccor = "vertical" if cpos in ["left", "right"] else "horizontal"

        # Assign the colorbar axis, if cax is None create a new one
        bar: Axes
        if cax is None:
            divider = make_axes_locatable(axs)
            bar = divider.append_axes(cpos, size="7%", pad=cpad)
        else:
            bar, naxc = self.ImageToolsManager.assign_ax(
                cax,
                _check=False,
                **kwargs,
            )
            self.ImageToolsManager.hide_text(naxc, bar.texts)

        # Place the colorbar
        cbar = self.state.fig.colorbar(
            mappable,
            cax=bar,
            label=kwargs.get("clabel", ""),
            orientation=ccor,
            extend=kwargs.get("extend", "neither"),
            extendrect=kwargs.get("extendrect", False),
        )

        # Keywords cticks and ctickslabels, through the same rules as xticks
        # and xtickslabels: True is automatic, None removes, a list fixes
        ctk = kwargs.get("cticks", True)
        ctl = kwargs.get("ctickslabels", True)
        if ctk is not True or ctl is not True:
            axis = "y" if ccor == "vertical" else "x"
            self.AxisManager.set_ticks(cbar.ax, ctk, ctl, axis, minor="off")

        # Ensure, if needed, the tight layout
        if self.state.tight:
            self.state.fig.tight_layout()

        return cbar

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
        # A collection knows the axis it was drawn on
        if pcm is not None:
            if not isinstance(pcm.axes, Axes):
                raise TypeError("Expected an Axes instance.")
            axs = pcm.axes

        # Without one, assign_ax picks the current pyPLUTO axis: never the
        # axis of a colorbar, which matplotlib may hold as the current one
        axs, _ = self.ImageToolsManager.assign_ax(axs, _check=False)

        return axs
