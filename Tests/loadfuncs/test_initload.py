from pathlib import Path

import pytest

import pyPLUTO as pp


# Check if raises erorr with wrong endianess
def test_wrong_endian(data_dir: Path):
    with pytest.raises(ValueError):
        pp.Load(path=data_dir / "single_file", text=False, endian="wrong")


# Check if raises an error with wrong multiple keyword
def test_wrong_multiple(data_dir: Path):
    with pytest.raises(
        TypeError, match="Invalid data type. 'multiple' must be a boolean."
    ):
        pp.Load(path=data_dir / "single_file", text=False, multiple="wrong")


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
def test_wrongattr(data_dir: Path):
    with pytest.raises(AttributeError):
        Data = pp.Load(path=data_dir / "single_file", text=False)
        Data.wrong


def test_Image_prints_message(caplog, data_dir: Path):
    import logging

    with caplog.at_level(logging.INFO):
        Data = pp.Load(path=data_dir / "single_file")
    assert "Load: folder " in caplog.text
    assert "output " in caplog.text


# Check if raises erorr with wrong endianess (particles)
def test_part_wrongendian(data_dir: Path):
    with pytest.raises(ValueError):
        pp.LoadPart(path=data_dir / "particles_cr", text=False, endian="wrong")


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
def test_part_wrongattr(data_dir: Path):
    with pytest.raises(AttributeError):
        Data = pp.LoadPart(path=data_dir / "particles_cr", text=False)
        rep = Data.wrong
