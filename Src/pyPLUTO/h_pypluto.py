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
    """Checks if a parameter is in the corresponding list depending on
    the function. If the parameter does not belong to the list it raises
    a warning.

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
