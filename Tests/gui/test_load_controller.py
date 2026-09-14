"""Test of the load_controller.py file."""

from pathlib import Path


def _items(selector):
    """Read back the entries of a Qt combo box."""
    return [selector.itemText(i) for i in range(selector.count())]


def _load(
    window,
    data_dir: Path,
    folder: str = "single_file",
    datatype: str = "dbl",
    nout: int | str = 0,
):
    """Point the window at a dataset and load it."""
    window.folder_path = str(data_dir / folder)
    window.datatype = datatype
    window.nout = nout
    window.load_controller.load_data()
    return window


# Loading a dataset marks the window as loaded
def test_load_data_sets_flag(window, data_dir: Path):
    assert _load(window, data_dir).data_loaded is True


# The variable selector is filled with the loaded variables
def test_load_data_fills_variables(window, data_dir: Path):
    items = _items(_load(window, data_dir).var_selector)
    assert "rho" in items
    assert "prs" in items


# The selector always offers the custom-variable entry last
def test_load_data_offers_custom_var(window, data_dir: Path):
    assert _items(_load(window, data_dir).var_selector)[-1] == "Custom var..."


# The axis selectors follow the geometry of the grid
def test_load_data_fills_axes(window, data_dir: Path):
    _load(window, data_dir)
    assert _items(window.xaxis_selector) == ["x", "y", "z"]
    assert _items(window.yaxis_selector) == ["y", "z", "x"]


# The info panel reports which folder was loaded
def test_load_data_fills_info(window, data_dir: Path):
    _load(window, data_dir)
    assert "single_file" in window.info_label.toPlainText()


# The time slider is enabled once there is something to scroll through
def test_load_data_enables_slider(window, data_dir: Path):
    _load(window, data_dir)
    assert window.time_slider.isEnabled() is True
    assert window.nout_display.isEnabled() is True


# A dataset with several outputs gives the slider a range to move over
def test_load_data_slider_range(window, data_dir: Path):
    _load(window, data_dir, folder="multiple_outputs", nout="last")
    assert window.time_slider.maximum() == 4


# A bad folder is reported as "not loaded" instead of raising
def test_load_data_failure(window, data_dir: Path):
    window.folder_path = str(data_dir / "does_not_exist")
    window.datatype = "dbl"
    window.nout = 0
    window.load_controller.load_data()
    assert window.data_loaded is False


# The path of a chosen file is split into folder, format and output number
def test_finalize_load_path(window, data_dir: Path):
    window.load_controller.finalize_load_path(
        str(data_dir / "single_file" / "data.0000.dbl")
    )
    assert window.folder_path == str(data_dir / "single_file")
    assert window.datatype == "dbl"
    assert window.nout == 0


# Reloading keeps the variable that was selected before
def test_reload_keeps_selection(window, data_dir: Path):
    """LONG TEST: CHECK"""
    _load(window, data_dir)
    window.var_selector.setCurrentText("prs")
    window.xaxis_selector.setCurrentText("y")

    window.load_controller.reload_data()

    assert window.var_selector.currentText() == "prs"
    assert window.xaxis_selector.currentText() == "y"


# Clearing the load panel resets it to its defaults
def test_clearload_resets_panel(window, data_dir: Path):
    """LONG TEST: CHECK"""
    _load(window, data_dir)
    window.frozen_lines.append({"label": "a"})

    window.load_controller.clearload()

    assert window.folder_path == "./"
    assert window.state.nout == 0
    assert window.frozen_lines == []
    assert window.time_slider.isEnabled() is False
    assert window.nout_display.isEnabled() is False
