"""Top-level package for pyPLUTO."""

from __future__ import annotations

from pyPLUTO.configure import Configure
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

# Define the version and additional environment variables
__version__ = "1.2.0"

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
    "show",
]
