"""Regression tests for the GUI canvas backend."""

import os

import pytest


def test_plot_controller_canvas_has_agg_renderer():
    """FigureCanvas used by PlotController must subclass FigureCanvasAgg.

    Regression: FigureCanvasQT (no Agg renderer) was used, producing a blank canvas.
    """
    pytest.importorskip("PySide6")
    os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")
    from matplotlib.backends.backend_agg import FigureCanvasAgg

    import pyPLUTO.gui.plot_controller as pc

    assert issubclass(pc.FigureCanvas, FigureCanvasAgg)


def test_main_window_canvas_annotation_matches_plot_controller():
    """The FigureCanvas type annotation in main_window must match plot_controller.

    Regression: main_window imported FigureCanvas from backend_template (a no-op
    stub unrelated to FigureCanvasQTAgg), causing a type mismatch.
    """
    pytest.importorskip("PySide6")
    os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")

    import pyPLUTO.gui.main_window as mw
    import pyPLUTO.gui.plot_controller as pc

    assert mw.FigureCanvas is pc.FigureCanvas
