from pathlib import Path

import numpy as np
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


def test_a_single_output_gives_plain_values(data_dir: Path) -> None:
    """Load one output by number and read its time and number.

    One output asked for is one value each: a float for the time and an
    int for the output number, plain Python types, as declared.
    """
    data = pp.Load(1, path=data_dir / "multiple_outputs", text=False)

    assert type(data.ntime) is float
    assert data.nout == 1
    assert type(data.nout) is int


@pytest.mark.parametrize(
    ("folder", "nout", "expected"),
    [
        ("multiple_outputs", [0, 1], [0, 1]),
        ("multiple_outputs", [0], [0]),
        ("single_file", "all", [0]),
    ],
    ids=["list", "list-of-one", "all-with-one-output"],
)
def test_a_collection_gives_arrays_however_many_outputs(
    folder: str,
    nout: list[int | str] | str,
    expected: list[int],
    data_dir: Path,
) -> None:
    """Load a collection of outputs and read the times and numbers.

    A list or 'all' gives arrays, one entry per output, even when only one
    output comes back: a list of one, or 'all' on a folder with a single
    output. Those two used to give plain values, so code written for
    several outputs broke on them at the first index. The arrays are of
    floats and of integers, as their declared types say.
    """
    data = pp.Load(nout, path=data_dir / folder, text=False)

    assert isinstance(data.ntime, np.ndarray)
    assert np.issubdtype(data.ntime.dtype, np.floating)
    assert len(data.ntime) == len(expected)
    assert isinstance(data.nout, np.ndarray)
    assert np.issubdtype(data.nout.dtype, np.integer)
    assert list(data.nout) == expected
