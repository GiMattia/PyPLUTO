"""Test of the state_accessors.py file."""

import numpy as np
import pytest

from pyPLUTO.gui.app_state import AppState
from pyPLUTO.gui.state_accessors import StateAccessorsMixin


class _Window(StateAccessorsMixin):
    """The smallest object that can use the accessors: it only has a state."""

    def __init__(self):
        self.state = AppState()


# Every value the GUI reads and writes goes through to the state
@pytest.mark.parametrize(
    ("name", "value"),
    [
        ("data_loaded", True),
        ("datadict", {"rho": 1}),
        ("datatype", "dbl"),
        ("firstplot", False),
        ("folder_path", "/tmp/data"),
        ("nout", 7),
        ("numlines", 3),
        ("vardim", 2),
        ("xmax", 1.5),
        ("xmin", -1.5),
        ("ymax", 2.5),
        ("ymin", -2.5),
    ],
)
def test_accessors_write_to_state(name, value):
    window = _Window()
    setattr(window, name, value)
    assert getattr(window.state, name) == value
    assert getattr(window, name) == value


# The loaded dataset and the image are stored as they are
def test_data_and_image_accessors():
    window = _Window()
    window.Data = "dataset"
    window.Image = "image"
    assert window.state.Data == "dataset"
    assert window.state.Image == "image"


# The plotted variable is stored as an array
def test_var_accessor():
    window = _Window()
    window.var = np.ones(4)
    assert window.state.var.shape == (4,)


# The line lists are read directly from the state
def test_line_lists_are_read_only_views():
    window = _Window()
    window.state.frozen_lines.append({"label": "a"})
    window.state.live_specs.append({"label": "b"})
    assert window.frozen_lines == [{"label": "a"}]
    assert window.live_specs == [{"label": "b"}]
