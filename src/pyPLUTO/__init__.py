"""Top-level package for pyPLUTO."""

from pyPLUTO.configure import Configure
from pyPLUTO.image import Image
from pyPLUTO.load import Load as Oldload
from pyPLUTO.loadpart import LoadPart
from pyPLUTO.newload import Load
from pyPLUTO.pytools import find_example, ring, savefig, show

# Define the version and additional environment variables
Configure()

__all__ = [
    "Image",
    "Load",
    "LoadPart",
    "Oldload",
    "find_example",
    "ring",
    "savefig",
    "show",
]
