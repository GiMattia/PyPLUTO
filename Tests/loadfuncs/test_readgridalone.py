"""Test of the readgridalone.py file."""

from pathlib import Path

import numpy as np
import numpy.testing as npt
import pytest

import pyPLUTO as pp

# Theoretical grid values for the selected output
xr = np.linspace(-1, 1, 129)
dx = 2 / 128
xc0 = xr[0] + 1 / 128
xc = np.linspace(xc0, -xc0, 128)

xr2D, yr2D = np.meshgrid(xr, xr)
xc2D, yc2D = np.meshgrid(xc, xc)


# Testing the grid from a standalone vtk file
def test_standalone_vtk(data_dir: Path):
    Data = pp.Load(
        path=data_dir / "single_file", text=False, datatype="vtk", alone=True
    )
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

    assert Data.gridsize == 128 * 128


# Testing the grid from a standalone h5 file
def test_alone_h5(data_dir: Path):
    warn = (
        "The geometry is unknown, therefore the grid spacing has not been "
        "computed. \nFor a more accurate grid analysis, the loading with "
        "the .out file is recommended.\n"
    )

    with pytest.warns(UserWarning, match=warn):
        Data = pp.Load(
            path=data_dir / "single_file",
            text=False,
            datatype="dbl.h5",
            alone=True,
        )
    npt.assert_allclose(Data.x1r, xr2D)
    npt.assert_allclose(Data.x2r, yr2D)

    npt.assert_allclose(Data.x1, xc2D)
    npt.assert_allclose(Data.x2, yc2D)

    assert Data.dim == 2
    assert (Data.nx1, Data.nx2, Data.nx3) == (128, 128, 1)
    assert Data.geom == "UNKNOWN"
    assert Data.nshp == (128, 128)

    assert Data.nshp_st1 == (128, 129)
    assert Data.nshp_st2 == (129, 128)

    assert Data.gridsize == 128 * 128
    assert Data.gridsize_st1 == 129 * 128
    assert Data.gridsize_st2 == 128 * 129
