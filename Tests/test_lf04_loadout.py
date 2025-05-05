import os
from pathlib import Path

import numpy as np
import numpy.testing as npt
import pyPLUTO as pp

# Assuming the root of the repo is your current working directory
repo_root = Path(os.getcwd())
path = repo_root / "Test_load"

outlist = np.linspace(0, 4, 5, dtype="int")
timelist = np.linspace(0, 0.2, 5)

typefile = ["single_file"]
endianess = ["<"]
binformat = ["<f8"]
varslist = ["rho", "vx1", "vx2", "vx3", "prs"]


# Test the dbl.out file when only last output is loaded
def test_load_outfile_oneoutput():

    endpath = [".0004.dbl"]

    Data = pp.Load(path=path / "multiple_outputs", text=False)
    npt.assert_array_equal(Data.outlist, outlist)
    npt.assert_allclose(
        Data.timelist, timelist, atol=0.001
    )  # Higher tolerance due to how the PLUTO ouput is generated
    assert Data.nout == 4
    assert Data.ntime == 0.2
    assert Data._d_info["typefile"] == typefile
    assert Data._d_info["endianess"] == endianess
    assert Data._d_info["binformat"] == binformat
    assert Data._d_info["endpath"] == endpath
    npt.assert_array_equal(Data._d_info["varslist"], [varslist])


# Test the dbl.out file when two outputs are loaded
def test_load_outfile_moreoutputs():

    Data = pp.Load(
        [0, "last"],
        path=path / "multiple_outputs",
        text=False,
        endian="little",
    )

    endpath = [".0000.dbl", ".0004.dbl"]

    npt.assert_array_equal(Data.outlist, outlist)
    npt.assert_allclose(
        Data.timelist, timelist, atol=0.001
    )  # Higher tolerance due to how the PLUTO ouput is generated
    npt.assert_array_equal(Data.nout, [0, 4])
    npt.assert_allclose(Data.ntime, [0, 0.2])
    npt.assert_array_equal(Data._d_info["typefile"], typefile * 2)
    npt.assert_array_equal(Data._d_info["endianess"], endianess * 2)
    npt.assert_array_equal(Data._d_info["binformat"], binformat * 2)
    npt.assert_array_equal(Data._d_info["endpath"], endpath)
    npt.assert_array_equal(Data._d_info["varslist"], [varslist, varslist])


# Test the vtk.out file when only last output is loaded
def test_load_outfilevtk_oneoutput():
    Data = pp.Load(path=path / "multiple_outputs", text=False, datatype="vtk")

    endianess = [">"]
    binformat = [">f4"]
    endpath = [".0004.vtk"]

    npt.assert_array_equal(Data.outlist, outlist)
    npt.assert_allclose(
        Data.timelist, timelist, atol=0.001
    )  # Higher tolerance due to how the PLUTO ouput is generated
    assert Data.nout == 4
    assert Data.ntime == 0.2
    assert Data._d_info["typefile"] == typefile
    assert Data._d_info["endianess"] == endianess
    assert Data._d_info["binformat"] == binformat
    assert Data._d_info["endpath"] == endpath
    npt.assert_array_equal(Data._d_info["varslist"], [varslist])


# Test the tab.out file when only last output is loaded
def test_load_outfiletab_oneoutput():

    Data = pp.Load(path=path / "multiple_outputs", text=False, datatype="tab")

    endianess = ["<"]
    binformat = ["<f4"]
    endpath = [".0004.tab"]

    npt.assert_array_equal(Data.outlist, outlist)
    npt.assert_allclose(
        Data.timelist, timelist, atol=0.001
    )  # Higher tolerance due to how the PLUTO ouput is generated
    assert Data.nout == 4
    assert Data.ntime == 0.2
    assert Data._d_info["typefile"] == typefile
    assert Data._d_info["endianess"] == endianess
    assert Data._d_info["binformat"] == binformat
    assert Data._d_info["endpath"] == endpath
    npt.assert_array_equal(Data._d_info["varslist"], [varslist])
