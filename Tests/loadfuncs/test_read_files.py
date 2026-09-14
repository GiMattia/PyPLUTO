"""Test of the read_files.py file."""

from pathlib import Path

import numpy.testing as npt
import pytest

import pyPLUTO as pp


def _load(data_dir: Path):
    return pp.Load(path=data_dir / "single_file", text=False)


def _write_h5(Data, tmp_path):
    """Write a small h5 file and give back its path."""
    out = tmp_path / "data.h5"
    Data.write_file(Data.rho, str(out), dataname="rho")
    return out


# An h5 file written by pyPLUTO can be read back
def test_read_h5_roundtrip(tmp_path, data_dir: Path):
    Data = _load(data_dir)
    stored = Data.read_file(str(_write_h5(Data, tmp_path)))
    npt.assert_allclose(stored["rho"], Data.rho)


# The reader returns one entry per variable in the file
def test_read_h5_keys(tmp_path, data_dir: Path):
    Data = _load(data_dir)
    assert list(Data.read_file(str(_write_h5(Data, tmp_path)))) == ["rho"]


# A dat file is read column by column, using its header as names
def test_read_dat_with_names(tmp_path, data_dir: Path):
    Data = _load(data_dir)
    dat = tmp_path / "table.dat"
    dat.write_text("a b\n1.0 2.0\n3.0 4.0\n")
    stored = Data.read_file(str(dat))
    npt.assert_allclose(stored["a"], [1.0, 3.0])
    npt.assert_allclose(stored["b"], [2.0, 4.0])


# Without names the columns are numbered instead
def test_read_dat_without_names(tmp_path, data_dir: Path):
    Data = _load(data_dir)
    dat = tmp_path / "plain.dat"
    dat.write_text("1.0 2.0\n3.0 4.0\n")
    stored = Data.read_file(str(dat), names=False)
    npt.assert_allclose(stored["col_0"], [1.0, 3.0])
    npt.assert_allclose(stored["col_1"], [2.0, 4.0])


# Header lines can be skipped
def test_read_dat_skip_header(tmp_path, data_dir: Path):
    Data = _load(data_dir)
    dat = tmp_path / "skip.dat"
    dat.write_text("# comment\n1.0 2.0\n3.0 4.0\n")
    stored = Data.read_file(str(dat), names=False, skip=1)
    npt.assert_allclose(stored["col_0"], [1.0, 3.0])


# The format is taken from the extension when it is not given
def test_read_datatype_from_extension(tmp_path, data_dir: Path):
    Data = _load(data_dir)
    out = _write_h5(Data, tmp_path)
    npt.assert_allclose(
        Data.read_file(str(out), datatype="h5")["rho"], Data.rho
    )


# The binary and text formats are not implemented yet and fall back to h5
@pytest.mark.parametrize("datatype", ["vtk", "tab", "dbl", "flt"])
def test_read_unimplemented_formats_fall_back(
    tmp_path, datatype, data_dir: Path
):
    Data = _load(data_dir)
    out = _write_h5(Data, tmp_path)
    with pytest.warns(UserWarning, match="not implemented yet"):
        stored = Data.read_file(str(out), datatype=datatype)
    npt.assert_allclose(stored["rho"], Data.rho)


# An unknown format warns and is read as h5
def test_read_unknown_format(tmp_path, data_dir: Path):
    Data = _load(data_dir)
    out = _write_h5(Data, tmp_path)
    with pytest.warns(UserWarning, match="Invalid datatype"):
        stored = Data.read_file(str(out), datatype="zzz")
    npt.assert_allclose(stored["rho"], Data.rho)


# Reading a VTK file is not implemented yet
def test_read_vtk_not_implemented(tmp_path, data_dir: Path):
    Data = _load(data_dir)
    with pytest.raises(NotImplementedError):
        Data.ReadFileManager._read_vtk("whatever.vtk")
