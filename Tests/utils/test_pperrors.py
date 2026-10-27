"""Test of the pperrors.py file.

The categories are what users catch, so the checks are about the promises
the module makes: one base for every error raised on purpose, each subclass
also a built-in so old except clauses keep working, and classes plain enough
to come back from a worker process.
"""

import pickle

import pytest

from pyPLUTO.utils import pperrors
from pyPLUTO.utils.pperrors import (
    PyPLUTOAttributeError,
    PyPLUTOAxisError,
    PyPLUTOConfigError,
    PyPLUTOCopyError,
    PyPLUTODataError,
    PyPLUTOError,
    PyPLUTOInternalError,
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
    PyPLUTOOptionError: ValueError,
}
IDS = ["attribute", "axis", "config", "copy", "data", "internal", "option"]


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
