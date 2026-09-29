"""Test of the zoom.py file.

ZoomManager places an inset in an axis and fills it with what the axis
shows, seen closer. Every line and collection of the parent -- maps, curves,
points, contour lines, streamlines, grids -- is copied, in the order it was
drawn: the geometry is rebuilt for each kind, the style is taken over whole,
and only what belongs to the parent is pointed at the inset, its data
transform and its clipping. With var, another 2D quantity is drawn in place
of the map, on its grid, and everything drawn over the map is still copied.

The inset is placed by a start and a size in each direction, in units of
its parent: from 0.6, spanning 0.15, unless told otherwise; an end given
wins over the size. It is an axis of the image like any other, so it can
be drawn on afterwards.
"""

import warnings
from collections.abc import Callable
from typing import Literal

import numpy as np
import numpy.testing as npt
import pytest
from matplotlib.axes import Axes
from matplotlib.collections import LineCollection, PathCollection, QuadMesh
from matplotlib.inset import InsetIndicator
from matplotlib.lines import Line2D

import pyPLUTO as pp
from pyPLUTO.imagekwargs import CheckRangeKwargs, ZoomKwargs

x = np.linspace(0, 1, 101)
y = np.linspace(1, 10, 101)
z = np.logspace(0, 1, 101)

# A bowl-shaped map on a 20 x 20 grid, and a second quantity on the same
# grid for the inset of another variable.
coord = np.linspace(-1.0, 1.0, 20)
x2d, y2d = np.meshgrid(coord, coord, indexing="ij")
bowl = x2d**2 + y2d**2
saddle = x2d * y2d

# The central window the zooms look at.
WINDOW: CheckRangeKwargs = {"xrange": [-0.5, 0.5], "yrange": [-0.5, 0.5]}


def _axis(image: pp.Image, nax: int = 0) -> Axes:
    """Return an axis of an image, checked to be one."""
    axis = image.ax[nax]
    assert isinstance(axis, Axes)
    return axis


def _box(image: pp.Image, axins: Axes) -> tuple[float, ...]:
    """Return where an inset is, in units of its parent: x, y, w, h."""
    parent = _axis(image).get_position().bounds
    inset = axins.get_position().bounds
    return (
        (inset[0] - parent[0]) / parent[2],
        (inset[1] - parent[1]) / parent[3],
        inset[2] / parent[2],
        inset[3] / parent[3],
    )


def _mesh(axis: Axes) -> QuadMesh:
    """Return the first map drawn on an axis."""
    meshes = [c for c in axis.collections if isinstance(c, QuadMesh)]
    assert len(meshes) >= 1
    return meshes[0]


# ---- Where the inset goes ----
def test_default_zoom() -> None:
    """Zoom with no position and check where the inset lands.

    It starts at 0.6 of its parent in both directions and spans 0.15, and
    it holds a copy of every line of the parent.
    """
    image = pp.Image(text=False)
    ax = image.create_axes(left=0.2, right=0.8, top=0.85, bottom=0.05)
    image.plot(x, y, ax=ax)
    image.plot(x, z, ax=ax)

    axins = image.zoom()

    assert len(image.ax) == 2
    npt.assert_allclose(_box(image, axins), (0.6, 0.6, 0.15, 0.15))
    line1, line2 = axins.get_lines()
    npt.assert_array_equal(line1.get_xdata(), x)
    npt.assert_array_equal(line1.get_ydata(), y)
    npt.assert_array_equal(line2.get_xdata(), x)
    npt.assert_array_equal(line2.get_ydata(), z)


def test_custom_loc() -> None:
    """Give a start and a size in each direction."""
    image = pp.Image(text=False)
    image.create_axes(left=0.2, right=0.8, top=0.85, bottom=0.05)
    image.plot(x, y)

    axins = image.zoom(left=0.2, bottom=0.1, height=0.3, width=0.4)

    npt.assert_allclose(_box(image, axins), (0.2, 0.1, 0.4, 0.3))


def test_cutom_pos() -> None:
    """Give the four edges at once, as [left, right, bottom, top]."""
    image = pp.Image(text=False)
    image.create_axes(left=0.2, right=0.8, top=0.85, bottom=0.05)
    image.plot(x, y)

    axins = image.zoom(pos=[0.25, 0.6, 0.15, 0.4])

    npt.assert_allclose(_box(image, axins), (0.25, 0.15, 0.35, 0.25))


@pytest.mark.parametrize(
    ("keywords", "box", "warning"),
    [
        ({"top": 0.9, "height": 0.2}, (0.6, 0.7, 0.15, 0.2), "bottom is set"),
        ({"right": 0.9, "width": 0.2}, (0.7, 0.6, 0.2, 0.15), "left is set"),
    ],
    ids=["top-height", "right-width"],
)
def test_an_end_wins_over_a_size(
    keywords: ZoomKwargs, box: tuple[float, ...], warning: str
) -> None:
    """Give an end and a size in the same direction.

    The box is over-determined, and the end wins, as documented: the inset
    ends where it was asked to, and its start is taken back from the two.
    The size used to win instead, with a warning claiming the opposite.
    """
    image = pp.Image(text=False)
    image.plot(x, y)

    with pytest.warns(UserWarning, match=warning):
        axins = image.zoom(**keywords)

    npt.assert_allclose(_box(image, axins), box)


def test_an_end_alone_moves_the_start() -> None:
    """Give only a top: the inset keeps its size and ends there.

    The end wins, so the start follows it. Keeping the default start
    instead stretched the inset to the top given, and a top below 0.6 gave
    it a negative height, which matplotlib refuses.
    """
    image = pp.Image(text=False)
    image.plot(x, y)

    axins = image.zoom(top=0.5)

    npt.assert_allclose(_box(image, axins), (0.6, 0.35, 0.15, 0.15))


def test_a_start_and_an_end_set_the_size() -> None:
    """Give a bottom and a top: the inset spans the two."""
    image = pp.Image(text=False)
    image.plot(x, y)

    axins = image.zoom(bottom=0.2, top=0.9)

    npt.assert_allclose(_box(image, axins), (0.6, 0.2, 0.15, 0.7))


def test_a_start_at_zero() -> None:
    """Put the inset in the corner, at 0: zero is a position, not a gap."""
    image = pp.Image(text=False)
    image.plot(x, y)

    axins = image.zoom(left=0.0, bottom=0.0)

    npt.assert_allclose(_box(image, axins), (0.0, 0.0, 0.15, 0.15), atol=1e-12)


def test_a_left_and_a_right_set_the_width() -> None:
    """Give a left and a right: the inset spans the two."""
    image = pp.Image(text=False)
    image.plot(x, y)

    axins = image.zoom(left=0.0, right=0.5)

    npt.assert_allclose(_box(image, axins), (0.0, 0.6, 0.5, 0.15), atol=1e-12)


def test_a_right_alone_moves_the_left() -> None:
    """Give only a right: the inset keeps its width and ends there."""
    image = pp.Image(text=False)
    image.plot(x, y)

    axins = image.zoom(right=0.3)

    npt.assert_allclose(_box(image, axins), (0.15, 0.6, 0.15, 0.15))


# ---- The axis of the inset ----
def test_axes_properties() -> None:
    """Give the inset a title, labels and ticks of its own.

    The ticks of an inset are off by default, since it is small; the ones
    given are drawn.
    """
    image = pp.Image(text=False)
    image.plot(x, y)

    axins = image.zoom(
        title="Inset zoom", xtitle="x", ytitle="y", yticks=[0, 0.2, 1.0]
    )

    assert axins.get_title() == "Inset zoom"
    assert axins.get_xlabel() == "x"
    assert axins.get_ylabel() == "y"
    assert len(axins.get_xticks()) == 0
    npt.assert_array_equal(axins.get_yticks(), [0, 0.2, 1.0])


def test_x_ticks_for_the_inset() -> None:
    """Give the inset x ticks, which are off by default, and read them."""
    image = pp.Image(text=False)
    image.plot(x, y)

    axins = image.zoom(xticks=[0.2, 0.4])

    npt.assert_array_equal(axins.get_xticks(), [0.2, 0.4])
    assert len(axins.get_yticks()) == 0


def test_range() -> None:
    """Give the window of the inset and check it is the one drawn."""
    image = pp.Image(text=False)
    image.plot(x, y)

    axins = image.zoom(xrange=[0.2, 0.5], yrange=[0.3, 0.7])

    npt.assert_allclose(axins.get_xlim(), (0.2, 0.5))
    npt.assert_allclose(axins.get_ylim(), (0.3, 0.7))


def test_without_a_range_the_window_is_the_parent() -> None:
    """Zoom with no range: the inset shows the window of its parent."""
    image = pp.Image(text=False)
    image.plot(x, y)

    axins = image.zoom()

    npt.assert_allclose(axins.get_xlim(), _axis(image).get_xlim())
    npt.assert_allclose(axins.get_ylim(), _axis(image).get_ylim())


def test_the_parent_is_left_as_it_was() -> None:
    """Zoom into a window and check the parent's own frame is unchanged."""
    image = pp.Image(text=False)
    image.plot(x, y)
    before = (_axis(image).get_xlim(), _axis(image).get_ylim())

    image.zoom(xrange=[0.2, 0.5], yrange=[2.0, 3.0])

    npt.assert_allclose(_axis(image).get_xlim(), before[0])
    npt.assert_allclose(_axis(image).get_ylim(), before[1])


def test_the_inset_is_an_axis_of_the_image() -> None:
    """Zoom, then draw on the inset through its index.

    The inset is registered like any axis, so it can be filled later: the
    zoom returns it, and it is ax[1].
    """
    image = pp.Image(text=False)
    image.plot(x, y)
    axins = image.zoom()

    image.plot(x, z, ax=1)

    assert axins is image.ax[1]
    assert len(axins.get_lines()) == 2


def test_the_inset_shows_no_axis_index() -> None:
    """Zoom on an image that labels its axes with their index.

    An axis gets its index written on it when created, and the drawing
    methods hide it; a copied inset used to keep it, a "2" in the middle
    of the zoomed map.
    """
    image = pp.Image()
    image.display(bowl, x1=coord, x2=coord)

    axins = image.zoom(**WINDOW)

    assert not [t for t in axins.texts if t.get_visible() and t.get_text()]


# ---- The tight layout ----
def test_a_zoom_keeps_the_tight_layout() -> None:
    """Zoom into a map with a colorbar, then draw with a long label.

    An inset lays out fine, so the figure keeps its tight layout and a
    later label still gets its room. A zoom used to switch the layout off
    for the whole figure, whatever came after.
    """
    image = pp.Image(text=False)
    image.display(bowl, x1=coord, x2=coord, cpos="right")

    image.zoom(**WINDOW)

    assert image.state.tight is True


def test_an_inset_colorbar_switches_the_layout_off() -> None:
    """Give the inset a colorbar of its own.

    Its axis is one tight_layout cannot handle, and every later layout
    would warn, so the layout is switched off -- and nothing warns.
    """
    image = pp.Image(text=False)
    image.display(bowl, x1=coord, x2=coord, cpos="right")

    with warnings.catch_warnings():
        warnings.simplefilter("error")
        image.zoom(cpos="bottom", **WINDOW)
        image.plot(coord, coord, ax=0)

    assert image.state.tight is False


# ---- What is copied ----
@pytest.mark.parametrize(
    ("draw", "kinds"),
    [
        (lambda i: i.scatter(coord, coord, c=coord), [PathCollection]),
        (
            lambda i: i.contour(bowl, x1=coord, x2=coord),
            [PathCollection],
        ),
        (
            lambda i: i.streamplot(-y2d, x2d, x1=coord, x2=coord),
            [LineCollection],
        ),
        (
            lambda i: i.showgrid(x1=coord, x2=coord),
            [LineCollection, LineCollection],
        ),
    ],
    ids=["scatter", "contour", "streamplot", "grid"],
)
def test_every_kind_of_drawing_is_zoomed(
    draw: Callable[[pp.Image], object], kinds: list[type]
) -> None:
    """Zoom into each kind of drawing that is not a map or a curve.

    Only maps and curves could be zoomed before: anything else raised
    "The zoom can be applied only to a QuadMesh object".
    """
    image = pp.Image(text=False)
    draw(image)

    axins = image.zoom(**WINDOW)

    assert [type(c) for c in axins.collections] == kinds


def test_what_is_drawn_over_a_map_is_kept() -> None:
    """Zoom into a map with contour lines and a curve over it.

    The overlay is what makes most zooms worth drawing, and it used to be
    lost: only the map was redrawn in the inset.
    """
    image = pp.Image(text=False)
    image.display(bowl, x1=coord, x2=coord)
    image.contour(bowl, x1=coord, x2=coord, c="k")
    image.plot(coord, coord, c="r")

    axins = image.zoom(**WINDOW)

    assert [type(c) for c in axins.collections] == [QuadMesh, PathCollection]
    assert len(axins.get_lines()) == 1


@pytest.mark.parametrize("shading", ["auto", "nearest", "gouraud"])
def test_the_copied_map_is_the_map(
    shading: Literal["auto", "nearest", "gouraud"],
) -> None:
    """Zoom into a map and compare the copy with the original.

    The values, the grid and the colors are the same: the copy is rebuilt
    from the map itself, not recomputed from the data by display.
    """
    image = pp.Image(text=False)
    image.display(bowl, x1=coord, x2=coord, shading=shading)
    original = _mesh(_axis(image))

    copy = _mesh(image.zoom(**WINDOW))

    npt.assert_allclose(
        np.asarray(copy.get_array()), np.asarray(original.get_array())
    )
    npt.assert_allclose(
        np.asarray(copy.get_coordinates()),
        np.asarray(original.get_coordinates()),
    )
    assert copy.get_cmap().name == original.get_cmap().name
    assert copy.get_clim() == original.get_clim()


def test_zoom_on_display() -> None:
    """Zoom into a map at a given place and window.

    The inset holds one map, framed on the window asked for.
    """
    image = pp.Image(text=False)
    image.display(bowl, x1=coord, x2=coord)

    axins = image.zoom(pos=[0.6, 0.9, 0.6, 0.9], **WINDOW)

    assert len(axins.collections) == 1
    npt.assert_allclose(axins.get_xlim(), (-0.5, 0.5))
    npt.assert_allclose(axins.get_ylim(), (-0.5, 0.5))


def test_zoom_on_display_keeps_cmap() -> None:
    """Check the inset keeps the colormap of the map it zooms into."""
    image = pp.Image(text=False)
    image.display(bowl, x1=coord, x2=coord, cmap="magma")

    axins = image.zoom(**WINDOW)

    assert _mesh(axins).get_cmap().name == "magma"


def test_a_log_map_keeps_its_scale() -> None:
    """Zoom into a map on a logarithmic scale."""
    image = pp.Image(text=False)
    image.display(bowl + 0.1, x1=coord, x2=coord, cscale="log")

    axins = image.zoom(**WINDOW)

    assert type(_mesh(axins).norm).__name__ == "LogNorm"


def test_the_copied_map_is_drawn_like_the_original() -> None:
    """Check the antialiasing and the rasterizing of the copy.

    A map is drawn without antialiasing and rasterized, while a mesh built
    from scratch has antialiasing on, which paints the edge of every cell
    as a faint line: the copy takes both from the original. A mesh keeps
    that flag apart from the one get_antialiased reports, and has no public
    accessor for it, so it is read from the instance.
    """
    image = pp.Image(text=False)
    image.display(bowl, x1=coord, x2=coord)
    original = _mesh(_axis(image))

    copy = _mesh(image.zoom(**WINDOW))

    assert vars(copy)["_antialiased"] == vars(original)["_antialiased"]
    assert copy.get_rasterized() == original.get_rasterized()


def test_the_copies_are_clipped_to_the_inset() -> None:
    """Check every copy is clipped to the inset, not to its parent.

    A copy clipped to the parent would paint the whole window it covers
    around the inset, over the parent's own drawing.
    """
    image = pp.Image(text=False)
    image.display(bowl, x1=coord, x2=coord)
    image.plot(coord, coord)

    axins = image.zoom(**WINDOW)

    for artist in [*axins.collections, *axins.lines]:
        box = artist.get_clip_box()
        assert box is not None
        npt.assert_allclose(box.bounds, axins.bbox.bounds)


def test_scatter_markers_keep_their_size() -> None:
    """Zoom into a scatter and check its markers.

    Their size is in points, so it stays: only their positions go through
    the data of the inset. Placing the markers themselves in data units
    would scale them with the zoom.
    """
    image = pp.Image(text=False)
    image.scatter(coord, coord, c=coord)
    original = _axis(image).collections[0]
    assert isinstance(original, PathCollection)

    axins = image.zoom(**WINDOW)

    copy = axins.collections[0]
    assert isinstance(copy, PathCollection)
    npt.assert_allclose(copy.get_sizes(), original.get_sizes())
    assert copy.get_transform() is not axins.transData
    npt.assert_allclose(
        np.asarray(copy.get_offsets()), np.asarray(original.get_offsets())
    )


def test_line_styles_are_copied() -> None:
    """Zoom into two styled curves, and check the palette is not used up.

    The copies take their style from the originals, so drawing them does
    not advance the palette of the inset either.
    """
    image = pp.Image(text=False)
    image.plot(x, y)
    image.plot(x, z, ls="--", marker="o", lw=2.5)
    originals = _axis(image).get_lines()

    axins = image.zoom()

    for original, copy in zip(originals, axins.get_lines(), strict=True):
        assert isinstance(copy, Line2D)
        assert copy.get_color() == original.get_color()
        assert copy.get_linestyle() == original.get_linestyle()
        assert copy.get_marker() == original.get_marker()
        assert copy.get_linewidth() == original.get_linewidth()
    assert image.nline[1] == 0


def test_an_unknown_kind_is_left_out() -> None:
    """Zoom into an axis with a band drawn by matplotlib directly.

    A kind of artist the copy does not know how to rebuild is skipped,
    rather than raising or being copied wrongly; the curve beside it is
    still copied.
    """
    image = pp.Image(text=False)
    image.plot(x, y)
    _axis(image).fill_between(x, y, z)

    axins = image.zoom()

    assert list(axins.collections) == []
    assert len(axins.get_lines()) == 1


def test_zoom_on_empty_axis() -> None:
    """Zoom into an empty axis: an empty inset, rather than an error."""
    image = pp.Image(text=False)
    image.create_axes()

    axins = image.zoom(xrange=[0.0, 1.0], yrange=[0.0, 1.0])

    assert axins.get_lines() == []
    assert list(axins.collections) == []


# ---- Restyling the map ----
def test_the_map_keywords_restyle_the_copy() -> None:
    """Give a colormap and limits without var.

    They restyle the map of the inset only: the parent keeps its own.
    """
    image = pp.Image(text=False)
    image.display(bowl, x1=coord, x2=coord)
    parent = _mesh(_axis(image))
    before = (parent.get_cmap().name, parent.get_clim())

    copy = _mesh(image.zoom(cmap="magma", vmin=0.2, vmax=0.8, **WINDOW))

    assert copy.get_cmap().name == "magma"
    npt.assert_allclose(copy.get_clim(), (0.2, 0.8))
    assert (parent.get_cmap().name, parent.get_clim()) == before


def test_a_new_scale_for_the_copy() -> None:
    """Give a logarithmic scale to the inset of a linear map."""
    image = pp.Image(text=False)
    image.display(bowl + 0.1, x1=coord, x2=coord)

    copy = _mesh(image.zoom(cscale="log", **WINDOW))

    assert type(copy.norm).__name__ == "LogNorm"


def test_a_colorbar_for_the_copy() -> None:
    """Give the copied map a colorbar of its own."""
    image = pp.Image(text=False)
    image.display(bowl, x1=coord, x2=coord)

    image.zoom(cpos="bottom", **WINDOW)

    assert image.fig is not None
    assert len(image.fig.axes) == 2


# ---- Another quantity ----
def test_var_takes_the_place_of_the_map() -> None:
    """Zoom with another quantity, over a map with contours and a curve.

    The inset draws the new quantity, with a scale and a colormap of its
    own, on the grid of the map, and the overlays are still copied on top.
    """
    image = pp.Image(text=False)
    image.display(bowl, x1=coord, x2=coord)
    image.contour(bowl, x1=coord, x2=coord, c="k")
    image.plot(coord, coord, c="r")

    axins = image.zoom(var=saddle, cmap="RdBu_r", vmin=-1.0, vmax=1.0, **WINDOW)

    mesh = _mesh(axins)
    npt.assert_allclose(np.asarray(mesh.get_array()), saddle.T)
    npt.assert_allclose(
        np.asarray(mesh.get_coordinates()),
        np.asarray(_mesh(_axis(image)).get_coordinates()),
    )
    assert mesh.get_cmap().name == "RdBu_r"
    npt.assert_allclose(mesh.get_clim(), (-1.0, 1.0))
    assert [type(c) for c in axins.collections] == [QuadMesh, PathCollection]
    assert len(axins.get_lines()) == 1


def test_var_with_a_colorbar_of_its_own() -> None:
    """Zoom with another quantity and a colorbar for it."""
    image = pp.Image(text=False)
    image.display(bowl, x1=coord, x2=coord, cpos="right")

    image.zoom(var=saddle, cpos="bottom", **WINDOW)

    assert image.fig is not None
    assert len(image.fig.axes) == 3


def test_var_on_a_gouraud_map() -> None:
    """Zoom with another quantity into a gouraud map.

    A gouraud map has a vertex on each border, holding the value of its
    cell, so the inset reaches the edges of the domain; the new quantity
    is given the same border and lies on exactly the same grid.
    """
    image = pp.Image(text=False)
    image.display(bowl, x1=coord, x2=coord, shading="gouraud")

    mesh = _mesh(image.zoom(var=saddle))

    npt.assert_allclose(
        np.asarray(mesh.get_coordinates()),
        np.asarray(_mesh(_axis(image)).get_coordinates()),
    )
    npt.assert_allclose(np.asarray(mesh.get_array())[1:-1, 1:-1], saddle.T)


def test_var_needs_a_grid() -> None:
    """Zoom with another quantity into an axis with no map on it."""
    image = pp.Image(text=False)
    image.plot(x, y)

    with pytest.raises(ValueError, match="needs a grid"):
        image.zoom(var=saddle)


@pytest.mark.parametrize(
    "zoom",
    [
        lambda i: i.zoom(var=saddle, x1=coord),
        lambda i: i.zoom(var=saddle, x2=coord),
    ],
    ids=["x1", "x2"],
)
def test_half_a_grid_is_refused(zoom: Callable[[pp.Image], Axes]) -> None:
    """Give only one of x1 and x2 with another quantity.

    The other would be completed from the grid of the map, which has
    another shape, and display failed on it with a confusing TypeError.
    """
    image = pp.Image(text=False)
    image.display(bowl, x1=coord, x2=coord)

    with pytest.raises(ValueError, match="must be given together"):
        zoom(image)


def test_var_on_a_grid_given() -> None:
    """Give the grid of the quantity explicitly, over an axis of curves."""
    image = pp.Image(text=False)
    image.plot(coord, coord)

    axins = image.zoom(var=saddle, x1=coord, x2=coord)

    assert [type(c) for c in axins.collections] == [QuadMesh]
    assert len(axins.get_lines()) == 1


# ---- The zoom lines ----
def _indicators(axis: Axes) -> list[InsetIndicator]:
    """Return the marks of the regions zoomed into on an axis."""
    return [c for c in axis.get_children() if isinstance(c, InsetIndicator)]


def test_the_zoom_is_indicated() -> None:
    """Check the region zoomed is marked on the parent, in the zoom color.

    The frame of the inset takes the same color, so the two read as one.
    """
    image = pp.Image(text=False)
    image.plot(x, y)

    axins = image.zoom(zoomcolor="r")

    (mark,) = _indicators(_axis(image))
    assert mark.rectangle.get_edgecolor()[:3] == (1.0, 0.0, 0.0)
    assert axins.spines["top"].get_edgecolor() == (1.0, 0.0, 0.0, 1.0)


def test_the_zoom_lines_can_be_left_out() -> None:
    """Zoom without marking the region on the parent."""
    image = pp.Image(text=False)
    image.plot(x, y)

    image.zoom(zoomlines=False)

    assert _indicators(_axis(image)) == []


def test_a_zoom_without_a_figure() -> None:
    """Zoom on an image whose figure is gone."""
    image = pp.Image(text=False)
    image.fig = None

    with pytest.raises(ValueError, match="No figure is present"):
        image.zoom()
