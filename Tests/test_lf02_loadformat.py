import pyPLUTO    as pp
import pytest
import os
from pathlib import Path

# Assuming the root of the repo is your current working directory
repo_root = Path(os.getcwd())
path = Path("Test_load")

# Format not given (single file), finding dbl
def test_single_finddbl():
    D = pp.Load(path = path / "single_file", text = False)
    assert D.format == "dbl"

# Format not given (single file), finding vtk
def test_single_findvtk():
    D = pp.Load(path = path / "single_file/vtk", text = False)
    assert D.format == "vtk"

# Given format (single file), alone = False
def test_find_singlegiven():
    for format in ["dbl","flt","vtk","dbl.h5","flt.h5"]:
        D = pp.Load(path = path / "single_file", text = False, datatype = format)
        assert D.format == format

# Given format (single file), alone = True
def test_alone_vtk():
    D = pp.Load(path = path / "single_file", text = False, datatype = 'vtk', alone = True)
    assert D.format == 'vtk'

# dbl.h5 and flt.h5 should raise a warning
def test_find_alone_h5():
    warn = ("The geometry is unknown, therefore the grid spacing has not been "
            "computed. \nFor a more accurate grid analysis, the loading with "
            "the .out file is recommended.\n")
    for format in ["dbl.h5","flt.h5"]:
        with pytest.warns(UserWarning, match=warn):
            D = pp.Load(path = path / "single_file", text = False, datatype = format, alone = True)
            assert D.format == format

# Format not given (multiple files), finding dbl
def test_multiple_finddbl():
    D = pp.Load(path = path / "multiple_files", text = False)
    assert D.format == "dbl"

# Format not given (multiple files), finding vtk
def test_multiple_findvtk():
    D = pp.Load(path = path / "multiple_files/vtk", text = False)
    assert D.format == "vtk"

# Given format (multiple files), alone = False
def test_multiple_findformat():
    for format in ["dbl","flt","vtk"]:
        D = pp.Load(path = path / "multiple_files", text = False, datatype = format)
        assert D.format == format

# Given format (multiple files), alone = True
def test_multiple_alone():
    D = pp.Load(path = "Test_load/multiple_files", text = False, datatype = 'vtk', alone = True)
    assert D.format == 'vtk'

# Check if raises error if the format is wrong
def test_wrong_format():
    with pytest.raises(ValueError):
        D = pp.Load(path = path / "single_file", text = False, datatype = "wrong")

# Check if raises an error if there is no good format
def test_noformat():
    with pytest.raises(FileNotFoundError):
        D = pp.Load(text = False)

# Check if raises error if the selected format does not exist
def test_format_noexists():
    with pytest.raises(FileNotFoundError):
        D = pp.Load(path = path / "multiple_files", text = False, datatype = "dbl.h5")
