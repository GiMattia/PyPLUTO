"""Pytest configuration for test stability across CI environments."""

import os
from collections.abc import Generator
from pathlib import Path

# Enforce a non-GUI backend so tests do not depend on system Tcl/Tk packages.
os.environ.setdefault("MPLBACKEND", "Agg")

# Enforce an offscreen Qt platform so the GUI tests need no display.
os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")

import matplotlib
import matplotlib.pyplot as plt
import pytest
from PySide6.QtWidgets import QApplication

from pyPLUTO.gui.main_window import PyPLUTOApp

matplotlib.use("Agg")


@pytest.fixture(scope="session")
def data_dir() -> Path:
    """Give the folder holding the PLUTO outputs used by the tests.

    It is built from the location of this file, so the tests find their data
    whatever directory pytest is launched from.
    """
    return Path(__file__).parent / "Test_load"


@pytest.fixture(scope="session")
def qapp() -> QApplication:
    """Give the GUI tests the single QApplication that Qt allows."""
    app = QApplication.instance()
    if app is None:
        app = QApplication([])
    assert isinstance(app, QApplication)
    return app


@pytest.fixture
def window(qapp: QApplication) -> Generator[PyPLUTOApp, None, None]:
    """Build a GUI main window, and close it once the test is done."""
    app = PyPLUTOApp()
    yield app
    app.close()
    # The window's figure is registered in pyplot as figure 1; once the window
    # is garbage-collected its Qt toolbar is deleted, and the next pp.Image()
    # would fetch that dead figure through plt.figure(1). Drop it from pyplot.
    plt.close("all")
