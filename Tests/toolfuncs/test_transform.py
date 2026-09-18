"""Test of the transform.py file.

The file is out of scope for the coverage push, so this holds only what a
fixed bug left behind: the regression test for the nested-call protocol.
When transform.py is reviewed, this file grows into the usual one.
"""

import warnings
from pathlib import Path

import pyPLUTO as pp


def test_reshape_cartesian_does_not_warn_about_its_own_keywords(
    data_dir: Path,
) -> None:
    """Reshape with a keyword the method honours and expect no warning.

    `reshape_cartesian` called `reshape_uniform` without marking it as a
    nested call, so the inner call restarted the keyword tracking and
    reported `transpose` -- which the outer method reads -- as unused,
    blaming the inner function. The same fault as the one fixed in
    `imagetools.text`.
    """
    data = pp.Load(path=data_dir / "single_file", text=False)

    with warnings.catch_warnings(record=True) as raised:
        warnings.simplefilter("always")
        data.reshape_cartesian(data.rho, transpose=True)

    assert [w for w in raised if "kwargs" in str(w.message)] == []
