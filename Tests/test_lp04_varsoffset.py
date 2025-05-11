import os
from pathlib import Path

import pyPLUTO as pp

# Assuming the root of the repo is your current working directory
repo_root = Path(os.getcwd())
path = repo_root / "Test_load/particles_cr"

varslist = ["points", "Identity", "tinj", "Color", "Four-Velocity"]
offsets_vtk = {
    "points": 104,
    "Identity": 65719,
    "tinj": 82146,
    "Color": 98574,
    "Four-Velocity": 114989,
}


# Test CR particles, dbl output
def test_offsetdbl():
    Data = pp.LoadPart(path=path, text=False)
    assert Data._offset["tot"] == 390


# Test CR particles, flt output
def test_offsetflt():
    Data = pp.LoadPart(path=path, text=False, datatype="flt")
    assert Data._offset["tot"] == 379


# Test CR particles, vtk output
def test_offsetvtk():
    Data = pp.LoadPart(path=path, text=False, datatype="vtk")
    for var in varslist:
        assert Data._offset[var] == offsets_vtk[var]
