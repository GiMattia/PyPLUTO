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
import typing
import warnings
from collections.abc import Callable
from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np
import pytest
from helper_image import DELEGATION, DOCUMENTED_KWARGS
from helper_image import KWARGS as IMAGE_KWARGS
from matplotlib.figure import Figure

import pyPLUTO as pp
import pyPLUTO.image as image_mod
import pyPLUTO.imagekwargs as image_kwargs
from pyPLUTO.imagefuncs.colorbar import ColorbarManager
from pyPLUTO.imagefuncs.imagetools import ImageToolsManager
from pyPLUTO.imagefuncs.range import RangeManager
from pyPLUTO.imagefuncs.set_axis import AxisManager


def _image() -> pp.Image:
    """Build a quiet image with one axis."""
    image = pp.Image(text=False)
    image.create_axes()
    return image


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
    strict=True, reason="the class docstring says one output at a time"
)
def test_loadpart_docstring_does_not_deny_several_outputs() -> None:
    """Check the class docstring does not claim a single output.

    `nout="all"` loads several, and a test in test_loadpart.py relies on it,
    so the sentence turns a working feature into one users avoid.
    """
    assert "only one output" not in (inspect.getdoc(pp.LoadPart) or "")


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


# ---- image.py, imagefuncs/figure.py ----
@pytest.mark.xfail(
    strict=True, reason="an existing figure overrides the keywords given"
)
@pytest.mark.parametrize(
    ("build", "read", "expected"),
    [
        (
            lambda fig: pp.Image(fig=fig, figsize=[12.0, 3.0], text=False),
            "figsize",
            [12.0, 3.0],
        ),
        (
            lambda fig: pp.Image(fig=fig, fontsize=30.0, text=False),
            "fontsize",
            30.0,
        ),
    ],
    ids=["figsize", "fontsize"],
)
def test_keywords_win_over_the_figure_they_attach_to(
    build: Callable[[Figure], pp.Image], read: str, expected: object
) -> None:
    """Attach to an existing figure and ask for a size and a fontsize.

    The figure's own values overwrite both after the keywords were read, so
    what the user asked for is silently dropped while the docstring
    documents the keywords unconditionally.
    """
    existing = plt.figure(71, figsize=(4.0, 4.0))

    assert getattr(build(existing), read) == expected


@pytest.mark.xfail(
    strict=True, reason="close defaults to True even when a figure is given"
)
def test_a_given_figure_is_not_closed() -> None:
    """Hand a drawn figure to an Image and check it survives.

    Closing is for the window number; a figure passed directly is one the
    user already owns, so `close` should default to False when `fig` is
    given, as decided.
    """
    existing = plt.figure(72)
    existing.add_subplot(111).plot([0.0, 1.0], [0.0, 1.0])

    pp.Image(fig=existing, text=False)

    assert existing.axes


@pytest.mark.xfail(
    strict=True,
    reason="state.figsize is not updated when the figure is resized",
)
def test_figsize_follows_the_figure() -> None:
    """Create two columns of axes and compare the reported size with the real one.

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


# ---- imagefuncs/set_axis.py ----
@pytest.mark.xfail(
    strict=True,
    reason="the docstring promises bool | str, which raises TypeError",
)
@pytest.mark.parametrize("keyword", ["sharex", "sharey"])
def test_share_axes_documents_what_it_accepts(keyword: str) -> None:
    """Compare the documented type of `sharex` with the one declared.

    `SetAxisKwargs` declares an `Axes`, and the value goes straight to
    `ax.sharex()`, which takes an axis, so `sharex=True` raises TypeError
    from matplotlib. The docstring promises `bool | str | Matplotlib axis`
    and a default of False: it is the documentation that is wrong, and the
    bool-like sharing is `sharexaxes`, read by create_axes.
    """
    documented = inspect.getdoc(AxisManager.share_axes) or ""
    entry = next(
        line
        for line in documented.splitlines()
        if line.startswith(f"- {keyword}:")
    )

    assert "bool" not in entry
    assert "default False" not in entry


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


# ---- imagefuncs/colorbar.py ----
@pytest.mark.xfail(
    strict=True, reason="docstring gives cpos default of None, the code 'right'"
)
def test_colorbar_documents_its_real_default() -> None:
    """Compare the documented default of `cpos` with the one the code uses.

    `kwargs.get("cpos", "right")` is what runs, so a user reading "default
    None" expects no colorbar to be placed and gets one on the right.
    """
    documented = inspect.getdoc(ColorbarManager.colorbar) or ""
    entry = next(
        line for line in documented.splitlines() if line.startswith("- cpos:")
    )

    assert "default 'right'" in entry


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


@pytest.mark.xfail(
    strict=True, reason="a constant negative value gives an inverted range"
)
def test_constant_negative_data_keeps_the_axis_upright() -> None:
    """Pad a range whose data is one negative constant.

    The zero-width case pads from `ymax * 0.1`, which is negative here, so
    the limits come back the wrong way round and matplotlib draws the axis
    upside down.
    """
    image = _image()
    manager = RangeManager(image.state)

    ymin, ymax = manager.range_offset(-5.0, -5.0, "linear")

    assert ymin < ymax


@pytest.mark.xfail(
    strict=True, reason="a constant zero gives no padding and a divide by zero"
)
def test_constant_zero_data_is_given_a_range() -> None:
    """Pad a range whose data is all zeros.

    The padding is computed from `ymax * 0.1`, which is zero, so the limits
    are (0, 0) -- an empty window -- and `log10(0)` warns on the way.
    """
    image = _image()
    manager = RangeManager(image.state)

    with warnings.catch_warnings():
        warnings.simplefilter("error", RuntimeWarning)
        ymin, ymax = manager.range_offset(0.0, 0.0, "linear")

    assert ymin < ymax


# ---- utils/inspector.py ----
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
