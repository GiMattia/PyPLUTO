"""Main GUI module.

The entry point of the graphical interface: the `pypluto` console command and
`python -m pyPLUTO.gui.main` both end up in `main()` below.

It does two things. It builds and shows the window, and it makes a failed Qt
import say something a user can act on, which matters because the GUI is an
optional extra that needs pieces pip cannot install.
"""

from __future__ import annotations

import sys

# PySide6 is an optional dependency, and on Linux it links against system
# GL/EGL libraries that no Python wheel is allowed to install. Both failures
# reach this module as an ImportError, which on its own says only
# "libEGL.so.1: cannot open shared object file" and leaves the user stuck.
_INSTALL_HINT = (
    "The PyPLUTO GUI needs PySide6, which is an optional dependency.\n"
    "Install it with:  pip install py-pluto[gui]"
)

_SYSTEM_LIBS_HINT = (
    "PySide6 is installed, but a system library it needs is missing. Qt "
    "links against libraries that cannot ship inside a Python wheel, so "
    "they have to come from the system package manager. On Debian/Ubuntu:\n"
    "  sudo apt install libegl1 libgl1 libxkbcommon-x11-0 libxcb-cursor0 "
    "libxcb-icccm4 libxcb-keysyms1 libxcb-randr0 libxcb-render-util0 "
    "libxcb-shape0 libxcb-xinerama0\n"
    "Other distributions ship the same libraries under similar names."
)


def _gui_import_error(err: ImportError) -> ImportError:
    """Turn a failed PySide6 import into a message that says what to do.

    A missing shared library and a missing PySide6 both arrive here as an
    ImportError, but they need opposite answers, so they are told apart by
    the library file named in the original message.

    Parameters
    ----------
    - err (not optional): ImportError
        The error raised while importing PySide6.

    Returns
    -------
    - ImportError

    Examples
    --------
    - Example #1: explain a missing system library

        >>> _gui_import_error(ImportError("libEGL.so.1: cannot open"))

    """
    # A missing shared library names a file; a missing package does not.
    missing_library = ".so" in str(err) or ".dll" in str(err).lower()
    hint = _SYSTEM_LIBS_HINT if missing_library else _INSTALL_HINT

    # The original message comes first, so the real cause is never hidden.
    return ImportError(f"{err}\n\n{hint}")


# Imported here rather than inside main(), so a broken installation is
# reported when the module is loaded rather than after a window was expected.
try:
    from PySide6.QtWidgets import QApplication
except ImportError as err:
    raise _gui_import_error(err) from err

# Imported after the guard above, and not before it: main_window imports Qt
# itself, so importing it first would raise the bare ImportError that the
# guard exists to replace.
from pyPLUTO.gui.main_window import PyPLUTOApp  # noqa: E402


def main() -> None:
    """Launch the PyPLUTO GUI application.

    Builds the one QApplication Qt allows per process, shows the window, and
    hands control over: `app.exec()` returns only when the last window is
    closed, and its value becomes the exit code of the process.

    Returns
    -------
    - None

    Examples
    --------
    - Example #1: what the `pypluto` command runs

        >>> main()

    """
    app = QApplication(sys.argv)
    window = PyPLUTOApp(code="PLUTO")
    window.resize(1150, 720)
    window.show()

    # exec() blocks here for the life of the interface.
    sys.exit(app.exec())


if __name__ == "__main__":
    # Reached only when the file is run as a script; importing it, as the
    # console command and the tests do, leaves this alone.
    main()
