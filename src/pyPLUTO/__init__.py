"""Top-level package for pyPLUTO."""

from pyPLUTO.configure import Configure
from pyPLUTO.image import Image
from pyPLUTO.load import Load as Oldload
from pyPLUTO.loadpart import LoadPart
from pyPLUTO.newload import Load
from pyPLUTO.pytools import find_example, ring, savefig, show

# Define the version and additional environment variables
__version__ = "1.1.5"

colorerr: bool = True
colorwarn: bool = True
greet: bool = True

Configure(__version__, colorerr, colorwarn, greet)

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
