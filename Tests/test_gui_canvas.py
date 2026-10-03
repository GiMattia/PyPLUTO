"""Regression tests for the GUI canvas backend."""

import importlib.util
from pathlib import Path


def _source(module: str) -> str:
    spec = importlib.util.find_spec(module)
    assert spec is not None and spec.origin is not None
    return Path(spec.origin).read_text()


def test_plot_controller_canvas_uses_qtagg():
    """Regression: FigureCanvas must be FigureCanvasQTAgg (has Agg renderer).

    FigureCanvasQT alone has no Agg renderer and produces a blank canvas.
    """
    src = _source("pyPLUTO.gui.plot_controller")
    assert "backend_qtagg" in src
    assert "FigureCanvasQTAgg" in src


def test_main_window_canvas_annotation_uses_qtagg():
    """Regression: main_window FigureCanvas annotation must match plot_controller.

    Previously imported from backend_template (a no-op stub), which is not a
    QWidget and caused a pyright type error.
    """
    src = _source("pyPLUTO.gui.main_window")
    assert "backend_qtagg" in src
    assert "backend_template" not in src
