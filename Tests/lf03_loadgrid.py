import pyPLUTO    as pp
import numpy      as np
import numpy.testing as npt
import pytest

print(f"Testing the Load grid reading methods ... ".ljust(50), end='')

assert "pippo" == "pluto"
# Theoretical grid values for the selected output
xr  = np.linspace(-1,1,129)
dx  = 2/128
xc0 = xr[0] + 1/128
xc  = np.linspace(xc0,-xc0,128)

xr2D, yr2D = np.meshgrid(xr, xr)
xc2D, yc2D = np.meshgrid(xc, xc)

# Testing the grid from the grid.out file
D = pp.Load(path = "Test_load/single_file", text = False)

npt.assert_allclose(D.x1r, xr)
npt.assert_allclose(D.x2r, xr)

npt.assert_allclose(D.dx1, dx)
npt.assert_allclose(D.dx2, dx)

npt.assert_allclose(D.x1, xc)
npt.assert_allclose(D.x2, xc)

assert D.dim == 2
assert (D.nx1,D.nx2,D.nx3) == (128,128,1)
assert D.geom == "CARTESIAN"
assert D.nshp == (128,128)

assert D._nshp_st1 == (128,129)
assert D._nshp_st2 == (129,128)

assert D.gridsize == 128*128
assert D._gridsize_st1 == 129*128
assert D._gridsize_st2 == 128*129

# Testing the grid from a standalone vtk file
D = pp.Load(path = "Test_load/single_file", text = False, datatype = "vtk", alone = True)
npt.assert_allclose(D.x1r, xr)
npt.assert_allclose(D.x2r, xr)

npt.assert_allclose(D.dx1, dx)
npt.assert_allclose(D.dx2, dx)

npt.assert_allclose(D.x1, xc)
npt.assert_allclose(D.x2, xc)

assert D.dim == 2
assert (D.nx1,D.nx2,D.nx3) == (128,128,1)
assert D.geom == "CARTESIAN"
assert D.nshp == (128,128)

assert D.gridsize == 128*128

# Testing the grid from a standalone h5 file
warn = ("The geometry is unknown, therefore the grid spacing has not been "
        "computed. \nFor a more accurate grid analysis, the loading with "
        "the .out file is recommended.\n")

with pytest.warns(UserWarning, match=warn):
    D = pp.Load(path = "Test_load/single_file", text = False, datatype = "dbl.h5", alone = True)
npt.assert_allclose(D.x1r, xr2D)
npt.assert_allclose(D.x2r, yr2D)

npt.assert_allclose(D.x1, xc2D)
npt.assert_allclose(D.x2, yc2D)

assert D.dim == 2
assert (D.nx1,D.nx2,D.nx3) == (128,128,1)
assert D.geom == "UNKNOWN"
assert D.nshp == (128,128)

assert D._nshp_st1 == (128,129)
assert D._nshp_st2 == (129,128)

assert D.gridsize == 128*128
assert D._gridsize_st1 == 129*128
assert D._gridsize_st2 == 128*129

print(" ---> \033[32mPASSED!\033[0m")
