'''
try:
    import importlib.metadata

    __version__ = importlib.metadata.version("plutoplot")
    del importlib
except ImportError:  # Python <3.8
    import pkg_resources

    __version__ = pkg_resources.get_distribution("plutoplot").version
    del pkg_resources
'''

from .pytools  import savefig, show, ring
from .image    import Image
from .load     import Load
from .loadpart import LoadPart