# Import the libraries, classes and functions
import sys
import warnings

from .h_pypluto import find_session, setup_handlers
from .image import Image
from .image_new import Image_new
from .load import Load
from .loadpart import LoadPart
from .pytools import ring, savefig, show

# Define the version and additional environment variables
__version__ = "1.0"
__colorerr__ = True
__colorwarn__ = True
__session__ = find_session()
__all__ = ["Image", "Image_new", "Load", "LoadPart", "ring", "savefig", "show"]

# Handle the errors/warnings (different colors)
setup_handlers(__colorwarn__, __colorerr__)

# Print the version and session
print(f"PyPLUTO version: {__version__}   session: {__session__}")
