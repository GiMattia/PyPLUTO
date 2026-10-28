"""Test of the pperrors.py file.

The categories are what users catch, so the checks are about the promises
the module makes: one base for every error raised on purpose, each subclass
also a built-in so old except clauses keep working, and classes plain enough
to come back from a worker process.
"""

import ast
import builtins
import pickle
import warnings

import pytest
from helper_scan import scanned_sources

from pyPLUTO.utils import pperrors
from pyPLUTO.utils.pperrors import (
    PyPLUTOAttributeError,
    PyPLUTOAxisError,
    PyPLUTOConfigError,
    PyPLUTOCopyError,
    PyPLUTODataError,
    PyPLUTOError,
    PyPLUTOInternalError,
    PyPLUTOMissingFeatureError,
    PyPLUTOOptionError,
)

# Each subclass, with the built-in it also derives from
BUILTIN = {
    PyPLUTOAttributeError: AttributeError,
    PyPLUTOAxisError: ValueError,
    PyPLUTOConfigError: ValueError,
    PyPLUTOCopyError: TypeError,
    PyPLUTODataError: ValueError,
    PyPLUTOInternalError: RuntimeError,
    PyPLUTOMissingFeatureError: NotImplementedError,
    PyPLUTOOptionError: ValueError,
}
IDS = [
    "attribute",
    "axis",
    "config",
    "copy",
    "data",
    "internal",
    "missing-feature",
    "option",
]


# ---- The categories ----
def test_the_base_is_an_exception() -> None:
    """Check the base is an Exception, so a plain except Exception sees it."""
    assert issubclass(PyPLUTOError, Exception)


def test_every_subclass_is_in_the_table() -> None:
    """Compare the subclasses defined in pperrors.py with BUILTIN.

    A new error added without its row here would escape every check below.
    """
    defined = {
        obj
        for obj in vars(pperrors).values()
        if isinstance(obj, type)
        and issubclass(obj, PyPLUTOError)
        and obj is not PyPLUTOError
    }
    assert defined == set(BUILTIN)


@pytest.mark.parametrize(("error", "builtin"), BUILTIN.items(), ids=IDS)
def test_a_subclass_is_also_its_builtin(
    error: type[PyPLUTOError], builtin: type[Exception]
) -> None:
    """Check each subclass is a PyPLUTOError and its built-in alike."""
    assert issubclass(error, PyPLUTOError)
    assert issubclass(error, builtin)


@pytest.mark.parametrize(("error", "builtin"), BUILTIN.items(), ids=IDS)
@pytest.mark.parametrize("by", ["pypluto", "builtin"])
def test_a_subclass_is_caught_by_either_name(
    error: type[PyPLUTOError], builtin: type[Exception], by: str
) -> None:
    """Raise each subclass and catch it by the base or by its built-in."""
    caught = PyPLUTOError if by == "pypluto" else builtin
    with pytest.raises(caught, match="message"):
        raise error("message")


# ---- Pickling ----
@pytest.mark.parametrize("error", [PyPLUTOError, *BUILTIN], ids=["base", *IDS])
def test_an_error_survives_pickling(error: type[PyPLUTOError]) -> None:
    """Pickle an error and check the copy keeps its class and its message.

    A worker process sends its errors back pickled; a class with extra
    required arguments would fail there instead of reporting the error.
    """
    copy = pickle.loads(pickle.dumps(error("message")))
    assert type(copy) is error
    assert str(copy) == "message"


# ---- The scan of the sources ----
# The names of Python's own errors, which a raise in pyPLUTO should not use
BUILTIN_ERRORS = {
    name
    for name, obj in vars(builtins).items()
    if isinstance(obj, type) and issubclass(obj, BaseException)
}


def raised_name(exc: ast.expr | None) -> str | None:
    """Return the name of the class a raise uses, as written in the source."""
    if isinstance(exc, ast.Call):
        exc = exc.func
    return exc.id if isinstance(exc, ast.Name) else None


def test_every_raise_uses_a_category_of_its_own() -> None:
    """Scan the sources and report each raise of a generic error, by file.

    A raise of a built-in error, or of the base PyPLUTOError, does not say
    what went wrong. The scan only reports, with one warning per file listing
    the lines, so the work left shows in every run without failing it. A bare
    raise, which raises again the error being handled, is not reported.
    """
    generic = BUILTIN_ERRORS | {"PyPLUTOError"}
    for path, tree in scanned_sources():
        lines = sorted(
            node.lineno
            for node in ast.walk(tree)
            if isinstance(node, ast.Raise) and raised_name(node.exc) in generic
        )
        if lines:
            warnings.warn(
                f"{path} raises generic errors at lines {lines}",
                UserWarning,
                stacklevel=1,
            )
