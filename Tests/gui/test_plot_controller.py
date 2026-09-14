"""Test of the plot_controller.py file."""

import importlib.util
from pathlib import Path

import numpy.testing as npt


def _source(module: str) -> str:
    spec = importlib.util.find_spec(module)
    assert spec is not None and spec.origin is not None
    return Path(spec.origin).read_text(encoding="utf-8")


def test_plot_controller_canvas_uses_qtagg():
    """Regression: FigureCanvas must be FigureCanvasQTAgg (has Agg renderer).

    FigureCanvasQT alone has no Agg renderer and produces a blank canvas.
    """
    src = _source("pyPLUTO.gui.plot_controller")
    assert "backend_qtagg" in src
    assert "FigureCanvasQTAgg" in src


def _loaded(window, data_dir: Path, var="rho"):
    """Load the 2D test dataset and select one variable."""
    window.folder_path = str(data_dir / "single_file")
    window.datatype = "dbl"
    window.nout = 0
    window.load_controller.load_data()
    window.var_selector.setCurrentText(var)
    return window


def _plot_1d(window, index="10"):
    """Slice the 2D variable down to a line and plot it."""
    window.xslicetext.setText(index)
    window.plot_controller.plot_data()
    return window


# The colormap selector is filled with the available colormaps
def test_update_cmap_selector(window):
    window.plot_controller.update_cmap_selector()
    assert window.cmap_selector.count() > 0


# A 2D variable is drawn as a colormap
def test_plot_2D(window, data_dir: Path):
    _loaded(window, data_dir)
    window.plot_controller.plot_data()
    assert window.vardim == 2
    assert len(window.Image.ax[0].collections) > 0


# The plotted values are the values of the selected variable
def test_plot_2D_uses_selected_variable(window, data_dir: Path):
    _loaded(window, data_dir)
    window.plot_controller.plot_data()
    npt.assert_allclose(window.var, window.Data.rho)


# Slicing the variable turns it into a line
def test_plot_1D_after_slice(window, data_dir: Path):
    _loaded(window, data_dir)
    _plot_1d(window)
    assert window.vardim == 1
    assert len(window.Image.ax[0].get_lines()) == 1


# The plotted line is the requested slice of the variable
def test_plot_1D_values(window, data_dir: Path):
    _loaded(window, data_dir)
    _plot_1d(window, index="10")
    npt.assert_allclose(window.var, window.Data.rho[10])


# Transposing swaps the two axes of the variable
def test_plot_transpose(window, data_dir: Path):
    _loaded(window, data_dir)
    window.transpose_checkbox.setChecked(True)
    window.plot_controller.plot_data()
    npt.assert_allclose(window.var, window.Data.rho.T)


# Plotting without data loaded does nothing instead of raising
def test_plot_without_data(window):
    window.plot_controller.plot_data()
    assert window.data_loaded is False


# Overplotting adds a second line rather than replacing the first
def test_overplot_adds_a_line(window, data_dir: Path):
    """LONG TEST: CHECK"""
    _loaded(window, data_dir)
    _plot_1d(window, index="10")
    assert window.numlines == 1

    window.overplot_checkbox.setChecked(True)
    _plot_1d(window, index="20")

    assert window.numlines == 2
    assert len(window.Image.ax[0].get_lines()) == 2


# Locking freezes the drawn lines and empties the live list
def test_lock_lines(window, data_dir: Path):
    """LONG TEST: CHECK"""
    _loaded(window, data_dir)
    _plot_1d(window)
    assert len(window.live_specs) == 1

    window.plot_controller.lock_lines()

    assert len(window.frozen_lines) == 1
    assert window.live_specs == []
    assert window.overplot_checkbox.isChecked() is True


# A frozen line keeps the data it had when it was locked
def test_lock_lines_keeps_data(window, data_dir: Path):
    _loaded(window, data_dir)
    _plot_1d(window, index="10")
    window.plot_controller.lock_lines()
    npt.assert_allclose(window.frozen_lines[0]["ydata"], window.Data.rho[10])


# Locking with nothing plotted only reports it in the info panel
def test_lock_lines_without_lines(window, data_dir: Path):
    _loaded(window, data_dir)
    window.plot_controller.lock_lines()
    assert window.frozen_lines == []
    assert "Nothing to lock" in window.info_label.toPlainText()


# Locking without data loaded is reported too
def test_lock_lines_without_data(window):
    window.plot_controller.lock_lines()
    assert "No data loaded" in window.info_label.toPlainText()


# A replay redraws both the frozen lines and the live ones
def test_replay_all(window, data_dir: Path):
    """LONG TEST: CHECK"""
    _loaded(window, data_dir)
    _plot_1d(window, index="10")
    window.plot_controller.lock_lines()
    _plot_1d(window, index="20")

    window.plot_controller.replay_all()

    assert len(window.Image.ax[0].get_lines()) == 2
    assert len(window.frozen_lines) == 1
    assert len(window.live_specs) == 1


# A new figure starts from a clean canvas
def test_create_new_figure(window, data_dir: Path):
    _loaded(window, data_dir)
    window.plot_controller.plot_data()
    window.plot_controller.create_new_figure()
    assert window.firstplot is True


# Reloading the canvas removes what was drawn on it
def test_reload_canvas(window, data_dir: Path):
    _loaded(window, data_dir)
    window.plot_controller.plot_data()
    window.plot_controller.reload_canvas()
    assert window.figure.axes == []


# The captured spec records what is needed to redraw the plot
def test_capture_spec(window, data_dir: Path):
    _loaded(window, data_dir)
    _plot_1d(window)
    spec = window.plot_controller._capture_spec()
    assert spec["var_name"] == "rho"
    assert "axis_x" in spec
    assert "axis_y" in spec
