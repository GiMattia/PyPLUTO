import numpy as np
import numpy.testing as npt
import pytest

from pyPLUTO.gui.custom_var_engine import (
    build_locals,
    evaluate_custom_var,
    frozen_var_names,
    normalize_expr,
    validate_lines_sequential,
)


class _DummyState:
    def __init__(self):
        self.d_vars = ["rho"]
        self.x1 = np.linspace(0.0, 1.0, 4)
        self.x2 = np.linspace(0.0, 1.0, 3)
        self.x3 = np.array([0.0])
        self.geom = "CARTESIAN"
        self.dim = 2
        self.nshp = (4, 3)


class _DummyLoad:
    def __init__(self):
        self.state = _DummyState()
        self.d_vars = self.state.d_vars
        self.geom = self.state.geom
        self.dim = self.state.dim
        self.nshp = self.state.nshp

        self.rho = np.ones((4, 3))
        self.x1 = self.state.x1
        self.x2 = self.state.x2
        self.x3 = self.state.x3


def test_evaluate_custom_var_assigns_array():
    d = _DummyLoad()
    out = evaluate_custom_var(d, "foo", "rho + 2", assign=True)
    assert hasattr(d, "foo")
    assert out.shape == (4, 3)
    assert np.allclose(np.asarray(out), 3.0)


def test_evaluate_custom_var_blocks_protected_name():
    d = _DummyLoad()
    with pytest.raises(ValueError, match="protected name"):
        evaluate_custom_var(d, "x1", "rho + 1", assign=False)


def test_validate_lines_sequential_allows_dependency():
    d = _DummyLoad()
    validate_lines_sequential(d, [("a", "rho + 1"), ("b", "a * 2")])


# The D. and Data. prefixes are stripped from an expression
@pytest.mark.parametrize("expr", ["D.rho", "Data.rho", "rho"])
def test_normalize_expr_strips_data_prefix(expr):
    assert normalize_expr(expr) == "rho"


# The numpy namespace is stripped too, so numexpr can read the expression
@pytest.mark.parametrize("expr", ["np.sqrt(D.rho)", "numpy.sqrt(rho)"])
def test_normalize_expr_strips_numpy_prefix(expr):
    assert normalize_expr(expr) == "sqrt(rho)"


# Surrounding blanks are removed
def test_normalize_expr_strips_blanks():
    assert normalize_expr("  rho + 1  ") == "rho + 1"


# An expression with nothing to strip is left alone
def test_normalize_expr_leaves_plain_expression():
    assert normalize_expr("rho * prs + 2") == "rho * prs + 2"


# The coordinate names are protected, so a custom variable cannot shadow them
def test_frozen_var_names():
    names = frozen_var_names(_DummyLoad())
    assert "x1" in names
    assert "x2" in names


# The namespace offered to an expression holds the loaded variables
def test_build_locals_contains_variables():
    local = build_locals(_DummyLoad())
    assert "rho" in local
    npt.assert_allclose(local["rho"], np.ones((4, 3)))


# The coordinates are offered to the expression as well
def test_build_locals_contains_coordinates():
    local = build_locals(_DummyLoad())
    assert "x1" in local


# An expression made only of numbers gives back a plain number
def test_evaluate_scalar_expression():
    result = evaluate_custom_var(_DummyLoad(), "two", "1 + 1", assign=False)
    assert result == 2


# An expression combining two variables is evaluated element by element
def test_evaluate_combines_variables():
    d = _DummyLoad()
    d.prs = np.full((4, 3), 2.0)
    d.state.d_vars = ["rho", "prs"]
    d.d_vars = d.state.d_vars
    out = evaluate_custom_var(d, "tot", "rho + prs", assign=False)
    npt.assert_allclose(np.asarray(out), 3.0)


# A name that does not exist cannot be used
def test_evaluate_unknown_name():
    with pytest.raises(ValueError, match="unknown name"):
        evaluate_custom_var(_DummyLoad(), "bad", "nosuchvar + 1", assign=False)


# An expression that is not valid python cannot be compiled
def test_evaluate_syntax_error():
    with pytest.raises(ValueError, match="compile error"):
        evaluate_custom_var(_DummyLoad(), "bad", "rho +", assign=False)


# Without assign the result is not stored on the dataset
def test_evaluate_without_assign():
    d = _DummyLoad()
    evaluate_custom_var(d, "foo", "rho + 1", assign=False)
    assert not hasattr(d, "foo")


# A later line can use a name defined by an earlier one
def test_validate_lines_sequential_order():
    validate_lines_sequential(_DummyLoad(), [("a", "rho + 1"), ("b", "a * 2")])


# Using a name before it is defined is refused
def test_validate_lines_sequential_wrong_order():
    with pytest.raises(ValueError):
        validate_lines_sequential(_DummyLoad(), [("b", "a * 2"), ("a", "rho")])


# A protected name cannot be redefined in a sequence either
def test_validate_lines_sequential_protected_name():
    with pytest.raises(ValueError, match="protected and cannot be redefined"):
        validate_lines_sequential(_DummyLoad(), [("x1", "rho + 1")])
