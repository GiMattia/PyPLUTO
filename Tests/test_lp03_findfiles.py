import pyPLUTO as pp
import numpy as np
import numpy.testing as npt
import pytest
import os
from pathlib import Path

# Assuming the root of the repo is your current working directory
repo_root = Path(os.getcwd())
path = repo_root / "Test_load/particles_cr"

# Test with particles CR
def test_CRfindfiles():
    D = pp.LoadPart(path = path, datatype = 'vtk', text = False)

    outlist = [0]
    typefile = ["single_file"]
    endianess = [">"]
    binformat = ['>f4']
    endpath = [".0000.vtk"]
    varslist = ['points', 'Identity', 'tinj', 'Color', 'Four-Velocity']

    npt.assert_array_equal(D.outlist, outlist)
    assert D.nout == 0
    assert D._d_info["typefile"] == typefile
    assert D._d_info["endianess"] == endianess
    assert D._d_info["endpath"] == endpath
    npt.assert_array_equal(D._d_info["varslist"], [varslist])
