import os
from pathlib import Path
from types import SimpleNamespace

import numpy as np
import pytest

import pyPLUTO as pp
from pyPLUTO.toolfuncs.compute_units import UnitManager

repo_root = Path(os.getcwd())
repo_root = repo_root if repo_root.name == "Tests" else repo_root / "Tests"
path = repo_root / "Test_load"


def _load_single(**kwargs):
    return pp.Load(path=path / "single_file", text=False, **kwargs)


def test_units_default_behavior():
    D = _load_single(units=False)
    assert isinstance(D.units, dict)
    assert not hasattr(D.rho, "unit")


def test_units_true_attach_all_known():
    u = pytest.importorskip("astropy.units")
    D = _load_single(units=True)
    assert hasattr(D.rho, "unit")
    assert D.rho.unit.is_equivalent(u.g / u.cm**3)


def test_units_single_var():
    pytest.importorskip("astropy.units")
    D = _load_single(units="rho")
    assert hasattr(D.rho, "unit")
    assert not hasattr(D.prs, "unit")


def test_units_list_var():
    pytest.importorskip("astropy.units")
    D = _load_single(units=["rho", "prs"])
    assert hasattr(D.rho, "unit")
    assert hasattr(D.prs, "unit")
    assert not hasattr(D.vx1, "unit")


def test_skip_units():
    pytest.importorskip("astropy.units")
    D = _load_single(units=True, skip_units="rho")
    assert not hasattr(D.rho, "unit")
    assert hasattr(D.prs, "unit")


def test_to_astropy_units():
    pytest.importorskip("astropy.units")
    D = _load_single(units=False)
    D.to_astropy_units("rho")
    assert hasattr(D.rho, "unit")


def test_double_conversion_protection():
    pytest.importorskip("astropy.units")
    D = _load_single(units=False)
    D.to_astropy_units("rho")
    first = D.rho.copy()
    D.to_astropy_units("rho")
    assert np.allclose(D.rho.value, first.value)


def test_to_code_units_roundtrip():
    pytest.importorskip("astropy.units")
    D = _load_single(units=False)
    rho0 = np.array(D.rho)
    D.to_astropy_units("rho")
    D.to_code_units("rho")
    assert not hasattr(D.rho, "unit")
    assert np.allclose(D.rho, rho0)


def test_unknown_unit_explicit_raises():
    pytest.importorskip("astropy.units")
    D = _load_single(units=False)
    with pytest.raises(KeyError, match="No known unit for variable 'foo'"):
        D.to_astropy_units("foo")


def test_units_true_without_astropy(monkeypatch):
    def _raise(_self):
        raise ImportError("Astropy is required for unit-aware operations.")

    monkeypatch.setattr(UnitManager, "_get_astropy_units", _raise)
    with pytest.raises(ImportError, match="Astropy is required"):
        _load_single(units=True)


def test_units_fallback_from_log_normalization(tmp_path):
    pytest.importorskip("astropy.units")
    log_text = """
Header line
Normalization Units:

  [Density]:      1.673e-24 (gr/cm^3), 1.000e+00 (1/cm^3)
  [Pressure]:     1.673e-14 (dyne/cm^2)
  [Velocity]:     1.000e+05 (cm/s)
  [Length]:       1.496e+13 (cm)
"""
    (tmp_path / "pluto.log").write_text(log_text, encoding="utf-8")

    state = SimpleNamespace(
        defh={},
        pathdir=tmp_path,
        unit_base={},
        unit_attached=set(),
        units={},
    )
    manager = UnitManager(state)
    units = manager._make_units_dict()

    assert state.unit_base["UNIT_DENSITY"] == pytest.approx(1.673e-24)
    assert state.unit_base["UNIT_VELOCITY"] == pytest.approx(1.0e5)
    assert state.unit_base["UNIT_LENGTH"] == pytest.approx(1.496e13)
    assert units["rho"].value == pytest.approx(1.673e-24)
    assert units["vx1"].value == pytest.approx(1.0e5)
    assert units["x1"].value == pytest.approx(1.496e13)


def test_units_log_priority_with_defh_fallback_for_missing(tmp_path):
    pytest.importorskip("astropy.units")
    log_text = """
Normalization Units:
  [Density]:      9.999e-24 (gr/cm^3)
  [Velocity]:     2.500e+06 (cm/s)
  [Length]:       3.000e+10 (cm)
"""
    (tmp_path / "pluto.log").write_text(log_text, encoding="utf-8")

    state = SimpleNamespace(
        defh={"UNIT_DENSITY": 2.0e-24},
        pathdir=tmp_path,
        unit_base={},
        unit_attached=set(),
        units={},
    )
    manager = UnitManager(state)
    manager._make_units_dict()

    assert state.unit_base["UNIT_DENSITY"] == pytest.approx(9.999e-24)
    assert state.unit_base["UNIT_VELOCITY"] == pytest.approx(2.5e6)
    assert state.unit_base["UNIT_LENGTH"] == pytest.approx(3.0e10)


def test_units_defh_fallback_when_log_missing_key(tmp_path):
    pytest.importorskip("astropy.units")
    log_text = """
Normalization Units:
  [Velocity]:     2.500e+06 (cm/s)
"""
    (tmp_path / "pluto.log").write_text(log_text, encoding="utf-8")

    state = SimpleNamespace(
        defh={"UNIT_DENSITY": 2.0e-24, "UNIT_LENGTH": 3.0e10},
        pathdir=tmp_path,
        unit_base={},
        unit_attached=set(),
        units={},
    )
    manager = UnitManager(state)
    manager._make_units_dict()

    assert state.unit_base["UNIT_DENSITY"] == pytest.approx(2.0e-24)
    assert state.unit_base["UNIT_LENGTH"] == pytest.approx(3.0e10)
    assert state.unit_base["UNIT_VELOCITY"] == pytest.approx(2.5e6)


def test_units_userdef_priority_over_log_and_defh(tmp_path):
    pytest.importorskip("astropy.units")
    log_text = """
Normalization Units:
  [Density]:      9.999e-24 (gr/cm^3)
  [Velocity]:     2.500e+06 (cm/s)
  [Length]:       3.000e+10 (cm)
"""
    (tmp_path / "pluto.log").write_text(log_text, encoding="utf-8")

    state = SimpleNamespace(
        defh={"UNIT_DENSITY": 2.0e-24},
        unit_userdef={"UNIT_DENSITY": 4.0e-24},
        pathdir=tmp_path,
        unit_base={},
        unit_attached=set(),
        units={},
    )
    manager = UnitManager(state)
    manager._make_units_dict()

    assert state.unit_base["UNIT_DENSITY"] == pytest.approx(4.0e-24)
    assert state.unit_base["UNIT_VELOCITY"] == pytest.approx(2.5e6)
    assert state.unit_base["UNIT_LENGTH"] == pytest.approx(3.0e10)


def test_units_userdef_from_load_kwargs():
    pytest.importorskip("astropy.units")
    D = _load_single(
        units=False,
        user_units={
            "UNIT_DENSITY": 5.0e-24,
            "UNIT_VELOCITY": 2.0e5,
            "UNIT_LENGTH": 7.0e12,
        },
    )
    assert D.unit_base["UNIT_DENSITY"] == pytest.approx(5.0e-24)
    assert D.unit_base["UNIT_VELOCITY"] == pytest.approx(2.0e5)
    assert D.unit_base["UNIT_LENGTH"] == pytest.approx(7.0e12)
