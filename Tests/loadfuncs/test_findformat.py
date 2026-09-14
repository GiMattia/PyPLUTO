from pathlib import Path

import pytest

import pyPLUTO as pp


# Format not given (single file), finding dbl
def test_single_finddbl(data_dir: Path):
    D = pp.Load(path=data_dir / "single_file", text=False)
    assert D.datatype == "dbl"


# Format not given (single file), finding vtk
def test_single_findvtk(data_dir: Path):
    D = pp.Load(path=data_dir / "single_file/vtk", text=False)
    assert D.datatype == "vtk"


# Given format (single file), alone = False
def test_find_singlegiven(data_dir: Path):
    for format in ["dbl", "flt", "vtk", "dbl.h5", "flt.h5"]:
        D = pp.Load(path=data_dir / "single_file", text=False, datatype=format)
        assert D.datatype == format


# Given format (single file), alone = True
def test_alone_vtk(data_dir: Path):
    D = pp.Load(
        path=data_dir / "single_file", text=False, datatype="vtk", alone=True
    )
    assert D.datatype == "vtk"


# dbl.h5 and flt.h5 should raise a warning
def test_find_alone_h5(data_dir: Path):
    warn = (
        "The geometry is unknown, therefore the grid spacing has not been "
        "computed. \nFor a more accurate grid analysis, the loading with "
        "the .out file is recommended.\n"
    )
    for format in ["dbl.h5", "flt.h5"]:
        with pytest.warns(UserWarning, match=warn):
            D = pp.Load(
                path=data_dir / "single_file",
                text=False,
                datatype=format,
                alone=True,
            )
            assert D.datatype == format


# Format not given (multiple files), finding dbl
def test_multiple_finddbl(data_dir: Path):
    D = pp.Load(path=data_dir / "multiple_files", text=False)
    assert D.datatype == "dbl"


# Format not given (multiple files), finding vtk
def test_multiple_findvtk(data_dir: Path):
    D = pp.Load(path=data_dir / "multiple_files/vtk", text=False)
    assert D.datatype == "vtk"


# Given format (multiple files), alone = False
def test_multiple_findformat(data_dir: Path):
    for format in ["dbl", "flt", "vtk"]:
        D = pp.Load(
            path=data_dir / "multiple_files", text=False, datatype=format
        )
        assert D.datatype == format


# Given format (multiple files), alone = True
def test_multiple_alone(data_dir: Path):
    D = pp.Load(
        path=data_dir / "multiple_files",
        text=False,
        datatype="vtk",
        alone=True,
    )
    assert D.datatype == "vtk"


# Check if raises error if the format is wrong
def test_wrong_format(data_dir: Path):
    with pytest.raises(ValueError):
        pp.Load(path=data_dir / "single_file", text=False, datatype="wrong")


# Check if raises an error if there is no good format
def test_noformat():
    with pytest.raises(FileNotFoundError):
        pp.Load(text=False)


# Check if raises error if the selected format does not exist
def test_format_noexists(data_dir: Path):
    with pytest.raises(FileNotFoundError):
        pp.Load(path=data_dir / "multiple_files", text=False, datatype="dbl.h5")


# Format not given finding dbl (particles)
def test_part_notgivendbl(data_dir: Path):
    Data = pp.LoadPart(path=data_dir / "particles_cr", text=False)
    assert Data.datatype == "dbl"


# Format not given (single file), finding vtk (particles)
def test_part_notgivenvtk(data_dir: Path):
    Data = pp.LoadPart(path=data_dir / "particles_cr" / "vtk", text=False)
    assert Data.datatype == "vtk"


# Given format (single file) (particles)
def test_part_formats(data_dir: Path):
    for format in ["dbl", "flt", "vtk"]:
        Data = pp.LoadPart(
            path=data_dir / "particles_cr", text=False, datatype=format
        )
        assert Data.datatype == format


# Check if raises error if the format is wrong (particles)
def test_part_wrongformat(data_dir: Path):
    with pytest.raises(ValueError):
        pp.LoadPart(
            path=data_dir / "particles_cr", text=False, datatype="wrong"
        )


# Check if raises an error if there is no good format (particles)
def test_part_noformat():
    with pytest.raises(FileNotFoundError):
        pp.LoadPart(text=False)


# Check if raises error if the selected format does not exist (particles)
def test_part_nogoodformat(data_dir: Path):
    with pytest.raises(FileNotFoundError):
        pp.LoadPart(
            path=data_dir / "particles_cr" / "vtk", text=False, datatype="dbl"
        )
