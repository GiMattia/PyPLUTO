import pyPLUTO as pp
import numpy as np
import numpy.testing as npt
import pytest
import os
from pathlib import Path

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
    D = pp.LoadPart(path=path, text=False)
    assert D._offset["tot"] == 390


# Test CR particles, flt output
def test_offsetflt():
    D = pp.LoadPart(path=path, text=False, datatype="flt")
    assert D._offset["tot"] == 379


# Test CR particles, vtk output
def test_offsetvtk():
    D = pp.LoadPart(path=path, text=False, datatype="vtk")
    for var in varslist:
        assert D._offset[var] == offsets_vtk[var]
