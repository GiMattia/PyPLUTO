import os
from pathlib import Path

import pyPLUTO as pp

# Assuming the root of the repo is your current working directory
repo_root = Path(os.getcwd())
path = repo_root / "Test_load"

size = 128 * 128
size_vtk0 = 1271
size_vtkm = 1282
size_dh50 = 3680
size_vtkh = 40
varslist = ["rho", "vx1", "vx2", "vx3", "prs"]


# Test single file, dbl output
def test_singledbl():
    Data = pp.Load(path=path / "single_file", text=False)
    for num, var in enumerate(varslist):
        assert Data._offset[var] == size * num * 8


# Test multiple files, dbl output
def test_multipledbl():
    Data = pp.Load(path=path / "multiple_files", text=False)
    assert Data._offset["prs"] == 0


# Test single file, flt output
def test_singleflt():
    Data = pp.Load(path=path / "single_file", text=False, datatype="flt")
    for num, var in enumerate(varslist):
        assert Data._offset[var] == size * num * 4


# Test multiple files, flt output
def test_multipleflt():
    Data = pp.Load(path=path / "multiple_files", text=False, datatype="flt")
    assert Data._offset["prs"] == 0


# Test single file, vtk output (+ descriptor files)
def test_singlevtkout():
    Data = pp.Load(path=path / "single_file", datatype="vtk", text=False)
    for num, var in enumerate(varslist):
        assert Data._offset[var] == size_vtk0 + num * (size_vtkh + size * 4)


# Test single file, vtk output (standalone)
def test_singlevtkalone():
    Data = pp.Load(path=path / "single_file", datatype="vtk", text=False, alone=True)
    for num, var in enumerate(varslist):
        assert Data._offset[var] == size_vtk0 + num * (size_vtkh + size * 4)


# Test multiple files, vtk output (+ descriptor files)
def test_multiplevtkout():
    Data = pp.Load(path=path / "multiple_files", datatype="vtk", text=False)
    assert Data._offset["prs"] == size_vtkm


# Test multiple files, vtk output (standalone)
def test_multiplevtkalone():
    Data = pp.Load(path=path / "multiple_files", datatype="vtk", text=False, alone=True)
    var = list(Data._offset.keys())[0]
    assert Data._offset[var] == size_vtkm


# Test dbl.h5 output
def test_dblh5():
    Data = pp.Load(path=path / "single_file", datatype="dbl.h5", text=False)
    for num, var in enumerate(varslist):
        assert Data._offset[var] == size_dh50 + num * (size * 8) + (
            0 if num == 0 else 2048
        )
