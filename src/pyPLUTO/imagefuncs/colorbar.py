"""Module providing colorbar management functionalities for image displays."""

from __future__ import annotations

from typing import Unpack

from matplotlib.axes import Axes
from matplotlib.cm import ScalarMappable
from matplotlib.collections import LineCollection, PathCollection, QuadMesh
from matplotlib.colorbar import Colorbar
from matplotlib.contour import ContourSet, QuadContourSet
from matplotlib.transforms import Bbox
from mpl_toolkits.axes_grid1 import make_axes_locatable
from mpl_toolkits.axes_grid1.axes_divider import AxesDivider

from pyPLUTO.imagefuncs.imagetools import ImageToolsManager
from pyPLUTO.imagefuncs.ticks import TicksManager
from pyPLUTO.imagekwargs import ColorbarKwargs
from pyPLUTO.imagemixin import ImageMixin
from pyPLUTO.imagestate import ImageState
from pyPLUTO.utils.inspector import track_kwargs
from pyPLUTO.utils.pperrors import (
    PyPLUTOAxisError,
    PyPLUTODataError,
    PyPLUTOInternalError,
    PyPLUTOOptionError,
)
from pyPLUTO.utils.ppwarnings import PPWarn, PyPLUTOConflictWarning


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
        self.TicksManager = TicksManager(state)

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
            it is placed. If None, the last considered axis is used.
        - bottom: float, default varies
            The bottom limit of the axis / axes set. For the figure layout it
            is the space from the bottom border to the plot (default 0.1); for
            an inset zoom it is the bottom position of the inset (default 0.6 +
            height).
        - cax: Axes | int, default None
            The axis where the colorbar should be placed. If None, a new axis
            is created next to the axis axs. It cannot be axs itself.
        - clabel: str, default None
            Sets the label of the colorbar.
        - cpad: float, default 0.07
            The space between the colorbar and the tick labels and titles of
            the axis on that side, in inches. Not used when cax is given.
        - cpos: {'top','bottom','left','right'}, default 'right'
            The side of axs where the colorbar is placed, with its ticks and
            label on the outer side. With cax, it sets only the orientation
            and the side of the ticks.
        - cticks: list[float] | None | bool, default True
            If enabled (and different from True), sets manually the ticks on
            the colorbar. In order to completely remove the ticks the keyword
            should be used with None. The same rules as xticks.
        - ctickslabels: str | list[str | float] | None | bool, default True
            If enabled (and different from True), sets manually the ticks
            labels on the colorbar. In order to remove the labels, keeping the
            ticks, the keyword should be used with None. Fixed labels should
            always correspond to fixed ticks, as for xtickslabels.
        - extend: {'neither','both','min','max'}, default 'neither'
            The ends of the colorbar that get an extension, for the values
            beyond its limits.
        - extendrect: bool, default False
            If True, the colorbar extensions are rectangular instead of
            triangular.
        - figsize: list[float], default varies
            Sets the figure size. The default is [6*sqrt(ncol), 5*sqrt(nrow)],
            computed from the number of rows and columns (or [8,5] for a single
            plot).
        - fillmap: bool, default True
            For contour lines only: if True, the colorbar is continuous on
            their color scale, as for a map; if False, it is matplotlib's own,
            with a line at each level.
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
        - sharex: bool | int | 'all' | 'row' | 'col' | Axes, default None
            Shares the x-axis: True or 'all' with the first axis (in
            create_axes, the first of those it makes), an index with that
            axis of the image, an Axes with that axis. 'row' and 'col' share
            within each row or column of the axes a create_axes call makes,
            and are refused for axes that already exist.
        - sharexaxes: bool | int | 'all' | 'row' | 'col' | Axes, default None
            Deprecated, use sharex.
        - sharey: bool | int | 'all' | 'row' | 'col' | Axes, default None
            Shares the y-axis, as sharex does.
        - shareyaxes: bool | int | 'all' | 'row' | 'col' | Axes, default None
            Deprecated, use sharey.
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
            The colorbar drawn, to adjust its label or ticks afterwards.

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
            raise PyPLUTOInternalError("_check must be a boolean value.")

        # If pcm and a source axes are selected, raise a warning and use pcm
        if pcm is not None and axs is not None:
            warn = "Both pcm and axs are not None, pcm will be used"
            PPWarn.warn(warn, PyPLUTOConflictWarning)

        # Standard check on the figure
        if self.state.fig is None:
            raise PyPLUTOInternalError("No figure is present.")

        # The side of the colorbar, checked before anything is drawn
        cpos = kwargs.get("cpos", "right")
        if cpos not in ("left", "right", "top", "bottom"):
            raise PyPLUTOOptionError(
                "cpos must be 'left', 'right', 'top' or 'bottom', "
                f"not {cpos!r}."
            )

        # The axis described: the one of pcm, else axs or the last considered
        axs = self.find_ax(pcm, axs)

        # Without a collection, take the last one drawn on the axis that is
        # colored by data: a map, contour lines, streamlines by magnitude.
        # Contour lines keep their levels even when drawn in a fixed color:in
        # that case colors is not None (while it is None for a colormap)
        if pcm is None:
            drawn = [
                c
                for c in axs.collections
                if c.get_array() is not None
                and getattr(c, "colors", None) is None
            ]
            if len(drawn) == 0:
                raise PyPLUTODataError(
                    "No collection colored by data is present on the axis.",
                )
            mappable = drawn[-1]
        else:
            mappable = pcm

        # Contour lines give matplotlib's colorbar one block per level; with
        # fillmap, a mappable with the same scale gives the bar of a map
        fill = kwargs.get("fillmap", True)
        if fill and isinstance(mappable, ContourSet) and not mappable.filled:
            mappable = ScalarMappable(norm=mappable.norm, cmap=mappable.cmap)

        # Assign the colorbar axis, if cax is None create a new one
        bar: Axes
        if cax is None:
            # The gap starts past the tick labels and titles on that side
            pad = kwargs.get("cpad", 0.07) + self.side_space(axs, cpos)

            # An axis with a bar keeps its divider in its locator, and the
            # next bar must use it too, or the two overlap
            owner = getattr(axs.get_axes_locator(), "func", None)
            found = getattr(owner, "__self__", None)
            divider = (
                found
                if isinstance(found, AxesDivider)
                else make_axes_locatable(axs)
            )
            bar = divider.append_axes(cpos, size="7%", pad=pad)
        else:
            bar, naxc = self.ImageToolsManager.assign_ax(
                cax,
                _check=False,
                **kwargs,
            )
            if bar is axs:
                raise PyPLUTOAxisError(
                    "cax is the axis the colorbar describes: give another one."
                )
            self.ImageToolsManager.hide_text(naxc, bar.texts)

            # The bar's axis is not drawn on: the panel it describes stays the
            # last considered one
            self.state.lastax = axs

        # Place the colorbar; location sets the orientation and puts the ticks
        # and the label on the outer side
        cbar = self.state.fig.colorbar(
            mappable,
            cax=bar,
            label=kwargs.get("clabel", ""),
            location=cpos,
            extend=kwargs.get("extend", "neither"),
            extendrect=kwargs.get("extendrect", False),
        )

        # Keywords cticks and ctickslabels, through the same rules as xticks
        # and xtickslabels: True is automatic, None removes, a list fixes
        ctk = kwargs.get("cticks", True)
        ctl = kwargs.get("ctickslabels", True)
        if ctk is not True or ctl is not True:
            axis = "y" if cpos in ("left", "right") else "x"
            self.TicksManager.set_ticks(cbar.ax, ctk, ctl, axis, minor="off")

        # Ensure, if needed, the tight layout
        if self.state.tight:
            self.state.fig.tight_layout()

        return cbar

    def find_ax(
        self,
        pcm: (
            QuadMesh | PathCollection | LineCollection | QuadContourSet | None
        ),
        axs: Axes | int | None,
    ) -> Axes:
        """Return the axis whose collection the colorbar describes.

        A collection knows the axis it was drawn on, so that one is used when
        pcm is given. Otherwise the axis is axs, or without it the last
        considered axis: going through assign_ax is what keeps the axis of an
        earlier colorbar, which matplotlib may hold as its current one, from
        being chosen.

        Parameters
        ----------
        - pcm (not optional): QuadMesh | PathCollection | LineCollection |
            QuadContourSet | None
            The collection the colorbar describes, or None.
        - axs (not optional): Axes | int | None
            The axis, or its index, to use when pcm is None.

        Returns
        -------
        - Axes
            The axis described, which becomes the last considered one.

        Raises
        ------
        - PyPLUTOInternalError
            If pcm was never added to an axis.

        Examples
        --------
        - Example #1: the axis of a map

            >>> manager.find_ax(mesh, None)

        - Example #2: the second axis of the image

            >>> manager.find_ax(None, 1)

        """
        # A collection knows the axis it was drawn on
        if pcm is not None:
            if not isinstance(pcm.axes, Axes):
                raise PyPLUTOInternalError("Expected an Axes instance.")
            axs = pcm.axes

        return self.ImageToolsManager.assign_ax(axs, _check=False)[0]

    def side_space(self, axs: Axes, cpos: str) -> float:
        """Return how far, in inches, an axis draws past its frame on a side.

        A colorbar cut from one side of an axis has to start past what the
        axis draws there, or it covers it: the tick labels and the title of
        the y axis on the left and the right, those of the x axis below, and
        on top the x axis and the title of the panel. Only what faces that
        side counts, so the last x tick label, which overhangs the right
        corner, does not push a bar on the right away. Tick labels drawn
        inside the frame give no space.

        The space is measured when the bar is placed, so a title added later
        is not counted.

        Parameters
        ----------
        - axs (not optional): Axes
            The axis the colorbar is placed next to.
        - cpos (not optional): str
            The side, 'left', 'right', 'top' or 'bottom'.

        Returns
        -------
        - float
            The space in inches, 0 when nothing is drawn past the frame.

        Examples
        --------
        - Example #1: the space taken by the y tick labels and title

            >>> manager.side_space(ax, "left")
            0.52

        """
        frame = axs.get_window_extent()

        # Only what faces that side: the y axis left and right, the x axis
        # below, the x axis and the title on top
        facing = axs.yaxis if cpos in ("left", "right") else axs.xaxis
        boxes = [facing.get_tightbbox() or frame]
        if cpos == "top" and axs.get_title():
            boxes.append(axs.title.get_window_extent())
        full = Bbox.union(boxes)

        beyond = {
            "left": frame.x0 - full.x0,
            "right": full.x1 - frame.x1,
            "bottom": frame.y0 - full.y0,
            "top": full.y1 - frame.y1,
        }[cpos]
        return max(beyond, 0.0) / axs.figure.dpi
