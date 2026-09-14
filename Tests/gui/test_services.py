import numpy as np
import numpy.testing as npt
import pytest

from pyPLUTO.gui.services import (
    apply_slices,
    axis_labels_for_geom,
    convert_axis_map,
    custom_var_lines,
    filtered_loaded_vars,
    grid_shape_candidates,
    loaded_step_repr,
    parse_selected_file,
    parse_slice_expr,
    parse_vars_text,
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


# An empty text means "load every variable"
def test_parse_vars_text_empty():
    assert parse_vars_text("") is True


# Names can be separated by commas, dashes or spaces
@pytest.mark.parametrize(
    "text", ["rho,prs", "rho, prs", "rho-prs", "rho - prs"]
)
def test_parse_vars_text_separators(text):
    assert parse_vars_text(text) == ["rho", "prs"]


# A single name still comes back as a list
def test_parse_vars_text_single():
    assert parse_vars_text("rho") == ["rho"]


# A 1D grid size is wrapped into a one-element shape
def test_grid_shape_candidates_scalar():
    assert grid_shape_candidates(400) == {(400,)}


# A 2D grid also accepts the transposed layout
def test_grid_shape_candidates_reversed():
    assert grid_shape_candidates((4, 3)) == {(4, 3), (3, 4)}


# A square grid has only one possible layout
def test_grid_shape_candidates_square():
    assert grid_shape_candidates((4, 4)) == {(4, 4)}


# A single output number is reported as a plain integer
def test_loaded_step_repr_scalar():
    assert loaded_step_repr(3) == 3


# Several output numbers are reported as a list
def test_loaded_step_repr_array():
    assert loaded_step_repr(np.array([0, 2])) == [0, 2]


# An array holding a single output is unwrapped again
def test_loaded_step_repr_single_element_array():
    assert loaded_step_repr(np.array([4])) == 4


# A custom variable is shown as "name = expression"
def test_custom_var_lines_pair():
    assert custom_var_lines([("a", "rho + 1")]) == ["a = rho + 1"]


# When a display form is stored, that is the one shown
def test_custom_var_lines_triplet():
    assert custom_var_lines([("a", "rho+1", "rho + 1")]) == ["a = rho + 1"]


# In cartesian geometry the axes map straight onto x1, x2, x3
def test_convert_axis_map_cartesian_1D():
    assert convert_axis_map("CARTESIAN", 1) == {
        "x": "x1",
        "y": "x2",
        "z": "x3",
    }


# For 2D variables the cell interfaces are used instead of the centers
def test_convert_axis_map_cartesian_2D():
    assert convert_axis_map("CARTESIAN", 2)["x"] == "x1r"


# In polar geometry the radius and angle are offered as well
def test_convert_axis_map_polar():
    axes = convert_axis_map("POLAR", 1)
    assert axes["R"] == "x1"
    assert axes["phi"] == "x2"


# In spherical geometry the polar angle is offered too
def test_convert_axis_map_spherical():
    assert convert_axis_map("SPHERICAL", 1)["theta"] == "x2"


# An empty slice expression leaves the array untouched
def test_apply_slices_none():
    var = np.ones((4, 3))
    out, xs, ys, zs = apply_slices(var, "", "", "")
    assert out.shape == (4, 3)
    assert (xs, ys, zs) == (None, None, None)


# A single index takes one row out of the array
def test_apply_slices_index():
    var = np.arange(12).reshape(4, 3)
    out, xslice, _, _ = apply_slices(var, "1", "", "")
    npt.assert_array_equal(out, var[1])
    assert xslice == 1


# A range expression keeps a block of the array
def test_apply_slices_range():
    var = np.arange(12).reshape(4, 3)
    out, _, _, _ = apply_slices(var, "1:3", "", "")
    npt.assert_array_equal(out, var[1:3])


# The y-direction can be sliced as well
def test_apply_slices_second_axis():
    var = np.arange(12).reshape(4, 3)
    out, _, yslice, _ = apply_slices(var, "", "2", "")
    npt.assert_array_equal(out, var[:, 2])
    assert yslice == 2


# The z-direction is only sliced on 3D arrays
def test_apply_slices_third_axis():
    var = np.arange(24).reshape(2, 3, 4)
    out, _, _, zslice = apply_slices(var, "", "", "1")
    npt.assert_array_equal(out, var[:, :, 1])
    assert zslice == 1


# An expression that makes no sense selects nothing
def test_parse_slice_expr_invalid():
    assert parse_slice_expr("not a slice") is None


# A full slice is understood as such
def test_parse_slice_expr_full():
    assert parse_slice_expr(":") == slice(None)
