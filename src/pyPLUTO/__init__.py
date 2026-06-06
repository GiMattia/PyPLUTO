"""Top-level package for pyPLUTO."""

from __future__ import annotations

from importlib.metadata import PackageNotFoundError
from importlib.metadata import version as _version

from pyPLUTO.configure import Configure, set_text
from pyPLUTO.examples_api import (
    copy_examples,
    examples_path,
    list_examples,
    run_example,
)
from pyPLUTO.image import Image
from pyPLUTO.load import Load
from pyPLUTO.loadpart import LoadPart
from pyPLUTO.pytools import find_example, ring, savefig, show

try:
    __version__ = _version("py-pluto")
except PackageNotFoundError:
    __version__ = "unknown"

colorerr: bool = True
colorwarn: bool = True
greet: bool = True

Configure(__version__, colorerr, colorwarn, greet)

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
