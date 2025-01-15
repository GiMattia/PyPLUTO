import pyPLUTO as pp
import pytest
import os
from pathlib import Path

# Assuming the root of the repo is your current working directory
repo_root = Path(os.getcwd())
path = repo_root / "Test_load/particles_cr"


# Format not given finding dbl
def test_notgivendbl():
    D = pp.LoadPart(path=path, text=False)
    assert D.format == "dbl"


# Format not given (single file), finding vtk
def test_notgivenvtk():
    D = pp.LoadPart(path=path / "vtk", text=False)
    assert D.format == "vtk"


# Given format (single file)
def test_formats():
    for format in ["dbl", "flt", "vtk"]:
        D = pp.LoadPart(path=path, text=False, datatype=format)
        assert D.format == format


# Check if raises error if the format is wrong
def test_wrongformat():
    with pytest.raises(ValueError):
        D = pp.LoadPart(path=path, text=False, datatype="wrong")


# Check if raises an error if there is no good format
def test_noformat():
    with pytest.raises(FileNotFoundError):
        D = pp.LoadPart(text=False)


# Check if raises error if the selected format does not exist
def test_nogoodformat():
    with pytest.raises(FileNotFoundError):
        D = pp.LoadPart(path=path / "vtk", text=False, datatype="dbl")
