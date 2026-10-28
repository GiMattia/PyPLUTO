"""Test of the ppwarnings.py file.

Two things are checked: the categories, which users filter on, and where
PPWarn.warn attributes a warning. The second is the reason the module
exists: a fixed stacklevel points at a file inside pyPLUTO as soon as the
call goes through one manager more than expected, while PPWarn.warn walks
out of the package to the user's own line.
"""

import ast
import inspect
import sys
import warnings
from pathlib import Path

import pytest
from helper_scan import scanned_sources

from pyPLUTO.utils import ppwarnings
from pyPLUTO.utils.ppwarnings import (
    PPWarn,
    PyPLUTOBehaviorWarning,
    PyPLUTOConfigWarning,
    PyPLUTOConflictWarning,
    PyPLUTODependencyWarning,
    PyPLUTODeprecationWarning,
    PyPLUTOKeywordWarning,
    PyPLUTOOptionWarning,
    PyPLUTOWarning,
)

# Every category a warning is raised with
CATEGORIES = [
    PyPLUTOBehaviorWarning,
    PyPLUTOConfigWarning,
    PyPLUTOConflictWarning,
    PyPLUTODependencyWarning,
    PyPLUTODeprecationWarning,
    PyPLUTOKeywordWarning,
    PyPLUTOOptionWarning,
]
IDS = [
    "behavior",
    "config",
    "conflict",
    "dependency",
    "deprecation",
    "keyword",
    "option",
]


# ---- The categories ----
def test_the_base_is_a_user_warning() -> None:
    """Check the base is a UserWarning, so filters on it keep working."""
    assert issubclass(PyPLUTOWarning, UserWarning)


@pytest.mark.parametrize("category", CATEGORIES, ids=IDS)
def test_every_category_is_a_pypluto_warning(
    category: type[PyPLUTOWarning],
) -> None:
    """Check each category descends from the base.

    The base is what the warnings setting acts on and what a user ignores
    to silence pyPLUTO alone.
    """
    assert issubclass(category, PyPLUTOWarning)


def test_every_category_is_in_the_table() -> None:
    """Compare the categories defined in ppwarnings.py with CATEGORIES.

    A new category added without its row here would escape every check.
    """
    defined = {
        obj
        for obj in vars(ppwarnings).values()
        if isinstance(obj, type)
        and issubclass(obj, PyPLUTOWarning)
        and obj is not PyPLUTOWarning
    }
    assert defined == set(CATEGORIES)


def test_a_deprecation_is_also_a_deprecation_warning() -> None:
    """Check pyPLUTO's deprecations are seen as such by Python and pytest.

    `pytest -W error::DeprecationWarning` and Python's own handling of
    deprecations only see the standard category.
    """
    assert issubclass(PyPLUTODeprecationWarning, DeprecationWarning)


# ---- Where a warning points ----
@pytest.fixture(params=["skip_file_prefixes", "counted"])
def both_paths(
    request: pytest.FixtureRequest, monkeypatch: pytest.MonkeyPatch
) -> None:
    """Run a test on the path of Python 3.12 and later, and on the 3.11 one.

    The 3.11 path is plain Python, so it runs on any version once
    version_info says 3.11; the other needs a Python that has
    skip_file_prefixes, and is skipped on 3.11.
    """
    if request.param == "counted":
        monkeypatch.setattr(sys, "version_info", (3, 11, 0))
    elif sys.version_info < (3, 12):
        pytest.skip("skip_file_prefixes needs Python 3.12")


def test_the_default_category_is_the_base_one() -> None:
    """Raise a warning without a category and check it is a PyPLUTOWarning."""
    with pytest.warns(PyPLUTOWarning) as record:
        PPWarn.warn("plain")

    assert record[0].category is PyPLUTOWarning


@pytest.mark.usefixtures("both_paths")
def test_a_warning_points_at_the_line_that_called() -> None:
    """Call PPWarn.warn from here and check the warning names this line.

    This test lies outside the package, so the first frame outside is the
    caller of PPWarn.warn itself.
    """
    frame = inspect.currentframe()
    assert frame is not None

    with pytest.warns(PyPLUTOKeywordWarning) as record:
        line = frame.f_lineno + 1
        PPWarn.warn("here", PyPLUTOKeywordWarning)

    assert record[0].filename == __file__
    assert record[0].lineno == line


def _inside_the_package() -> None:
    """Raise a warning from a function the test pretends is inside pyPLUTO."""
    PPWarn.warn("from inside", PyPLUTOBehaviorWarning)


@pytest.mark.usefixtures("both_paths")
def test_the_frames_inside_the_package_are_skipped(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """Pretend this test folder is the package and check its frames are passed.

    With the folder counted as pyPLUTO, the helper above and this test are
    both inside, so the warning goes to the first frame beyond them, in
    pytest, rather than to the helper that raised it.
    """
    monkeypatch.setattr(ppwarnings, "_PACKAGE", str(Path(__file__).parent))

    with pytest.warns(PyPLUTOWarning) as record:
        _inside_the_package()

    assert Path(record[0].filename).parent != Path(__file__).parent


# ---- The scan of the sources ----
def is_generic_warning(node: ast.Call) -> bool:
    """Tell whether a call is a warning without a category of its own.

    That is warnings.warn, which PPWarn.warn replaces, or PPWarn.warn with
    no category or with the base PyPLUTOWarning.
    """
    if not isinstance(node.func, ast.Attribute):
        return False
    owner = node.func.value
    if not isinstance(owner, ast.Name) or node.func.attr != "warn":
        return False
    if owner.id == "warnings":
        return True
    if owner.id != "PPWarn":
        return False
    given = [kw.value for kw in node.keywords if kw.arg == "category"]
    category = node.args[1] if len(node.args) > 1 else next(iter(given), None)
    return not isinstance(category, ast.Name) or category.id == "PyPLUTOWarning"


def test_every_warning_uses_a_category_of_its_own() -> None:
    """Scan the sources and report each generic warning, by file.

    A warnings.warn, or a PPWarn.warn with no category or with the base, does
    not say what the warning is about. The scan only reports, with one
    warning per file listing the lines, so the work left shows in every run
    without failing it. ppwarnings.py itself is left out: PPWarn.warn is
    where warnings.warn is called on purpose.
    """
    for path, tree in scanned_sources():
        if path == "utils/ppwarnings.py":
            continue
        lines = sorted(
            node.lineno
            for node in ast.walk(tree)
            if isinstance(node, ast.Call) and is_generic_warning(node)
        )
        if lines:
            warnings.warn(
                f"{path} raises generic warnings at lines {lines}",
                UserWarning,
                stacklevel=1,
            )
