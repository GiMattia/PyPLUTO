"""Test of the offsetpart.py file."""

from pathlib import Path

import pyPLUTO as pp

varslist = ["points", "Identity", "tinj", "Color", "Four-Velocity"]
offsets_vtk = {
    "points": 104,
    "Identity": 65719,
    "tinj": 82146,
    "Color": 98574,
    "Four-Velocity": 114989,
}


# Test CR particles, dbl output
def test_offsetdbl(data_dir: Path):
    Data = pp.LoadPart(path=data_dir / "particles_cr", text=False)
    assert Data.varoffset["tot"] == 390


# Test CR particles, flt output
def test_offsetflt(data_dir: Path):
    Data = pp.LoadPart(
        path=data_dir / "particles_cr", text=False, datatype="flt"
    )
    assert Data.varoffset["tot"] == 379


# Test CR particles, vtk output
def test_offsetvtk(data_dir: Path):
    Data = pp.LoadPart(
        path=data_dir / "particles_cr", text=False, datatype="vtk"
    )
    for var in varslist:
        assert Data.varoffset[var] == offsets_vtk[var]
