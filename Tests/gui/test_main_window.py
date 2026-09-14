"""Test of the main_window.py file."""

import importlib.util
from pathlib import Path

import pytest
from PySide6.QtWidgets import QApplication

from pyPLUTO.gui.main_window import PyPLUTOApp


def _source(module: str) -> str:
    spec = importlib.util.find_spec(module)
    assert spec is not None and spec.origin is not None
    return Path(spec.origin).read_text(encoding="utf-8")


# Without arguments the window is built for PLUTO
def test_default_code(window: PyPLUTOApp) -> None:
    assert window.code == "PLUTO"


# The PLUTO window has the plain title, with no code suffix
def test_default_title(window: PyPLUTOApp) -> None:
    assert window.windowTitle() == "PyPLUTO GUI"


# Any other code is not supported yet, and says so explicitly
def test_unsupported_code(qapp: QApplication) -> None:
    with pytest.raises(NotImplementedError, match="Code ECHO not yet"):
        PyPLUTOApp(code="ECHO")


def test_main_window_canvas_annotation_uses_qtagg() -> None:
    """Regression: main_window FigureCanvas annotation must match plot_controller.

    Previously imported from backend_template (a no-op stub), which is not a
    QWidget and caused a pyright type error.
    """
    src = _source("pyPLUTO.gui.main_window")
    assert "backend_qtagg" in src
    assert "backend_template" not in src
