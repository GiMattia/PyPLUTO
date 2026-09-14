"""Test of the loadtools.py file."""

from pathlib import Path

import numpy as np
import numpy.testing as npt
import pytest

import pyPLUTO as pp
from pyPLUTO.toolfuncs.loadtools import LoadToolsManager


def _manager(data_dir: Path):
    Data = pp.Load(path=data_dir / "single_file", text=False)
    return LoadToolsManager(Data.state), Data


# An array is returned unchanged
def test_check_var_array(data_dir: Path):
    manager, _ = _manager(data_dir)
    npt.assert_array_equal(manager.check_var(np.array([1, 2, 3])), [1, 2, 3])


# A string is looked up in the dataset
def test_check_var_string(data_dir: Path):
    manager, Data = _manager(data_dir)
    npt.assert_array_equal(manager.check_var("rho"), Data.rho)


# The transpose keyword flips the array
def test_check_var_transpose(data_dir: Path):
    manager, _ = _manager(data_dir)
    var = np.array([[1, 2], [3, 4]])
    npt.assert_array_equal(manager.check_var(var, transpose=True), var.T)


# Anything that is not an array raises an error
def test_check_var_wrong_type(data_dir: Path):
    manager, _ = _manager(data_dir)
    with pytest.raises(TypeError):
        manager.check_var(42)


# Downsampling returns the requested shape
def test_congrid_smaller(data_dir: Path):
    manager, _ = _manager(data_dir)
    out = manager.congrid(np.arange(16.0).reshape(4, 4), (2, 2))
    assert out.shape == (2, 2)


# Upsampling returns the requested shape
def test_congrid_larger(data_dir: Path):
    manager, _ = _manager(data_dir)
    out = manager.congrid(np.arange(16.0).reshape(4, 4), (8, 8))
    assert out.shape == (8, 8)


# A constant array stays constant after resampling
def test_congrid_constant(data_dir: Path):
    manager, _ = _manager(data_dir)
    out = manager.congrid(np.full((4, 4), 5.0), (6, 6))
    npt.assert_allclose(out, 5.0)


# The spline method is also available
def test_congrid_spline(data_dir: Path):
    manager, _ = _manager(data_dir)
    out = manager.congrid(
        np.arange(16.0).reshape(4, 4), (8, 8), method="spline"
    )
    assert out.shape == (8, 8)


# Resampling to the same size gives back the same values
def test_congrid_identity(data_dir: Path):
    manager, _ = _manager(data_dir)
    arr = np.arange(16.0).reshape(4, 4)
    npt.assert_allclose(manager.congrid(arr, (4, 4)), arr)


# A mismatch between the array and the new dimensions raises an error
def test_congrid_dimension_mismatch(data_dir: Path):
    manager, _ = _manager(data_dir)
    with pytest.raises(ValueError):
        manager.congrid(np.arange(16.0).reshape(4, 4), (2, 2, 2))


# The center keyword is accepted and keeps the requested shape
def test_congrid_center(data_dir: Path):
    manager, _ = _manager(data_dir)
    out = manager.congrid(np.arange(16.0).reshape(4, 4), (3, 3), center=True)
    assert out.shape == (3, 3)
