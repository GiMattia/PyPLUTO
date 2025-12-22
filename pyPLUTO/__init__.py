"""Top-level package for pyPLUTO."""

# Import the libraries, classes and functions
from .configure import Configure
from .image import Image
from .load import Load
from .loadpart import LoadPart
from .newload import Load as Newload
from .pytools import find_example, ring, savefig, show

# Define the version and additional environment variables
Configure()

__all__ = [
    "Image",
    "Load",
    "LoadPart",
    "Newload",
    "find_example",
    "ring",
    "savefig",
    "show",
]
