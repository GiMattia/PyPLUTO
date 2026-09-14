"""Test of the offsetfluid.py file."""

from pathlib import Path

import pyPLUTO as pp

size = 128 * 128
size_vtk0 = 1271
size_vtkm = 1282
size_dh50 = 3680
size_vtkh = 40
varslist = ["rho", "vx1", "vx2", "vx3", "prs"]


# Test single file, dbl output
def test_singledbl(data_dir: Path):
    Data = pp.Load(path=data_dir / "single_file", text=False)
    for num, var in enumerate(varslist):
        assert Data.varoffset[var] == size * num * 8


# Test multiple files, dbl output
def test_multipledbl(data_dir: Path):
    Data = pp.Load(path=data_dir / "multiple_files", text=False)
    assert Data.varoffset["prs"] == 0


# Test single file, flt output
def test_singleflt(data_dir: Path):
    Data = pp.Load(path=data_dir / "single_file", text=False, datatype="flt")
    for num, var in enumerate(varslist):
        assert Data.varoffset[var] == size * num * 4


# Test multiple files, flt output
def test_multipleflt(data_dir: Path):
    Data = pp.Load(path=data_dir / "multiple_files", text=False, datatype="flt")
    assert Data.varoffset["prs"] == 0


# Test single file, vtk output (+ descriptor files)
def test_singlevtkout(data_dir: Path):
    Data = pp.Load(path=data_dir / "single_file", datatype="vtk", text=False)
    for num, var in enumerate(varslist):
        assert Data.varoffset[var] == size_vtk0 + num * (size_vtkh + size * 4)


# Test single file, vtk output (standalone)
def test_singlevtkalone(data_dir: Path):
    Data = pp.Load(
        path=data_dir / "single_file", datatype="vtk", text=False, alone=True
    )
    for num, var in enumerate(varslist):
        assert Data.varoffset[var] == size_vtk0 + num * (size_vtkh + size * 4)


# Test multiple files, vtk output (+ descriptor files)
def test_multiplevtkout(data_dir: Path):
    Data = pp.Load(path=data_dir / "multiple_files", datatype="vtk", text=False)
    assert Data.varoffset["prs"] == size_vtkm


# Test multiple files, vtk output (standalone)
def test_multiplevtkalone(data_dir: Path):
    Data = pp.Load(
        path=data_dir / "multiple_files",
        datatype="vtk",
        text=False,
        alone=True,
    )
    var = list(Data.varoffset.keys())[0]
    assert Data.varoffset[var] == size_vtkm


# Test dbl.h5 output
def test_dblh5(data_dir: Path):
    Data = pp.Load(path=data_dir / "single_file", datatype="dbl.h5", text=False)
    for num, var in enumerate(varslist):
        assert Data.varoffset[var] == size_dh50 + num * (size * 8) + (
            0 if num == 0 else 2048
        )
