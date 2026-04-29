"""Test of the configure.py file."""

import sys
import warnings

import pytest

from pyPLUTO.configure import Configure


@pytest.fixture(autouse=True)
def reset_greeted_flag() -> None:
    """Ensure tests do not share Configure.greeted state."""
    Configure.greeted = False


def test_version_and_session() -> None:
    """Ensure that the version and session are as expected."""
    c = Configure(greet=False)
    assert c.version == "Unknown"
    assert c.colorwarn is True
    assert c.colorerr is True
    assert isinstance(c.session, str)


def test_find_session_standard_when_ipython_import_fails(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """Ensure standard session is found when IPython import fails."""
    monkeypatch.setattr(
        "pyPLUTO.configure.importlib.import_module",
        lambda name: (_ for _ in ()).throw(ImportError),
    )

    c = Configure(greet=False)
    assert c.session == "Standard Python interpreter"


def test_find_session_standard_when_get_ipython_returns_none(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """Ensure standard session is found when get_ipython returns None."""

    class DummyModule:
        @staticmethod
        def get_ipython() -> None:
            return None

    monkeypatch.setattr(
        "pyPLUTO.configure.importlib.import_module",
        lambda name: DummyModule,
    )

    c = Configure(greet=False)
    assert c.session == "Standard Python interpreter"


def test_find_session_jupyter(monkeypatch: pytest.MonkeyPatch) -> None:
    """Ensure Jupyter session is found."""
    ZMQInteractiveShell = type("ZMQInteractiveShell", (), {})

    class DummyModule:
        @staticmethod
        def get_ipython() -> ZMQInteractiveShell:
            return ZMQInteractiveShell()

    monkeypatch.setattr(
        "pyPLUTO.configure.importlib.import_module",
        lambda name: DummyModule,
    )

    c = Configure(greet=False)
    assert c.session == "Jupyter notebook or qtconsole"


def test_find_session_ipython_terminal(monkeypatch: pytest.MonkeyPatch) -> None:
    """Ensure IPython terminal session is found."""
    TerminalInteractiveShell = type("TerminalInteractiveShell", (), {})

    class DummyModule:
        @staticmethod
        def get_ipython() -> TerminalInteractiveShell:
            return TerminalInteractiveShell()

    monkeypatch.setattr(
        "pyPLUTO.configure.importlib.import_module",
        lambda name: DummyModule,
    )

    c = Configure(greet=False)
    assert c.session == "Terminal running IPython"


def test_find_session_unknown_shell(monkeypatch: pytest.MonkeyPatch) -> None:
    """Ensure unknown session is found."""
    SomeOtherShell = type("SomeOtherShell", (), {})

    class DummyModule:
        @staticmethod
        def get_ipython() -> SomeOtherShell:
            return SomeOtherShell()

    monkeypatch.setattr(
        "pyPLUTO.configure.importlib.import_module",
        lambda name: DummyModule,
    )

    c = Configure(greet=False)
    assert c.session == "Unknown session"


def test_greeting_printed_only_on_first_initialization(
    capsys: pytest.CaptureFixture[str],
) -> None:
    """Ensure greeting is printed only on first initialization."""
    Configure()
    first = capsys.readouterr().out
    assert "PyPLUTO version: Unknown" in first
    assert "session:" in first

    Configure()
    second = capsys.readouterr().out
    assert second == ""


def test_greet_false_suppresses_greeting(
    capsys: pytest.CaptureFixture[str],
) -> None:
    """Ensure greeting is suppressed when greet=False."""
    Configure(greet=False)
    assert capsys.readouterr().out == ""


@pytest.mark.parametrize(
    "message", ["test warning", UserWarning("test warning")]
)
def test_color_warning_formats_warning(message: str | UserWarning) -> None:
    """Ensure warning is formatted with colors."""
    c = Configure(greet=False)
    result = c.color_warning(message, UserWarning, "testfile.py", 42)
    assert result == "\33[33mUserWarning: test warning[testfile.py:42]\33[0m\n"


def test_color_error_writes_colored_traceback_and_message(
    capsys: pytest.CaptureFixture[str],
) -> None:
    """Ensure error is written with colors."""
    c = Configure(greet=False)

    try:
        raise ValueError("something went wrong")
    except ValueError as exc:
        c.color_error(type(exc), exc, exc.__traceback__)

    err = capsys.readouterr().err
    assert "\033[91m" in err
    assert "\33[31m" in err
    assert "something went wrong" in err


def test_setup_handlers_installs_both_handlers(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """Ensure that both warning and error handlers are installed."""
    c = Configure(greet=False)

    original_warning = warnings.formatwarning
    original_error = sys.excepthook
    try:
        c._setup_handlers(colorwarn=True, colorerr=True)
        assert warnings.formatwarning == c.color_warning
        assert sys.excepthook == c.color_error
    finally:
        warnings.formatwarning = original_warning
        sys.excepthook = original_error


def test_setup_handlers_leaves_existing_handlers_when_both_flags_false() -> (
    None
):
    """Ensure that handlers are left unchanged when both flags are False."""
    c = Configure(greet=False)

    original_warning = warnings.formatwarning
    original_error = sys.excepthook
    try:
        c._setup_handlers(colorwarn=False, colorerr=False)
        assert warnings.formatwarning is original_warning
        assert sys.excepthook is original_error
    finally:
        warnings.formatwarning = original_warning
        sys.excepthook = original_error


def test_setup_handlers_sets_only_warning_handler() -> None:
    """Ensure that the code works well if only the warning handler is set."""
    c = Configure(greet=False)

    original_warning = warnings.formatwarning
    original_error = sys.excepthook
    try:
        c._setup_handlers(colorwarn=True, colorerr=False)
        assert warnings.formatwarning == c.color_warning
        assert sys.excepthook is original_error
    finally:
        warnings.formatwarning = original_warning
        sys.excepthook = original_error


def test_setup_handlers_sets_only_error_handler() -> None:
    """Ensure that the code works well if only the error handler is set."""
    c = Configure(greet=False)

    original_warning = warnings.formatwarning
    original_error = sys.excepthook
    try:
        c._setup_handlers(colorwarn=False, colorerr=True)
        assert warnings.formatwarning is original_warning
        assert sys.excepthook == c.color_error
    finally:
        warnings.formatwarning = original_warning
        sys.excepthook = original_error


def test_setup_handlers_always_enables_warning_filter(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """Ensure that the warnings.simplefilter("always") is enabled."""
    c = Configure(greet=False)
    calls = []

    monkeypatch.setattr(
        warnings, "simplefilter", lambda *args: calls.append(args)
    )

    c._setup_handlers(colorwarn=False, colorerr=False)

    assert calls == [("always",)]
