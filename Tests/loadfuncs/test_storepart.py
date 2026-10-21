"""Test of the storepart.py file."""

from pathlib import Path

import numpy as np
import numpy.testing as npt
import pytest

import pyPLUTO as pp

xr = np.linspace(-4000, 4000, 65)
dx = xr[1] - xr[0]
xc = np.linspace(xr[0] + dx / 2, xr[-1] - dx / 2, 64)[::-1]
xc2d, yc2d = np.meshgrid(xc, xc)


# Test dbl output
def test_CRdbl(data_dir: Path):
    Data = pp.LoadPart(0, path=data_dir / "particles_cr", text=False)
    npt.assert_array_equal(Data.id, np.linspace(1, 4096, 4096))
    npt.assert_array_equal(Data.x1, xc2d.flatten())
    npt.assert_array_equal(Data.x2, yc2d.flatten())
    npt.assert_array_equal(Data.vx1, xc2d.flatten())
    npt.assert_array_equal(Data.vx2, yc2d.flatten())
    npt.assert_array_equal(Data.vx3, 0.5)
    npt.assert_array_equal(Data.tinj, 0.0)
    npt.assert_array_equal(Data.color, 1)


# Test flt output
def test_CRflt(data_dir: Path):
    Data = pp.LoadPart(
        0, path=data_dir / "particles_cr", datatype="flt", text=False
    )
    npt.assert_array_equal(Data.id, np.linspace(1, 4096, 4096))
    npt.assert_allclose(Data.x1, xc2d.flatten())
    npt.assert_allclose(Data.x2, yc2d.flatten())
    npt.assert_allclose(Data.vx1, xc2d.flatten())
    npt.assert_allclose(Data.vx2, yc2d.flatten())
    npt.assert_array_equal(Data.vx3, 0.5)
    npt.assert_array_equal(Data.tinj, 0.0)
    npt.assert_array_equal(Data.color, 1)


# Test vtk output
def test_CRvtk(data_dir: Path):
    Data = pp.LoadPart(
        0, path=data_dir / "particles_cr", datatype="vtk", text=False
    )
    npt.assert_array_equal(Data.id, np.linspace(1, 4096, 4096))
    npt.assert_allclose(Data.x1, xc2d.flatten())
    npt.assert_allclose(Data.x2, yc2d.flatten())
    npt.assert_allclose(Data.ux1, xc2d.flatten())
    npt.assert_allclose(Data.ux2, yc2d.flatten())
    npt.assert_array_equal(Data.ux3, 0.5)
    npt.assert_array_equal(Data.tinj, 0.0)


@pytest.mark.parametrize("nout", [[0], "all"], ids=["list-of-one", "all"])
def test_a_collection_of_one_particle_output_is_a_dict(
    nout: list[int | str] | str, data_dir: Path
) -> None:
    """Load particles as a collection from a folder with one output.

    The same rule as for the fluid: a list or 'all' gives one entry per
    output, so the particle ids are a dict keyed by output 0.
    """
    data = pp.LoadPart(
        nout, path=data_dir / "particles_cr", datatype="vtk", text=False
    )

    assert isinstance(data.id, dict)
    npt.assert_array_equal(data.id[0], np.linspace(1, 4096, 4096))
