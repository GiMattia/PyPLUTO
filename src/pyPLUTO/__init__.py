"""Top-level package for pyPLUTO.

Everything a user needs is imported here, so `import pyPLUTO as pp` is enough
to reach `pp.Load`, `pp.Image` and the handful of helpers below. The internal
modules -- the managers, the states, the mixins -- are deliberately not
re-exported: they are reached through the three classes.

This file also runs at import time, which is unusual for a package __init__
and intentional here: it settles the version, reads the settings (see
utils/settings.py), and configures the handlers, the logging and the
greeting before any class exists.
"""

from __future__ import annotations

from importlib.metadata import PackageNotFoundError
from importlib.metadata import version as _version

from pyPLUTO.image import Image
from pyPLUTO.load import Load
from pyPLUTO.loadpart import LoadPart
from pyPLUTO.utils import settings
from pyPLUTO.utils.configure import Configure, configure
from pyPLUTO.utils.examples_api import (
    copy_examples,
    examples_path,
    list_examples,
    run_example,
)
from pyPLUTO.utils.pperrors import PyPLUTOError
from pyPLUTO.utils.pplogging import set_text
from pyPLUTO.utils.ppwarnings import PyPLUTOWarning
from pyPLUTO.utils.pytools import find_example, ring, savefig, show

# The version is read from the installed distribution rather than written
# here, so there is one source of truth. It is absent when the source tree is
# used without installing, which is a normal thing to do and must not raise.
try:
    __version__ = _version("py-pluto")
except PackageNotFoundError:
    __version__ = "unknown"

# The settings come from the files and the environment, read before the
# greeting so that they can silence it; then the handlers, the logging and
# the greeting follow them.
settings.load()
Configure(__version__)

# The public API. Checked against this file by test__init_.py, so a name
# exported without being listed, or listed without existing, fails there.
__all__ = [
    "Image",
    "Load",
    "LoadPart",
    "PyPLUTOError",
    "PyPLUTOWarning",
    "configure",
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
