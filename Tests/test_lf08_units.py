"""Tests for the add_units method of the Load class."""

import os
from pathlib import Path

import numpy as np
import pytest

import pyPLUTO as pp

astropy = pytest.importorskip("astropy")
import astropy.units as u  # noqa: E402

# Assuming the root of the repo is your current working directory
repo_root = Path(os.getcwd())
repo_root = repo_root if repo_root.name == "Tests" else repo_root / "Tests"
path = repo_root / "Test_load"


@pytest.fixture(scope="module")
def data():
    """Load data fixture."""
    return pp.Load(0, path=path / "single_file", text=False)


def test_add_units_string_var_string_unit(data):
    """Test add_units with string variable name and string unit."""
    result = data.add_units("rho", "g/cm**3")
    assert isinstance(result, u.Quantity)
    assert result.unit == u.Unit("g/cm**3")
    np.testing.assert_array_equal(result.value, data.rho)


def test_add_units_array_var_unit_object(data):
    """Test add_units with numpy array and astropy unit object."""
    result = data.add_units(data.vx1, u.cm / u.s)
    assert isinstance(result, u.Quantity)
    assert result.unit == u.cm / u.s
    np.testing.assert_array_equal(result.value, data.vx1)


def test_add_units_string_var_unit_object(data):
    """Test add_units with string variable name and astropy unit object."""
    result = data.add_units("prs", u.dyn / u.cm**2)
    assert isinstance(result, u.Quantity)
    assert result.unit == u.dyn / u.cm**2
    np.testing.assert_array_equal(result.value, data.prs)


def test_add_units_grid_variable(data):
    """Test add_units with a grid variable."""
    result = data.add_units("x1", u.cm)
    assert isinstance(result, u.Quantity)
    assert result.unit == u.cm
    np.testing.assert_array_equal(result.value, data.x1)


def test_add_units_preserves_shape(data):
    """Test that add_units preserves the array shape."""
    result = data.add_units("rho", u.g / u.cm**3)
    assert result.shape == data.rho.shape


def test_add_units_invalid_var(data):
    """Test that add_units raises AttributeError for unknown variable."""
    with pytest.raises(AttributeError):
        data.add_units("nonexistent_var", u.g / u.cm**3)
