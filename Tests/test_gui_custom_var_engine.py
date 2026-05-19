import numpy as np
import pytest

from pyPLUTO.gui.custom_var_engine import (
    evaluate_custom_var,
    validate_lines_sequential,
)


class _DummyState:
    def __init__(self):
        self.x1 = np.linspace(0.0, 1.0, 4)
        self.x2 = np.linspace(0.0, 1.0, 3)
        self.x3 = np.array([0.0])


class _DummyLoad:
    def __init__(self):
        self._load_vars = ["rho"]
        self.geom = "CARTESIAN"
        self.dim = 2
        self.nshp = (4, 3)
        self.state = _DummyState()
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
