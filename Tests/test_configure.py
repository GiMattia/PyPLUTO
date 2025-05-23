import builtins
import sys
import types
import warnings

import pyPLUTO as pp
import pytest
from pyPLUTO.configure import Configure


@pytest.fixture(autouse=True)
def reset_greeted_flag():
    # Reset the class flag before each test
    Configure._greeted = False


def test_version_and_session():
    # Ensure that the version and session are as expected
    assert pp.Configure().version == "1.0"
    assert pp.Configure().colorwarn is True
    assert pp.Configure().colorerr is True


def test_find_session_standard(monkeypatch):
    monkeypatch.setitem(sys.modules, "IPython.core.getipython", None)
    c = Configure(greet=False)
    assert c.session in [
        "Standard Python interpreter",
        "Jupyter notebook or qtconsole",
        "Terminal running IPython",
        "Unknown session",
    ]


def test_find_session_jupyter(monkeypatch):
    class ZMQInteractiveShell:
        pass

    class DummyIPython:
        __class__ = ZMQInteractiveShell

    def dummy_get_ipython():
        return DummyIPython()

    monkeypatch.setitem(
        sys.modules,
        "IPython.core.getipython",
        types.SimpleNamespace(get_ipython=dummy_get_ipython),
    )

    c = Configure(greet=False)
    assert c.session == "Jupyter notebook or qtconsole"


def test_find_session_ipython_terminal(monkeypatch):
    class TerminalInteractiveShell:
        pass

    class DummyIPython:
        __class__ = TerminalInteractiveShell

    def dummy_get_ipython():
        return DummyIPython()

    monkeypatch.setitem(
        sys.modules,
        "IPython.core.getipython",
        types.SimpleNamespace(get_ipython=dummy_get_ipython),
    )

    c = Configure(greet=False)
    assert c.session == "Terminal running IPython"


def test_find_session_simulated(monkeypatch):
    # Patch get_ipython to return a dummy object
    class DummyShell:
        __name__ = "DummyShell"

    class DummyIPython:
        __class__ = DummyShell

    def dummy_get_ipython():
        return DummyIPython()

    monkeypatch.setitem(builtins.__dict__, "get_ipython", dummy_get_ipython)
    monkeypatch.setitem(
        sys.modules,
        "IPython.core.getipython",
        types.SimpleNamespace(get_ipython=dummy_get_ipython),
    )

    c = Configure(greet=False)
    assert c.session == "Unknown session"


def test_greeting_printed_once(capsys):
    Configure._greeted = False
    c1 = Configure()
    out1 = capsys.readouterr().out
    assert "PyPLUTO version:" in out1

    c2 = Configure()
    out2 = capsys.readouterr().out
    assert out2 == ""  # No second greeting


def test_greet_flag_suppresses_print(capsys):
    c = Configure(greet=False)
    captured = capsys.readouterr()
    assert captured.out == ""


def test_color_warning_format():
    c = Configure(greet=False)
    result = c.color_warning(
        message="test warning",
        category=UserWarning,
        filename="testfile.py",
        lineno=42,
    )
    assert "\33[33mUserWarning: test warning[testfile.py:42]\33[0m" in result


def test_color_error_format(capsys):
    c = Configure(greet=False)

    def raise_error():
        raise ValueError("something went wrong")

    try:
        raise_error()
    except ValueError as e:
        c.color_error(type(e), e, e.__traceback__)
        out = capsys.readouterr().err
        assert "something went wrong" in out
        assert "\033[91m" in out  # Red traceback
        assert "\33[31m" in out  # Red error message


def test_setup_handlers(monkeypatch):
    c = Configure(greet=False)
    # Monkeypatch sys.excepthook and warnings.formatwarning
    monkeypatch.setattr(warnings, "formatwarning", lambda *a, **kw: "patched")
    monkeypatch.setattr(sys, "excepthook", lambda *a, **kw: "patched")

    c._setup_handlers(True, True)
    assert callable(warnings.formatwarning)
    assert callable(sys.excepthook)


def test_setup_handlers_all(monkeypatch):
    c = Configure(greet=False)

    # Save originals to restore later
    original_formatwarning = warnings.formatwarning
    original_excepthook = sys.excepthook

    try:
        # Test with both flags False - should NOT change handlers
        c._setup_handlers(colorwarn=False, colorerr=False)
        assert warnings.formatwarning is original_formatwarning
        assert sys.excepthook is original_excepthook

    finally:
        # Restore originals
        warnings.formatwarning = original_formatwarning
        sys.excepthook = original_excepthook
