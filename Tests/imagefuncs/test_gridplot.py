"""Test of the gridplot.py file.

GridPlotManager draws the cell interfaces of a grid as two collections of
lines: the lines at constant x1, then those at constant x2. Nothing is
converted on the way: two 1D arrays are a straight grid, drawn as given, and
a curved grid is passed as its 2D projection, in the order display takes it,
[j, i] with i along x1. That is also what makes the lines sit exactly on the
cell edges of a map drawn on the same mesh.

Speed is part of the design, so part of what is tested: each family is one
artist, and a straight line is drawn from its two ends only -- every line of
a 1D grid, and the straight ones, such as rays, of a curved mesh. The arcs
keep all their points, since each is a corner of a cell.

The frame is the extent of the grid, with no padding, and the axis is left
free, so the seams with what is drawn before and after are checked here too.
"""

import warnings
from pathlib import Path

import numpy as np
import numpy.testing as npt
import pytest
from matplotlib.axes import Axes
from matplotlib.collections import LineCollection
from matplotlib.colors import to_hex

import pyPLUTO as pp
from pyPLUTO.imagefuncs.gridplot import _every, _lines, _straighten

# A straight grid of 6 x 4 faces, from 0 to 5 along x and 0 to 3 along y, so
# that a line running along the wrong axis cannot pass.
x = np.linspace(0.0, 5.0, 6)
y = np.linspace(0.0, 3.0, 4)

# A quarter of a polar mesh, radius 1 to 2 and angle 0 to pi/2, projected
# as pyPLUTO projects it: [j, i], with i along the radius.
radius = np.linspace(1.0, 2.0, 5)
angle = np.linspace(0.0, np.pi / 2, 4)
r2d, a2d = np.meshgrid(radius, angle)
polar_x, polar_y = r2d * np.cos(a2d), r2d * np.sin(a2d)


def _segments(lines: LineCollection) -> list[np.ndarray]:
    """Return the lines of a collection, one array of points each."""
    return [np.asarray(segment) for segment in lines.get_segments()]


def _axis(image: pp.Image) -> Axes:
    """Return the first axis of an image, checked to be one."""
    axis = image.ax[0]
    assert isinstance(axis, Axes)
    return axis


# ---- The lines that are drawn ----
def test_the_two_families_are_returned() -> None:
    """Check the grid hands back its two collections, one per family.

    They are what a user restyles afterwards, and each is a single artist
    however many lines it holds, which is what keeps a large grid fast.
    """
    image = pp.Image(text=False)
    first, second = image.showgrid(x1=x, x2=y)

    assert isinstance(first, LineCollection)
    assert isinstance(second, LineCollection)
    assert list(_axis(image).collections) == [first, second]


def test_showgrid_line_count() -> None:
    """Check one line is drawn per face in each direction."""
    first, second = pp.Image(text=False).showgrid(x1=x, x2=y)

    assert len(_segments(first)) == len(x)
    assert len(_segments(second)) == len(y)


def test_the_lines_are_where_the_faces_are() -> None:
    """Read the lines back and check which coordinate each one holds.

    The first family is the lines at constant x1, one per face along x and
    running the whole height of the domain; the second, at constant x2,
    runs its whole width. Swapping them is a grid that looks right on a
    square and wrong everywhere else.
    """
    first, second = pp.Image(text=False).showgrid(x1=x, x2=y)

    for face, line in zip(x, _segments(first), strict=True):
        npt.assert_allclose(line, [[face, 0.0], [face, 3.0]])
    for face, line in zip(y, _segments(second), strict=True):
        npt.assert_allclose(line, [[0.0, face], [5.0, face]])


def test_a_straight_line_is_drawn_from_its_ends() -> None:
    """Draw a fine straight grid and count the points of its lines.

    A straight line looks the same drawn from its two ends, so that is all
    it is given: the points in between would only slow the renderer down.
    """
    fine = np.linspace(0.0, 1.0, 200)
    first, second = pp.Image(text=False).showgrid(x1=fine, x2=fine)

    assert {len(line) for line in _segments(first)} == {2}
    assert {len(line) for line in _segments(second)} == {2}


def test_a_straight_grid_is_drawn_as_given() -> None:
    """Draw the faces of a polar run as they are.

    Nothing is converted, so a radius and an angle give a straight (r, phi)
    grid: the raw view of the mesh, which a user may well want.
    """
    image = pp.Image(text=False)
    image.showgrid(x1=radius, x2=angle)

    npt.assert_allclose(_axis(image).get_xlim(), (1.0, 2.0))
    npt.assert_allclose(_axis(image).get_ylim(), (0.0, np.pi / 2))


def test_a_polar_mesh_draws_arcs_and_rays() -> None:
    """Draw the projection of a polar mesh.

    Its lines at constant radius are arcs, whose every point stays on the
    circle and is kept; its lines at constant angle are rays, straight, and
    reduced to their two ends.
    """
    arcs, rays = pp.Image(text=False).showgrid(x1=polar_x, x2=polar_y)

    for value, arc in zip(radius, _segments(arcs), strict=True):
        assert len(arc) == len(angle)
        npt.assert_allclose(np.hypot(arc[:, 0], arc[:, 1]), value)
    assert {len(ray) for ray in _segments(rays)} == {2}


def test_a_closed_line_is_kept_whole() -> None:
    """Draw a full circle, whose two ends are the same point.

    A line with no chord could pass for straight -- every point lies on a
    chord of zero length -- and would be reduced to nothing.
    """
    full = np.linspace(0.0, 2 * np.pi, 9)
    r2d_full, a2d_full = np.meshgrid(radius, full)
    circles, _ = pp.Image(text=False).showgrid(
        x1=r2d_full * np.cos(a2d_full),
        x2=r2d_full * np.sin(a2d_full),
    )

    assert {len(circle) for circle in _segments(circles)} == {len(full)}


def test_the_lines_sit_on_the_cells_of_a_map() -> None:
    """Draw a map on a polar mesh and its grid on the same mesh.

    The corners of the map's cells and the points of the grid's arcs are
    the same, so the grid falls exactly on the cell edges, however far the
    figure is zoomed.
    """
    image = pp.Image(text=False)
    mesh = image.display(np.ones((4, 3)), x1=polar_x, x2=polar_y)

    arcs, _ = image.showgrid(x1=polar_x, x2=polar_y)

    corners = np.asarray(mesh.get_coordinates())
    for column, arc in enumerate(_segments(arcs)):
        npt.assert_allclose(arc, corners[:, column])


def test_lists_are_accepted() -> None:
    """Give the coordinates as lists instead of arrays."""
    first, second = pp.Image(text=False).showgrid(x1=list(x), x2=list(y))

    assert len(_segments(first)) + len(_segments(second)) == len(x) + len(y)


def test_coordinates_that_do_not_match() -> None:
    """Give a 2D mesh with a 1D array, then two meshes of different shape.

    Neither describes one grid, and saying so is better than drawing
    whatever the broadcasting makes of them.
    """
    image = pp.Image(text=False)

    with pytest.raises(ValueError, match="both 1D, or 2D meshes"):
        image.showgrid(x1=polar_x, x2=y)
    with pytest.raises(ValueError, match="both 1D, or 2D meshes"):
        image.showgrid(x1=polar_x, x2=polar_y[:, :3])


def test_showgrid_without_coordinates() -> None:
    """Ask for a grid with neither coordinates nor data."""
    image = pp.Image(text=False)

    with pytest.raises(ValueError, match="cannot be None"):
        image.showgrid()


def test_geom_is_an_unknown_keyword() -> None:
    """Pass the old `geom` keyword and check it is reported.

    The grid is no longer converted from a geometry: a curved grid is
    given as its projection, so `geom` warns like any unknown keyword.
    """
    image = pp.Image(text=False)

    with pytest.warns(UserWarning, match="Unused kwargs: {'geom'}"):
        image.showgrid(x1=x, x2=y, geom="POLAR")  # type: ignore[call-arg]


def test_showgrid_from_data(data_dir: Path) -> None:
    """Draw the grid of a loaded dataset.

    Its faces, x1r and x2r, are the coordinates: one line per face in each
    direction, spanning the domain from -1 to 1.
    """
    data = pp.Load(path=data_dir / "single_file", text=False)
    image = pp.Image(text=False)

    first, second = image.showgrid(data=data)

    assert len(_segments(first)) == len(data.x1r)
    assert len(_segments(second)) == len(data.x2r)
    npt.assert_allclose(_axis(image).get_xlim(), (-1.0, 1.0))


# ---- Thinning ----
def test_thinning_keeps_the_borders() -> None:
    """Keep one line every two, on a count that does not fall on the end.

    Slicing alone keeps 0, 2 and 4 of six faces and drops the last, which
    is the border of the domain; it is always drawn.
    """
    first, second = pp.Image(text=False).showgrid(
        x1=x, x2=y, everyx=2, everyy=2
    )

    assert [line[0, 0] for line in _segments(first)] == [0.0, 2.0, 4.0, 5.0]
    assert [line[0, 1] for line in _segments(second)] == [0.0, 2.0, 3.0]


def test_thinned_lines_still_cross_the_domain() -> None:
    """Thin both families and check how far each line reaches.

    Thinning picks whole lines, never points, so every line still runs
    from one border to the other; it used to take the points of the other
    family away as well, and the lines stopped short of the domain.
    """
    first, second = pp.Image(text=False).showgrid(
        x1=x, x2=y, everyx=2, everyy=2
    )

    for line in _segments(first):
        npt.assert_allclose(line[[0, -1], 1], [0.0, 3.0])
    for line in _segments(second):
        npt.assert_allclose(line[[0, -1], 0], [0.0, 5.0])


@pytest.mark.parametrize(
    ("nlines", "every", "kept"),
    [
        (6, 1, [0, 1, 2, 3, 4, 5]),
        (6, 2, [0, 2, 4, 5]),
        (5, 2, [0, 2, 4]),
        (1, 3, [0]),
    ],
)
def test_every(nlines: int, every: int, kept: list[int]) -> None:
    """Check which lines are kept for a few counts and steps."""
    assert _every(nlines, every) == kept


def test_straighten() -> None:
    """Check a straight line keeps its ends and a bent one every point."""
    straight = [[0.0, 0.0], [1.0, 1.0], [2.0, 2.0]]
    bent = [[0.0, 0.0], [1.0, 2.0], [2.0, 0.0]]

    lines = _straighten(np.array([straight, bent]))

    npt.assert_allclose(lines[0], [straight[0], straight[-1]])
    npt.assert_allclose(lines[1], bent)


def test_lines_from_a_mesh_follow_the_thinning() -> None:
    """Thin a 2D mesh and check the columns and rows that are kept."""
    first, second = _lines(polar_x, polar_y, 2, 2)

    assert len(first) == len(_every(len(radius), 2))
    assert len(second) == len(_every(len(angle), 2))


# ---- The frame ----
def test_the_frame_is_the_grid() -> None:
    """Draw a grid alone and read the limits.

    They are its extent exactly, in both directions: a line would be
    padded, but a grid is the domain.
    """
    image = pp.Image(text=False)
    image.showgrid(x1=x, x2=y)

    npt.assert_allclose(_axis(image).get_xlim(), (0.0, 5.0))
    npt.assert_allclose(_axis(image).get_ylim(), (0.0, 3.0))


def test_the_frame_of_a_curved_grid() -> None:
    """Check the frame of the polar quarter, from 0 to 2 in both directions."""
    image = pp.Image(text=False)
    image.showgrid(x1=polar_x, x2=polar_y)

    npt.assert_allclose(_axis(image).get_xlim(), (0.0, 2.0), atol=1e-12)
    npt.assert_allclose(_axis(image).get_ylim(), (0.0, 2.0), atol=1e-12)


def test_the_axis_is_left_free() -> None:
    """Draw a grid, then a line that reaches past it.

    The line is not cut off: the grid set the frame without fixing it.
    Faking an `xrange` used to mark the limits as the user's, and froze
    them on the grid.
    """
    image = pp.Image(text=False)
    image.showgrid(x1=x, x2=y)

    image.plot([0.0, 9.0], [0.0, 9.0])

    assert _axis(image).get_xlim()[1] >= 9.0
    assert _axis(image).get_ylim()[1] >= 9.0


def test_what_was_drawn_before_stays_in_the_frame() -> None:
    """Draw a line first, then a smaller grid over it.

    The frame keeps the line; the grid used to shrink it to its own extent
    and cut the line off.
    """
    image = pp.Image(text=False)
    image.plot([0.0, 9.0], [0.0, 9.0])
    before = _axis(image).get_xlim()

    image.showgrid(x1=x, x2=y)

    npt.assert_allclose(_axis(image).get_xlim(), before)


def test_a_range_given_stays_fixed() -> None:
    """Give an x range, then draw a line far beyond it.

    A range the user gives is the user's, so it holds; y, which was not
    given, is still the grid's.
    """
    image = pp.Image(text=False)
    image.showgrid(x1=x, x2=y, xrange=[1.0, 2.0])

    image.plot([0.0, 9.0], [0.0, 9.0])

    npt.assert_allclose(_axis(image).get_xlim(), (1.0, 2.0))


def test_a_grid_over_a_map() -> None:
    """Draw a map, then its grid, and check the frame of the map is kept."""
    image = pp.Image(text=False)
    image.display(np.ones((5, 3)), x1=x, x2=y)

    image.showgrid(x1=x, x2=y)

    npt.assert_allclose(_axis(image).get_xlim(), (0.0, 5.0))
    npt.assert_allclose(_axis(image).get_ylim(), (0.0, 3.0))


# ---- The style and the legend ----
def test_the_default_style() -> None:
    """Check the default look: thin black lines, taking no palette color.

    A grid is a background, so it does not advance the colors the curves
    drawn after it take.
    """
    image = pp.Image(text=False)
    first, _ = image.showgrid(x1=x, x2=y)

    assert to_hex(np.asarray(first.get_edgecolor())[0]) == "#000000"
    npt.assert_allclose(first.get_linewidth(), 0.75)
    assert image.nline == [0]


def test_showgrid_color() -> None:
    """Choose the color of the grid lines."""
    first, second = pp.Image(text=False).showgrid(x1=x, x2=y, c="red")

    assert to_hex(np.asarray(first.get_edgecolor())[0]) == "#ff0000"
    assert to_hex(np.asarray(second.get_edgecolor())[0]) == "#ff0000"


def test_showgrid_linewidth() -> None:
    """Choose the width of the grid lines."""
    first, _ = pp.Image(text=False).showgrid(x1=x, x2=y, lw=2.0)

    npt.assert_allclose(first.get_linewidth(), 2.0)


def test_showgrid_linestyle() -> None:
    """Choose a dashed style and compare it with the solid default."""
    dashed, _ = pp.Image(text=False).showgrid(x1=x, x2=y, ls="--")
    solid, _ = pp.Image(text=False).showgrid(x1=x, x2=y)

    assert dashed.get_linestyle() != solid.get_linestyle()


def test_a_label_is_one_legend_entry() -> None:
    """Label the grid and build a legend.

    The grid is one entry, however many lines it has: each line used to
    carry the label, which made one entry per line.
    """
    image = pp.Image(text=False)
    image.showgrid(x1=x, x2=y, label="grid", legpos="best")

    legend = _axis(image).get_legend()
    assert legend is not None
    assert [text.get_text() for text in legend.get_texts()] == ["grid"]


def test_a_curve_joins_the_legend() -> None:
    """Draw a labelled grid, then a labelled curve on the same axis."""
    image = pp.Image(text=False)
    image.showgrid(x1=x, x2=y, label="grid", legpos="best")

    image.plot(x, x / 2, label="data")

    legend = _axis(image).get_legend()
    assert legend is not None
    assert [t.get_text() for t in legend.get_texts()] == ["grid", "data"]


def test_an_unlabelled_grid_stays_out_of_the_legend() -> None:
    """Draw a labelled curve, then a grid without a label."""
    image = pp.Image(text=False)
    image.plot(x, x / 2, label="data", legpos="best")

    image.showgrid(x1=x, x2=y)

    legend = _axis(image).get_legend()
    assert legend is not None
    assert [t.get_text() for t in legend.get_texts()] == ["data"]


# ---- The axis and the figure ----
def test_the_axis_keywords_are_applied() -> None:
    """Give a title, an axis label and an aspect, and read them back."""
    image = pp.Image(text=False)
    image.showgrid(x1=x, x2=y, title="grid", xtitle="x", aspect="equal")

    assert _axis(image).get_title() == "grid"
    assert _axis(image).get_xlabel() == "x"
    assert _axis(image).get_aspect() == 1.0


def test_showgrid_on_second_axis() -> None:
    """Send the grid to the second axis of a two-panel figure."""
    image = pp.Image(text=False)
    image.create_axes(ncol=2)

    image.showgrid(x1=x, x2=y, ax=1)

    assert isinstance(image.ax[1], Axes)
    assert len(image.ax[1].collections) == 2
    assert len(_axis(image).collections) == 0


def test_the_layout_is_tight() -> None:
    """Draw a grid with long labels and compare with a fresh tight layout.

    set_axis makes the layout once, and nothing drawn after it moves what
    the layout is computed from, so a second pass would change nothing:
    the axis box is the one a tight layout of the finished figure gives.
    """
    image = pp.Image(text=False)
    image.showgrid(
        x1=x * 1e6,
        x2=y,
        label="grid",
        legpos="best",
        xtitle="x",
        ytitle="a very long y title indeed",
    )
    drawn = _axis(image).get_position().bounds

    assert image.fig is not None
    image.fig.tight_layout()

    npt.assert_allclose(_axis(image).get_position().bounds, drawn)


def test_a_grid_says_nothing_of_its_own() -> None:
    """Draw the ordinary way and listen for warnings."""
    image = pp.Image(text=False)

    with warnings.catch_warnings():
        warnings.simplefilter("error")
        first, _ = image.showgrid(x1=polar_x, x2=polar_y, label="grid")

    assert isinstance(first, LineCollection)
