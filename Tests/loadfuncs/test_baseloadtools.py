"""Test of the baseloadtools.py file.

Only one part of it is tested so far: how check_nout reads the form of the
request. The rest of the file is still to be written (see tests_recap.md).

The form decides what a load gives back. A single output asked for -- a
number, 'last', -1 -- comes back as plain values; a collection asked for --
a list, or 'all' -- comes back as one entry per output, even when only one
output is found. Deciding from the request rather than from the number of
files found is what lets the overloads of Load state the types in advance,
and keeps code written for 'all' working on a folder with a single output.
"""

from pathlib import Path

import pytest

import pyPLUTO as pp


@pytest.mark.parametrize(
    ("nout", "expected"),
    [
        (0, False),
        ("last", False),
        (-1, False),
        ([0], True),
        ([0, 1], True),
        ("all", True),
    ],
    ids=["number", "last", "minus-one", "list-of-one", "list", "all"],
)
def test_a_collection_is_asked_for_by_a_list_or_all(
    nout: int | str | list[int | str], expected: bool, data_dir: Path
) -> None:
    """Load the same folder with each form of nout, and read the flag.

    The flag follows the form alone: a list of one output is a collection,
    as a list of several is, and 'last' is a single output, as a number is.
    """
    data = pp.Load(nout, path=data_dir / "multiple_outputs", text=False)

    assert data.manyout is expected
