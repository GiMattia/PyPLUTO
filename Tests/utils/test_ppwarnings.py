"""Test of the ppwarnings.py file.

Two things are checked: the categories, which users filter on, and where
ppwarn attributes a warning. The second is the reason the module exists: a
fixed stacklevel points at a file inside pyPLUTO as soon as the call goes
through one manager more than expected, while ppwarn walks out of the
package to the user's own line.
"""

import inspect
from pathlib import Path

import pytest

from pyPLUTO.utils import ppwarnings
from pyPLUTO.utils.ppwarnings import (
    PyPLUTODeprecationWarning,
    PyPLUTOKeywordWarning,
    PyPLUTOWarning,
    ppwarn,
)


# ---- The categories ----
def test_every_category_is_a_pypluto_warning() -> None:
    """Check the three categories descend from one base, itself a UserWarning.

    The base is what Configure shows every time and what a user ignores to
    silence pyPLUTO; being a UserWarning keeps every existing filter on
    UserWarning working.
    """
    assert issubclass(PyPLUTOWarning, UserWarning)
    assert issubclass(PyPLUTOKeywordWarning, PyPLUTOWarning)
    assert issubclass(PyPLUTODeprecationWarning, PyPLUTOWarning)


def test_a_deprecation_is_also_a_deprecation_warning() -> None:
    """Check pyPLUTO's deprecations are seen as such by Python and pytest.

    `pytest -W error::DeprecationWarning` and Python's own handling of
    deprecations only see the standard category.
    """
    assert issubclass(PyPLUTODeprecationWarning, DeprecationWarning)


# ---- Where a warning points ----
def test_the_default_category_is_the_base_one() -> None:
    """Raise a warning without a category and check it is a PyPLUTOWarning."""
    with pytest.warns(PyPLUTOWarning) as record:
        ppwarn("plain")

    assert record[0].category is PyPLUTOWarning


def test_a_warning_points_at_the_line_that_called() -> None:
    """Call ppwarn from here and check the warning names this very line.

    This test lies outside the package, so the first frame outside is the
    caller of ppwarn itself.
    """
    frame = inspect.currentframe()
    assert frame is not None

    with pytest.warns(PyPLUTOKeywordWarning) as record:
        line = frame.f_lineno + 1
        ppwarn("here", PyPLUTOKeywordWarning)

    assert record[0].filename == __file__
    assert record[0].lineno == line


def _inside_the_package() -> None:
    """Raise a warning from a function the test pretends is inside pyPLUTO."""
    ppwarn("from inside")


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
