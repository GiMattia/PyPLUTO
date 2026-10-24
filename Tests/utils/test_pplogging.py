"""Test of the pplogging.py file."""

import logging
from collections.abc import Generator
from types import SimpleNamespace

import pytest

from pyPLUTO.utils.pplogging import LEVELS, pplog, set_text


class Sender:
    """An object with a state holding classlog, as every manager has."""

    def __init__(self, text: bool | None) -> None:
        self.state = SimpleNamespace(classlog=text)

    def info(self) -> None:
        pplog.info("message %s", 1)

    def debug(self) -> None:
        pplog.debug("message %s", 1)


@pytest.fixture(autouse=True)
def reset_the_text_of_the_package() -> Generator[None, None, None]:
    """Give the package's text back its default after every test."""
    yield
    pplog.text = None


# ---- set_text ----
@pytest.mark.parametrize(
    "text", [False, True, None], ids=["silent", "debug", "default"]
)
def test_set_text_sets_the_text_of_the_package(text: bool | None) -> None:
    """Set the verbosity and read the package's text back."""
    set_text(text)
    assert pplog.text is text


def test_set_text_defaults_to_the_ordinary_information() -> None:
    """Call set_text without arguments and expect None, the default."""
    pplog.text = False
    set_text()
    assert pplog.text is None


def test_every_text_has_a_level() -> None:
    """Check the table: False only warnings, None information, True debug."""
    assert LEVELS == {
        False: logging.WARNING,
        None: logging.INFO,
        True: logging.DEBUG,
    }


# ---- pplog ----
@pytest.mark.parametrize(
    ("package", "text", "kind", "shown"),
    [
        (None, None, "info", True),
        (None, None, "debug", False),
        (False, None, "info", False),
        (True, None, "debug", True),
        (False, True, "debug", True),
        (True, False, "info", False),
    ],
    ids=[
        "default-info",
        "default-debug",
        "package-silent",
        "package-debug",
        "object-debug-over-silent-package",
        "object-silent-over-debug-package",
    ],
)
def test_pplog_follows_the_object_then_the_package(
    caplog: pytest.LogCaptureFixture,
    package: bool | None,
    text: bool | None,
    kind: str,
    shown: bool,
) -> None:
    """Send one message per pair of package and object text.

    None on the object follows the package; True or False decide for the
    message alone, with the same meaning as for the package.
    """
    set_text(package)
    with caplog.at_level(logging.DEBUG, logger="pyPLUTO"):
        getattr(Sender(text), kind)()
    assert ("message 1" in caplog.text) is shown


@pytest.mark.parametrize(
    ("package", "shown"),
    [(None, True), (False, False)],
    ids=["default", "silent"],
)
def test_pplog_outside_an_object_follows_the_package(
    caplog: pytest.LogCaptureFixture, package: bool | None, shown: bool
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
