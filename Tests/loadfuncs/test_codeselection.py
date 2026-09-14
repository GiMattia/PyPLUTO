"""Test of the codeselection.py file."""

from pathlib import Path

import pytest

import pyPLUTO as pp


# PLUTO is the default code and needs no special loading
def test_default_code(data_dir: Path):
    Data = pp.Load(path=data_dir / "single_file", text=False)
    assert Data.datatype == "dbl"


# The code name is not case sensitive
@pytest.mark.parametrize("code", ["PLUTO", "pluto", "gPLUTO"])
def test_pluto_code_names(code, data_dir: Path):
    Data = pp.Load(path=data_dir / "single_file", text=False, code=code)
    assert Data.datatype == "dbl"


# An unknown code cannot be loaded
def test_unknown_code(data_dir: Path):
    with pytest.raises(NotImplementedError, match="not implemented"):
        pp.Load(path=data_dir / "single_file", text=False, code="bogus")


# The ECHO code is known, so it looks for its own files instead
def test_echo_code_is_known(data_dir: Path):
    with pytest.raises(FileNotFoundError):
        pp.Load(path=data_dir / "single_file", text=False, code="echo")
