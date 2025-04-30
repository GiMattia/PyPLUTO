import os
from pathlib import Path

import pytest

import pyPLUTO as pp

# Assuming the root of the repo is your current working directory
repo_root = Path(os.getcwd())
path = repo_root / "Test_load/particles_cr"


# Format not given finding dbl
def test_notgivendbl():
    Data = pp.LoadPart(path=path, text=False)
    assert Data.format == "dbl"


# Format not given (single file), finding vtk
def test_notgivenvtk():
    Data = pp.LoadPart(path=path / "vtk", text=False)
    assert Data.format == "vtk"


# Given format (single file)
def test_formats():
    for format in ["dbl", "flt", "vtk"]:
        Data = pp.LoadPart(path=path, text=False, datatype=format)
        assert Data.format == format


# Check if raises error if the format is wrong
def test_wrongformat():
    with pytest.raises(ValueError):
        pp.LoadPart(path=path, text=False, datatype="wrong")


# Check if raises an error if there is no good format
def test_noformat():
    with pytest.raises(FileNotFoundError):
        pp.LoadPart(text=False)


# Check if raises error if the selected format does not exist
def test_nogoodformat():
    with pytest.raises(FileNotFoundError):
        pp.LoadPart(path=path / "vtk", text=False, datatype="dbl")
