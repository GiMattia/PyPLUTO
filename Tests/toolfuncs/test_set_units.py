"""Test of the set_units.py file."""

from pathlib import Path

import numpy as np
import numpy.testing as npt
import pytest

import pyPLUTO as pp
from pyPLUTO.toolfuncs.set_units import SetUnitsManager


def _manager(data_dir: Path):
    Data = pp.Load(path=data_dir / "single_file", text=False, units=True)
    return SetUnitsManager(Data.state), Data


# Without a selection every known variable is taken, and it is not explicit
def test_resolve_default(data_dir: Path):
    manager, _ = _manager(data_dir)
    selected, explicit = manager._resolve_unit_vars()
    assert "rho" in selected
    assert explicit is False


# Passing True also means "all variables", so it is not explicit either
def test_resolve_true(data_dir: Path):
    manager, _ = _manager(data_dir)
    assert manager._resolve_unit_vars(True)[1] is False


# A single name is wrapped into a list and marked as explicit
def test_resolve_single_name(data_dir: Path):
    manager, _ = _manager(data_dir)
    assert manager._resolve_unit_vars("rho") == (["rho"], True)


# A list of names is kept in order
def test_resolve_list_of_names(data_dir: Path):
    manager, _ = _manager(data_dir)
    assert manager._resolve_unit_vars(["rho", "prs"]) == (["rho", "prs"], True)


# A skipped name is removed from the selection
def test_resolve_skip_single(data_dir: Path):
    manager, _ = _manager(data_dir)
    selected, _ = manager._resolve_unit_vars(["rho", "prs"], skip_units="prs")
    assert selected == ["rho"]


# Several names can be skipped at once
def test_resolve_skip_list(data_dir: Path):
    manager, _ = _manager(data_dir)
    selected, _ = manager._resolve_unit_vars(["rho", "prs"], skip_units=["prs"])
    assert selected == ["rho"]


# An invalid variable selector raises an error
def test_resolve_wrong_var_type(data_dir: Path):
    manager, _ = _manager(data_dir)
    with pytest.raises(TypeError, match="var must be"):
        manager._resolve_unit_vars(123)


# An invalid skip selector raises an error
def test_resolve_wrong_skip_type(data_dir: Path):
    manager, _ = _manager(data_dir)
    with pytest.raises(TypeError, match="skip_units must be"):
        manager._resolve_unit_vars(skip_units=123)


# Asking explicitly for an unknown variable raises an error
def test_astropy_units_unknown_variable(data_dir: Path):
    manager, _ = _manager(data_dir)
    with pytest.raises(KeyError, match="No known unit"):
        manager.to_astropy_units("nosuchvar")


# The same holds when converting back to code units
def test_code_units_unknown_variable(data_dir: Path):
    manager, _ = _manager(data_dir)
    with pytest.raises(KeyError, match="No known unit"):
        manager.to_code_units("nosuchvar")


# Attaching a unit marks the variable as carrying one
def test_astropy_units_marks_attached(data_dir: Path):
    manager, Data = _manager(data_dir)
    manager.to_astropy_units("rho")
    assert "rho" in Data.state.unit_attached


# Attaching twice leaves the variable untouched the second time
def test_astropy_units_is_idempotent(data_dir: Path):
    manager, Data = _manager(data_dir)
    manager.to_astropy_units("rho")
    first = Data.state.rho
    manager.to_astropy_units("rho")
    assert Data.state.rho is first


# Converting back to code units removes the unit again
def test_code_units_roundtrip(data_dir: Path):
    """LONG TEST: CHECK"""
    manager, Data = _manager(data_dir)
    original = np.asarray(Data.state.rho, dtype=float).copy()

    manager.to_astropy_units("rho")
    assert hasattr(Data.state.rho, "unit")

    manager.to_code_units("rho")
    assert not hasattr(Data.state.rho, "unit")
    npt.assert_allclose(np.asarray(Data.state.rho, dtype=float), original)
