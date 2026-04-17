import os
from pathlib import Path

import numpy as np
import numpy.testing as npt

import pyPLUTO as pp

# Assuming the root of the repo is your current working directory
repo_root = Path(os.getcwd())
repo_root = repo_root if repo_root.name == "Tests" else repo_root / "Tests"
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
    typefile = "single_file"
    endianess = ["", "", "", "", ">"]
    binformat = ["", "", "", "", ">f4"]
    endpath = [".0000.vtk", ".0001.vtk", ".0002.vtk", ".0003.vtk", ".0004.vtk"]

    npt.assert_array_equal(Data.outlist, outlist)
    assert Data.nout == 4
    assert np.all(Data.d_info["typefile"] == typefile)
    assert np.all(Data.d_info["endianess"] == endianess)
    assert np.all(Data.d_info["binformat"] == binformat)
    assert np.all(Data.d_info["endpath"] == endpath)
    assert all(
        v == (varslist if i == 4 else [])
        for i, v in enumerate(Data.d_info["varslist"])
    )


# Test when two outputs are loaded
def test_twooutputs():
    Data = pp.Load(
        [0, -1],
        path=path / "multiple_outputs",
        datatype="vtk",
        alone=True,
        text=False,
    )

    outlist = np.linspace(0, 4, 5, dtype="int")
    typefile = "single_file"
    endianess = [">", "", "", "", ">"]
    binformat = [">f4", "", "", "", ">f4"]
    endpath = [".0000.vtk", ".0001.vtk", ".0002.vtk", ".0003.vtk", ".0004.vtk"]
    print(Data.d_info["endpath"])

    npt.assert_array_equal(Data.outlist, outlist)
    npt.assert_array_equal(Data.nout, [0, 4])
    assert np.all(Data.d_info["typefile"] == typefile)
    assert np.all(Data.d_info["endianess"] == endianess)
    assert np.all(Data.d_info["binformat"] == binformat)
    assert np.all(Data.d_info["endpath"] == endpath)
    assert all(
        v == (varslist if i in (0, 4) else [])
        for i, v in enumerate(Data.d_info["varslist"])
    )


# Test when only last output is loaded (tab)
def test_lasttab():
    Data = pp.Load(
        path=path / "multiple_outputs", datatype="tab", alone=True, text=False
    )

    outlist = np.linspace(0, 4, 5, dtype="int")
    typefile = ["single_file"]
    endpath = [".0000.tab", ".0001.tab", ".0002.tab", ".0003.tab", ".0004.tab"]
    varslist = ["var1", "var2", "var3", "var4", "var5"]

    npt.assert_array_equal(Data.outlist, outlist)
    assert Data.nout == 4
    assert np.all(Data.d_info["typefile"] == typefile)
    assert np.all(Data.d_info["endpath"] == endpath)
    assert all(
        v == (varslist if i == 4 else [])
        for i, v in enumerate(Data.d_info["varslist"])
    )
