import numpy as np

from pyPLUTO.gui.services import (
    axis_labels_for_geom,
    filtered_loaded_vars,
    parse_selected_file,
    parse_slice_expr,
)


class _DummyLoad:
    def __init__(self):
        self.nshp = (4, 3)
        self.load_vars = ["rho", "prs", "bad"]
        self.rho = np.ones((4, 3))
        self.prs = np.ones((3, 4))
        self.bad = np.ones((2,))


def test_parse_selected_file_dbl_h5():
    folder, datatype, nout = parse_selected_file("/tmp/data.0012.dbl.h5")
    assert folder == "/tmp"
    assert datatype == "dbl.h5"
    assert nout == 12


def test_parse_selected_file_fallback():
    folder, datatype, nout = parse_selected_file("/tmp/grid.out")
    assert folder == "/tmp"
    assert datatype == "out"
    assert nout == "last"


def test_parse_slice_expr():
    assert parse_slice_expr("2") == 2
    s = parse_slice_expr("1:5:2")
    assert isinstance(s, slice)
    assert s.start == 1 and s.stop == 5 and s.step == 2


def test_axis_labels_for_geom():
    x, y = axis_labels_for_geom("CARTESIAN")
    assert x == ["x", "y", "z"]
    assert y == ["y", "z", "x"]


def test_filtered_loaded_vars_accepts_direct_and_reversed_shapes():
    d = _DummyLoad()
    out = filtered_loaded_vars(d)
    assert "rho" in out
    assert "prs" in out
    assert "bad" not in out
