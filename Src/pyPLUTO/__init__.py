# Import the libraries, classes and functions
from .libraries import *
from .pytools   import savefig, show, ring
from .image     import Image
from .load      import Load
from .loadpart  import LoadPart

__version__ = "1.0.0"

try:
    shell = get_ipython().__class__.__name__
    if shell == 'ZMQInteractiveShell':
        __session__= "Jupyter notebook or qtconsole"
    elif shell == 'TerminalInteractiveShell':
        __session__ = "Terminal running IPython"
    else:
        __session__ = "Unknown session"
except NameError:
    __session__ = "Standard Python interpreter"
print(f"PyPLUTO version: {__version__}   session: {__session__}")

# Set color warning formatter
def color_warning(message, category, filename, lineno, file=None, line=None):
    message = (f"\33[33m{category.__name__}: {message}"
               f"[{filename}:{lineno}]\33[0m\n")  # Yellow color for warnings
    return message
warnings.simplefilter('always', DeprecationWarning)
warnings.formatwarning = color_warning


# Set color error formatter
def color_error(type, value, tb):
    traceback_str = "".join(traceback.format_tb(tb))
    sys.stderr.write(f"\033[91m{traceback_str}\033[0m")
    sys.stderr.write(f"\33[31m{value}\33[0m\n")  # Red color for errors
sys.excepthook = color_error
