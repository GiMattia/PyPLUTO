"""Helper functions for pyPLUTO."""

from typing import TypeVar

T = TypeVar("T")


def makelist(el: T | list[T]) -> list[T]:
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

        >>> makelist([1, 2, 3])
        [1,2,3]

    - Example #2: element is not a list

        >>> makelist(1)
        [1]

    """
    # Return the element as a list
    return el if isinstance(el, list) else [el]
