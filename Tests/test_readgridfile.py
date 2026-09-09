"""Test of the readgridfile.py file."""

import os
from pathlib import Path

import numpy as np
import numpy.testing as npt

import pyPLUTO as pp

# Assuming the root of the repo is your current working directory
repo_root = Path(os.getcwd())
repo_root = repo_root if repo_root.name == "Tests" else repo_root / "Tests"
path = repo_root / "Test_load"

# Theoretical grid values for the selected output
xr = np.linspace(-1, 1, 129)
dx = 2 / 128
xc0 = xr[0] + 1 / 128
xc = np.linspace(xc0, -xc0, 128)


# Testing the grid from the grid.out file
def test_gridfile():
    Data = pp.Load(path=path / "single_file", text=False)

    npt.assert_allclose(Data.x1r, xr)
    npt.assert_allclose(Data.x2r, xr)

    npt.assert_allclose(Data.dx1, dx)
    npt.assert_allclose(Data.dx2, dx)

    npt.assert_allclose(Data.x1, xc)
    npt.assert_allclose(Data.x2, xc)

    assert Data.dim == 2
    assert (Data.nx1, Data.nx2, Data.nx3) == (128, 128, 1)
    assert Data.geom == "CARTESIAN"
    assert Data.nshp == (128, 128)

    assert Data.nshp_st1 == (128, 129)
    assert Data.nshp_st2 == (129, 128)

    assert Data.gridsize == 128 * 128
    assert Data.gridsize_st1 == 129 * 128
    assert Data.gridsize_st2 == 128 * 129
