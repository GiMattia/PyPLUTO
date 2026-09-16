"""Top-level package for pyPLUTO.

Everything a user needs is imported here, so `import pyPLUTO as pp` is enough
to reach `pp.Load`, `pp.Image` and the handful of helpers below. The internal
modules -- the managers, the states, the mixins -- are deliberately not
re-exported: they are reached through the three classes.

This file also runs at import time, which is unusual for a package __init__
and intentional here: it settles the version and configures the logging and
the greeting before any class exists.
"""

from __future__ import annotations

from importlib.metadata import PackageNotFoundError
from importlib.metadata import version as _version

from pyPLUTO.image import Image
from pyPLUTO.load import Load
from pyPLUTO.loadpart import LoadPart
from pyPLUTO.utils.configure import Configure, set_text
from pyPLUTO.utils.examples_api import (
    copy_examples,
    examples_path,
    list_examples,
    run_example,
)
from pyPLUTO.utils.pytools import find_example, ring, savefig, show

# The version is read from the installed distribution rather than written
# here, so there is one source of truth. It is absent when the source tree is
# used without installing, which is a normal thing to do and must not raise.
try:
    __version__ = _version("py-pluto")
except PackageNotFoundError:
    __version__ = "unknown"

# Module-level switches a user can flip before doing anything else: coloured
# errors and warnings, and the greeting printed on import.
colorerr: bool = True
colorwarn: bool = True
greet: bool = True

# Sets up the logging and prints the greeting. Runs on import, which is why
# the switches above are read here and not later.
Configure(__version__, colorerr, colorwarn, greet)

# The public API. Checked against this file by test__init_.py, so a name
# exported without being listed, or listed without existing, fails there.
__all__ = [
    "Image",
    "Load",
    "LoadPart",
    "copy_examples",
    "examples_path",
    "find_example",
    "list_examples",
    "ring",
    "run_example",
    "savefig",
    "set_text",
    "show",
]
