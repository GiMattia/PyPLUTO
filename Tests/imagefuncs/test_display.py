"""Test of the display.py file.

DisplayManager draws a 2D variable as a map, through pcolormesh. Two things
about it are easy to get backwards and are checked here on a rectangular
array, where a transposition shows.

The first is the orientation: the variable is indexed as `var[x, y]`, which
is the PLUTO order and the opposite of what matplotlib wants, so the array is
transposed on the way out. The tests read single values back out of the mesh
to pin which corner is which, since a square test array hides the whole
question.

The second is the grid: `x1` and `x2` are the coordinates, and without them
the map is drawn on the cell indices, one edge more than there are cells.
Given the centers, the frame is still the edges of the outermost cells,
which is where the domain ends, and every shading is made to paint up to
them.

The limits are the extent of the map exactly, with no padding, and the axis
is left free afterwards: a map is normally the background of something else
-- field lines, particles, a box -- and none of it may be cut off because the
map was drawn first.
"""

import warnings
from collections.abc import Callable

import numpy as np
import numpy.testing as npt
import pytest
from matplotlib.axes import Axes
from matplotlib.collections import QuadMesh
from matplotlib.colors import LogNorm, Normalize, SymLogNorm, TwoSlopeNorm

import pyPLUTO as pp

# A rectangular variable, so that an accidental transposition cannot pass,
# with values that say where they came from: var[i, j] is 4 * i + j.
var = np.arange(24.0).reshape(6, 4)
# Cell centers a whole unit apart, so the edges of the map -- half a cell
# beyond the outermost center -- are round numbers: 0 to 6 and 0 to 4.
x1 = np.linspace(0.5, 5.5, 6)
x2 = np.linspace(0.5, 3.5, 4)

# The color scales and the norm each one has to build.
CSCALES: list[tuple[Callable[[pp.Image], QuadMesh], type[Normalize]]] = [
    (lambda i: i.display(var, cscale="norm"), Normalize),
    (lambda i: i.display(var + 1.0, cscale="log"), LogNorm),
    (
        lambda i: i.display(var, cscale="symlog", vmin=-4.0, vmax=8.0),
        SymLogNorm,
    ),
    (
        lambda i: i.display(var, cscale="twoslope", vmin=-4.0, vmax=8.0),
        TwoSlopeNorm,
    ),
]


def _mesh(image: pp.Image, nax: int = 0) -> QuadMesh:
    """Return the map drawn on one axis, as the mesh matplotlib holds."""
    assert isinstance(image.ax[nax], Axes)
    meshes = [
        artist
        for artist in image.ax[nax].collections
        if isinstance(artist, QuadMesh)
    ]
    assert len(meshes) >= 1
    return meshes[0]


def _drawn(mesh: QuadMesh) -> np.ndarray:
    """Return the values of a mesh, in matplotlib's own order.

    That order is the transpose of the variable, one row per y and one column
    per x, so a value of `var[i, j]` is read back at `[j, i]`.
    """
    return np.asarray(mesh.get_array())


# ---- The map that is drawn ----
def test_the_mesh_is_returned() -> None:
    """Check the display hands back the mesh it drew.

    It is what a colorbar is built from, so a display that returns nothing
    cannot be given one of its own.
    """
    image = pp.Image(text=False)
    mesh = image.display(var)

    assert isinstance(mesh, QuadMesh)


def test_the_variable_is_indexed_x_first() -> None:
    """Read two corners of the map back and check where they landed.

    `var[i, j]` is the value at the i-th x and the j-th y, which is how a
    PLUTO variable is indexed and the transpose of what pcolormesh takes. A
    map drawn the other way round is a figure that looks plausible and is
    wrong everywhere.
    """
    image = pp.Image(text=False)
    mesh = image.display(var)

    drawn = _drawn(mesh)
    assert drawn.shape == (4, 6)
    assert drawn[0, 5] == var[5, 0]
    assert drawn[3, 0] == var[0, 3]


def test_without_coordinates_the_map_is_drawn_on_the_indices() -> None:
    """Display a variable and nothing else.

    The grid is then the cell numbers, with one edge more than there are
    cells in each direction, so the map fills the axis from 0 to the number
    of cells and the frame is the data.
    """
    image = pp.Image(text=False)
    image.display(var)

    assert isinstance(image.ax[0], Axes)
    npt.assert_allclose(image.ax[0].get_xlim(), (0.0, 6.0))
    npt.assert_allclose(image.ax[0].get_ylim(), (0.0, 4.0))


def test_the_coordinates_are_used_when_they_are_given() -> None:
    """Give the two coordinate arrays, which are the cell centers.

    This is the ordinary call on real data, where the axes are lengths and
    not cell numbers. The frame is the edge of the outermost cells, half a
    cell beyond the first and the last center, since that is where the map
    is drawn to: framing the centers instead cuts the outer half cell of the
    domain off, and leaves anything sitting in it -- a field line ending on
    the border, a particle at the wall -- outside a map it belongs to.
    """
    image = pp.Image(text=False)
    image.display(var, x1=x1, x2=x2)

    assert isinstance(image.ax[0], Axes)
    npt.assert_allclose(image.ax[0].get_xlim(), (0.0, 6.0))
    npt.assert_allclose(image.ax[0].get_ylim(), (0.0, 4.0))


def test_coordinates_given_as_edges_are_taken_as_they_are() -> None:
    """Give one coordinate more than there are cells.

    Then they are the edges already, and nothing is added to them: the two
    forms have to give the same frame for the same map.
    """
    image = pp.Image(text=False)
    image.display(var, x1=np.arange(7.0), x2=np.arange(5.0))

    assert isinstance(image.ax[0], Axes)
    npt.assert_allclose(image.ax[0].get_xlim(), (0.0, 6.0))
    npt.assert_allclose(image.ax[0].get_ylim(), (0.0, 4.0))


def test_a_map_one_cell_wide() -> None:
    """Display a variable with a single cell along one direction.

    There is no spacing to take half of, so the cell is given the width
    matplotlib gives it, one unit: a slice of a domain is still a map, and
    it must not come out with a frame of zero width.
    """
    image = pp.Image(text=False)
    slab = np.arange(4.0).reshape(1, 4)

    image.display(slab, x1=np.array([2.0]), x2=x2)

    assert isinstance(image.ax[0], Axes)
    npt.assert_allclose(image.ax[0].get_xlim(), (1.5, 2.5))
    npt.assert_allclose(image.ax[0].get_ylim(), (0.0, 4.0))


@pytest.mark.parametrize("transpose", [True, 1])
def test_the_map_can_be_transposed(transpose: bool) -> None:
    """Ask for the transposed map, as a flag and as a number.

    It swaps which index runs along which axis, for a variable stored the
    other way round: the variable is transposed on the way in and again on
    the way out, so what matplotlib holds is the variable itself. Comparing
    the keyword with `True` rather than reading it as a flag leaves every
    other true value silently doing nothing.
    """
    image = pp.Image(text=False)
    mesh = image.display(var, transpose=transpose)

    drawn = _drawn(mesh)
    assert drawn.shape == (6, 4)
    npt.assert_array_equal(drawn, var)


def test_the_shading_is_forwarded() -> None:
    """Ask for the smooth shading rather than the flat cells.

    With `gouraud` matplotlib interpolates between the values instead of
    drawing one block per cell, so on its own it would stop at the outermost
    centers and leave the half cell beyond them empty. A vertex is added on
    each border, holding the value of the cell it belongs to, so the map
    covers the same domain as any other shading: two extra rows and columns
    of values, and the same frame.
    """
    image = pp.Image(text=False)
    mesh = image.display(var, x1=x1, x2=x2, shading="gouraud")

    assert _drawn(mesh).shape == (6, 8)
    assert _drawn(mesh)[0, 0] == var[0, 0]
    assert isinstance(image.ax[0], Axes)
    npt.assert_allclose(image.ax[0].get_xlim(), (0.0, 6.0))
    npt.assert_allclose(image.ax[0].get_ylim(), (0.0, 4.0))


def test_the_opacity_is_forwarded() -> None:
    """Draw a map that can be seen through.

    A map is often the background of something else, so being able to fade
    it is what keeps what is drawn on top readable.
    """
    image = pp.Image(text=False)
    mesh = image.display(var, alpha=0.5)

    assert mesh.get_alpha() == 0.5


# ---- The colors ----
def test_the_default_colormap() -> None:
    """Display without naming a colormap.

    The default is written in the call rather than taken from matplotlib's
    settings, so every figure of a session looks the same whatever the
    user's rc file says.
    """
    image = pp.Image(text=False)
    mesh = image.display(var)

    assert mesh.get_cmap().name == "plasma"


def test_the_colormap_is_resolved_by_name() -> None:
    """Name a colormap and read it back off the mesh.

    The name goes through `find_cmap`, which is what lets it come from a
    package other than matplotlib; a failure here means the map is drawn in
    a colormap the user did not ask for.
    """
    image = pp.Image(text=False)
    mesh = image.display(var, cmap="magma")

    assert mesh.get_cmap().name == "magma"


def test_the_color_limits_are_the_extremes_of_the_data() -> None:
    """Display without color limits and read them back.

    Without them the whole colormap is used over the whole variable, which
    is what makes the first look at an unknown file useful.
    """
    image = pp.Image(text=False)
    mesh = image.display(var)

    limits = (float(np.min(var)), float(np.max(var)))
    assert mesh.get_clim() == pytest.approx(limits)


def test_the_color_limits_are_chosen() -> None:
    """Give `vmin` and `vmax` by hand.

    Fixed limits are what makes two maps comparable -- two files, two
    times -- so they must win over the extremes of the data.
    """
    image = pp.Image(text=False)
    mesh = image.display(var, vmin=-4.0, vmax=8.0)

    assert mesh.get_clim() == pytest.approx((-4.0, 8.0))
    npt.assert_allclose(image.vlims[0][:2], (-4.0, 8.0))


def test_the_threshold_kept_on_the_axis() -> None:
    """Check the threshold stored with the color limits.

    It is a hundredth of the largest limit by default, and it is kept on the
    axis so that a colorbar drawn afterwards divides its scale at the same
    point as the map.
    """
    image = pp.Image(text=False)
    image.display(var, vmin=-4.0, vmax=8.0, cscale="symlog")

    npt.assert_allclose(image.vlims[0], (-4.0, 8.0, 0.08))


@pytest.mark.parametrize(("call", "norm"), CSCALES)
def test_the_color_scale(
    call: Callable[[pp.Image], QuadMesh], norm: type[Normalize]
) -> None:
    """Ask for each color scale and check the norm that was built.

    The scale is the arithmetic between the values and the colors, so the
    wrong norm is a map that looks right and reads wrong.
    """
    image = pp.Image(text=False)

    mesh = call(image)

    assert isinstance(mesh.norm, norm)


def test_no_colorbar_unless_one_is_asked_for() -> None:
    """Display without `cpos`, then with it.

    A map is unreadable without a colorbar, but it takes room from the
    figure, so it is drawn only when a side is named.
    """
    image = pp.Image(text=False)
    image.display(var)
    assert image.fig is not None
    assert len(image.fig.axes) == 1

    image.display(var, cpos="right")

    assert len(image.fig.axes) == 2


# ---- The limits ----
def test_the_limits_are_the_extent_of_the_map() -> None:
    """Display on given coordinates and read the limits back.

    They are the edges of the domain exactly: padding a map would leave a
    strip of empty frame around it, which is not what a map of a domain
    should look like.
    """
    image = pp.Image(text=False)
    image.display(var, x1=x1, x2=x2)

    assert isinstance(image.ax[0], Axes)
    npt.assert_allclose(image.ax[0].get_xlim(), (0.0, 6.0))
    npt.assert_allclose(image.ax[0].get_ylim(), (0.0, 4.0))


def test_a_second_map_widens_the_axis() -> None:
    """Display a second map further along the x-axis.

    Two maps side by side are one figure of a domain in pieces, so the axis
    has to hold both rather than keep the first and cut the second.
    """
    image = pp.Image(text=False)
    image.display(var)
    image.display(var, x1=np.arange(7.0) + 10.0)

    assert isinstance(image.ax[0], Axes)
    npt.assert_allclose(image.ax[0].get_xlim(), (0.0, 16.0))


def test_a_line_drawn_over_a_map_is_not_clipped() -> None:
    """Display a map, then plot a line that leaves it.

    A map is the background of field lines, of particles, of a fit; the axis
    must not be frozen by it, or everything drawn on top is silently cut at
    the edge of the map.
    """
    image = pp.Image(text=False)
    image.display(var, x1=x1, x2=x2)
    image.plot(x1, 10.0 * np.ones_like(x1))

    assert isinstance(image.ax[0], Axes)
    assert image.ax[0].get_ylim()[1] >= 10.0


def test_a_range_given_by_hand_is_kept() -> None:
    """Fix the ranges, then display a map that falls outside them.

    A range the user chose is a decision, and a zoom into a map is made of
    exactly that: the second map is clipped rather than the frame reopened.
    """
    image = pp.Image(text=False)
    image.display(var, x1=x1, x2=x2, xrange=[1.0, 2.0], yrange=[0.0, 1.0])
    image.display(var, x1=x1 + 10.0, x2=x2)

    assert isinstance(image.ax[0], Axes)
    npt.assert_allclose(image.ax[0].get_xlim(), (1.0, 2.0))
    npt.assert_allclose(image.ax[0].get_ylim(), (0.0, 1.0))


# ---- The axis ----
def test_the_axis_keywords_are_forwarded() -> None:
    """Give the titles and the aspect ratio to the display call.

    `aspect="equal"` is the one that matters for a map: a domain drawn with
    the two axes on different scales is a distorted picture of it.
    """
    image = pp.Image(text=False)
    image.display(var, title="a map", xtitle="x", ytitle="y", aspect="equal")

    assert isinstance(image.ax[0], Axes)
    assert image.ax[0].get_title() == "a map"
    assert image.ax[0].get_xlabel() == "x"
    assert image.ax[0].get_ylabel() == "y"
    assert image.ax[0].get_aspect() == 1.0


def test_the_axis_is_chosen_by_index() -> None:
    """Display on the second of two axes.

    Nothing must land on the other one, and the number written on the panel
    goes as soon as it is used.
    """
    image = pp.Image(text=False)
    image.create_axes(ncol=2)
    image.display(var, ax=1)

    assert isinstance(image.ax[0], Axes)
    assert len(image.ax[0].collections) == 0
    assert isinstance(_mesh(image, 1), QuadMesh)
    assert image.ntext[1] == 1


# ---- The figure ----
def test_a_display_without_a_figure() -> None:
    """Display on an image whose figure is gone.

    There is nothing to draw on, and saying so is better than the error
    matplotlib would give further down, in a call the user never made.
    """
    image = pp.Image(text=False)
    image.fig = None

    with pytest.raises(ValueError, match="No figure is present"):
        image.display(var)


def test_the_layout_is_tightened_again() -> None:
    """Display with a long axis label on a tight figure.

    The layout is redone after every map, since what it adds -- a label, a
    colorbar -- is what the layout has to make room for.
    """
    image = pp.Image(text=False)
    image.display(var)
    assert isinstance(image.ax[0], Axes)
    before = image.ax[0].get_position().x0

    image.display(var * 1e6, ytitle="a very long y title indeed")

    assert image.ax[0].get_position().x0 > before


def test_a_loose_layout_is_left_alone() -> None:
    """Display the same map on a figure that asked for no tight layout.

    The axis box is where the figure put it and stays there, whatever is
    drawn on it.
    """
    image = pp.Image(text=False, tight=False)
    image.display(var)
    assert isinstance(image.ax[0], Axes)
    before = image.ax[0].get_position().x0

    image.display(var * 1e6, ytitle="a very long y title indeed")

    assert image.ax[0].get_position().x0 == before


def test_an_unknown_keyword_warns() -> None:
    """Misspell a keyword and check the display says which one.

    The warning names the method the user called, and the map is drawn
    anyway: a misspelt keyword is not a reason to lose the figure.
    """
    image = pp.Image(text=False)

    with pytest.warns(UserWarning, match="Unused kwargs: {'cbar'}"):
        image.display(var, cbar="right")  # type: ignore[call-overload]

    assert isinstance(_mesh(image), QuadMesh)


def test_a_map_says_nothing_of_its_own() -> None:
    """Display the ordinary way and listen for warnings.

    Nothing about a plain map is worth a warning, and one that appears here
    comes from matplotlib rather than from us -- which is how the wrong
    shading or an edge color for an unfilled marker used to get out.
    """
    image = pp.Image(text=False)

    with warnings.catch_warnings():
        warnings.simplefilter("error")
        image.display(var, x1=x1, x2=x2, cpos="right")

    assert isinstance(_mesh(image), QuadMesh)
