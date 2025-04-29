import os
from pathlib import Path
import pytest
import pyPLUTO as pp

# Assuming the root of the repo is your current working directory
repo_root = Path(os.getcwd())
path = repo_root / "Test_load/particles_cr"


# Check if raises erorr with wrong endianess
def test_wrongendian():
    with pytest.raises(ValueError):
        pp.LoadPart(path=path, text=False, endian="wrong")


# Check if raises error when the path is not a non-empty string
def test_emptystring():
    with pytest.raises(
        TypeError, match="Invalid data type. 'path' must be path or string"
    ):
        pp.LoadPart(path=123, text=False)
    with pytest.raises(ValueError, match="'path' cannot be an empty string."):
        pp.LoadPart(path="", text=False)


# Check if raises an error if the path is not a directory
def test_wrongpath():
    with pytest.raises(NotADirectoryError):
        pp.LoadPart(path="wrong", text=False)


# Check if raises an error with wrong attribute
def test_wrongattr():
    with pytest.raises(AttributeError):
        Data = pp.LoadPart(path=path, text=False)
        Data.wrong
