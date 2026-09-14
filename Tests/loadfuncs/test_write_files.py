"""Test of the write_files.py file."""

from pathlib import Path

import h5py
import numpy as np
import numpy.testing as npt
import pytest

import pyPLUTO as pp


def _load(data_dir: Path):
    return pp.Load(path=data_dir / "single_file", text=False)


# An h5 file is created on disk
def test_write_h5_creates_file(tmp_path, data_dir: Path):
    Data = _load(data_dir)
    out = tmp_path / "out.h5"
    Data.write_file(Data.rho, str(out), dataname="rho")
    assert out.exists()
    assert out.stat().st_size > 0


# The data written to the file is the data that was given
def test_write_h5_roundtrip(tmp_path, data_dir: Path):
    """LONG TEST: CHECK"""
    Data = _load(data_dir)
    out = tmp_path / "out.h5"
    Data.write_file(Data.rho, str(out), dataname="rho")

    with h5py.File(out, "r") as f:
        # The dataset is stored somewhere in the file, find the first one
        names = []
        f.visit(names.append)
        stored = [n for n in names if isinstance(f[n], h5py.Dataset)]
        assert stored
        npt.assert_allclose(np.asarray(f[stored[0]]).ravel(), Data.rho.ravel())


# A dictionary of variables is written under its own name
def test_write_h5_dictionary(tmp_path, data_dir: Path):
    Data = _load(data_dir)
    out = tmp_path / "dict.h5"
    Data.write_file({"rho": Data.rho}, str(out), dataname="rho")
    with h5py.File(out, "r") as stored:
        npt.assert_allclose(np.asarray(stored["rho"]), Data.rho)


# The grid is written next to the data when it is asked for
def test_write_h5_with_grid(tmp_path, data_dir: Path):
    """LONG TEST: CHECK"""
    Data = _load(data_dir)
    out = tmp_path / "grid.h5"
    Data.write_file({"rho": Data.rho}, str(out), dataname="rho", grid=True)

    with h5py.File(out, "r") as stored:
        for name in ["x1", "x2", "x3", "dx1", "dx2", "dx3"]:
            assert name in stored
        npt.assert_allclose(np.asarray(stored["x1"]), Data.x1)
        npt.assert_allclose(np.asarray(stored["rho"]), Data.rho)


# Without the grid keyword only the data is written
def test_write_h5_without_grid(tmp_path, data_dir: Path):
    Data = _load(data_dir)
    out = tmp_path / "nogrid.h5"
    Data.write_file({"rho": Data.rho}, str(out), dataname="rho")
    with h5py.File(out, "r") as stored:
        assert "x1" not in stored


# The format is taken from the file extension when not given
def test_write_datatype_from_extension(tmp_path, data_dir: Path):
    Data = _load(data_dir)
    out = tmp_path / "implicit.h5"
    Data.write_file(Data.rho, str(out), dataname="rho")
    assert out.exists()


# The other formats are not implemented yet and fall back to h5
@pytest.mark.parametrize("datatype", ["vtk", "tab", "dbl", "flt"])
def test_write_unimplemented_formats_fall_back(
    tmp_path, datatype, data_dir: Path
):
    Data = _load(data_dir)
    out = tmp_path / f"file.{datatype}"
    with pytest.warns(UserWarning, match="not implemented yet"):
        Data.write_file(Data.rho, str(out), dataname="rho")
    assert (tmp_path / f"file.{datatype}.h5").exists()


# An unknown format warns and is written as h5
def test_write_unknown_format(tmp_path, data_dir: Path):
    Data = _load(data_dir)
    out = tmp_path / "file.zzz"
    with pytest.warns(UserWarning, match="Invalid datatype"):
        Data.write_file(Data.rho, str(out), dataname="rho")
    assert (tmp_path / "file.zzz.h5").exists()
