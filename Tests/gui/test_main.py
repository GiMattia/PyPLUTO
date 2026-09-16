"""Test of the gui/main.py file.

Two halves, matching the two things the module does.

The first half checks the message a user gets when Qt cannot be imported.
That message is the only thing standing between a failed install and a bare
"libEGL.so.1: cannot open shared object file", so it is worth pinning: which
of the two answers is given, and that the original error survives inside it.

The second half checks that the window is actually built and shown. Nothing
here starts a real event loop -- `app.exec()` would block until a human
closed the window -- so QApplication and the window are replaced by the two
stubs below, which record what was done to them.
"""

import importlib
import runpy
import sys

import pytest
from PySide6 import QtWidgets

from pyPLUTO.gui import main as main_mod
from pyPLUTO.gui import main_window as main_window_mod


class _FakeWindow:
    """Record what main() does to the window it builds.

    A stand-in for PyPLUTOApp, which would otherwise create real widgets. It
    answers the three things main() asks of a window and remembers each, so
    a test can check the sequence afterwards rather than watching it happen.
    """

    def __init__(self, code: str | None = None) -> None:
        self.code = code
        self.size: tuple[int, int] | None = None
        self.shown = False

    def resize(self, width: int, height: int) -> None:
        """Record the size main() asks for."""
        self.size = (width, height)

    def show(self) -> None:
        """Record that the window was shown."""
        self.shown = True


class _FakeApp:
    """Stand in for QApplication, without starting a real event loop.

    The whole reason main() cannot be called as it is: `exec()` blocks until
    the interface is closed, so a test calling the real one would hang.
    """

    def __init__(self, argv: list[str]) -> None:
        """Accept the argv that QApplication is given, and ignore it."""
        self.argv = argv

    def exec(self) -> int:
        """Return the exit code a finished event loop would give.

        Zero, as a clean exit would, which is what the tests then expect to
        see handed to sys.exit.
        """
        return 0


# ---- The error message ----
def test_missing_system_library_is_explained() -> None:
    """Name the system packages when a shared library is missing.

    This is the failure a Linux user hits after pip install: PySide6 is
    there, but libEGL is not, and the bare ImportError says nothing about
    what to install.
    """
    error = main_mod._gui_import_error(
        ImportError("libEGL.so.1: cannot open shared object file")
    )
    assert "apt install" in str(error)
    assert "libegl1" in str(error)
    assert "libxcb-cursor0" in str(error)


def test_missing_pyside_is_explained() -> None:
    """Check the other answer: the extra to install, not a system package.

    The two cases need opposite advice, and getting them the wrong way round
    would send a user to apt for a missing pip package. The second assertion
    is what pins that: the system hint must be absent, not merely the install
    hint present.
    """
    error = main_mod._gui_import_error(ImportError("No module named 'PySide6'"))
    assert "py-pluto[gui]" in str(error)
    assert "apt install" not in str(error)


def test_original_message_is_kept() -> None:
    """Check the original error text survives inside the new one.

    The advice is a guess based on the message; the message itself is the
    fact. Replacing it rather than wrapping it would leave a user with our
    guess and no way to see what actually failed.
    """
    error = main_mod._gui_import_error(ImportError("the original problem"))
    assert "the original problem" in str(error)


@pytest.mark.parametrize(
    "message",
    ["libEGL.so.1: cannot open", "MSVCP140.DLL not found"],
)
def test_shared_library_is_recognised(message: str) -> None:
    """Check a missing library is recognised on Linux and on Windows alike.

    The two cases are told apart by the file extension in the message, so
    both spellings have to be covered: `.so` on Linux, `.dll` on Windows.
    The Windows one is matched case-insensitively, which is why an uppercase
    name is used here.
    """
    assert "apt install" in str(
        main_mod._gui_import_error(ImportError(message))
    )


def test_import_without_pyside_raises_the_helpful_error() -> None:
    """Reimport the module with Qt blocked, and check the guard fires.

    The tests above call the helper directly; this one exercises the
    try/except around the import itself, which is the only thing that
    connects the helper to a real failure.

    Qt is blocked by putting None in sys.modules, which makes the import
    statement raise -- there is no other way to simulate a missing package in
    a process where it is installed. The blocked import reads as a missing
    module rather than a missing library, so the answer expected here is the
    install hint.

    Everything is restored in the finally block, including a final reload, or
    every later test in the session would see a half-broken module.
    """
    saved = sys.modules.get("PySide6.QtWidgets")
    # A None entry in sys.modules makes the import statement raise.
    sys.modules["PySide6.QtWidgets"] = None  # pyright: ignore[reportArgumentType]  # ty: ignore[invalid-assignment]
    try:
        with pytest.raises(ImportError, match="optional dependency"):
            importlib.reload(main_mod)
    finally:
        if saved is None:
            del sys.modules["PySide6.QtWidgets"]
        else:
            sys.modules["PySide6.QtWidgets"] = saved
        importlib.reload(main_mod)


# ---- Launching ----
def test_main_shows_the_window(monkeypatch: pytest.MonkeyPatch) -> None:
    """Call main() with Qt stubbed and check what it did to the window.

    Four things in order: the window was built with the right code, resized
    to the intended size, shown, and the exit code of the event loop was
    handed to sys.exit. A main() that forgot the `show()` would open nothing
    and raise nothing.

    QApplication, the window and sys.exit are all replaced: the first two so
    nothing real is created, and sys.exit because it would otherwise end the
    test run rather than the test.
    """
    built: list[_FakeWindow] = []

    def make_window(code: str | None = None) -> _FakeWindow:
        window = _FakeWindow(code)
        built.append(window)
        return window

    codes: list[int] = []
    monkeypatch.setattr(main_mod, "QApplication", _FakeApp)
    monkeypatch.setattr(main_mod, "PyPLUTOApp", make_window)
    monkeypatch.setattr(sys, "exit", codes.append)

    main_mod.main()

    (window,) = built
    assert window.code == "PLUTO"
    assert window.size == (1150, 720)
    assert window.shown
    assert codes == [0]


# runpy warns that the module is already in sys.modules, which is exactly what
# this test does on purpose: the fresh copy is wanted, the imported one stays.
@pytest.mark.filterwarnings("ignore:.*found in sys.modules:RuntimeWarning")
def test_running_as_a_script_launches(monkeypatch: pytest.MonkeyPatch) -> None:
    """Run the module as a script and check the window was launched.

    This is what the `pypluto` command does, and the only way to reach the
    `if __name__ == "__main__"` guard: importing the module, as every other
    test does, leaves that block alone.

    The subtlety is where the stubs go. `run_module` imports the module
    afresh under the name __main__, and that fresh copy does its own imports,
    so patching the already-imported `main_mod` would have no effect on it.
    The stubs are therefore placed on the modules it imports *from*:
    PySide6.QtWidgets and pyPLUTO.gui.main_window.
    """
    built: list[_FakeWindow] = []
    codes: list[int] = []

    def make_window(code: str | None = None) -> _FakeWindow:
        window = _FakeWindow(code)
        built.append(window)
        return window

    monkeypatch.setattr(QtWidgets, "QApplication", _FakeApp)
    monkeypatch.setattr(main_window_mod, "PyPLUTOApp", make_window)
    monkeypatch.setattr(sys, "exit", codes.append)

    runpy.run_module("pyPLUTO.gui.main", run_name="__main__")

    (window,) = built
    assert window.shown
    assert codes == [0]
