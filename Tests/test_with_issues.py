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

import inspect
import re
import shutil
import typing
import warnings
from pathlib import Path

import numpy as np
import pytest
from helper_image import DELEGATION, DOCUMENTED_KWARGS
from helper_image import KWARGS as IMAGE_KWARGS

import pyPLUTO as pp
import pyPLUTO.image as image_mod
import pyPLUTO.imagekwargs as image_kwargs
from pyPLUTO.utils.ppwarnings import PyPLUTOKeywordWarning


def _documented(function: object) -> set[str]:
    """Return the names listed in the Parameters section of a docstring."""
    doc = getattr(function, "__doc__", None) or ""
    if "Parameters" not in doc:
        return set()
    section = doc.split("Parameters")[1].split("Returns")[0]
    return set(re.findall(r"^\s*- (\w+)", section, re.MULTILINE))


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


# ---- imagefuncs/plot.py, scatter.py ----
@pytest.mark.xfail(
    strict=True,
    reason="legend keywords given with legpos=None are reported as unused",
)
@pytest.mark.parametrize("method", ["plot", "scatter"])
def test_legend_keywords_are_accepted_with_legpos(method: str) -> None:
    """Draw with legpos=None and a legend keyword: nothing is reported.

    legpos is the switch of the legend. Given in the call, with any value,
    it makes the other legend keywords legitimate, as in a loop where only
    one panel gets a legend; with no legend drawn they are simply forgotten.
    Only without legpos is a legend keyword a mistake, and reported.
    """
    image = pp.Image()
    with warnings.catch_warnings(record=True) as caught:
        warnings.simplefilter("always")
        getattr(image, method)(
            [1.0, 2.0], [1.0, 2.0], label="a", legpos=None, legsize=15
        )
    assert not [w for w in caught if w.category is PyPLUTOKeywordWarning]


# ---- imagefuncs/set_axis.py ----
@pytest.mark.xfail(
    strict=True,
    reason="a scale given again resets the ticks set before",
)
@pytest.mark.parametrize(
    "first", ["log", "linear"], ids=["same-scale", "scale-change"]
)
def test_a_scale_given_again_keeps_the_ticks(first: str) -> None:
    """Remove the labels, then plot again on the axis with xscale="log".

    matplotlib's set_xscale gives the axis the default ticks of the scale,
    even when the scale does not change, so a second plot(xscale="log")
    brought back the labels the first had removed. The labels given are to
    hold whatever the order of the calls, so the case where the scale really
    changes, from linear to log, keeps them removed too.
    """
    image = pp.Image()
    x = np.array([64.0, 128.0, 256.0, 512.0, 1024.0])
    image.plot(x, 1 / x, xscale=first, xtickslabels=None)
    image.plot(x, 2 / x, ax=0, xscale="log")
    ax = image.ax[0]
    ax.figure.canvas.draw()
    assert not [t.get_text() for t in ax.get_xticklabels() if t.get_text()]


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


# ---- imagefuncs/imagetools.py, range.py ----
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
