"""Benchmarks for loading PLUTO fluid and particle output files."""

from pathlib import Path

import pytest

import pyPLUTO as pp

DATA_DIR = Path(__file__).resolve().parent.parent / "Tests" / "Test_load"


@pytest.mark.parametrize("datatype", ["dbl", "flt", "vtk", "tab"])
def test_load_single_file(benchmark, datatype):
    """Load a 2D 128x128 output stored in a single file."""
    path = DATA_DIR / "single_file"

    data = benchmark(pp.Load, 0, path=path, datatype=datatype, text=False)
    assert data.rho.shape == (128, 128)


@pytest.mark.parametrize("datatype", ["dbl.h5", "flt.h5"])
def test_load_hdf5(benchmark, datatype):
    """Load a 2D 128x128 HDF5 output."""
    path = DATA_DIR / "single_file"

    data = benchmark(pp.Load, 0, path=path, datatype=datatype, text=False)
    assert data.rho.shape == (128, 128)


@pytest.mark.parametrize("datatype", ["dbl", "flt", "vtk"])
def test_load_multiple_files(benchmark, datatype):
    """Load a 2D 128x128 output split into one file per variable."""
    path = DATA_DIR / "multiple_files"

    data = benchmark(pp.Load, 0, path=path, datatype=datatype, text=False)
    assert data.rho.shape == (128, 128)


def test_load_all_outputs(benchmark):
    """Load every output of a run at once."""
    path = DATA_DIR / "multiple_outputs"

    data = benchmark(pp.Load, "all", path=path, text=False)
    assert data.rho is not None


@pytest.mark.parametrize("datatype", ["dbl", "flt", "vtk"])
def test_load_particles(benchmark, datatype):
    """Load 4096 cosmic-ray particles."""
    path = DATA_DIR / "particles_cr"

    data = benchmark(pp.LoadPart, 0, path=path, datatype=datatype, text=False)
    assert data.id.shape == (4096,)
