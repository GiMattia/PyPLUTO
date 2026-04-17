import os
from pathlib import Path

import numpy as np
import numpy.testing as npt

import pyPLUTO as pp

# Assuming the root of the repo is your current working directory
repo_root = Path(os.getcwd())
repo_root = repo_root if repo_root.name == "Tests" else repo_root / "Tests"
path = repo_root / "Test_load"

outlist = np.linspace(0, 4, 5, dtype="int")
timelist = np.linspace(0, 0.2, 5)

typefile = ["single_file"]
endianess = ["<"]
binformat = ["<f8"]
varslist = ["rho", "vx1", "vx2", "vx3", "prs"]
endpath = [".0000.dbl", ".0001.dbl", ".0002.dbl", ".0003.dbl", ".0004.dbl"]


# Test the dbl.out file when only last output is loaded
def test_load_outfile_oneoutput():

    Data = pp.Load(path=path / "multiple_outputs", text=False)
    npt.assert_array_equal(Data.outlist, outlist)
    npt.assert_allclose(
        Data.timelist, timelist, atol=0.001
    )  # Higher tolerance due to how the PLUTO ouput is generated
    assert Data.nout == 4
    assert Data.ntime == 0.2
    assert np.all(Data.d_info["typefile"] == "single_file")
    assert np.all(Data.d_info["endianess"] == endianess)
    assert np.all(Data.d_info["binformat"] == binformat)
    assert np.all(Data.d_info["endpath"] == endpath)
    assert all(v == varslist for v in Data.d_info["varslist"])


# Test the dbl.out file when two outputs are loaded
def test_load_outfile_moreoutputs():
    Data = pp.Load(
        [0, "last"],
        path=path / "multiple_outputs",
        text=False,
        endian="little",
    )

    npt.assert_array_equal(Data.outlist, outlist)
    npt.assert_allclose(
        Data.timelist, timelist, atol=0.001
    )  # Higher tolerance due to how the PLUTO ouput is generated
    npt.assert_array_equal(Data.nout, [0, 4])
    npt.assert_allclose(Data.ntime, [0, 0.2])
    assert np.all(Data.d_info["typefile"] == "single_file")
    assert np.all(Data.d_info["endianess"] == endianess)
    assert np.all(Data.d_info["binformat"] == binformat)
    assert np.all(Data.d_info["endpath"] == endpath)
    assert all(v == varslist for v in Data.d_info["varslist"])


# Test the vtk.out file when only last output is loaded
def test_load_outfilevtk_oneoutput():
    Data = pp.Load(path=path / "multiple_outputs", text=False, datatype="vtk")

    endianess = [">"]
    binformat = [">f4"]
    endpath = [".0000.vtk", ".0001.vtk", ".0002.vtk", ".0003.vtk", ".0004.vtk"]

    npt.assert_array_equal(Data.outlist, outlist)
    npt.assert_allclose(
        Data.timelist, timelist, atol=0.001
    )  # Higher tolerance due to how the PLUTO ouput is generated
    assert Data.nout == 4
    assert Data.ntime == 0.2
    assert np.all(Data.d_info["typefile"] == "single_file")
    assert np.all(Data.d_info["endianess"] == endianess)
    assert np.all(Data.d_info["binformat"] == binformat)
    assert np.all(Data.d_info["endpath"] == endpath)
    assert all(v == varslist for v in Data.d_info["varslist"])


# Test the tab.out file when only last output is loaded
def test_load_outfiletab_oneoutput():
    Data = pp.Load(path=path / "multiple_outputs", text=False, datatype="tab")

    endianess = ["<"]
    binformat = ["<f4"]
    endpath = [".0000.tab", ".0001.tab", ".0002.tab", ".0003.tab", ".0004.tab"]

    npt.assert_array_equal(Data.outlist, outlist)
    npt.assert_allclose(
        Data.timelist, timelist, atol=0.001
    )  # Higher tolerance due to how the PLUTO ouput is generated
    assert Data.nout == 4
    assert Data.ntime == 0.2
    assert np.all(Data.d_info["typefile"] == "single_file")
    assert np.all(Data.d_info["endianess"] == endianess)
    assert np.all(Data.d_info["binformat"] == binformat)
    assert np.all(Data.d_info["endpath"] == endpath)
    assert all(v == varslist for v in Data.d_info["varslist"])
