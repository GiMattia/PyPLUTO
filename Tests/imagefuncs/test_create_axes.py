"""Test of the create_axes.py file.

Everything a user sees sits on the axes this file creates, so the tests are
about geometry: how many axes, where each one is, and what the figure carries
afterwards. The positions are written out by hand from the arithmetic in the
docstring -- a plot laid out wrongly looks plausible, so an inequality would
not be enough.

There are two layouts, and they are computed in different places. Without any
of the border keywords the axes come from `add_subplot` and matplotlib places
them; with any of `left`, `right`, `top`, `bottom`, `hspace`, `wspace`,
`hratio` or `wratio` the manager computes every box itself and calls
`set_position`, and it turns the tight layout off because matplotlib cannot
lay out axes it did not place.

Unlike in test_figure.py, `fig.get_tight_layout()` is meaningful here:
create_axes installs matplotlib's layout engine, while the figure manager
only calls `tight_layout()` once. So it answers True after a tight
create_axes and False after a custom layout.
"""

import typing
from collections.abc import Callable
from typing import Literal

import matplotlib.pyplot as plt
import numpy as np
import pytest
from matplotlib.axes import Axes

import pyPLUTO as pp
import pyPLUTO.imagekwargs as image_kwargs

# The per-axis lists in the state, one entry appended for every axis created.
# They are kept in step only by the loop in add_ax, so a new one added there
# and forgotten here is exactly what this table is for.
PER_AXIS_FIELDS = [
    "legpar",
    "legpos",
    "nline",
    "ntext",
    "setax",
    "setay",
    "shade",
    "tickspar",
    "vlims",
    "xscale",
    "yscale",
]


def _image() -> pp.Image:
    """Build a quiet image, without axes."""
    return pp.Image(text=False)


# ---- The grid ----
def test_one_axis_by_default() -> None:
    """Create axes with no keywords and check the grid is a single cell.

    The simplest call, and the one every plot makes for itself when the user
    has not created axes: one axis in a 1x1 grid.
    """
    image = _image()
    image.create_axes()

    assert image.fig is not None
    spec = image.fig.axes[0].get_subplotspec()
    assert spec is not None
    assert spec.get_gridspec().get_geometry() == (1, 1)


def test_rows_and_columns() -> None:
    """Ask for a grid and check both the geometry and the number of axes.

    The two can disagree: the grid is what matplotlib is told, the list is
    what pyPLUTO keeps, and a plot drawn by index would go to the wrong
    place if they did.
    """
    image = _image()
    axes = image.create_axes(ncol=2, nrow=3)

    assert isinstance(axes, list)
    assert len(axes) == 6
    assert image.fig is not None
    spec = image.fig.axes[0].get_subplotspec()
    assert spec is not None
    assert spec.get_gridspec().get_geometry() == (3, 2)


def test_a_single_axis_is_returned_alone() -> None:
    """Check one axis comes back as itself and several as a list.

    What lets `ax = I.create_axes()` be used directly while
    `ax = I.create_axes(ncol=2)` is indexed. A list of one would make the
    first form fail in the user's next line.
    """
    image = _image()

    assert not isinstance(image.create_axes(), list)
    assert isinstance(image.create_axes(ncol=2), list)


def test_the_grid_grows_with_every_call() -> None:
    """Create axes twice and check the recorded grid counts both.

    `nrow0` and `ncol0` are what `__str__` reports as the number of
    subplots, and what the next call adds its own grid to.
    """
    image = _image()
    image.create_axes(ncol=2, nrow=3)
    image.create_axes(ncol=1, nrow=1)

    assert (image.nrow0, image.ncol0) == (4, 3)


# ---- The custom layout ----
def test_the_borders_place_the_axis() -> None:
    """Give all four borders and check the axis fills exactly that box.

    The box is (left, bottom, width, height), so the width is right - left
    and the height is top - bottom: 0.8 - 0.2 and 0.85 - 0.05.
    """
    image = _image()
    image.create_axes(left=0.2, right=0.8, top=0.85, bottom=0.05)

    assert image.fig is not None
    assert image.fig.get_tight_layout() is False
    box = image.fig.axes[0].get_position().bounds
    assert np.isclose(box[0], 0.2)
    assert np.isclose(box[1], 0.05)
    assert np.isclose(box[2], 0.6)
    assert np.isclose(box[3], 0.8)


def test_two_columns_with_a_ratio() -> None:
    """Split the width between two columns with a ratio and a gap.

    The usable width is 0.8 - 0.15 - 0.2 = 0.45, split 2:1, so the first
    column is 0.3 wide and the second 0.15, which starts at
    0.15 + 0.3 + 0.2 = 0.65.
    """
    image = _image()
    axes = image.create_axes(
        ncol=2, left=0.15, right=0.8, wspace=0.2, wratio=[2, 1]
    )

    assert isinstance(axes, list)
    assert np.isclose(axes[0].get_position().bounds[0], 0.15)
    assert np.isclose(axes[0].get_position().bounds[2], 0.3)
    assert np.isclose(axes[1].get_position().bounds[0], 0.65)
    assert np.isclose(axes[1].get_position().bounds[2], 0.15)


def test_three_rows_with_ratios_and_spaces() -> None:
    """Stack three rows with their own heights and gaps.

    The usable height is 0.9 - 0.1 - 0.3 = 0.5, split 1:2:1, so the rows are
    0.125, 0.25 and 0.125 tall, counted downwards from the top.
    """
    image = _image()
    axes = image.create_axes(
        ncol=1, nrow=3, hspace=[0.2, 0.1], hratio=[1, 2, 1]
    )

    assert isinstance(axes, list)
    assert np.isclose(axes[0].get_position().bounds[1], 0.775)
    assert np.isclose(axes[0].get_position().bounds[3], 0.125)
    assert np.isclose(axes[1].get_position().bounds[1], 0.325)
    assert np.isclose(axes[1].get_position().bounds[3], 0.25)
    assert np.isclose(axes[2].get_position().bounds[1], 0.1)
    assert np.isclose(axes[2].get_position().bounds[3], 0.125)


def test_a_custom_grid_of_rows_and_columns() -> None:
    """Give two borders of a 2x3 grid and check the corners land on them.

    The first axis starts at the left border and the last one sits on the
    bottom: the loop fills the grid row by row.
    """
    image = _image()
    axes = image.create_axes(ncol=2, nrow=3, left=0.05, bottom=0.05)

    assert isinstance(axes, list)
    assert np.isclose(axes[0].get_position().bounds[0], 0.05)
    assert np.isclose(axes[-1].get_position().bounds[1], 0.05)


def test_a_single_space_is_used_between_every_column() -> None:
    """Give one number for the spacing rather than a list.

    A single float means the same gap everywhere, which is what a user
    writes for a regular grid; a list is for gaps that differ.
    """
    image = _image()
    axes = image.create_axes(ncol=3, left=0.1, right=0.9, wspace=0.1)

    assert isinstance(axes, list)
    # 0.8 of width, less two gaps of 0.1, split evenly: 0.2 each.
    assert np.isclose(axes[0].get_position().bounds[2], 0.2)
    assert np.isclose(axes[1].get_position().bounds[0], 0.4)
    assert np.isclose(axes[2].get_position().bounds[0], 0.7)


def test_a_second_set_of_axes_beside_the_first() -> None:
    """Place two sets of axes side by side with their own borders.

    The documented way to build an irregular layout: each call positions its
    own axes, and the second returns every axis the image now has.
    """
    image = _image()
    image.create_axes(left=0.2, right=0.5)
    axes = image.create_axes(left=0.6, right=0.85)

    assert isinstance(axes, list)
    assert len(axes) == 2
    assert np.isclose(axes[0].get_position().bounds[0], 0.2)
    assert np.isclose(axes[0].get_position().bounds[2], 0.3)
    assert np.isclose(axes[1].get_position().bounds[0], 0.6)
    assert np.isclose(axes[1].get_position().bounds[2], 0.25)


# ---- Sharing ----
def test_sharing_with_the_first_axis() -> None:
    """Share both axes across a column and check they are joined.

    `True` means "share with the first axis of this set", so panels above
    one another keep the same x range while they are panned or zoomed.
    """
    image = _image()
    axes = image.create_axes(ncol=1, nrow=2, sharexaxes=True, shareyaxes=True)

    assert isinstance(axes, list)
    assert axes[0].get_shared_x_axes().joined(axes[0], axes[1])
    assert axes[0].get_shared_y_axes().joined(axes[0], axes[1])


def test_sharing_with_an_axis_created_earlier() -> None:
    """Share with an axis by its index, across two calls.

    An index refers to the image's own list of axes, so a set created later
    can be tied to one created before it.
    """
    image = _image()
    image.create_axes(ncol=1, nrow=2)
    axes = image.create_axes(ncol=1, nrow=2, sharexaxes=0)

    assert isinstance(axes, list)
    assert axes[0].get_shared_x_axes().joined(axes[0], axes[2])


def test_sharing_with_an_axis_given() -> None:
    """Share with an axis passed as itself, not by its index."""
    image = _image()
    first = image.create_axes()
    assert isinstance(first, Axes)

    axes = image.create_axes(ncol=2, sharexaxes=first)

    assert isinstance(axes, list)
    assert first.get_shared_x_axes().joined(first, axes[1])
    assert first.get_shared_x_axes().joined(first, axes[2])


def test_sharing_with_an_axis_of_the_same_call() -> None:
    """Share with the second axis of the set being created, by its index.

    The axes share once they all exist, so an index can point at one made
    later in the same call; sharing at creation raised IndexError, since
    the axis pointed at did not exist yet.
    """
    image = _image()
    axes = image.create_axes(ncol=3, sharexaxes=1)

    assert isinstance(axes, list)
    assert axes[1].get_shared_x_axes().joined(axes[0], axes[1])
    assert axes[1].get_shared_x_axes().joined(axes[1], axes[2])


@pytest.mark.parametrize("share", ["sharexaxes", "shareyaxes"])
def test_sharing_by_index_is_declared(share: str) -> None:
    """Check the index form of the sharing keywords is in the declared type.

    It is how a set of axes is tied to one created earlier, and every
    checker refused the call that worked: `CreateAxesKwargs` offered only
    `bool | str | Axes`.
    """
    declared = typing.get_type_hints(image_kwargs.CreateAxesKwargs)[share]

    assert int in typing.get_args(declared)


def test_sharing_can_be_switched_off() -> None:
    """Create axes with the sharing the docstring gives as the default.

    False used to raise IndexError: `isinstance(False, int)` is true, so it
    was taken for the index 0 and looked up in a list still empty. False
    and None are tested first now, and share nothing.
    """
    image = _image()
    axes = image.create_axes(ncol=2, sharexaxes=False)

    assert isinstance(axes, list)
    assert not axes[0].get_shared_x_axes().joined(axes[0], axes[1])


@pytest.mark.parametrize(
    ("share", "joined", "apart"),
    [
        ("all", [(0, 1), (0, 2), (0, 3)], []),
        ("row", [(0, 1), (2, 3)], [(0, 2), (1, 3)]),
        ("col", [(0, 2), (1, 3)], [(0, 1), (2, 3)]),
    ],
)
def test_sharing_by_row_or_column(
    share: Literal["all", "row", "col"],
    joined: list[tuple[int, int]],
    apart: list[tuple[int, int]],
) -> None:
    """Share within each row, within each column, or across the whole grid.

    As in matplotlib's subplots, 'row' ties each axis to the first of its
    row and 'col' to the first of its column, on a 2 x 2 grid laid out row
    by row; 'all' is the same as True.
    """
    image = _image()
    axes = image.create_axes(ncol=2, nrow=2, sharexaxes=share)

    assert isinstance(axes, list)
    shared = axes[0].get_shared_x_axes()
    for first, second in joined:
        assert shared.joined(axes[first], axes[second])
    for first, second in apart:
        assert not shared.joined(axes[first], axes[second])


def test_an_unknown_sharing_is_refused() -> None:
    """Ask for a sharing that has no meaning.

    Any string used to reach matplotlib, which refused it with "'other'
    must be an instance of _AxesBase"; the error now names the choices.
    """
    image = _image()

    with pytest.raises(ValueError, match="Unknown sharing 'diag'"):
        image.create_axes(ncol=2, sharexaxes="diag")  # pyright: ignore[reportArgumentType]  # ty: ignore[invalid-argument-type]


# ---- The figure around the axes ----
def test_the_suptitle_and_the_layout() -> None:
    """Give a title over the grid and switch the tight layout off.

    Both are figure-wide rather than per-axis. `get_tight_layout()` answers
    here because create_axes installs the layout engine.
    """
    image = _image()
    image.create_axes(ncol=2, nrow=3, suptitle="this is title", tight=False)

    assert image.fig is not None
    assert image.fig.get_suptitle() == "this is title"
    assert image.fig.get_tight_layout() is False


def test_the_tight_layout_is_the_default() -> None:
    """Create axes without saying anything about the layout.

    The counterpart of the test above: the engine is installed unless it is
    refused, which is what keeps labels from being cut off.
    """
    image = _image()
    image.create_axes(ncol=2)

    assert image.fig is not None
    assert image.fig.get_tight_layout() is True


def test_a_custom_layout_is_never_tight() -> None:
    """Place the axes by hand without saying anything about the layout.

    A tight layout moves the axes, which would undo the borders given, so
    a custom layout switches it off.
    """
    image = _image()
    image.create_axes(ncol=2, left=0.2)

    assert image.tight is False


def test_a_custom_layout_refuses_an_explicit_tight() -> None:
    """Ask for a custom layout and a tight one at the same time.

    The two cannot both hold: the layout given wins, and the tight asked
    for with it is refused with a warning instead of being dropped
    without a word, as it was before.
    """
    image = _image()

    with pytest.warns(UserWarning, match="custom layout cannot be tight"):
        image.create_axes(ncol=2, left=0.2, tight=True)

    assert image.tight is False


def test_the_size_and_the_title_can_be_changed_afterwards() -> None:
    """Build an image with a size and a title, then change both.

    create_axes takes the same keywords as the constructor, so a script can
    set up the figure and then lay it out in one call.
    """
    image = pp.Image(suptitle="This is a title", figsize=[6, 7], text=False)

    assert image.fig is not None
    assert image.fig.get_suptitle() == "This is a title"
    assert image.fig.get_figwidth() == 6
    assert image.fig.get_figheight() == 7

    image.create_axes(suptitle="This is another title", figsize=[5, 8])

    assert image.fig.get_suptitle() == "This is another title"
    assert image.fig.get_figwidth() == 5
    assert image.fig.get_figheight() == 8


def test_the_automatic_size_grows_with_the_grid() -> None:
    """Create a wider grid and check the figure grows to hold it.

    Without a size of its own the figure is sized from the grid,
    6*sqrt(ncol) by 5*sqrt(nrow), so the panels keep their proportions
    instead of being squeezed.
    """
    image = _image()
    image.create_axes(ncol=4, nrow=1)

    assert image.fig is not None
    assert image.fig.get_figwidth() == pytest.approx(12.0)
    assert image.fig.get_figheight() == pytest.approx(5.0)


def test_a_size_given_to_create_axes_is_kept() -> None:
    """Give create_axes a size, then create more axes, and check it survives.

    `set_size` is what marks a size as chosen by the user rather than
    computed. The constructor set it and create_axes did not, so the next
    call recomputed the size and the figure went back to 6x5 while the
    state still reported what was asked for.
    """
    image = _image()
    image.create_axes(figsize=[10.0, 4.0])
    image.create_axes()

    assert image.fig is not None
    assert list(image.fig.get_size_inches()) == [10.0, 4.0]


def test_the_fontsize_reaches_matplotlib() -> None:
    """Give a fontsize to create_axes and check matplotlib is set to it.

    It is written straight into the global parameters, so everything drawn
    afterwards uses it.
    """
    image = _image()
    image.create_axes(fontsize=13)

    assert plt.rcParams["font.size"] == 13


def test_the_fontsize_given_to_create_axes_is_recorded() -> None:
    """Give create_axes a fontsize and read it back off the image.

    It reached matplotlib but not the state, which kept 17: the image
    reported one size while the figure was drawn at another, and the
    legend, the text box and the labels, which read the state, used the
    stale one.
    """
    image = _image()
    image.create_axes(fontsize=13)

    assert image.fontsize == 13


def test_a_projection_is_passed_on() -> None:
    """Ask for a 3D projection and check the axis really has one.

    The keyword goes straight to `add_subplot`, and a 3D axis has a `zaxis`
    that a plain one does not -- which is what `volume` needs.
    """
    image = _image()
    image.create_axes(proj="3d")

    assert hasattr(image.ax[0], "zaxis")


# ---- Per-axis bookkeeping ----
@pytest.mark.parametrize("field", PER_AXIS_FIELDS)
def test_every_per_axis_list_grows_with_the_axes(field: str) -> None:
    """Create three axes and check one per-axis list has three entries.

    Eleven lists are kept in step by hand in add_ax, and everything later
    indexes them by axis number: a list left short raises IndexError from
    somewhere unrelated, and one left long silently describes an axis that
    does not exist.
    """
    image = _image()
    image.create_axes(ncol=3)

    assert len(getattr(image, field)) == 3


def test_the_per_axis_defaults_are_independent() -> None:
    """Change a per-axis entry and check the others are untouched.

    The defaults are copied rather than shared, since several of them are
    lists: without the copy, two axes would hold the same object and a
    legend on one would appear on the other.
    """
    image = _image()
    image.create_axes(ncol=2)

    image.legpar[0][0] = 99

    assert image.legpar[1][0] != 99


def test_each_axis_is_numbered_on_the_plot() -> None:
    """Check every axis carries its own index, written in its middle.

    It is what tells a user which number to pass as `ax=`, and the first
    plot on that axis hides it again.
    """
    image = _image()
    image.create_axes(ncol=2)

    assert [text.get_text() for text in image.ax[0].texts] == ["0"]
    assert [text.get_text() for text in image.ax[1].texts] == ["1"]


# ---- Refusals and warnings ----
def test_axes_need_a_figure() -> None:
    """Ask for axes on an image whose figure was taken away.

    Everything here draws on the figure, so the message says what is
    missing rather than failing on a None three lines later.
    """
    image = _image()
    image.fig = None

    with pytest.raises(
        ValueError, match="create a figure before creating axes"
    ):
        image.create_axes()


@pytest.mark.parametrize(
    ("create", "wrong"),
    [
        (
            lambda image: image.create_axes(ncol=2, nrow=2, wratio=[1, 2, 3]),
            "wratio",
        ),
        (
            lambda image: image.create_axes(ncol=2, nrow=4, wspace=[0.5, 0.2]),
            "wspace",
        ),
    ],
    ids=["too many ratios", "too few spaces"],
)
def test_a_wrong_number_of_ratios_or_spaces_warns(
    create: Callable[[pp.Image], object], wrong: str
) -> None:
    """Give more ratios than columns, or too few spaces, and expect a warning.

    The layout is still drawn -- the excess is dropped and the gaps are
    filled with 0.1 -- so without the warning a user would see a plausible
    figure that is not the one they described.
    """
    image = _image()

    with pytest.warns(UserWarning, match=f"{wrong} has wrong length!"):
        create(image)
