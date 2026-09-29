"""GridPlotManager class."""

from __future__ import annotations

from typing import Unpack

import numpy as np
from matplotlib.axes import Axes
from matplotlib.collections import LineCollection
from numpy.typing import ArrayLike

from pyPLUTO.imagefuncs.imagetools import ImageToolsManager
from pyPLUTO.imagefuncs.legend import LegendManager
from pyPLUTO.imagefuncs.range import RangeManager
from pyPLUTO.imagefuncs.set_axis import AxisManager
from pyPLUTO.imagekwargs import ShowGridKwargs
from pyPLUTO.imagemixin import ImageMixin
from pyPLUTO.imagestate import ImageState
from pyPLUTO.load import Load
from pyPLUTO.utils.inspector import track_kwargs


def _every(nlines: int, every: int) -> list[int]:
    """Return the lines kept when only one every `every` is drawn.

    The first and the last line are always kept, since they are the borders
    of the domain: slicing alone would drop the last whenever the count does
    not fall on it.

    Parameters
    ----------
    - nlines (not optional): int
        The number of lines in that direction.
    - every (not optional): int
        Draw one line every this many.

    Returns
    -------
    - list[int]

    Examples
    --------
    - Example #1: six lines, one every two

        >>> _every(6, 2)
        [0, 2, 4, 5]

    """
    index = list(range(0, nlines, every))
    if index[-1] != nlines - 1:
        index.append(nlines - 1)
    return index


def _straighten(lines: np.ndarray) -> list[np.ndarray]:
    """Return the lines of a mesh, each straight one reduced to its ends.

    A line of a mesh holds one point per grid face, but a straight one is
    drawn the same from its two ends alone, and the points in between are
    only work for the renderer: the rays of a polar mesh, or every line of
    a mesh that is not curved at all. A line is straight when every point
    lies on the chord between its ends, to a tolerance relative to the
    length of the chord. A closed line, a full circle, has its two ends in
    the same place and no chord, so it is never taken for straight.

    Parameters
    ----------
    - lines (not optional): np.ndarray
        The lines, as an array of shape (number of lines, points, 2).

    Returns
    -------
    - list[np.ndarray]

    Examples
    --------
    - Example #1: a straight line keeps its ends, a bent one every point

        >>> lines = np.array([[[0, 0],[1, 1],[2, 2]],[[0, 0],[1, 2],[2, 0]]])
        >>> [len(line) for line in _straighten(lines.astype(float))]
        [2, 3]

    """
    start = lines[:, :1]
    chord = lines[:, -1:] - start
    offset = lines - start
    cross = chord[..., 0] * offset[..., 1] - chord[..., 1] * offset[..., 0]
    length = np.hypot(chord[..., 0], chord[..., 1])
    straight = (length[:, 0] > 0) & np.all(
        np.abs(cross) <= 1e-9 * length**2,
        axis=1,
    )
    return [
        line[[0, -1]] if flat else line
        for line, flat in zip(lines, straight, strict=True)
    ]


def _lines(
    x1: np.ndarray,
    x2: np.ndarray,
    everyx: int,
    everyy: int,
) -> tuple[list[np.ndarray], list[np.ndarray]]:
    """Return the two families of grid lines, as arrays of points.

    The first family holds the lines at constant x1, the second those at
    constant x2. Two 1D arrays are the coordinates of a straight grid, so
    every line is built from its two ends and no mesh is ever made. Two 2D
    arrays are a mesh in matplotlib order, [j, i] with i along x1 and j
    along x2, which is how display takes them and how pyPLUTO builds its
    projections (x1rc, x1rp, ...): its columns and rows are the lines, and
    the straight ones among them are reduced to their ends. Thinning picks
    whole lines before any of this, so every line still crosses the domain.

    Parameters
    ----------
    - x1 (not optional): np.ndarray
        The first coordinate: 1D, or the 2D mesh of the x-coordinates.
    - x2 (not optional): np.ndarray
        The second coordinate, with the same number of dimensions as x1.
    - everyx (not optional): int
        Keep one line every this many at constant x1.
    - everyy (not optional): int
        Keep one line every this many at constant x2.

    Returns
    -------
    - tuple[list[np.ndarray], list[np.ndarray]]

    Examples
    --------
    - Example #1: the ends of the lines of a straight 3 x 2 grid

        >>> first, second = _lines(np.arange(3.0), np.arange(2.0), 1, 1)
        >>> len(first), len(second), first[0].tolist()
        (3, 2, [[0.0, 0.0], [0.0, 1.0]])

    """
    twodim = 2
    if x1.ndim == 1 and x2.ndim == 1:
        xs = x1[_every(x1.size, everyx)]
        ys = x2[_every(x2.size, everyy)]
        first = np.empty((xs.size, 2, 2))
        first[:, :, 0] = xs[:, None]
        first[:, :, 1] = x2[[0, -1]]
        second = np.empty((ys.size, 2, 2))
        second[:, :, 0] = x1[[0, -1]]
        second[:, :, 1] = ys[:, None]
        return list(first), list(second)
    if x1.ndim == twodim and x1.shape == x2.shape:
        cols = _every(x1.shape[1], everyx)
        rows = _every(x1.shape[0], everyy)
        first = np.stack((x1[:, cols].T, x2[:, cols].T), axis=-1)
        second = np.stack((x1[rows, :], x2[rows, :]), axis=-1)
        return _straighten(first), _straighten(second)
    text = "x1 and x2 must be both 1D, or 2D meshes of the same shape."
    raise ValueError(text)


class GridPlotManager(ImageMixin):
    """GridPlotManager class.

    It provides the `showgrid` method, which draws the cell interfaces of
    a grid -- given as coordinates, as a 2D mesh, or read from a loaded
    dataset -- as two collections of lines, one per family. It relies on
    ImageToolsManager to set up the target axis, on RangeManager for the
    frame, on AxisManager for the axis keywords and on LegendManager for
    the legend.
    """

    def __init__(self, state: ImageState) -> None:
        """Initialize the GridPlotManager with the given state."""
        self.state = state
        self.AxisManager = AxisManager(state)
        self.ImageToolsManager = ImageToolsManager(state)
        self.LegendManager = LegendManager(state)
        self.RangeManager = RangeManager(state)

    @track_kwargs
    def showgrid(
        self,
        x1: ArrayLike | None = None,
        x2: ArrayLike | None = None,
        data: Load | None = None,
        ax: Axes | list[Axes] | int | None = None,
        _check: bool = True,
        **kwargs: Unpack[ShowGridKwargs],
    ) -> tuple[LineCollection, LineCollection]:
        """Draw the grid lines of a mesh on the plot.

        The lines are the columns (constant x1) and the rows (constant x2)
        of a mesh, and nothing is converted: what is given is what is
        drawn. Two 1D arrays are the coordinates of a straight grid, so the
        faces of a spherical run given as they are draw a straight (r,
        theta) grid. A curved grid is given as its 2D projection, in the
        order display takes it -- D.x1rc/D.x2rc for a polar or cylindrical
        mesh, D.x1rp/D.x2rp or D.x1rt/D.x2rt for the two planes of a
        spherical one -- so the lines fall exactly on the edges of the
        cells of a map drawn on the same mesh.

        Each family is one collection of lines, a single artist however
        many lines it holds, and a straight line is drawn from its two ends
        only: a grid of a million cells is drawn in a fraction of a second.
        The frame is the extent of the grid, with no padding, and the axis
        is left free for what is drawn next. Thinning with everyx/everyy
        drops whole lines, never points, so every line still crosses the
        domain, and the first and last lines, its borders, are always kept.

        Parameters
        ----------
        - ax: ax | int | None, default None
            The axis where to plot. If None, the last considered axis will be
            used.
        - c: str, default 'k'
            Sets the color of the grid lines.
        - data: Load, default None
            A loaded dataset whose faces (x1r, x2r) are drawn for whichever
            of x1 and x2 is not given. They are drawn as they are, straight:
            for a curved grid, pass its projection as x1 and x2.
        - everyx: int, default 1
            Plots only one every `everyx` lines along the x1-direction. The
            first and the last line are always drawn.
        - everyy: int, default 1
            Plots only one every `everyy` lines along the x2-direction. The
            first and the last line are always drawn.
        - label: str, default None
            The legend entry of the grid: one entry for the whole grid, not
            one per line.
        - ls: str, default '-'
            Sets the linestyle of the grid lines.
        - lw: float, default 0.75
            Sets the linewidth of the grid lines.
        - x1 (not optional unless data is given): 1D or 2D array
            The coordinates of the faces along the first direction, or the
            2D mesh of the x-coordinates of the grid points, as [j, i] with
            i along the first direction.
        - x2 (not optional unless data is given): 1D or 2D array
            The coordinates of the faces along the second direction, or the
            2D mesh of the y-coordinates of the grid points, with the same
            shape as x1.
        - xrange: [float, float], default 'Default'
            Sets the range in the x-direction, which then stays fixed. If
            not defined, the frame is the extent of the grid and the axis is
            left free.
        - yrange: [float, float], default 'Default'
            Sets the range in the y-direction, which then stays fixed. If
            not defined, the frame is the extent of the grid and the axis is
            left free.

        Any other keyword accepted by `AxisManager.set_axis`,
        `LegendManager.legend` and `ImageToolsManager.assign_ax` (e.g.
        titles, legend position, figure/axis layout options) is also
        forwarded to those methods.

        Returns
        -------
        - tuple[LineCollection, LineCollection]
            The lines at constant x1, then the lines at constant x2.

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

        - Example #3: the curved grid of a polar run over a map of it, with
            a circular aspect ratio

            >>> import pyPLUTO as pp
            >>> D = pp.Load()
            >>> I = pp.Image()
            >>> I.display(D.rho, x1=D.x1rc, x2=D.x2rc, aspect="equal")
            >>> I.showgrid(x1=D.x1rc, x2=D.x2rc, everyx=4, everyy=4)

        """
        # Set or create figure and axes
        ax, nax = self.ImageToolsManager.assign_ax(ax, _check=False, **kwargs)

        # The faces of a loaded dataset, for whichever of x1, x2 is missing
        if data is not None:
            x1 = data.x1r if x1 is None else x1
            x2 = data.x2r if x2 is None else x2

        if x1 is None or x2 is None:
            raise ValueError("x1 and x2 cannot be None")

        # The lines at constant x1 and at constant x2, as arrays of points
        first, second = _lines(
            np.asarray(x1, dtype=float),
            np.asarray(x2, dtype=float),
            kwargs.get("everyx", 1),
            kwargs.get("everyy", 1),
        )

        # The frame is the extent of the grid, exactly, and the axis is left
        # free for what is drawn next; an xrange or yrange given is applied
        # after, by set_axis, and fixes it
        points = np.concatenate([*first, *second])
        strict = self.RangeManager.strictrange
        xlim = [float(points[:, 0].min()), float(points[:, 0].max())]
        ylim = [float(points[:, 1].min()), float(points[:, 1].max())]
        self.RangeManager.set_xrange(ax, nax, xlim, strict)
        self.RangeManager.set_yrange(ax, nax, ylim, strict)

        # Set ax parameters
        self.AxisManager.set_axis(ax=ax, _check=False, **kwargs)
        self.ImageToolsManager.hide_text(nax, ax.texts)

        # One collection per family, a single artist however many lines it
        # holds; the label goes to the first, so the grid is one entry
        label = kwargs.get("label")
        color = kwargs.get("c", "k")
        width = kwargs.get("lw", 0.75)
        style = kwargs.get("ls", "-")
        grid = (
            LineCollection(
                first,
                colors=color,
                linewidths=width,
                linestyles=style,
                label=label if isinstance(label, str) else "",
            ),
            LineCollection(
                second, colors=color, linewidths=width, linestyles=style
            ),
        )
        for lines in grid:
            ax.add_collection(lines)

        # The legend, built as a curve builds it: from the labelled artists
        self.state.legpos[nax] = kwargs.get("legpos", self.state.legpos[nax])
        if self.state.legpos[nax] is not None:
            kwargs["label"] = None
            self.LegendManager.legend(ax, _check=False, fromplot=True, **kwargs)

        return grid
