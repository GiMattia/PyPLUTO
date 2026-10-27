"""Test of the pplogging.py file."""

import logging
from collections.abc import Generator
from types import SimpleNamespace
from typing import Any

import pytest

from pyPLUTO.utils.pperrors import PyPLUTOConfigError
from pyPLUTO.utils.pplogging import LEVELS, pplog, set_text
from pyPLUTO.utils.settings import SETTINGS, TextValue


class Sender:
    """An object with a state holding classlog, as every manager has."""

    def __init__(self, text: TextValue) -> None:
        self.state = SimpleNamespace(classlog=text)

    def info(self) -> None:
        pplog.info("message %s", 1)

    def debug(self) -> None:
        pplog.debug("message %s", 1)


@pytest.fixture(autouse=True)
def reset_the_text_of_the_package() -> Generator[None, None, None]:
    """Give the package's text back its default after every test."""
    yield
    SETTINGS["text"] = "default"


# ---- set_text ----
@pytest.mark.parametrize(
    ("text", "stored"),
    [
        (False, False),
        ("default", "default"),
        (None, "default"),
        ("verbose", "verbose"),
        (True, "verbose"),
    ],
    ids=["silent", "default", "none", "verbose", "true"],
)
def test_set_text_sets_the_text_of_the_package(
    text: TextValue, stored: TextValue
) -> None:
    """Set the verbosity and read the package's text back.

    True and None are stored as "verbose" and "default", one spelling per
    meaning.
    """
    set_text(text)
    assert SETTINGS["text"] is stored


def test_set_text_defaults_to_the_ordinary_information() -> None:
    """Call set_text without arguments and expect "default"."""
    SETTINGS["text"] = False
    set_text()
    assert SETTINGS["text"] == "default"


def test_set_text_refuses_a_wrong_value() -> None:
    """Give set_text a value it does not accept and expect the error.

    The value is typed Any because a checker rightly refuses it: this is
    the check at runtime, for callers no checker sees.
    """
    wrong: Any = "loud"
    with pytest.raises(PyPLUTOConfigError, match="Unknown value"):
        set_text(wrong)


def test_every_text_has_a_level() -> None:
    """Check the table: False only warnings, "default" information, True and
    "verbose" the debug details too."""
    assert LEVELS == {
        False: logging.WARNING,
        "default": logging.INFO,
        True: logging.DEBUG,
        "verbose": logging.DEBUG,
    }


# ---- pplog ----
@pytest.mark.parametrize(
    ("package", "text", "kind", "shown"),
    [
        ("default", None, "info", True),
        ("default", None, "debug", False),
        (False, None, "info", False),
        ("verbose", None, "debug", True),
        (False, True, "debug", True),
        (False, "verbose", "debug", True),
        (False, "default", "info", True),
        ("verbose", False, "info", False),
    ],
    ids=[
        "default-info",
        "default-debug",
        "package-silent",
        "package-verbose",
        "object-true-over-silent-package",
        "object-verbose-over-silent-package",
        "object-default-over-silent-package",
        "object-silent-over-verbose-package",
    ],
)
def test_pplog_follows_the_object_then_the_package(
    caplog: pytest.LogCaptureFixture,
    package: TextValue,
    text: TextValue,
    kind: str,
    shown: bool,
) -> None:
    """Send one message per pair of package and object text.

    None on the object follows the package; any other value decides for the
    message alone, with the same meaning as for the package.
    """
    set_text(package)
    with caplog.at_level(logging.DEBUG, logger="pyPLUTO"):
        getattr(Sender(text), kind)()
    assert ("message 1" in caplog.text) is shown


@pytest.mark.parametrize(
    ("package", "shown"),
    [("default", True), (False, False)],
    ids=["default", "silent"],
)
def test_pplog_outside_an_object_follows_the_package(
    caplog: pytest.LogCaptureFixture, package: TextValue, shown: bool
) -> None:
    """Send a message from a plain function, which has no state to read."""
    set_text(package)
    with caplog.at_level(logging.DEBUG, logger="pyPLUTO"):
        pplog.info("message %s", 1)
    assert ("message 1" in caplog.text) is shown


def test_pplog_points_the_record_at_the_sender(
    caplog: pytest.LogCaptureFixture,
) -> None:
    """Check the record names the method that sent it, not pplogging."""
    with caplog.at_level(logging.DEBUG, logger="pyPLUTO"):
        Sender(None).info()
    assert caplog.records[0].funcName == "info"
    assert caplog.records[0].filename == "test_pplogging.py"
