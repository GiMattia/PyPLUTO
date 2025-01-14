import os
import pytest
from pathlib import Path
import pyPLUTO as pp

# Assuming the root of the repo is your current working directory
repo_root = Path(os.getcwd())
path = repo_root / "Test_load"

# Given format (multiple files), alone = True
def test_multiple_alone():
    file_path = path / "multiple_files"
    vtk_file = file_path / "rho.0000.vtk"  # Correct file name

    print(f"Checking path: {file_path}")
    assert file_path.exists(), f"Path {file_path} does not exist"

    # Check if the vtk file exists
    if not vtk_file.exists():
        pytest.skip(f"Required file {vtk_file} not found, skipping test.")

    D = pp.Load(path=file_path, text=False, datatype='vtk', alone=True)
    assert D.format == 'vtk'

test_multiple_alone()
