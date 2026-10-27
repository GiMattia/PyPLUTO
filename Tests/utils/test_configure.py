"""Test of the configure.py file.

The handlers read the settings each time they show something, so most tests
set a setting and look at what comes out. The autouse fixture gives back
everything a test may change -- the settings, the warning filters, the two
hooks and the greeting flag -- since all of them are process-wide.
"""

import subprocess
import sys
import warnings
from collections.abc import Generator
from pathlib import Path
from typing import Any

import pytest

from pyPLUTO.utils import configure as cfg
from pyPLUTO.utils.configure import Configure, Settings, configure
from pyPLUTO.utils.pperrors import (
    PyPLUTOConfigError,
    PyPLUTOError,
    PyPLUTOInternalError,
)
from pyPLUTO.utils.ppwarnings import (
    PPWarn,
    PyPLUTOBehaviorWarning,
    PyPLUTOWarning,
)
from pyPLUTO.utils.settings import SETTINGS, check

YELLOW, RED, RESET = "\33[33m", "\33[31m", "\33[0m"


@pytest.fixture(autouse=True)
def isolated(monkeypatch: pytest.MonkeyPatch) -> Generator[None, None, None]:
    """Give back the settings, filters, hooks and greeting after each test.

    The greeting is off unless a test turns it on, so the output of the
    other tests stays clean.
    """
    saved = dict(SETTINGS)
    SETTINGS["greet"] = False
    monkeypatch.setattr(Configure, "greeted", False)
    monkeypatch.setattr(warnings, "formatwarning", warnings.formatwarning)
    monkeypatch.setattr(sys, "excepthook", sys.excepthook)
    with warnings.catch_warnings():
        yield
    SETTINGS.clear()
    SETTINGS.update(saved)


def report_of(error: BaseException, capsys: pytest.CaptureFixture[str]) -> str:
    """Give an error to the error hook and return what it writes."""
    Configure().color_error(type(error), error, error.__traceback__)
    return capsys.readouterr().err


def raised_inside_pypluto() -> PyPLUTOConfigError:
    """Return a PyPLUTOError raised from inside the package, by settings.py."""
    with pytest.raises(PyPLUTOConfigError) as info:
        check("text", "loud")
    return info.value


# ---- Session and greeting ----
def test_version_and_session() -> None:
    """Ensure that the version and session are as expected."""
    c = Configure()
    assert c.version == "Unknown"
    assert isinstance(c.session, str)


def test_find_session_standard_when_ipython_import_fails(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """Ensure standard session is found when IPython import fails."""
    monkeypatch.setattr(
        "pyPLUTO.utils.configure.importlib.import_module",
        lambda name: (_ for _ in ()).throw(ImportError),
    )

    c = Configure()
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

    c = Configure()
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

    c = Configure()
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

    c = Configure()
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

    c = Configure()
    assert c.session == "Unknown session"


def test_greeting_printed_only_on_first_initialization(
    capsys: pytest.CaptureFixture[str],
) -> None:
    """Ensure greeting is printed only on first initialization."""
    SETTINGS["greet"] = True
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
    """Ensure greeting is suppressed when the greet setting is off."""
    Configure()
    assert capsys.readouterr().out == ""


# ---- Warnings ----
@pytest.mark.parametrize(
    "message", ["test warning", PyPLUTOWarning("test warning")]
)
def test_color_warning_formats_warning(message: str | PyPLUTOWarning) -> None:
    """Ensure a pyPLUTO warning, given as text or as an instance, is yellow."""
    c = Configure()
    result = c.color_warning(message, PyPLUTOWarning, "testfile.py", 42)
    assert result == (
        f"{YELLOW}PyPLUTOWarning: test warning[testfile.py:42]{RESET}\n"
    )


@pytest.mark.parametrize(
    ("colors", "category", "colored"),
    [
        ("PyPLUTO", PyPLUTOWarning, True),
        ("PyPLUTO", UserWarning, False),
        ("always", UserWarning, True),
        (None, PyPLUTOWarning, False),
    ],
    ids=["ours", "theirs", "always", "none"],
)
def test_color_warning_follows_the_colors_setting(
    colors: str | None, category: type[Warning], colored: bool
) -> None:
    """Format a warning under each colors setting.

    A warning left uncolored keeps Python's own format, word for word.
    """
    SETTINGS["colors"] = colors
    result = Configure().color_warning("text", category, "file.py", 7)
    python = cfg.PYTHON_FORMATWARNING("text", category, "file.py", 7, None)
    assert result.startswith(YELLOW) is colored
    assert (result == python) is not colored


# ---- Errors ----
def test_color_error_writes_colored_traceback_and_message(
    capsys: pytest.CaptureFixture[str],
) -> None:
    """Ensure a pyPLUTO error is written in red, with its traceback."""
    try:
        raise PyPLUTOError("something went wrong")
    except PyPLUTOError as exc:
        err = report_of(exc, capsys)

    assert err.startswith(f"{RED}Traceback (most recent call last):")
    assert "PyPLUTOError: something went wrong" in err
    assert err.endswith(RESET)


def test_color_error_keeps_the_chained_exception(
    capsys: pytest.CaptureFixture[str],
) -> None:
    """Raise an error from another and check both are reported.

    The hook used to print the frames and the message only, so the type of
    the error and the exception that caused it were lost.
    """
    try:
        try:
            raise KeyError("x")
        except KeyError as cause:
            raise ValueError("boom") from cause
    except ValueError as exc:
        err = report_of(exc, capsys)

    assert "KeyError: 'x'" in err
    assert "direct cause" in err
    assert "ValueError: boom" in err


@pytest.mark.parametrize(
    ("colors", "error", "colored"),
    [
        ("PyPLUTO", PyPLUTOError("ours"), True),
        ("PyPLUTO", ValueError("theirs"), False),
        ("always", ValueError("theirs"), True),
        (None, PyPLUTOError("ours"), False),
    ],
    ids=["ours", "theirs", "always", "none"],
)
def test_color_error_follows_the_colors_setting(
    capsys: pytest.CaptureFixture[str],
    colors: str | None,
    error: Exception,
    colored: bool,
) -> None:
    """Report an error under each colors setting."""
    SETTINGS["colors"] = colors
    assert report_of(error, capsys).startswith(RED) is colored


@pytest.mark.parametrize(
    ("errors", "shown"),
    [("short", False), ("full", True)],
    ids=["short", "full"],
)
def test_a_pypluto_error_hides_the_package_frames_when_short(
    capsys: pytest.CaptureFixture[str], errors: str, shown: bool
) -> None:
    """Report an error raised inside settings.py, short and full.

    Short keeps this file's frame and the message, and drops the frame of
    settings.py where the error was raised.
    """
    SETTINGS["errors"] = errors
    err = report_of(raised_inside_pypluto(), capsys)
    assert "test_configure.py" in err
    assert "Unknown value 'loud'" in err
    assert ("settings.py" in err) is shown


def raise_value_error() -> None:
    """Raise a built-in error from a function the test counts as pyPLUTO."""
    raise ValueError("a real bug")


def test_another_error_keeps_every_frame_when_short(
    monkeypatch: pytest.MonkeyPatch, capsys: pytest.CaptureFixture[str]
) -> None:
    """Count this folder as pyPLUTO and raise a ValueError from it.

    A short report is only for a PyPLUTOError: any other error may be a bug,
    so its frames inside the package stay.
    """
    monkeypatch.setattr(cfg, "PACKAGE", str(Path(__file__).parent))
    with pytest.raises(ValueError, match="a real bug") as info:
        raise_value_error()
    assert "raise_value_error" in report_of(info.value, capsys)


def test_user_frames_gives_none_when_every_frame_is_inside(
    monkeypatch: pytest.MonkeyPatch, capsys: pytest.CaptureFixture[str]
) -> None:
    """Count every file as pyPLUTO: no frame is left, only the message."""
    monkeypatch.setattr(cfg, "PACKAGE", "")
    error = raised_inside_pypluto()
    assert Configure.user_frames(error.__traceback__) is None
    err = report_of(error, capsys)
    assert "Traceback" not in err
    assert "PyPLUTOConfigError: Unknown value 'loud'" in err


def raise_internal_error() -> None:
    """Raise an internal error from a function the test counts as pyPLUTO."""
    raise PyPLUTOInternalError("a guard tripped")


def test_an_internal_error_is_full_and_asks_to_be_reported(
    monkeypatch: pytest.MonkeyPatch, capsys: pytest.CaptureFixture[str]
) -> None:
    """Count this folder as pyPLUTO and raise an internal error from it.

    It is a PyPLUTOError, but only a bug in pyPLUTO trips it: errors="short"
    keeps its frames, which are what fixing it needs, and the report ends
    asking to report it.
    """
    monkeypatch.setattr(cfg, "PACKAGE", str(Path(__file__).parent))
    with pytest.raises(PyPLUTOInternalError, match="a guard tripped") as info:
        raise_internal_error()
    err = report_of(info.value, capsys)
    assert "raise_internal_error" in err
    assert err.endswith(f"{cfg.BUG_REPORT}{RESET}")


def test_an_ordinary_pypluto_error_is_not_reported_as_a_bug(
    capsys: pytest.CaptureFixture[str],
) -> None:
    """Report a PyPLUTOError of the user's: no line about reporting a bug."""
    assert cfg.BUG_REPORT not in report_of(raised_inside_pypluto(), capsys)


# ---- The handlers ----
def test_setup_handlers_installs_both_handlers() -> None:
    """Ensure that both warning and error handlers are installed."""
    c = Configure()
    c.setup_handlers()
    assert warnings.formatwarning == c.color_warning
    assert sys.excepthook == c.color_error


def test_setup_handlers_puts_the_setting_in_front(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """Ensure the filter of the setting goes in front of the module one.

    filterwarnings puts each new filter first, so the last call wins: the
    warnings setting holds over the filter kept for the old warnings, which
    are not raised through PPWarn yet.
    """
    c = Configure()
    calls = []

    monkeypatch.setattr(
        warnings,
        "filterwarnings",
        lambda *args, **kwargs: calls.append((args, kwargs)),
    )

    c.setup_handlers()

    assert calls == [
        (("always",), {"module": "pyPLUTO"}),
        (("always",), {"category": PyPLUTOWarning}),
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


# ---- configure ----
def test_configure_without_keywords_gives_the_settings() -> None:
    """Call configure with nothing and get the settings in use, as a dict."""
    result = configure()
    assert isinstance(result, Settings)
    assert result == SETTINGS


def test_configure_changes_and_gives_back_the_new_settings() -> None:
    """Change two settings; the result already holds the new values."""
    result = configure(colors="always", text=True)
    assert SETTINGS["colors"] == "always"
    assert result["text"] == "verbose"


def test_a_wrong_value_changes_nothing() -> None:
    """Give one good and one wrong value: the error comes, and neither is
    stored, since every value is checked before any is.

    The wrong value is typed Any because a checker rightly refuses it: this
    is the check at runtime, for callers no checker sees.
    """
    before = dict(SETTINGS)
    wrong: Any = "long"
    with pytest.raises(PyPLUTOConfigError, match="'errors'"):
        configure(colors="always", errors=wrong)
    assert before == SETTINGS


def test_configure_in_a_with_restores_the_settings() -> None:
    """Change settings inside a with, and find the old ones after it."""
    before = dict(SETTINGS)
    with configure(text=False, errors="full") as inside:
        assert inside["text"] is False
        assert SETTINGS["errors"] == "full"
    assert before == SETTINGS


def test_warnings_error_turns_a_pypluto_warning_into_an_error() -> None:
    """Set warnings to error and raise a pyPLUTO warning: it is raised."""
    configure(warnings="error")
    with pytest.raises(PyPLUTOWarning, match="raised"):
        PPWarn.warn("raised", PyPLUTOBehaviorWarning)


def test_warnings_ignore_hides_a_pypluto_warning() -> None:
    """Set warnings to ignore and raise a pyPLUTO warning: nothing shows."""
    with warnings.catch_warnings(record=True) as caught:
        configure(warnings="ignore")
        PPWarn.warn("hidden", PyPLUTOBehaviorWarning)
    assert caught == []
