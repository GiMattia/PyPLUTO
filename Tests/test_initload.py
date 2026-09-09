import os
from pathlib import Path

import pytest

import pyPLUTO as pp

# Assuming the root of the repo is your current working directory
repo_root = Path(os.getcwd())
repo_root = repo_root if repo_root.name == "Tests" else repo_root / "Tests"
path = repo_root / "Test_load"
path_part = repo_root / "Test_load/particles_cr"


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


def test_Image_prints_message(caplog):
    import logging

    with caplog.at_level(logging.INFO):
        Data = pp.Load(path=path / "single_file")
    assert "Load: folder " in caplog.text
    assert "output " in caplog.text


# Check if raises erorr with wrong endianess (particles)
def test_part_wrongendian():
    with pytest.raises(ValueError):
        pp.LoadPart(path=path_part, text=False, endian="wrong")


# Check if raises error when the path is not a non-empty string (particles)
def test_part_emptystring():
    with pytest.raises(
        TypeError, match="Invalid data type. 'path' must be path or string"
    ):
        pp.LoadPart(path=123, text=False)
    with pytest.raises(ValueError, match="'path' cannot be an empty string."):
        pp.LoadPart(path="", text=False)


# Check if raises an error if the path is not a directory (particles)
def test_part_wrongpath():
    with pytest.raises(NotADirectoryError):
        pp.LoadPart(path="wrong", text=False)


# Check if raises an error with wrong attribute (particles)
def test_part_wrongattr():
    with pytest.raises(AttributeError):
        Data = pp.LoadPart(path=path_part, text=False)
        rep = Data.wrong
