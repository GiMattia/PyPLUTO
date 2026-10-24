"""Test of the configure.py file."""

import subprocess
import sys
import warnings

import pytest

from pyPLUTO.utils.configure import Configure
from pyPLUTO.utils.ppwarnings import PyPLUTOWarning


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
        "pyPLUTO.utils.configure.importlib.import_module",
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
        "pyPLUTO.utils.configure.importlib.import_module",
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
        "pyPLUTO.utils.configure.importlib.import_module",
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
        "pyPLUTO.utils.configure.importlib.import_module",
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
        "pyPLUTO.utils.configure.importlib.import_module",
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
    assert err.startswith("\33[31mTraceback (most recent call last):")
    assert "ValueError: something went wrong" in err
    assert err.endswith("\33[0m")


def test_color_error_keeps_the_chained_exception(
    capsys: pytest.CaptureFixture[str],
) -> None:
    """Raise an error from another and check both are reported.

    The hook used to print the frames and the message only, so the type of
    the error and the exception that caused it were lost.
    """
    c = Configure(greet=False)

    try:
        try:
            raise KeyError("x")
        except KeyError as cause:
            raise ValueError("boom") from cause
    except ValueError as exc:
        c.color_error(type(exc), exc, exc.__traceback__)

    err = capsys.readouterr().err
    assert "KeyError: 'x'" in err
    assert "direct cause" in err
    assert "ValueError: boom" in err


def test_setup_handlers_installs_both_handlers() -> None:
    """Ensure that both warning and error handlers are installed."""
    c = Configure(greet=False)

    original_warning = warnings.formatwarning
    original_error = sys.excepthook
    try:
        c.setup_handlers(colorwarn=True, colorerr=True)
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
        c.setup_handlers(colorwarn=False, colorerr=False)
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
        c.setup_handlers(colorwarn=True, colorerr=False)
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
        c.setup_handlers(colorwarn=False, colorerr=True)
        assert warnings.formatwarning is original_warning
        assert sys.excepthook == c.color_error
    finally:
        warnings.formatwarning = original_warning
        sys.excepthook = original_error


def test_setup_handlers_shows_every_pypluto_warning(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """Ensure the "always" filter is installed for pyPLUTO's warnings only.

    The category filter holds wherever a warning points, the user's own line
    included; the module filter covers the warnings not raised through
    ppwarn yet, which still point inside the package.
    """
    c = Configure(greet=False)
    calls = []

    monkeypatch.setattr(
        warnings,
        "filterwarnings",
        lambda *args, **kwargs: calls.append((args, kwargs)),
    )

    c.setup_handlers(colorwarn=False, colorerr=False)

    assert calls == [
        (("always",), {"category": PyPLUTOWarning}),
        (("always",), {"module": "pyPLUTO"}),
    ]


def test_importing_pypluto_keeps_the_warning_filters() -> None:
    """Silence warnings, import pyPLUTO, and check they stay silent.

    `Configure` used to call `simplefilter("always")` while the package
    imported, which put a catch-all in front of every filter, so `-W ignore`
    and any `filterwarnings` call made beforehand stopped working
    process-wide. A subprocess, because the import happens once per process.
    """
    script = (
        "import warnings; warnings.filterwarnings('ignore');"
        "import pyPLUTO; warnings.warn('should be silent')"
    )
    result = subprocess.run(
        [sys.executable, "-W", "ignore", "-c", script],
        capture_output=True,
        text=True,
        check=False,
    )

    assert "should be silent" not in result.stderr


def test_importing_pypluto_leaves_library_deprecations_hidden() -> None:
    """Raise a DeprecationWarning from a library module after the import.

    Python hides a library's deprecations by default, and the catch-all
    filter used to show them: matplotlib's Qt backend printed one per
    toolbar icon. A subprocess, because the import happens once per process.
    """
    script = (
        "import warnings; import pyPLUTO;"
        "exec(compile(\"import warnings; warnings.warn('library', "
        "DeprecationWarning)\", 'lib.py', 'exec'), {'__name__': 'lib'})"
    )
    result = subprocess.run(
        [sys.executable, "-c", script],
        capture_output=True,
        text=True,
        check=False,
    )

    assert "library" not in result.stderr
