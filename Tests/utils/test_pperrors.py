"""Test of the pperrors.py file.

The categories are what users catch, so the checks are about the promises
the module makes: one base for every error raised on purpose, each subclass
also a built-in so old except clauses keep working, and classes plain enough
to come back from a worker process.
"""

import pickle

import pytest

from pyPLUTO.utils.pperrors import PyPLUTOConfigError, PyPLUTOError


# ---- The categories ----
def test_the_base_is_an_exception() -> None:
    """Check the base is an Exception, so a plain except Exception sees it."""
    assert issubclass(PyPLUTOError, Exception)


def test_a_config_error_is_also_a_value_error() -> None:
    """Check a wrong setting is a PyPLUTOError and a ValueError alike."""
    assert issubclass(PyPLUTOConfigError, PyPLUTOError)
    assert issubclass(PyPLUTOConfigError, ValueError)


@pytest.mark.parametrize(
    "caught", [PyPLUTOError, ValueError], ids=["pypluto", "builtin"]
)
def test_a_config_error_is_caught_by_either_name(
    caught: type[Exception],
) -> None:
    """Raise a config error and catch it by the base or by the built-in."""
    with pytest.raises(caught, match="unknown value"):
        raise PyPLUTOConfigError("unknown value")


# ---- Pickling ----
@pytest.mark.parametrize(
    "error", [PyPLUTOError, PyPLUTOConfigError], ids=["base", "config"]
)
def test_an_error_survives_pickling(error: type[PyPLUTOError]) -> None:
    """Pickle an error and check the copy keeps its class and its message.

    A worker process sends its errors back pickled; a class with extra
    required arguments would fail there instead of reporting the error.
    """
    copy = pickle.loads(pickle.dumps(error("message")))
    assert type(copy) is error
    assert str(copy) == "message"
