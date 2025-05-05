import sys
import traceback
import warnings
from typing import Any


def makelist(el: Any) -> list[Any]:
    """If the element is not a list, it converts it into a list.

    Returns
    -------
    - list[Any]
        The list of chosen elements.

    Parameters
    ----------
    - el (not optional): Any
        The element to be converted into a list.

    Notes
    -----
    - None

    ----

    Examples
    --------
    - Example #1: element is a list

        >>> makelist([1,2,3])
        [1,2,3]

    - Example #2: element is not a list

        >>> makelist(1)
        [1]

    """
    # Return the element as a list
    return el if isinstance(el, list) else [el]


def check_par(par: set[str], func: str, **kwargs: Any) -> None:
    """Checks if a parameter is in the corresponding list depending on the
    function. If the parameter does not belong to the list it raises a warning.

    Returns
    -------
    - None

    Parameters
    ----------
    - func (not optional): str
        The name of the function.
    - par (not optional): list[str]
        The function correct parameters.
    - **kwargs: dict
        The selected parameters.

    Notes
    -----
    - None

    ----

    Examples
    --------
    - Example #1: check if the parameters are in the list (no warning)

        **kwargs = {'a': 1, 'b': 2, 'c': 3}
        >>> check_par({'a','b','c'}, 'func', **kwargs)

    - Example #2: check if the parameters are in the list (raises warning)

        **kwargs = {'a': 1, 'd': 2, 'c': 3}
        >>> check_par({'a','b','c'}, 'func', **kwargs)

    """
    # Check if the parameters are in the list
    notfound: list[str] = [(i) for i in kwargs if i not in par]

    # If the parameters are not in the list, raise a warning
    if len(notfound) > 0:
        warn = (
            f"WARNING: elements {notfound!s} not found!"
            f"Please check your spelling! (function {func})"
        )
        warnings.warn(warn, UserWarning)

    # End of the function


# Set color warning formatter
def color_warning(message, category, filename, lineno, file=None, line=None):
    message = f"\33[33m{category.__name__}: {message}" f"[{filename}:{lineno}]\33[0m\n"
    return message


# Set color error formatter
def color_error(type, value, tb):
    traceback_str = "".join(traceback.format_tb(tb))
    sys.stderr.write(f"\033[91m{traceback_str}\033[0m")
    sys.stderr.write(f"\33[31m{value}\33[0m\n")  # Red color for errors


# Define the session
def find_session():
    """Find the session in which the code is running.

    Returns
    -------
    - session: str
        The name of the session.

    Parameters
    ----------
    - None

    Notes
    -----
    - None

    ----

    Examples
    --------
    - Example #1: Standard Python interpreter

        >>> find_session()
        'Standard Python interpreter'

    - Example #2: Jupyter notebook or qtconsole

        >>> find_session()
        'Jupyter notebook or qtconsole'

    - Example #3: Terminal running IPython

        >>> find_session()
        'Terminal running IPython'

    - Example #4: Unknown session

        >>> find_session()
        'Unknown session'

    """
    # Try to get IPython. If not available, it's not an IPython session.
    try:
        from IPython import get_ipython
    except ImportError:

        def get_ipython():
            return None

    # Get the ipython method (from IPthon or from the ImportError)
    ipython = get_ipython()

    # Find the session name
    shell = ipython.__class__.__name__

    # Standard Python interpreter
    if ipython is None:
        session = "Standard Python interpreter"
    # Jupyter notebook or qtconsole
    elif shell == "ZMQInteractiveShell":
        session = "Jupyter notebook or qtconsole"
    # Terminal running IPython
    elif shell == "TerminalInteractiveShell":
        session = "Terminal running IPython"
    # Unknown session
    else:
        session = "Unknown session"

    # Return the session
    return session
