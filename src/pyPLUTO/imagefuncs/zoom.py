"""Module to manage the zoom functionality in pyPLUTO."""

from __future__ import annotations

import warnings
from typing import Unpack

import numpy as np
from matplotlib.artist import Artist
from matplotlib.axes import Axes
from matplotlib.collections import (
    Collection,
    LineCollection,
    PathCollection,
    QuadMesh,
)
from matplotlib.contour import ContourSet
from matplotlib.lines import Line2D

from pyPLUTO.imagefuncs.colorbar import ColorbarManager
from pyPLUTO.imagefuncs.create_axes import CreateAxesManager
from pyPLUTO.imagefuncs.display import DisplayManager
from pyPLUTO.imagefuncs.imagetools import ImageToolsManager
from pyPLUTO.imagefuncs.range import RangeManager
from pyPLUTO.imagefuncs.set_axis import AxisManager
from pyPLUTO.imagekwargs import SetLocKwargs, ZoomKwargs
from pyPLUTO.imagemixin import ImageMixin
from pyPLUTO.imagestate import ImageState
from pyPLUTO.utils.inspector import track_kwargs


class ZoomManager(ImageMixin):
    """Manager for the zoom functionality in pyPLUTO.

    This class provides methods to create inset zooms of existing plots or
    displays. It allows customization of the zoom axes, including position,
    size, and various display options.
    """

    def __init__(self, state: ImageState) -> None:
        """Initialize the ZoomManager with the given state."""
        self.state = state
        self.AxisManager = AxisManager(state)
        self.ColorbarManager = ColorbarManager(state)
        self.CreateAxesManager = CreateAxesManager(state)
        self.DisplayManager = DisplayManager(state)
        self.ImageToolsManager = ImageToolsManager(state)
        self.RangeManager = RangeManager(state)

    @track_kwargs
    def zoom(
        self,
        ax: Axes | list[Axes] | int | None = None,
        _check: bool = True,
        **kwargs: Unpack[ZoomKwargs],
    ) -> Axes:
        """Creation of an inset zoom of an already existent plot or display.

        The inset is an axis inside the parent, filled with what the parent
        shows, seen closer: every line and collection -- maps, curves, points,
        contour lines, streamlines, grids -- is copied, in the order it was
        drawn, and the region it shows is marked on the parent. With var, a
        different 2D quantity is drawn in place of the map, on the same grid,
        with a colormap, a scale and a colorbar of its own; what was drawn
        over the map is still copied on top. Texts, legends and the arrows of
        streamlines are not copied.

        The inset is placed in units of its parent: by pos, or by a start and
        a size in each direction, from 0.6 and spanning 0.15 unless told
        otherwise. An end given (right, top) wins over the rest: alone it
        moves the start, with a start it sets the size, and with a size as
        well the start is taken back from the two. The inset is an axis of
        the image like any other, so it can be drawn on afterwards through
        its index. An inset colorbar switches the tight layout of the figure
        off, since matplotlib cannot lay it out.

        Parameters
        ----------
        - alpha: float, default 1.0
            Sets the opacity of the plot, where 1.0 is fully opaque and 0.0 is
            fully transparent.
        - aspect: 'auto' | 'equal' | float, default 'auto'
            Sets the aspect ratio of the plot. The 'auto' keyword is the
            default option. The 'equal' keyword sets the same scaling for x and
            y. A float fixes the ratio between the y-scale and the x-scale (1.0
            is the same as 'equal').
        - ax: ax object, default None
            The axis to customize. If None the current axis will be selected.
        - bottom: float, default 0.6
            The bottom of the inset, in units of the parent axis.
        - clabel: str, default None
            Sets the label of the colorbar.
        - cmap: str, default the map's
            The colormap of the map in the inset: it restyles the copy, or is
            the colormap of var. Some useful colormaps are: plasma, magma,
            seismic. Please avoid colormaps like jet or rainbow, which are not
            perceptively uniform and not suited for people with vision
            deficiencies.
        - cpad: float, default 0.07
            The space between the inset and its colorbar, in inches.
        - cpos: {'top','bottom','left','right'}, default None
            Gives the map of the inset a colorbar on that side. If not
            defined, no colorbar is shown. It switches the tight layout of
            the figure off.
        - cscale: {'linear','log','symlog','twoslope'}, default the map's
            The color scale of the map in the inset: it restyles the copy, or
            is the scale of var.
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
        - grid: bool | string, default False
            Enables/disables the grid on the plot. If True it enables both axes
            grids. If 'x' or 'y' it enables only the x- or y-axis grid.
        - height: float, default 0.15
            The height of the inset, in units of the parent axis.
        - hratio: [float], default [1.0]
            Ratio between the rows of the plot. The default is that every plot
            row has the same height.
        - hspace: [float], default []
            The space between plot rows (in figure units). If not enough or too
            many spaces are considered, the program will remove the excess and
            fill the lacks with [0.1].
        - labelsize: float, default fontsize
            Sets the labels fontsize (which is the same for both labels). The
            default value corresponds to the value of the keyword 'fontsize'.
        - left: float, default 0.6
            The left side of the inset, in units of the parent axis.
        - minorticks: str, default None
            If not None enables the minor ticks on the plot (for both grid
            axes).
        - ncol: int, default 1
            The number of columns of subplots.
        - nrow: int, default 1
            The number of rows of subplots.
        - pos: [float,float,float,float], default None
            The four sides of the inset, as [left, right, bottom, top], in
            units of the parent axis. If missing, the inset is placed by left,
            bottom, right, top, width and height.
        - proj: str, default None
            Custom projection for the plot (e.g. 3D). Recommended only if
            needed. WARNING: pyPLUTO does not support 3D plotting for now, only
            3D axes. The 3D plot feature will be available in future releases.
        - right: float, default left + width
            The right side of the inset, in units of the parent axis. It wins
            over width: alone it moves left, and with a width as well left is
            taken back from the two, with a warning.
        - shading: {'flat', 'nearest', 'auto', 'gouraud'}, default 'auto'
            With var only: the shading of var. A copied map keeps its own.
            The shading between the grid points. If not defined, the shading
            will be one between 'flat' and 'nearest' depending on the size of
            the x, y and z arrays. The 'flat' shading works only if, given a
            NxM z-array, the x- and y-arrays have sizes of, respectively, N+1
            and M+1. All the other shadings require a N x-array and a M
            y-array.
        - sharex: bool | str | Matplotlib axis, default False
            Enables/disables the sharing of the x-axis between the subplots.
        - sharey: bool | str | Matplotlib axis, default False
            Enables/disables the sharing of the y-axis between the subplots.
        - sharexaxes: bool | str | Matplotlib axis, default False
            Enables/disables the sharing of the x-axis between the subplots.
        - shareyaxes: bool | str | Matplotlib axis, default False
            Enables/disables the sharing of the y-axis between the subplots.
        - suptitle: str, default None
            Creates a figure title over all the subplots.
        - ticksdir: {'in', 'out'}, default 'in'
            Sets the ticks direction. The default option is 'in'.
        - tickssize: float | bool, default True
            Sets the ticks fontsize (which is the same for both grid axes). The
            default value corresponds to the value of the keyword 'fontsize'.
        - tight: bool, default True
            Enables/disables tight layout options for the figure. In case of a
            highly customized plot (e.g. ratios or space between rows and
            columns) the option is set by default to False since that option
            would not be available for standard matplotlib functions.
        - title: str, default None
            Places the title of the plot on top of it.
        - titlepad: float, default 8.0
            Sets the distance between the title and the top of the plot.
        - titlesize: float, default fontsize
            Sets the title fontsize. The default value corresponds to the value
            of the keyword 'fontsize'.
        - top: float, default bottom + height
            The top of the inset, in units of the parent axis. It wins over
            height: alone it moves bottom, and with a height as well bottom
            is taken back from the two, with a warning.
        - transpose: True/False, default False
            With var only: declares var as var[y, x] instead of var[x, y].
        - tresh: float, default max(abs(vmin),vmax)*0.01
            The threshold of a symlog or twoslope scale in the inset.
        - var: np.ndarray, default None
            A 2D quantity, indexed as var[x, y], drawn in place of the map of
            the parent, on its grid unless x1 and x2 are given.
        - vmax: float, default the map's
            The top of the color scale in the inset.
        - vmin: float, default the map's
            The bottom of the color scale in the inset.
        - width: float, default 0.15
            The width of the inset, in units of the parent axis.
        - wratio: [float], default [1.0]
            Ratio between the columns of the plot. The default is that every
            plot column has the same width.
        - wspace: [float], default []
            The space between plot columns (in figure units). If not enough or
            too many spaces are considered, the program will remove the excess
            and fill the lacks with [0.1].
        - x1: np.ndarray, default the grid of the map
            With var only, and together with x2: the x-coordinates of var.
        - x2: np.ndarray, default the grid of the map
            With var only, and together with x1: the y-coordinates of var.
        - xlabelpad: float, default 4.0
            The padding between the x-axis label and the axis.
        - xrange: [float, float], default the parent's
            The x-range the inset shows.
        - xscale: {'linear','log'}, default 'linear'
            If enabled (and different from 'Default'), sets automatically the
            scale on the x-axis. Data in log scale should be used with the
            keyword 'log', while data in linear scale should be used with the
            keyword 'linear'.
        - xticks: list[float] | None | bool, default True
            If enabled (and different from True), sets manually ticks on the
            x-axis. In order to completely remove the ticks the keyword should
            be used with None.
        - xtickslabels: list[str] | None | bool, default True
            If enabled (and different from True), sets manually the ticks
            labels on the x-axis. In order to completely remove the ticks the
            keyword should be used with None. Note that fixed tickslabels
            should always correspond to fixed ticks.
        - xtitle: str, default None
            Sets and places the label of the x-axis.
        - xtresh: float
            The threshold parameter for the x-axis symlog/asinh scale.
        - ylabelpad: float, default 4.0
            The padding between the y-axis label and the axis.
        - yrange: [float, float], default the parent's
            The y-range the inset shows.
        - yscale: {'linear','log'}, default 'linear'
            If enabled (and different from 'Default'), sets automatically the
            scale on the y-axis. Data in log scale should be used with the
            keyword 'log', while data in linear scale should be used with the
            keyword 'linear'.
        - yticks: list[float] | None | bool, default True
            If enabled (and different from True), sets manually ticks on the
            y-axis. In order to completely remove the ticks the keyword should
            be used with None.
        - ytickslabels: list[str] | None | bool, default True
            If enabled (and different from True), sets manually the ticks
            labels on the y-axis. In order to completely remove the ticks the
            keyword should be used with None. Note that fixed tickslabels
            should always correspond to fixed ticks.
        - ytitle: str, default None
            Sets and places the label of the y-axis.
        - ytresh: float
            The threshold parameter for the y-axis symlog/asinh scale.
        - zoomcolor: str, default 'k'
            Sets the color of the inset zoom lines.
        - zoomlines: bool, default True
            Keyword in order to add/remove the inset zoom lines. The default
            option is True.

        Returns
        -------
        - Axes

        Examples
        --------
        - Example #1: create a simple zoom of a 1d plot

            >>> import pyPLUTO as pp
            >>> I = pp.Image()
            >>> I.plot(x1, var)
            >>> I.zoom(pos=[0.1,0.2,0.1,0.3], xrange=[1, 10], yrange=[10, 20])

        - Example #2: create a simple zoom of a 2d plot

            >>> import pyPLUTO as pp
            >>> I = pp.Image()
            >>> I.display(var, x1=x1, x2=x2)
            >>> I.zoom(
            ...     left=0.8,
            ...     bottom=0.9,
            ...     height=0.2,
            ...     width=0.2,
            ...     xrange=[1, 10],
            ...     yrange=[10, 20],
            ... )

        - Example #3: create a zoom of a different quantity over a 2d plot

            >>> import pyPLUTO as pp
            >>> I = pp.Image()
            >>> I.display(var, x1=x1, x2=x2)
            >>> I.zoom(var=var2, xrange=[1, 10], yrange=[10, 20])

        """
        if self.state.fig is None:
            raise ValueError(
                "No figure is present. Please create a figure first.",
            )

        # The colorbar of an inset is an axis tight_layout cannot handle, so
        # it would warn on every later layout: switched off for the figure,
        # but only then, since an inset alone lays out fine
        if kwargs.get("cpos") is not None:
            self.state.tight = False

        # Set or create figure and axes
        ax, _ = self.ImageToolsManager.assign_ax(ax, _check=False, **kwargs)

        # Sets position of the zoom
        if pos := kwargs.get("pos"):
            axins = self.place_inset_pos(ax, pos)
        else:
            axins = self.place_inset_loc(ax, _check=False, **kwargs)
        kwargs["fontsize"] = kwargs.get("fontsize", self.state.fontsize)
        kwargs["titlesize"] = kwargs.get("titlesize", self.state.fontsize)

        self.state.ax.append(axins)
        self.CreateAxesManager.add_ax(axins, len(self.state.ax))

        # Set ticks (None is the default value)
        if "xticks" not in kwargs:
            kwargs["xticks"] = None
        if "yticks" not in kwargs:
            kwargs["yticks"] = None

        self.AxisManager.set_axis(ax=axins, _check=False, **kwargs)
        self.ImageToolsManager.hide_text(
            self.state.ax.index(axins), axins.texts
        )

        # The inset shows what the parent shows, or var in place of its map
        self.zoomcopy(ax, axins, _check=False, **kwargs)

        # Indicates the inset zoom
        zoomc = kwargs.get("zoomcolor", "k")
        if kwargs.get("zoomlines", True) is True:
            ax.indicate_inset_zoom(axins, edgecolor=zoomc)

        axins.spines["left"].set_color(zoomc)
        axins.spines["bottom"].set_color(zoomc)
        axins.spines["right"].set_color(zoomc)
        axins.spines["top"].set_color(zoomc)

        return axins

    @track_kwargs
    def zoomcopy(
        self,
        ax: Axes,
        axins: Axes,
        _check: bool = True,
        **kwargs: Unpack[ZoomKwargs],
    ) -> None:
        """Fill the inset with what the parent axis shows.

        Every line and collection of the parent -- maps, curves, points,
        contour lines, streamlines, grids -- is copied into the inset in the
        order it was drawn, so the inset is exactly the parent, seen closer.
        With var, another quantity is drawn in place of the map, on its
        grid, and everything drawn over the map is still copied on top.

        Without var, the map keywords restyle the copied maps: cmap changes
        the colormap, and cscale, vmin, vmax and tresh rebuild the color
        scale from the one the map had. The inset shows the same window as
        the parent unless xrange or yrange are given.

        Parameters
        ----------
        - ax (not optional): Axes
            The parent axis, whose artists are copied.
        - axins (not optional): Axes
            The inset axis, which is filled.
        - cmap: str, default the map's
            Restyles the copied maps with this colormap.
        - cpos: {'top','bottom','left','right'}, default None
            Gives the inset map a colorbar on that side.
        - cscale: {'linear','log','symlog','twoslope'}, default the map's
            Restyles the copied maps with this color scale.
        - tresh: float, default max(abs(vmin),vmax)*0.01
            The threshold of a restyled symlog or twoslope scale.
        - var: np.ndarray, default None
            A 2D quantity drawn in place of the map of the parent.
        - vmax: float, default the map's
            The top of the color scale of the restyled maps.
        - vmin: float, default the map's
            The bottom of the color scale of the restyled maps.
        - xrange: [float, float], default the parent's
            The x-range of the inset.
        - yrange: [float, float], default the parent's
            The y-range of the inset.

        Returns
        -------
        - None

        Examples
        --------
        - Example #1: copy an axis into an inset of it

            >>> self.zoomcopy(ax, axins)

        """
        maps = [c for c in ax.collections if isinstance(c, QuadMesh)]
        base = maps[0] if maps else None

        # With var, another quantity takes the place of the map
        if (swap := "var" in kwargs) is True:
            self.zoomdisplay(axins, base, _check=False, **kwargs)

        # Every other line and collection, in the order they were drawn
        copies = [
            new
            for artist in [*ax.collections, *ax.lines]
            if not (swap and artist is base)
            and (new := self.copyartist(artist, axins)) is not None
        ]
        meshes = [c for c in copies if isinstance(c, QuadMesh)]

        # Without var, the map keywords restyle the copied maps
        cmap = self.ImageToolsManager.find_cmap(kwargs.get("cmap"))
        if not swap and cmap is not None:
            for mesh in meshes:
                mesh.set_cmap(cmap)
        if not swap and kwargs.keys() & {"cscale", "vmin", "vmax", "tresh"}:
            for mesh in meshes:
                scale = {"LogNorm": "log", "SymLogNorm": "symlog"}
                scale |= {"TwoSlopeNorm": "twoslope"}
                name = scale.get(type(mesh.norm).__name__, "norm")
                lims = mesh.get_clim()
                vmin = kwargs.get("vmin", lims[0])
                vmax = kwargs.get("vmax", lims[1])
                tresh = kwargs.get("tresh", max(abs(vmin), vmax) * 0.01)
                norm = self.ImageToolsManager.set_cscale(
                    kwargs.get("cscale", name), vmin, vmax, tresh
                )
                mesh.set_norm(norm)
        if not swap and kwargs.get("cpos") is not None and meshes:
            self.ColorbarManager.colorbar(meshes[0], _check=False, **kwargs)

        # The inset shows the window of the parent unless one is given
        nins = self.state.ax.index(axins)
        fix = self.RangeManager.fixrange
        if "xrange" not in kwargs:
            xlim = list(ax.get_xlim())
            self.RangeManager.set_xrange(axins, nins, xlim, fix)
        if "yrange" not in kwargs:
            ylim = list(ax.get_ylim())
            self.RangeManager.set_yrange(axins, nins, ylim, fix)

    def copyartist(self, artist: Artist, axins: Axes) -> Artist | None:
        """Copy one line or collection of the parent axis into the inset.

        The geometry is rebuilt for each kind of artist, and everything else
        -- colors, widths, markers, colormap, color scale, the values of a
        map -- is taken over by update_from, so the copy is drawn exactly as
        the original. Two things of the original belong to the parent and
        are pointed at the inset instead: the transform, when it is the
        parent's data (a scatter keeps its marker transform, in points, and
        places its markers through the inset's data), and the clipping.
        Anything else -- texts, legends, the arrows of streamlines, which
        matplotlib draws as separate patches -- is not copied.

        Parameters
        ----------
        - artist (not optional): Artist
            The line or collection of the parent axis.
        - axins (not optional): Axes
            The inset axis.

        Returns
        -------
        - Artist | None
            The copy, already on the inset, or None if not copied.

        Examples
        --------
        - Example #1: copy the map of an axis

            >>> self.copyartist(ax.collections[0], axins)

        """
        new: Line2D | Collection
        if isinstance(artist, Line2D):
            new = Line2D(artist.get_xdata(), artist.get_ydata())
        elif isinstance(artist, QuadMesh):
            # A mesh keeps its antialiasing apart from its style: pcolormesh
            # turns it off, a bare QuadMesh on, which shows the cell edges
            gouraud = getattr(artist, "_shading", "flat") == "gouraud"
            new = QuadMesh(
                artist.get_coordinates(),
                antialiased=getattr(artist, "_antialiased", False),
                shading="gouraud" if gouraud else "flat",
            )
        elif isinstance(artist, ContourSet):
            new = PathCollection(artist.get_paths())
        elif isinstance(artist, LineCollection):
            new = LineCollection(artist.get_segments())
        elif isinstance(artist, PathCollection):
            new = PathCollection(
                artist.get_paths(),
                sizes=artist.get_sizes(),
                offsets=artist.get_offsets(),
                offset_transform=axins.transData,
            )
        else:
            return None

        # The style is the original's; what pointed at the parent's data
        # now points at the inset's, and the copy is clipped to the inset
        new.update_from(artist)
        new.set_zorder(artist.get_zorder())
        new.set_rasterized(artist.get_rasterized())
        if artist.axes is not None and artist.get_transform() is (
            artist.axes.transData
        ):
            new.set_transform(axins.transData)
        if isinstance(new, Line2D):
            axins.add_line(new)
        else:
            axins.add_collection(new, autolim=False)
        new.set_clip_path(axins.patch)
        return new

    @track_kwargs
    def zoomdisplay(
        self,
        axins: Axes,
        base: QuadMesh | None,
        _check: bool = True,
        **kwargs: Unpack[ZoomKwargs],
    ) -> None:
        """Display another quantity in the inset, on the grid of the map.

        The inset of a map can show a different 2D quantity of the same
        region -- a velocity next to a density -- with a colormap, a color
        scale and a colorbar of its own. It is drawn by display, on the grid
        of the map of the parent axis unless x1 and x2 are given together;
        everything drawn over that map is copied on top of it afterwards by
        zoomcopy. A gouraud map holds a vertex on each border with the value
        of its cell, so var is given the same border, as display does for a
        map, and lies on exactly the same grid.

        Parameters
        ----------
        - axins (not optional): Axes
            The inset axis, where var is drawn.
        - base (not optional): QuadMesh | None
            The map of the parent axis, whose grid is used, or None.
        - x1: np.ndarray, default the grid of the map
            The x-coordinates of var, given together with x2.
        - x2: np.ndarray, default the grid of the map
            The y-coordinates of var, given together with x1.

        The other keywords are passed on to display, which draws var, and are
        documented there.

        Returns
        -------
        - None

        Examples
        --------
        - Example #1: a velocity in the inset of a map of the density

            >>> self.zoomdisplay(axins, base, var=D.vx1, cmap="RdBu_r")

        """
        # A grid is given whole or not at all: half of one would be completed
        # from the map's, which has another shape
        if len(kwargs.keys() & {"x1", "x2"}) == 1:
            raise ValueError("x1 and x2 must be given together.")

        # The grid of the map, unless one is given. A gouraud map has a vertex
        # on each border holding the value of its cell, so var is given the
        # same border, as display does, and the inset reaches the same edges
        if base is not None:
            grid = np.asarray(base.get_coordinates())
            gouraud = getattr(base, "_shading", "flat") == "gouraud"
            if gouraud and "x1" not in kwargs and "x2" not in kwargs:
                var = np.asarray(kwargs.get("var"))
                kwargs["var"] = np.pad(var, 1, mode="edge")
                kwargs["shading"] = "gouraud"
            kwargs["x1"] = kwargs.get("x1", grid[:, :, 0])
            kwargs["x2"] = kwargs.get("x2", grid[:, :, 1])
        elif "x1" not in kwargs or "x2" not in kwargs:
            text = "The zoom of var needs a grid: a map on the axis, or x1, x2."
            raise ValueError(text)

        self.DisplayManager.display(ax=axins, _check=False, **kwargs)

    def place_inset_pos(self, ax: Axes, pos: list[float]) -> Axes:
        """Place an inset axes given the position (left, top, bottom, right).

        Parameters
        ----------
        - ax: ax object
            The axis where the inset axes is placed.
        - pos: list[float]
            The position of the inset axes.

        Returns
        -------
        - Axes

        """
        # Compute the position of the inset axis and return it
        left = pos[0]
        bottom = pos[2]
        width = pos[1] - pos[0]
        height = pos[3] - pos[2]
        return ax.inset_axes((left, bottom, width, height))

    @track_kwargs
    def place_inset_loc(
        self,
        ax: Axes,
        _check: bool = True,
        **kwargs: Unpack[SetLocKwargs],
    ) -> Axes:
        """Place an inset axes given different keywords.

        In case both top and bottom are given, the top is given priority and a
        warning is raised.

        Parameters
        ----------
        - ax: ax object
            The axis where the inset axes is placed.
        - left: float, default varies
            The left limit of the axis / axes set. For the figure layout it is
            the space from the left border to the plot (default 0.125); for an
            inset zoom it is the left position of the inset (default 0.6).
        - bottom: float, default varies
            The bottom limit of the axis / axes set. For the figure layout it
            is the space from the bottom border to the plot (default 0.1); for
            an inset zoom it is the bottom position of the inset (default 0.6 +
            height).
        - right: float, default varies
            The right limit of the axis / axes set. For the figure layout it is
            the space from the right border to the plot (default 0.9); for an
            inset zoom it is the right position of the inset (default left +
            0.15).
        - top: float, default varies
            The top limit of the axis / axes set. For the figure layout it is
            the space from the top border to the plot (default 0.9); for an
            inset zoom it is the top position of the inset (default bottom +
            height).
        - width: float, default 0.15
            The width of the axis / axes set (used for an inset zoom).
        - height: float, default 0.15
            The height of the axis / axes set (used for an inset zoom).

        Returns
        -------
        - Axes

        """
        # The inset starts at 0.6 of its parent and spans 0.15
        left = kwargs.get("left", 0.6)
        bottom = kwargs.get("bottom", 0.6)
        width = kwargs.get("width", 0.15)
        height = kwargs.get("height", 0.15)

        # An end given wins: with a size as well the box is over-determined
        # and the start is taken back from the two; with a start it sets the
        # size, and alone it moves the start, keeping the default size
        if (right := kwargs.get("right")) is not None:
            if "width" in kwargs:
                warn = "Both right and width are specified: left is set to "
                warn += "right - width."
                warnings.warn(warn, UserWarning, stacklevel=2)
            if "left" in kwargs and "width" not in kwargs:
                width = right - left
            else:
                left = right - width

        if (top := kwargs.get("top")) is not None:
            if "height" in kwargs:
                warn = "Both top and height are specified: bottom is set to "
                warn += "top - height."
                warnings.warn(warn, UserWarning, stacklevel=2)
            if "bottom" in kwargs and "height" not in kwargs:
                height = top - bottom
            else:
                bottom = top - height

        return ax.inset_axes((left, bottom, width, height))
