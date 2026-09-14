"""Test of the readdefplini.py file."""

from pathlib import Path

import pytest

import pyPLUTO as pp
from pyPLUTO.loadfuncs.readdefplini import FiledefpliniManager


def _manager(data_dir: Path):
    Data = pp.Load(path=data_dir / "single_file", text=False)
    return FiledefpliniManager(Data.state, defh=False, plini=False)


# The YES and TRUE keywords become True
@pytest.mark.parametrize("value", ["YES", "yes", "TRUE", "true"])
def test_convert_value_true(value, data_dir: Path):
    assert _manager(data_dir).convert_value(value) is True


# The NO and FALSE keywords become False
@pytest.mark.parametrize("value", ["NO", "no", "FALSE", "false"])
def test_convert_value_false(value, data_dir: Path):
    assert _manager(data_dir).convert_value(value) is False


# A plain number becomes an integer
def test_convert_value_integer(data_dir: Path):
    assert _manager(data_dir).convert_value("42") == 42


# A number with a dot or an exponent becomes a float
def test_convert_value_float(data_dir: Path):
    assert _manager(data_dir).convert_value("1.5") == 1.5
    assert _manager(data_dir).convert_value("1e3") == 1000.0


# Anything else is left as it is
def test_convert_value_string(data_dir: Path):
    assert _manager(data_dir).convert_value("CARTESIAN") == "CARTESIAN"


# Only the '#define' lines of a header file are read
def test_read_defh(tmp_path, data_dir: Path):
    """LONG TEST: CHECK"""
    header = tmp_path / "definitions.h"
    header.write_text(
        "#define  GEOMETRY   CARTESIAN\n"
        "#define  NVAR       8\n"
        "#define  COOLING    NO\n"
        "/* a comment that must be ignored */\n"
        "int main() { return 0; }\n"
    )

    defs = _manager(data_dir).read_defh(header)
    assert defs == {"GEOMETRY": "CARTESIAN", "NVAR": 8, "COOLING": False}


# A header file without definitions gives an empty dictionary
def test_read_defh_empty(tmp_path, data_dir: Path):
    header = tmp_path / "empty.h"
    header.write_text("/* nothing here */\n")
    assert _manager(data_dir).read_defh(header) == {}


# A missing definitions file leaves the state without any definitions
def test_missing_definitions_file(data_dir: Path):
    Data = pp.Load(path=data_dir / "single_file", text=False)
    FiledefpliniManager(Data.state, defh=True, plini=True)
    assert getattr(Data.state, "defh", None) is None
    assert getattr(Data.state, "plini", None) is None


# A definitions file that is present is read into the state
def test_definitions_file_is_read(tmp_path, data_dir: Path):
    """LONG TEST: CHECK"""
    (tmp_path / "definitions.h").write_text("#define  GEOMETRY  POLAR\n")
    (tmp_path / "data.0000.dbl").write_bytes(b"")

    Data = pp.Load(path=data_dir / "single_file", text=False)
    Data.state.pathdir = tmp_path
    FiledefpliniManager(Data.state, defh=True, plini=False)

    assert Data.state.defh == {"GEOMETRY": "POLAR"}
