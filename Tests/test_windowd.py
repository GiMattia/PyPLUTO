import pyPLUTO as pp
import pytest
import os
from pathlib import Path

# Assuming the root of the repo is your current working directory
repo_root = Path(os.getcwd())
path = repo_root / "Test_load"

# Format not given (single file), finding dbl
def test_single_finddbl():
    file_path = path / "single_file"
    print(f"Checking path: {file_path}")
    assert file_path.exists(), f"Path {file_path} does not exist"
    D = pp.Load(path=file_path, text=False)
    assert D.format == "dbl"

# Format not given (single file), finding vtk
def test_single_findvtk():
    file_path = path / "single_file/vtk"
    print(f"Checking path: {file_path}")
    assert file_path.exists(), f"Path {file_path} does not exist"
    D = pp.Load(path=file_path, text=False)
    assert D.format == "vtk"

# Check if raises error if the format is wrong
def test_wrong_format():
    file_path = path / "single_file"
    print(f"Checking path: {file_path}")
    assert file_path.exists(), f"Path {file_path} does not exist"
    with pytest.raises(ValueError):
        D = pp.Load(path=file_path, text=False, datatype="wrong")

# Format not given (multiple files), finding dbl
def test_multiple_finddbl():
    file_path = path / "multiple_files"
    print(f"Checking path: {file_path}")
    assert file_path.exists(), f"Path {file_path} does not exist"
    D = pp.Load(path=file_path, text=False)
    assert D.format == "dbl"

# Given format (multiple files), alone = True
def test_multiple_alone():
    file_path = path / "multiple_files"
    print(f"Checking path: {file_path}")
    assert file_path.exists(), f"Path {file_path} does not exist"
    D = pp.Load(path=file_path, text=False, datatype='vtk', alone=True)
    assert D.format == 'vtk'
