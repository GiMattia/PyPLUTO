import os
from pathlib import Path

import numpy as np
import numpy.testing as npt

import pyPLUTO as pp

# Assuming the root of the repo is your current working directory
repo_root = Path(os.getcwd())
path = repo_root / "Test_load"


endianess = [">"]
binformat = [">f4"]
varslist = ["rho", "vx1", "vx2", "vx3", "prs"]


# Test when only last output is loaded
def test_lastoutput():
    Data = pp.Load(
        path=path / "multiple_outputs", datatype="vtk", alone=True, text=False
    )

    outlist = np.linspace(0, 4, 5, dtype="int")
    typefile = ["single_file"]
    endpath = [".0004.vtk"]

    npt.assert_array_equal(Data.outlist, outlist)
    assert Data.nout == 4
    assert Data._d_info["typefile"] == typefile
    assert Data._d_info["endianess"] == endianess
    assert Data._d_info["binformat"] == binformat
    assert Data._d_info["endpath"] == endpath
    npt.assert_array_equal(Data._d_info["varslist"], [varslist])


# Test when two outputs are loaded
def test_twooutputs():
    Data = pp.Load(
        [0, -1],
        path / "multiple_outputs",
        datatype="vtk",
        alone=True,
        text=False,
    )

    outlist = np.linspace(0, 4, 5, dtype="int")
    typefile = ["single_file"]
    endpath = [".0000.vtk", ".0004.vtk"]

    npt.assert_array_equal(Data.outlist, outlist)
    npt.assert_array_equal(Data.nout, [0, 4])
    npt.assert_array_equal(Data._d_info["endianess"], endianess * 2)
    npt.assert_array_equal(Data._d_info["binformat"], binformat * 2)
    npt.assert_array_equal(Data._d_info["typefile"], typefile * 2)
    npt.assert_array_equal(Data._d_info["endpath"], endpath)
    npt.assert_array_equal(Data._d_info["varslist"], [varslist, varslist])


# Test when only last output is loaded (tab)
def test_lasttab():
    Data = pp.Load(
        path=path / "multiple_outputs", datatype="tab", alone=True, text=False
    )

    outlist = np.linspace(0, 4, 5, dtype="int")
    typefile = ["single_file"]
    endpath = [".0004.tab"]
    varslist = ["var0", "var1", "var2", "var3", "var4"]

    npt.assert_array_equal(Data.outlist, outlist)
    assert Data.nout == 4
    assert Data._d_info["typefile"] == typefile
    assert Data._d_info["endpath"] == endpath
    npt.assert_array_equal(Data._d_info["varslist"], [varslist])
