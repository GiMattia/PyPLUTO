"""GridPlotManager class."""

from __future__ import annotations

from typing import Unpack

import numpy as np
from matplotlib.axes import Axes

from pyPLUTO.imagefuncs.imagetools import ImageToolsManager
from pyPLUTO.imagefuncs.plot import PlotManager
from pyPLUTO.imagekwargs import ShowGridKwargs
from pyPLUTO.imagemixin import ImageMixin
from pyPLUTO.imagestate import ImageState
from pyPLUTO.load import Load
from pyPLUTO.utils.inspector import track_kwargs

SUPPORTED_GEOMETRIES = ("CARTESIAN", "POLAR", "CYLINDRICAL", "SPHERICAL")


def _to_cartesian(
    coord1: np.ndarray,
    coord2: np.ndarray,
    geom: str,
) -> tuple[np.ndarray, np.ndarray]:
    """Convert a pair of grid coordinates to Cartesian plot coordinates.

    For 'POLAR'/'CYLINDRICAL' geometries `coord1`/`coord2` are the radius
    and azimuthal angle (`x1`, `x2`) of the x-y plane. For 'SPHERICAL'
    they are the radius and polar angle of the meridional (R, z) plane,
    matching the `x1c`/`x2c` and `x1p`/`x2p` conventions used elsewhere in
    pyPLUTO (see `readgridfile.py`).

    Parameters
    ----------
    - coord1 (not optional): array
        The first grid coordinate (`x1`).
    - coord2 (not optional): array
        The second grid coordinate (`x2`).
    - geom (not optional): str
        The geometry, one of `SUPPORTED_GEOMETRIES`.

    Returns
    -------
    - tuple[array, array]

    """
    if geom == "CARTESIAN":
        return coord1, coord2
    if geom in ("POLAR", "CYLINDRICAL"):
        return coord1 * np.cos(coord2), coord1 * np.sin(coord2)
    if geom == "SPHERICAL":
        return coord1 * np.sin(coord2), coord1 * np.cos(coord2)
    text = (
        f"Unsupported geometry {geom!r}, expected one of {SUPPORTED_GEOMETRIES}"
    )
    raise ValueError(text)


class GridPlotManager(ImageMixin):
    """GridPlotManager class.

    It provides the `showgrid` method, which draws the cell
    interfaces of a simulation grid (or of any pair of 1D coordinate
    arrays) as a mesh of straight lines. It relies on ImageToolsManager
    to set up the target axis and on PlotManager to draw each grid
    line.
    """

    def __init__(self, state: ImageState) -> None:
        """Initialize the GridPlotManager with the given state."""
        self.state = state
        self.ImageToolsManager = ImageToolsManager(state)
        self.PlotManager = PlotManager(state)

    @track_kwargs
    def showgrid(
        self,
        x1: np.ndarray | None = None,
        x2: np.ndarray | None = None,
        data: Load | None = None,
        geom: str | None = None,
        ax: Axes | list[Axes] | int | None = None,
        **kwargs: Unpack[ShowGridKwargs],
    ) -> None:
        """Draw the grid lines of a mesh on the plot.

        This function draws the cell interfaces of a 2D grid as a set
        of straight lines, one per coordinate in `x1` and one per
        coordinate in `x2`. It creates a simple figure and a single
        axis if none are given prior. The coordinate arrays can either
        be passed directly or read from a `Load` object through
        `data`.

        Parameters
        ----------
        - ax: ax | int | None, default None
            The axis where to plot. If None, the last considered axis will be
            used.
        - c: str, default 'k'
            Sets the color of the grid lines.
        - data: Load, default None
            A loaded dataset from which the grid face coordinates (`x1r`,
            `x2r`) and the geometry (`geom`) are taken whenever `x1`, `x2`
            or `geom` are not explicitly provided.
        - everyx: int, default 1
            Plots only one every `everyx` lines along the x1-direction.
        - everyy: int, default 1
            Plots only one every `everyy` lines along the x2-direction.
        - geom: str, default None
            The geometry of the grid. If None, it is taken from `data.geom`
            when `data` is given, otherwise it defaults to 'CARTESIAN'.
            Supported values are 'CARTESIAN', 'POLAR', 'CYLINDRICAL' and
            'SPHERICAL'. For 'POLAR'/'CYLINDRICAL', `x1`/`x2` are
            interpreted as the radius and azimuthal angle of the x-y
            plane. For 'SPHERICAL', they are the radius and polar angle
            of the meridional (R, z) plane. In both cases the
            constant-`x1` lines become arcs/circles and the constant-`x2`
            lines become straight rays through the origin, so an
            `aspect='equal'` axis is recommended to keep circles looking
            circular.
        - lw: float, default 0.75
            Sets the linewidth of the grid lines.
        - x1 (not optional unless data is given): 1D array
            The grid coordinates along the first direction (e.g. the cell
            interfaces).
        - x2 (not optional unless data is given): 1D array
            The grid coordinates along the second direction (e.g. the cell
            interfaces).
        - xrange: [float, float], default 'Default'
            Sets the range in the x-direction. If not defined, the range is
            computed automatically from the plotted (Cartesian) grid
            coordinates.
        - yrange: [float, float], default 'Default'
            Sets the range in the y-direction. If not defined, the range is
            computed automatically from the plotted (Cartesian) grid
            coordinates.

        Any other keyword accepted by `PlotManager.plot` and
        `ImageToolsManager.assign_ax` (e.g. figure/axis layout options)
        is also forwarded to those methods.

        Returns
        -------
        - None

        Examples
        --------
        - Example #1: show the grid of a loaded dataset

            >>> import pyPLUTO as pp
            >>> D = pp.Load()
            >>> I = pp.Image()
            >>> I.showgrid(data=D)

        - Example #2: show the grid from explicit coordinate arrays,
            plotting only one every two lines

            >>> import pyPLUTO as pp
            >>> I = pp.Image()
            >>> I.showgrid(x1=x1, x2=x2, everyx=2, everyy=2)

        - Example #3: show a polar grid (x1 = radius, x2 = angle) with a
            circular aspect ratio

            >>> import pyPLUTO as pp
            >>> I = pp.Image()
            >>> I.showgrid(x1=r, x2=phi, geom="POLAR", aspect="equal")

        """
        # Set or create figure and axes
        ax, nax = self.ImageToolsManager.assign_ax(ax, _check=False, **kwargs)

        # Fall back to the coordinates/geometry of the loaded dataset for
        # whichever of x1, x2, geom was not explicitly provided
        if data is not None:
            x1 = data.x1r if x1 is None else x1
            x2 = data.x2r if x2 is None else x2
            geom = data.geom if geom is None else geom
        geom = "CARTESIAN" if geom is None else geom

        if x1 is None or x2 is None:
            raise ValueError("x1 and x2 cannot be None")

        if geom not in SUPPORTED_GEOMETRIES:
            text = (
                f"Unsupported geometry {geom!r}, "
                f"expected one of {SUPPORTED_GEOMETRIES}"
            )
            raise ValueError(text)

        if "c" not in kwargs:
            kwargs["c"] = "k"

        if "lw" not in kwargs:
            kwargs["lw"] = 0.75

        # Subsample the grid lines: keep only one every everyx/everyy lines
        everyx = kwargs.pop("everyx", 1)
        everyy = kwargs.pop("everyy", 1)

        xs = x1[::everyx]
        ys = x2[::everyy]

        # Build the (x1, x2) meshes for the two line families (vertical:
        # constant x1, varying x2; horizontal: constant x2, varying x1),
        # then convert them to Cartesian plot coordinates according to the
        # geometry. For CARTESIAN this is a no-op; for POLAR/CYLINDRICAL/
        # SPHERICAL the constant-x1 lines become arcs and the constant-x2
        # lines become straight rays.
        vert_c1 = np.broadcast_to(xs, (len(ys), len(xs)))
        vert_c2 = np.broadcast_to(np.asarray(ys)[:, None], (len(ys), len(xs)))
        horiz_c1 = np.broadcast_to(np.asarray(xs)[:, None], (len(xs), len(ys)))
        horiz_c2 = np.broadcast_to(ys, (len(xs), len(ys)))

        vert_x, vert_y = _to_cartesian(vert_c1, vert_c2, geom)
        horiz_x, horiz_y = _to_cartesian(horiz_c1, horiz_c2, geom)

        # Keywords xrange and yrange, computed from the Cartesian extent of
        # the grid actually being plotted
        if not kwargs.get("xrange") and self.setax[nax] != 1:
            kwargs["xrange"] = [
                min(vert_x.min(), horiz_x.min()),
                max(vert_x.max(), horiz_x.max()),
            ]
        if not kwargs.get("yrange") and self.setay[nax] != 1:
            kwargs["yrange"] = [
                min(vert_y.min(), horiz_y.min()),
                max(vert_y.max(), horiz_y.max()),
            ]

        # Fast path: draw all the vertical lines with a single plot() call
        # and all the horizontal lines with another, instead of one call
        # per line. matplotlib natively draws one line per column when x/y
        # are 2D arrays sharing a single style, so PlotManager.plot only
        # has to run its (relatively expensive) axis/range/tight_layout
        # setup twice in total rather than once per grid line.
        self.PlotManager.plot(vert_x, vert_y, ax, _check=False, **kwargs)
        self.PlotManager.plot(horiz_x, horiz_y, ax, _check=False, **kwargs)
