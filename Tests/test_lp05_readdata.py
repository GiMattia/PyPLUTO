import pyPLUTO as pp
import numpy as np
import numpy.testing as npt
import pytest
import os
from pathlib import Path

# Assuming the root of the repo is your current working directory
repo_root = Path(os.getcwd())
path = repo_root / "Test_load/particles_cr"

xr = np.linspace(-4000,4000,65)
dx = xr[1] - xr[0]
xc = np.linspace(xr[0] + dx/2, xr[-1] - dx/2, 64)[::-1]
xc2d, yc2d = np.meshgrid(xc,xc)


# Test dbl output
def test_CRdbl():
    D = pp.LoadPart(0,path = path, text = False)
    npt.assert_array_equal(D.id, np.linspace(1,4096,4096))
    npt.assert_array_equal(D.x1, xc2d.flatten())
    npt.assert_array_equal(D.x2, yc2d.flatten())
    npt.assert_array_equal(D.vx1, xc2d.flatten())
    npt.assert_array_equal(D.vx2, yc2d.flatten())
    npt.assert_array_equal(D.vx3, 0.5)
    npt.assert_array_equal(D.tinj, 0.0)
    npt.assert_array_equal(D.color, 1)

# Test flt output
def test_CRflt():
    D = pp.LoadPart(0,path = path, datatype = "flt", text = False)
    npt.assert_array_equal(D.id, np.linspace(1,4096,4096))
    npt.assert_allclose(D.x1, xc2d.flatten())
    npt.assert_allclose(D.x2, yc2d.flatten())
    npt.assert_allclose(D.vx1, xc2d.flatten())
    npt.assert_allclose(D.vx2, yc2d.flatten())
    npt.assert_array_equal(D.vx3, 0.5)
    npt.assert_array_equal(D.tinj, 0.0)
    npt.assert_array_equal(D.color, 1)

# Test vtk output
def test_CRvtk():
    D = pp.LoadPart(0,path = path, datatype = "vtk", text = False)
    npt.assert_array_equal(D.id, np.linspace(1,4096,4096))
    npt.assert_allclose(D.x1, xc2d.flatten())
    npt.assert_allclose(D.x2, yc2d.flatten())
    npt.assert_allclose(D.vx1, xc2d.flatten())
    npt.assert_allclose(D.vx2, yc2d.flatten())
    npt.assert_array_equal(D.vx3, 0.5)
    npt.assert_array_equal(D.tinj, 0.0)
