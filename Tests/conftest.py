"""Pytest configuration for test stability across CI environments.

A conftest.py is imported by pytest before it collects anything, and the
fixtures defined in it are available to every test file in its directory and
below without being imported. That makes this the right place for two kinds
of thing: the shared fixtures, and the few settings that have to be applied
before PyPLUTO is imported at all.

The settings come first in the file for that reason, and the order matters:
matplotlib and Qt both decide which backend to use when they are first
imported, so an environment variable set afterwards would come too late.

The suite has to run unattended -- in CI, on a machine with no screen and no
window manager -- and still exercise the GUI. Nothing here mocks Qt away: the
windows are real, they are simply drawn offscreen.
"""

import os
from collections.abc import Generator
from pathlib import Path

# Enforce a non-GUI backend so tests do not depend on system Tcl/Tk packages.
os.environ.setdefault("MPLBACKEND", "Agg")

# Enforce an offscreen Qt platform so the GUI tests need no display.
os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")

# Imported after the two variables above, which they read on import.
# setdefault rather than assignment, so a developer can override either from
# the shell to watch the tests draw on a real screen.
import matplotlib
import matplotlib.pyplot as plt
import pytest
from PySide6.QtWidgets import QApplication

from pyPLUTO.gui.main_window import PyPLUTOApp

# Belt and braces: MPLBACKEND is read at import, but a plugin or a stray
# import elsewhere could already have chosen another backend.
matplotlib.use("Agg")


@pytest.fixture(scope="session")
def data_dir() -> Path:
    """Give the folder holding the PLUTO outputs used by the tests.

    It is built from the location of this file, so the tests find their data
    whatever directory pytest is launched from.

    The folder holds one subfolder per case (single_file, multiple_outputs,
    particles_cr, ...), and a test asks for the one it needs by joining the
    name onto what this returns.
    """
    return Path(__file__).parent / "Test_load"


@pytest.fixture(scope="session")
def qapp() -> QApplication:
    """Give the GUI tests the single QApplication that Qt allows.

    Qt permits one QApplication per process and refuses a second, so this is
    session-scoped: it is built on first use and the same instance is handed
    to every test that asks for it. The `instance()` check also picks up an
    application that something else created first.

    A test rarely uses this fixture directly. It is requested by the `window`
    fixture below, which is what creates widgets -- but a QApplication has to
    exist before any widget does.
    """
    app = QApplication.instance()
    if app is None:
        app = QApplication([])
    assert isinstance(app, QApplication)
    return app


@pytest.fixture
def window(qapp: QApplication) -> Generator[PyPLUTOApp, None, None]:
    """Build a GUI main window, and close it once the test is done.

    Function-scoped, unlike `qapp`: each test gets a window of its own, so
    one test cannot leave a loaded dataset or a drawn figure behind for the
    next. Asking for `qapp` as an argument is what guarantees the
    QApplication exists first.

    Everything after the `yield` is the teardown, and it runs even when the
    test fails.
    """
    app = PyPLUTOApp()
    yield app
    app.close()
    # The window's figure is registered in pyplot as figure 1; once the window
    # is garbage-collected its Qt toolbar is deleted, and the next pp.Image()
    # would fetch that dead figure through plt.figure(1). Drop it from pyplot.
    plt.close("all")
