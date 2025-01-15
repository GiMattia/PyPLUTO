# Import the libraries, classes and functions
from .image import Image
from .libraries import *
from .load import Load
from .loadpart import LoadPart
from .pytools import ring, savefig, show

# Define the version and additional environment variables
__version__ = "1.0"
__colorerr__ = True
__colorwarn__ = True
__session__ = find_session()

# Print the version and session
print(f"PyPLUTO version: {__version__}   session: {__session__}")

# Set the color warning handler
warnings.simplefilter("always")
if __colorwarn__ is True:
    warnings.formatwarning = color_warning

# Set the color error handler
if __colorerr__ is True:
    sys.excepthook = color_error
