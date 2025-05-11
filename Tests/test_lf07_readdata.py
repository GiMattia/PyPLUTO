import os
from pathlib import Path

import numpy as np
import numpy.testing as npt
import pyPLUTO as pp
import pytest

# Assuming the root of the repo is your current working directory
repo_root = Path(os.getcwd())
path = repo_root / "Test_load"

# Compute exact solution
nx1, nx2 = 128, 128
exact_vars = {}

exact_vals = {
    "rho": [0.138, 0.5323, 0.5323, 1.5],
    "vx1": [1.206, 1.206, 0.0, 0.0],
    "vx2": [1.206, 0.0, 1.206, 0.0],
    "vx3": [0.0, 0.0, 0.0, 0.0],
    "prs": [0.029, 0.3, 0.3, 1.5],
}

slices = [
    (slice(0, nx1 // 2 + 1), slice(0, nx2 // 2 + 1)),
    (slice(0, nx1 // 2 + 1), slice(nx2 // 2, nx2)),
    (slice(nx1 // 2, nx1), slice(0, nx2 // 2 + 1)),
    (slice(nx1 // 2, nx1), slice(nx2 // 2, nx2)),
]

for i, var in enumerate(["rho", "vx1", "vx2", "vx3", "prs"]):
    array = np.zeros((nx1, nx2))
    for j, sl in enumerate(slices):
        array[sl] = exact_vals[var][j]
    exact_vars[var] = array

varslist = ["rho", "vx1", "vx2", "vx3", "prs"]


# Test single file, dbl output
def test_2D_singledbl():
    Data = pp.Load(0, path=path / "single_file", text=False)
    for num, var in enumerate(varslist):
        npt.assert_array_equal(getattr(Data, var), exact_vars[var])


# Test multiple files, dbl output
def test_2D_multipledbl():
    Data = pp.Load(0, path=path / "multiple_files", text=False)
    for num, var in enumerate(varslist):
        npt.assert_array_equal(getattr(Data, var), exact_vars[var])


# Test single file, vtk output
def test_singlevtk():
    Data = pp.Load(0, path=path / "single_file", datatype="vtk", text=False)
    for num, var in enumerate(varslist):
        npt.assert_allclose(getattr(Data, var), exact_vars[var])


# Test multiple files, vtk output
def test_multiplevtk():
    Data = pp.Load(0, path=path / "multiple_files", datatype="vtk", text=False)
    for num, var in enumerate(varslist):
        npt.assert_allclose(getattr(Data, var), exact_vars[var])


# Test dbl.h5 output
def test_dblh5():
    Data = pp.Load(0, path=path / "single_file", datatype="dbl.h5", text=False)
    for num, var in enumerate(varslist):
        npt.assert_array_equal(getattr(Data, var), exact_vars[var])


# Test flt.h5 output
def test_flth5():
    Data = pp.Load(0, path=path / "single_file", datatype="flt.h5", text=False)
    for num, var in enumerate(varslist):
        npt.assert_allclose(getattr(Data, var), exact_vars[var])


# Test single file, tab output
def test_tab():
    Data = pp.Load(0, path=path / "single_file", datatype="tab", text=False)
    for num, var in enumerate(varslist):
        npt.assert_allclose(getattr(Data, var), exact_vars[var])


# Test single file, vtk output (standalone)
def test_singlevtkalone():
    Data = pp.Load(
        0, path=path / "single_file", datatype="vtk", text=False, alone=True
    )
    for num, var in enumerate(varslist):
        npt.assert_allclose(getattr(Data, var), exact_vars[var])


# Test multiple files, vtk output (standalone)
def test_multiplevtkalone():
    Data = pp.Load(
        0, path=path / "multiple_files", datatype="vtk", text=False, alone=True
    )
    for num, var in enumerate(varslist):
        npt.assert_allclose(getattr(Data, var), exact_vars[var])


warn = (
    "The geometry is unknown, therefore the grid spacing has not been "
    "computed. \nFor a more accurate grid analysis, the loading with "
    "the .out file is recommended.\n"
)


# Test dbl.h5 output (standalone)
def test_dblh5alone():
    with pytest.warns(UserWarning, match=warn):
        Data = pp.Load(
            path=path / "single_file",
            text=False,
            datatype="dbl.h5",
            alone=True,
        )
    for num, var in enumerate(varslist):
        npt.assert_array_equal(getattr(Data, var), exact_vars[var])


# Test flt.h5 output (standalone)
def test_flth5alone():
    with pytest.warns(UserWarning, match=warn):
        Data = pp.Load(
            path=path / "single_file",
            text=False,
            datatype="flt.h5",
            alone=True,
        )
    for num, var in enumerate(varslist):
        npt.assert_allclose(getattr(Data, var), exact_vars[var])


# Test single file, tab output (standalone)
def test_tabalone():
    vars_conversion = {
        "rho": "var0",
        "vx1": "var1",
        "vx2": "var2",
        "vx3": "var3",
        "prs": "var4",
    }

    Data = pp.Load(
        0, path=path / "single_file", datatype="tab", text=False, alone=True
    )
    for num, var in enumerate(varslist):
        npt.assert_allclose(
            getattr(Data, vars_conversion[var]), exact_vars[var]
        )


# Test single file, tab output (1D)
rho = np.array([1] * 200 + [0.125] * 200)
prs = np.array([1] * 200 + [0.1] * 200)


def test_tab1D():
    Data = pp.Load(
        0, path=path / "multiple_outputs", datatype="tab", text=False
    )
    npt.assert_allclose(Data.rho, rho)
    npt.assert_allclose(Data.prs, prs)


# Test muptiple outputs
def test_multipleout():
    Data = pp.Load(
        [0, 1], path=path / "multiple_outputs", datatype="dbl", text=False
    )
    assert isinstance(Data.rho, dict)
    assert list(Data.rho.keys()) == [0, 1]
    npt.assert_allclose(Data.rho[0], rho)
