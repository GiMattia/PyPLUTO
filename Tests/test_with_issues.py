"""The known bugs, each written as the behaviour the code should have.

Every test here is marked `xfail(strict=True)`, so each run reports the bugs
that are still open, and the day one is fixed its test passes, strict mode
turns that into a failure, and whoever fixed it is told to remove the marker
and move the test into the file it belongs to.

Nothing here pins what the code does today. A test that asserts a wrong
result would go green, hide the bug from every run, and defend it against the
person who fixes it. The bugs are listed in the Open bugs table of
tests_recap.md; this file is the executable half of that table, so the two
are updated together.

Tests are grouped by the file the fault is in, and the reason on each marker
is one line saying what is wrong.
"""

import copy
import inspect
import pickle
import re
import shutil
import subprocess
import sys
import textwrap
import typing
import warnings
from collections.abc import Callable
from pathlib import Path

import numpy as np
import pytest
from helper_image import DELEGATION, DOCUMENTED_KWARGS
from helper_image import KWARGS as IMAGE_KWARGS

import pyPLUTO as pp
import pyPLUTO.image as image_mod
import pyPLUTO.imagekwargs as image_kwargs
from pyPLUTO.imagefuncs.imagetools import ImageToolsManager
from pyPLUTO.imagefuncs.range import RangeManager
from pyPLUTO.utils import inspector
from pyPLUTO.utils.inspector import track_kwargs


def _image() -> pp.Image:
    """Build a quiet image with one axis."""
    image = pp.Image(text=False)
    image.create_axes()
    return image


def _sample_for_scanning(_check: bool = True, **kwargs: object) -> object:
    """Read one keyword by name, for the scanner to find.

    Defined here rather than inside the test because the scan works from the
    source on disk, which a function built at runtime does not have.
    """
    return kwargs.get("real_key")


def _documented(function: object) -> set[str]:
    """Return the names listed in the Parameters section of a docstring."""
    doc = getattr(function, "__doc__", None) or ""
    if "Parameters" not in doc:
        return set()
    section = doc.split("Parameters")[1].split("Returns")[0]
    return set(re.findall(r"^\s*- (\w+)", section, re.MULTILINE))


# ---- load.py, loadpart.py, image.py ----
@pytest.mark.xfail(
    strict=True,
    reason="__getattr__ recurses on 'state', so the facades cannot be copied",
)
@pytest.mark.parametrize("operation", [copy.copy, copy.deepcopy])
def test_the_facades_can_be_copied(operation: object, data_dir: Path) -> None:
    """Copy an Image and expect a copy rather than a RecursionError.

    `copy` builds the new object without running `__init__` and then looks up
    `__setstate__`, which reaches `__getattr__`, which reads `self.state`,
    which calls `__getattr__` again. `Load` and `LoadPart` do the same.
    """
    assert callable(operation)
    assert operation(_image()) is not None


@pytest.mark.xfail(
    strict=True,
    reason="unpickling reaches __getattr__ before the state exists",
)
def test_a_load_survives_a_pickle_round_trip(data_dir: Path) -> None:
    """Send a Load through pickle, as multiprocessing does.

    Writing works; reading back raises RecursionError, so a Load cannot be
    handed to a worker process.
    """
    data = pp.Load(path=data_dir / "single_file", text=False)
    assert pickle.loads(pickle.dumps(data)) is not None


# ---- loadfuncs/ ----
@pytest.mark.xfail(
    strict=True,
    reason="passing the correct endian explicitly corrupts the data",
)
def test_explicit_endian_reads_the_same_data(data_dir: Path) -> None:
    """Load a standalone vtk with and without `endian`, and compare.

    The keyword names the byte order the file already has, so both calls must
    read the same number. With `endian` given, `binformat` loses its byte
    order and the value comes back as -1.49e+19 instead of 0.138.
    """
    path = data_dir / "single_file" / "vtk"
    given = pp.Load(
        path=path, datatype="vtk", alone=True, endian="big", text=False
    )
    default = pp.Load(path=path, datatype="vtk", alone=True, text=False)

    assert float(given.rho.flat[0]) == pytest.approx(float(default.rho.flat[0]))


@pytest.mark.xfail(
    strict=True, reason="alone=False is ignored: the probes run regardless"
)
def test_alone_false_is_honoured(data_dir: Path, tmp_path: Path) -> None:
    """Ask for a non-standalone load of a folder holding one vtk file.

    `check_format` builds the table that should gate the probes on `alone`
    and then never reads it, so the standalone file is found anyway and the
    user gets a load full of NaN timestamps instead of an error.
    """
    shutil.copy(data_dir / "single_file" / "data.0000.vtk", tmp_path)
    data = pp.Load(path=tmp_path, datatype="vtk", alone=False, text=False)
    assert data.state.alone is False


@pytest.mark.xfail(
    strict=True,
    reason="the deprecated vars= keyword is warned about, then dropped",
)
def test_deprecated_vars_keyword_still_selects(data_dir: Path) -> None:
    """Load with the deprecated `vars=` and check it chose the variable.

    The shim warns and never assigns, so every variable is loaded. Its
    sibling `nfile_lp` on LoadPart does forward its value.
    """
    with pytest.warns(
        DeprecationWarning, match="'vars' argument is deprecated"
    ):
        data = pp.Load(path=data_dir / "single_file", vars="rho", text=False)

    assert sorted(data.state.d_vars) == ["rho"]


@pytest.mark.xfail(
    strict=True,
    reason="codedict evaluates echomanager, which LoadPart never builds",
)
def test_loadpart_reports_an_unsupported_code(data_dir: Path) -> None:
    """Ask LoadPart for a code it does not support.

    The dictionary of codes is built eagerly and names a manager that exists
    only for Load, so every non-default `code` raises AttributeError and the
    intended NotImplementedError is unreachable.
    """
    with pytest.raises(NotImplementedError):
        pp.LoadPart(path=data_dir / "particles_cr", code="echo", text=False)


@pytest.mark.xfail(strict=True, reason="a tab load leaves d_vars empty")
def test_tab_load_lists_its_variables(data_dir: Path) -> None:
    """Load the tab format and check the variables are there.

    Nothing fills `d_vars`, so the GUI lists no variable for a tab dataset.
    """
    data = pp.Load(path=data_dir / "single_file", datatype="tab", text=False)
    assert sorted(data.state.d_vars)


@pytest.mark.xfail(
    strict=True, reason="the memory maps are never closed after the copy"
)
def test_a_load_closes_its_memory_maps(data_dir: Path) -> None:
    """Read a particle variable and check the mapping is released.

    `AttrResolver` copies the data into memory the state owns, after which
    the mapping is dead weight, but nothing closes it: the file handles live
    for the whole process, and the object cannot be pickled either.
    """
    data = pp.LoadPart(path=data_dir / "particles_cr", text=False)
    assert data.x1 is not None

    assert all(mapping.closed for mapping in data.state.mmaps)


@pytest.mark.xfail(
    strict=True, reason="LoadPart declares and accepts a keyword it cannot use"
)
def test_loadpart_does_not_accept_multiple(data_dir: Path) -> None:
    """Pass `multiple` to LoadPart and expect it to be refused.

    `multiple` means one file per variable, while particle output is split
    by chunk, so the keyword means nothing here. It is declared in
    `LoadPartKwargs`, accepted, and silently ignored -- not even reported as
    unused, so nothing tells the user their request had no effect.
    """
    with pytest.warns(UserWarning, match="multiple"):
        pp.LoadPart(path=data_dir / "particles_cr", multiple=True, text=False)


@pytest.mark.xfail(strict=True, reason="repr and str need fields no load set")
@pytest.mark.parametrize("show", [repr, str])
def test_a_load_that_read_nothing_can_be_printed(
    show: object, data_dir: Path
) -> None:
    """Print a load made with `nout=None`, which reads no output.

    `nout=None` is documented as "do not load", and a repr must never raise:
    it is what a debugger and an interactive prompt call by themselves.
    """
    with pytest.warns(UserWarning, match="No output is loaded"):
        data = pp.Load(path=data_dir / "single_file", nout=None, text=False)

    assert callable(show)
    assert show(data)


@pytest.mark.xfail(
    strict=True, reason="the dataclass __eq__ compares fields no load set"
)
def test_two_states_can_be_compared(data_dir: Path) -> None:
    """Compare two states and expect an answer rather than an exception.

    The generated `__eq__` reads the load-only fields, so a fresh state
    raises AttributeError and two real ones raise ValueError on the array
    comparison. `eq=False` would make it identity, which is at least usable.
    """
    first = pp.Load(path=data_dir / "single_file", text=False)
    second = pp.Load(path=data_dir / "single_file", text=False)

    assert isinstance(first.state == second.state, bool)


@pytest.mark.xfail(strict=True, reason="a named defh file is never read")
def test_defh_reads_the_named_file(data_dir: Path, tmp_path: Path) -> None:
    """Point `defh` at a file and check that file is the one read.

    The docstring says a string is used as the path to the header. The
    reader always looks for `definitions.h` in the folder instead, so the
    name is ignored and the wrong file wins.
    """
    for name, value in (("definitions.h", 1), ("mydefs.h", 2)):
        (tmp_path / name).write_text(f"#define A {value}\n")
    shutil.copy(data_dir / "single_file" / "data.0000.dbl", tmp_path)
    shutil.copy(data_dir / "single_file" / "dbl.out", tmp_path)
    shutil.copy(data_dir / "single_file" / "grid.out", tmp_path)

    data = pp.Load(path=tmp_path, datatype="dbl", defh="mydefs.h", text=False)

    assert data.defh == {"A": 2}


# ---- toolfuncs/ ----
@pytest.mark.xfail(strict=True, reason="fourier without dx raises KeyError")
def test_fourier_without_dx(data_dir: Path) -> None:
    """Take a Fourier transform without saying what the spacing is.

    The keyword is optional, so the grid spacing should be taken from the
    load rather than looked up blindly.
    """
    data = pp.Load(path=data_dir / "single_file", text=False)
    assert data.fourier(data.rho) is not None


@pytest.mark.xfail(
    strict=True,
    reason="state.figsize is not updated when the figure is resized",
)
def test_figsize_follows_the_figure() -> None:
    """Create two columns of axes, compare the reported size with the real one.

    `create_axes` resizes the figure without telling the state, so the
    property and the repr keep reporting the size the figure had before.
    """
    image = pp.Image(text=False)
    image.create_axes(ncol=2)
    assert image.fig is not None

    assert list(image.figsize) == pytest.approx(
        list(image.fig.get_size_inches())
    )


@pytest.mark.xfail(
    strict=True,
    reason="figure-only keywords are declared on every drawing method",
)
@pytest.mark.parametrize(
    "draw",
    [
        lambda image: image.plot([0.0, 1.0], [0.0, 1.0], withblack=True),
        lambda image: image.plot([0.0, 1.0], [0.0, 1.0], style="classic"),
        lambda image: image.plot([0.0, 1.0], [0.0, 1.0], nwin=2),
        lambda image: image.plot([0.0, 1.0], [0.0, 1.0], numcolors=4),
    ],
    ids=["withblack", "style", "nwin", "numcolors"],
)
def test_declared_keywords_are_usable(
    draw: Callable[[pp.Image], None],
) -> None:
    """Pass a keyword the type checkers accept on `plot` and check it is used.

    `CreateAxesKwargs` inherits the figure-level table, so these type-check
    on every drawing method and are then reported as unused at runtime: the
    mirror of a keyword read but not declared.
    """
    image = pp.Image(text=False)

    with warnings.catch_warnings(record=True) as raised:
        warnings.simplefilter("always")
        draw(image)

    assert [w for w in raised if "kwargs" in str(w.message)] == []


# ---- imagefuncs/set_axis.py ----
@pytest.mark.xfail(
    strict=True,
    reason="a single string as tick labels works but is declared nowhere",
)
@pytest.mark.parametrize("keyword", ["xtickslabels", "ytickslabels"])
def test_a_single_string_of_tick_labels_is_declared(keyword: str) -> None:
    """Check one string is in the declared type of the tick labels.

    `set_ticks` handles a lone string on purpose -- it labels the first tick
    and formats the rest with nothing, which is how a single annotated
    value is drawn -- while `SetAxisKwargs` declares `list[str] | bool |
    None`, so the call works and every checker refuses it.
    """
    declared = typing.get_type_hints(image_kwargs.SetAxisKwargs)[keyword]

    assert str in typing.get_args(declared)


@pytest.mark.xfail(
    strict=True, reason="tick_params is given the string 'off', which is truthy"
)
@pytest.mark.parametrize("axis", ["yaxis", "xaxis"], ids=["right", "top"])
def test_the_far_side_ticks_are_switched_off(axis: str) -> None:
    """Check the ticks on the far side are off, as the call asks for.

    `tick_params(right="off", top="off")` is written to switch them off, but
    matplotlib takes a bool there and stores the string: `get_visible()`
    returns `'off'`, which is truthy, so the ticks are drawn. Plain
    matplotlib leaves them at False.

    The string form was accepted by matplotlib years ago and removed since,
    so this is a call that no longer means what it did.
    """
    image = pp.Image(text=False)
    image.plot([0.0, 1.0], [0.0, 1.0])

    tick = getattr(image.ax[0], axis).get_major_ticks()[0].tick2line

    assert tick.get_visible() is False


@pytest.mark.xfail(
    strict=True, reason="the labels are applied after the call warns against it"
)
def test_labels_on_automatic_ticks_are_not_applied() -> None:
    """Give tick labels while the ticks are left automatic.

    `set_ticks` warns that labels should be fixed only when the ticks are,
    and then sets the formatter regardless, so matplotlib warns in turn --
    "FixedFormatter should only be used together with FixedLocator" -- and
    the labels stay pinned to ticks that move with the data.

    Either the warning is right and the labels are dropped, or they are
    accepted and the warning goes; doing both is what makes two warnings
    and a wrong axis.
    """
    image = pp.Image(text=False)
    image.create_axes()

    with warnings.catch_warnings(record=True) as raised:
        warnings.simplefilter("always")
        image.set_axis(xtickslabels=["a", "b"])

    assert not [w for w in raised if "FixedFormatter" in str(w.message)]


@pytest.mark.xfail(
    strict=True, reason="alpha is set on the Axes, which draws nothing"
)
def test_alpha_reaches_something_that_is_drawn() -> None:
    """Set the transparency and check something drawn actually carries it.

    `set_axis(alpha=...)` calls `ax.set_alpha()`, which stores the value on
    the Axes artist; the background patch and the lines keep their own
    alpha, so the figure looks exactly the same. Whatever the keyword is
    meant to fade -- the patch, or everything on the axis -- has to be told.
    """
    image = pp.Image(text=False)
    image.plot([0.0, 1.0], [0.0, 1.0])

    image.set_axis(alpha=0.3)

    assert image.ax[0].patch.get_alpha() == 0.3


# ---- imagefuncs/create_axes.py ----
@pytest.mark.xfail(
    strict=True, reason="False is an int, so it is read as the index 0"
)
def test_sharing_can_be_switched_off() -> None:
    """Create axes with the sharing the docstring gives as the default.

    `sharexaxes` is documented as `bool | ..., default False`, and passing
    that default raises IndexError: `isinstance(False, int)` is true, so it
    is taken for the index 0 and the first axis is looked up in a list that
    is still empty.
    """
    image = pp.Image(text=False)
    image.create_axes(ncol=2, sharexaxes=False)

    assert len(image.ax) == 2
    assert not image.ax[0].get_shared_x_axes().joined(image.ax[0], image.ax[1])


@pytest.mark.xfail(
    strict=True, reason="sharing by axis index works but is declared nowhere"
)
@pytest.mark.parametrize("keyword", ["sharexaxes", "shareyaxes"])
def test_sharing_by_index_is_declared(keyword: str) -> None:
    """Check the index form of the sharing keywords is in the declared type.

    `_check_shareaxis` handles an int on purpose -- it is how a set of axes
    is tied to one created earlier, and `test_sharing_with_an_axis_created_
    earlier` relies on it -- while `CreateAxesKwargs` offers only
    `bool | str | Axes`, so every checker refuses the call that works.
    """
    declared = typing.get_type_hints(image_kwargs.CreateAxesKwargs)[keyword]

    assert int in typing.get_args(declared)


@pytest.mark.xfail(
    strict=True, reason="a custom layout overwrites the tight given with it"
)
def test_a_custom_layout_keeps_an_explicit_tight() -> None:
    """Ask for a custom layout and a tight one at the same time.

    A custom layout sets `tight` to False, because matplotlib cannot lay out
    axes it did not place -- but it does so by writing into the keywords
    before they are read, so it overrides the user rather than defaulting.
    """
    image = pp.Image(text=False)
    image.create_axes(ncol=2, left=0.2, tight=True)

    assert image.tight is True


@pytest.mark.xfail(
    strict=True, reason="create_axes sets rcParams but not state.fontsize"
)
def test_a_fontsize_given_to_create_axes_is_recorded() -> None:
    """Give create_axes a fontsize and read it back off the image.

    It reaches matplotlib -- `rcParams["font.size"]` becomes 13 -- but the
    state keeps 17, so `image.fontsize` reports one size while the figure
    is drawn at another, and everything reading the state (the legend, the
    text box, the axis labels) uses the stale one.

    The old test passed `fontsize=17`, the value already there, so it could
    not fail.
    """
    image = pp.Image(text=False)
    image.create_axes(fontsize=13)

    assert image.fontsize == 13


@pytest.mark.xfail(
    strict=True, reason="create_axes sets figsize without recording set_size"
)
def test_a_size_given_to_create_axes_is_kept() -> None:
    """Give create_axes a size, then create more axes, and check it survives.

    `set_size` is what marks a size as chosen by the user rather than
    computed. The constructor sets it and create_axes does not, so the next
    call recomputes the size and the figure silently goes back to 6x5 while
    the state still reports what was asked for.
    """
    image = pp.Image(text=False)
    image.create_axes(figsize=[10.0, 4.0])
    image.create_axes()

    assert image.fig is not None
    assert list(image.fig.get_size_inches()) == [10.0, 4.0]


# ---- imagefuncs/imagetools.py ----
@pytest.mark.xfail(
    strict=True,
    reason="an out-of-range index raises IndexError, not ValueError",
)
def test_assign_ax_rejects_an_index_out_of_range() -> None:
    """Ask for an axis number the figure does not have.

    The docstring and the neighbouring branch promise "The provided axis is
    not valid", but the list lookup raises IndexError first.
    """
    image = _image()
    manager = ImageToolsManager(image.state)

    with pytest.raises(ValueError, match="not valid"):
        manager.assign_ax(5, _check=False)


@pytest.mark.xfail(
    strict=True, reason="assign_ax forces ncol and nrow to 1 on an empty figure"
)
def test_plot_on_an_empty_figure_honours_ncol() -> None:
    """Plot with `ncol=2` on a figure with no axes yet.

    `assign_ax` overwrites both keywords before creating the axes, and they
    still count as consumed, so the user gets one axis and no warning.
    """
    image = pp.Image(text=False)
    image.plot([0.0, 1.0], [0.0, 1.0], ncol=2)
    assert len(image.ax) == 2


# ---- imagefuncs/range.py ----
@pytest.mark.xfail(
    strict=True,
    reason="the y-window filter compares x with its own min and max",
)
def test_y_limits_come_from_the_visible_window() -> None:
    """Compute y-limits with a point far outside the x-range.

    The filter is meant to keep the points inside the x-window, but it
    compares `x` with its own minimum and maximum, which is true everywhere,
    so the far point sets the upper limit of the y-axis.
    """
    image = _image()
    manager = RangeManager(image.state)
    image.ax[0].set_xlim(0.0, 1.0)
    far_x = np.array([0.0, 0.5, 100.0])
    far_y = np.array([1.0, 2.0, 50.0])

    manager.set_yrange(
        image.ax[0], 0, [0.0, 0.0], manager.changerange, data=(far_x, far_y)
    )

    assert image.ax[0].get_ylim()[1] < 50.0


@pytest.mark.xfail(
    strict=True, reason="ymax is recomputed from the already-reassigned ymin"
)
def test_negative_log_range_keeps_its_widest_value() -> None:
    """Fold a range crossing zero onto a logarithmic scale.

    Both limits should be read from the original values, so (-100, 10) gives
    a range reaching 100. `ymin` is reassigned first and `ymax` is then
    computed from it, so the 100 is lost and the result is (5, 21).
    """
    image = _image()
    manager = RangeManager(image.state)

    with pytest.warns(UserWarning, match="Negative range"):
        _, ymax = manager.range_offset(-100.0, 10.0, "log")

    assert ymax >= 100.0


# ---- imagefuncs/interactive.py ----
@pytest.mark.xfail(
    strict=True, reason="the documented lint keyword is read nowhere"
)
def test_documented_lint_keyword_is_accepted() -> None:
    """Pass the `lint` keyword the docstring documents.

    It promises linear interpolation between frames. Nothing reads it, so
    the documentation itself produces an "Unused kwargs" warning.
    """
    grid = np.linspace(0.0, 1.0, 8)
    image = pp.Image(text=False)

    with warnings.catch_warnings(record=True) as raised:
        warnings.simplefilter("always")
        image.interactive({0: grid, 1: grid * 2}, lint=True)  # type: ignore[call-arg]

    assert [w for w in raised if "kwargs" in str(w.message)] == []


# ---- imagefuncs/contour.py, streamplot.py ----
@pytest.mark.xfail(
    strict=True, reason="colors is read as a presence test and never applied"
)
@pytest.mark.parametrize(
    "draw",
    [
        lambda image, var, grid: image.contour(
            var, x1=grid, x2=grid, colors="red"
        ),
        lambda image, var, grid: image.streamplot(
            var, var, x1=grid, x2=grid, colors="red"
        ),
    ],
    ids=["contour", "streamplot"],
)
def test_colors_keyword_is_applied(draw: Callable[..., object]) -> None:
    """Draw with `colors` and check the drawing really is that colour.

    `colors` is only tested for presence, to warn when it is given together
    with `cmap`; the value applied comes from `c`. So `colors="red"` is
    accepted, warns about nothing, and changes nothing -- the colormap stays
    viridis. Either it applies, or it should not be silently swallowed.
    """
    grid = np.linspace(0.0, 1.0, 8)
    mesh = np.outer(grid, grid)
    drawn = draw(pp.Image(text=False), mesh, grid)

    assert getattr(drawn, "colors", None) == "red"


# ---- imagekwargs.py ----
# The methods already written up are guarded by test_imagekwargs.py; the rest
# are expected failures here until their manager is reviewed.
UNDOCUMENTED = [
    (method, table)
    for method, table in IMAGE_KWARGS.items()
    if method not in DOCUMENTED_KWARGS
]


@pytest.mark.xfail(strict=True, reason="declared keywords are undocumented")
@pytest.mark.parametrize(("method", "table"), UNDOCUMENTED)
def test_every_declared_keyword_is_documented(method: str, table: str) -> None:
    """Check one method documents every keyword its table declares.

    The keywords are the whole interface of these methods, and an
    undocumented one is unreachable in practice: nothing tells the user it
    exists. The figure-level keywords are excluded, being documented on
    `Image.__init__` instead.
    """
    function = inspect.unwrap(
        getattr(getattr(image_mod, DELEGATION[method]), method)
    )
    documented = _documented(function)
    declared = set(typing.get_type_hints(getattr(image_kwargs, table)))
    figure_level = set(typing.get_type_hints(image_kwargs.FigureKwargs))

    assert not declared - documented - figure_level


# ---- utils/configure.py ----
@pytest.mark.xfail(
    strict=True,
    reason="simplefilter('always') at import resets the user's filters",
)
def test_importing_pypluto_keeps_the_warning_filters() -> None:
    """Silence warnings, import pyPLUTO, and check they stay silent.

    `Configure` calls `simplefilter("always")` while the package imports,
    which clears the whole filter list, so `-W ignore` and any
    `filterwarnings` call made beforehand stop working process-wide. A
    subprocess, because the import happens once per process.
    """
    script = (
        "import warnings; warnings.filterwarnings('ignore');"
        "import pyPLUTO; warnings.warn('should be silent')"
    )
    result = subprocess.run(
        [sys.executable, "-W", "ignore", "-c", script],
        capture_output=True,
        text=True,
        check=False,
    )

    assert "should be silent" not in result.stderr


# ---- imagefuncs/imagetools.py, range.py ----
@pytest.mark.xfail(
    strict=True, reason="the documented spelling is not one of the keys"
)
def test_text_accepts_the_documented_xycoords() -> None:
    """Place a text with the coordinate system the docstring documents.

    `text` documents `xycoords='figure fraction'` and the lookup knows
    'fraction', 'points' and 'figure', so the documented spelling raises a
    bare KeyError naming nothing useful.
    """
    image = _image()
    image.text(text="hi", x=0.5, y=0.5, xycoords="figure fraction")

    assert image.ax[0].texts


# ---- utils/inspector.py ----
@pytest.mark.xfail(
    strict=True, reason="the decorator mutates the cached scan in place"
)
def test_the_scan_cache_is_not_written_into() -> None:
    """Decorate a function with extra keys, then scan its source again.

    `_find_kwargs_keys_from_source` is cached and hands back a mutable set,
    and `track_kwargs` does `used_keys |= extra_keys` on it, so the extra
    keys are written back into the cache: scanning an untouched source then
    reports keys that do not appear in it. Two functions with the same
    source text share the entry, and any caller can poison it.

    Asserting on the scan of an unrelated source is the visible half; the
    cause is the in-place union, which a non-mutating one would fix.
    """
    source = textwrap.dedent(inspect.getsource(_sample_for_scanning))
    before = set(inspector.find_kwargs_keys(_sample_for_scanning))

    track_kwargs(extra_keys={"injected"})(_sample_for_scanning)

    assert set(inspector._find_kwargs_keys_from_source(source)) == before


@pytest.mark.xfail(
    strict=True,
    reason="stacklevel counts from the wrapper, not the user's frame",
)
def test_unused_kwargs_warning_points_at_the_caller() -> None:
    """Misspell a keyword and check the warning names the user's own file.

    It names `image.py` instead, because the outermost tracked call is the
    manager method the facade invokes, one frame further in than
    `stacklevel=2` reaches.
    """
    image = pp.Image(text=False)

    with warnings.catch_warnings(record=True) as raised:
        warnings.simplefilter("always")
        image.plot([0.0, 1.0], [0.0, 1.0], nosuchkeyword=1)  # type: ignore[call-arg]

    unused = [w for w in raised if "kwargs" in str(w.message)]
    assert unused
    assert Path(unused[0].filename).name == Path(__file__).name


# ---- load.py, loadpart.py docstrings ----
@pytest.mark.xfail(
    strict=True,
    reason="the class docstrings show keywords that warn or do not exist",
)
@pytest.mark.parametrize(
    ("cls", "keyword"),
    [
        (pp.Load, "vars="),
        (pp.Load, "data="),
        (pp.LoadPart, "vars="),
        (pp.LoadPart, "nfile_lp="),
    ],
)
def test_docstring_examples_use_real_keywords(cls: type, keyword: str) -> None:
    """Check an example in the documentation does not use a dead keyword.

    `vars=` and `nfile_lp=` are deprecated and warn, and `data=` is not a
    keyword at all -- it is `datatype`. A user copying the example gets a
    warning from the documentation.
    """
    source = inspect.getdoc(cls) or ""
    source += inspect.getdoc(cls.__init__) or ""
    assert keyword not in source
