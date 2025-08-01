import os
from pathlib import Path

import pytest

import pyPLUTO as pp

# Assuming the root of the repo is your current working directory
repo_root = Path(os.getcwd())
repo_root = repo_root if repo_root.name == "Tests" else repo_root / "Tests"
path = repo_root / "Test_load"


# Check if raises erorr with wrong endianess
def test_wrong_endian():
    with pytest.raises(ValueError):
        pp.Load(path=path / "single_file", text=False, endian="wrong")


# Check if raises an error with wrong multiple keyword
def test_wrong_multiple():
    with pytest.raises(
        TypeError, match="Invalid data type. 'multiple' must be a boolean."
    ):
        pp.Load(path=path / "single_file", text=False, multiple="wrong")


# Check if raises error when the path is not a non-empty string
def test_wrong_Stringpath():
    with pytest.raises(
        TypeError, match="Invalid data type. 'path' must be path or string"
    ):
        pp.Load(path=123, text=False)
    with pytest.raises(ValueError, match="'path' cannot be an empty string."):
        pp.Load(path="", text=False)


# Check if raises an error if the path is not a directory
def test_notadirectory():
    with pytest.raises(NotADirectoryError):
        pp.Load(path="wrong", text=False)


# Check if raises an error with wrong attribute
def test_wrongattr():
    with pytest.raises(AttributeError):
        Data = pp.Load(path=path / "single_file", text=False)
        Data.wrong
