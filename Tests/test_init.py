import sys
import warnings

from pyPLUTO import (
    __colorerr__,
    __colorwarn__,
    __session__,
    __version__,
    find_session,
)
from pyPLUTO.h_pypluto import color_error, color_warning, setup_handlers


def test_version_and_session():
    # Ensure that the version and session are as expected
    assert __version__ == "1.0"
    assert __colorwarn__ is True
    assert __colorerr__ is True
    assert __session__ == find_session()


def test_warning_handler(monkeypatch):
    monkeypatch.setattr(warnings, "formatwarning", lambda *args, **kwargs: None)
    setup_handlers(colorwarn=True, colorerr=False)
    assert warnings.formatwarning == color_warning


def test_error_handler(monkeypatch):
    monkeypatch.setattr(sys, "excepthook", lambda *args, **kwargs: None)
    setup_handlers(colorwarn=False, colorerr=True)
    assert sys.excepthook == color_error
