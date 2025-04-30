import os
from pathlib import Path

import numpy.testing as npt

import pyPLUTO as pp

# Assuming the root of the repo is your current working directory
repo_root = Path(os.getcwd())
path = repo_root / "Test_load/particles_cr"


# Test with particles CR find files
def test_CRfindfiles():
    Data = pp.LoadPart(path=path, datatype="vtk", text=False)

    outlist = [0]
    typefile = ["single_file"]
    endianess = [">"]
    endpath = [".0000.vtk"]
    varslist = ["points", "Identity", "tinj", "Color", "Four-Velocity"]

    npt.assert_array_equal(Data.outlist, outlist)
    assert Data.nout == 0
    assert Data._d_info["typefile"] == typefile
    assert Data._d_info["endianess"] == endianess
    assert Data._d_info["endpath"] == endpath
    npt.assert_array_equal(Data._d_info["varslist"], [varslist])
