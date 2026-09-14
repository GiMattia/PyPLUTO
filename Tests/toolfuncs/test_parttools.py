"""Test of the parttools.py file."""

from pathlib import Path

import numpy as np
import numpy.testing as npt
import pytest

import pyPLUTO as pp
from pyPLUTO.toolfuncs.parttools import PartToolsManager

var = np.arange(1.0, 11.0)


def _manager(data_dir: Path):
    Data = pp.LoadPart(0, path=data_dir / "particles_cr", text=False)
    return PartToolsManager(Data.state)


# The spectrum returns one histogram value per bin
def test_spectrum_shape(data_dir: Path):
    hist, bins = _manager(data_dir).spectrum(var, bins=5)
    assert hist.shape == (5,)
    assert bins.shape == (5,)


# A normalized spectrum integrates to one
def test_spectrum_normalized(data_dir: Path):
    hist, bins = _manager(data_dir).spectrum(var, bins=5)
    npt.assert_allclose(hist.sum() * (bins[1] - bins[0]), 1.0)


# The bins are the centers, so they stay inside the data range
def test_spectrum_bin_centers(data_dir: Path):
    _, bins = _manager(data_dir).spectrum(var, bins=5)
    assert bins[0] > var.min()
    assert bins[-1] < var.max()


# The logarithmic scale is also available
def test_spectrum_log_scale(data_dir: Path):
    hist, bins = _manager(data_dir).spectrum(var, scale="log", bins=4)
    assert hist.shape == (4,)
    assert bins.shape == (4,)


# Explicit bounds restrict the range of the spectrum
def test_spectrum_vmin_vmax(data_dir: Path):
    _, bins = _manager(data_dir).spectrum(var, vmin=2.0, vmax=8.0, bins=6)
    assert bins[0] > 2.0
    assert bins[-1] < 8.0


# A callable condition selects the matching indices
def test_select_callable(data_dir: Path):
    indx = _manager(data_dir).select(var, lambda v: v > 7.0)
    npt.assert_array_equal(indx, [7, 8, 9])


# A string condition works too, but warns about the use of eval
def test_select_string_warns(data_dir: Path):
    with pytest.warns(UserWarning, match="callable"):
        indx = _manager(data_dir).select(var, "> 7.0")
    npt.assert_array_equal(indx, [7, 8, 9])


# Sorting returns the indices ordered by the variable value
def test_select_sorted_descending(data_dir: Path):
    indx = _manager(data_dir).select(
        var, lambda v: v > 7.0, sort=True, ascending=False
    )
    npt.assert_array_equal(indx, [9, 8, 7])


# Sorting in ascending order is the default
def test_select_sorted_ascending(data_dir: Path):
    indx = _manager(data_dir).select(var, lambda v: v > 7.0, sort=True)
    npt.assert_array_equal(indx, [7, 8, 9])


# A condition that is neither a string nor a callable raises an error
def test_select_wrong_condition(data_dir: Path):
    with pytest.raises(ValueError):
        _manager(data_dir).select(var, 123)


# A condition matching nothing gives an empty array
def test_select_no_match(data_dir: Path):
    assert _manager(data_dir).select(var, lambda v: v > 100.0).size == 0
