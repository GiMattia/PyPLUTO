"""Warnings of pyPLUTO: their categories, and one way to raise them.

Every warning of the package is a PyPLUTOWarning, which is what Configure
shows every time and what a user ignores to silence pyPLUTO alone. The
subclasses say what kind of problem it is, so a user can act on one kind:
PyPLUTODeprecationWarning is also a DeprecationWarning, so Python and pytest
treat it as one, and PyPLUTOKeywordWarning marks a keyword that was not used
or conflicts with another.

ppwarn attributes a warning to the user's own line, the first frame outside
the package, however deep inside it the warning was raised: a fixed
stacklevel cannot, since the depth depends on how many managers the call
went through. Python 3.12 added skip_file_prefixes to warnings.warn for
this; the package supports 3.11, so the frames are counted here.
"""

from __future__ import annotations

import inspect
import warnings
from pathlib import Path

# Every frame whose file lies under this folder belongs to pyPLUTO
_PACKAGE = str(Path(__file__).resolve().parent.parent)


class PyPLUTOWarning(UserWarning):
    """Base category of every warning raised by pyPLUTO."""


class PyPLUTODeprecationWarning(PyPLUTOWarning, DeprecationWarning):
    """A keyword or a function of pyPLUTO that will be removed."""


class PyPLUTOKeywordWarning(PyPLUTOWarning):
    """A keyword that was not used, or conflicts with another one."""


def ppwarn(message: str, category: type[Warning] = PyPLUTOWarning) -> None:
    """Warn from the first frame outside pyPLUTO, the user's own line.

    The frames are walked up from the caller of ppwarn until one lies
    outside the package; its depth is the stacklevel handed to
    warnings.warn. When every frame is inside the package, as during the
    import of pyPLUTO itself, the warning goes to the outermost one.

    Parameters
    ----------
    - message (not optional): str
        The text of the warning.
    - category: type[Warning], default PyPLUTOWarning
        The category of the warning, normally one of the pyPLUTO ones.

    Returns
    -------
    - None

    Examples
    --------
    - Example #1: a keyword that was not used

        >>> ppwarn("Unused kwargs: {'colour'}", PyPLUTOKeywordWarning)

    - Example #2: a keyword that will be removed

        >>> ppwarn("'close' is deprecated", PyPLUTODeprecationWarning)

    """
    # Level 2 is the caller of ppwarn; every frame inside the package adds one
    level = 2
    frame = inspect.currentframe()
    frame = frame.f_back if frame is not None else None
    while frame is not None and frame.f_code.co_filename.startswith(_PACKAGE):
        frame = frame.f_back
        level += 1
    warnings.warn(message, category, stacklevel=level)
