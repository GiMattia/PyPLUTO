"""Warnings of pyPLUTO: their categories, and one way to raise them.

Every warning of the package is a PyPLUTOWarning, which is what Configure
shows every time and what a user ignores to silence pyPLUTO alone. The
subclasses say what kind of problem it is, so a user can act on one kind:
PyPLUTODeprecationWarning is also a DeprecationWarning, so Python and pytest
treat it as one, and PyPLUTOKeywordWarning marks a keyword that was not used.
The base itself is never raised: every warning uses the subclass that says
what it is about.

PPWarn.warn(message, category) is written as warnings.warn is, so a warning
of the standard library becomes one of pyPLUTO by changing only the name. It
attributes the warning to the user's own line, the first frame outside the
package, however deep inside it the warning was raised: a fixed stacklevel
cannot, since the depth depends on how many managers the call went through.
Python 3.12 added skip_file_prefixes to warnings.warn for this, which is
used from 3.12 on; on 3.11 the frames are counted here.
"""

from __future__ import annotations

import inspect
import sys
import warnings
from pathlib import Path

# Every frame whose file lies under this folder belongs to pyPLUTO
_PACKAGE = str(Path(__file__).resolve().parent.parent)


class PyPLUTOWarning(UserWarning):
    """Base category of every warning raised by pyPLUTO.

    Only for filtering: every warning raised is one of the subclasses below.
    The warnings setting acts on it.

    Examples
    --------
    - pp.configure(warnings="ignore") silences every warning of PyPLUTO.

    """


class PyPLUTOBehaviorWarning(PyPLUTOWarning):
    """PyPLUTO does something the user may not expect.

    Nothing is wrong, but the result may differ from what the call seems to
    ask for.

    Examples
    --------
    - I.plot(x, y, ncol=2) on a figure with axes creates new ones;
    - I.plot(x, y, legpos=0) with no labelled line draws no legend.

    """


class PyPLUTOConfigWarning(PyPLUTOWarning):
    """A setting from a file or the environment is ignored.

    Raised while PyPLUTO is imported, so a typo never makes the import fail;
    the setting keeps its earlier value.

    Examples
    --------
    - colors = "pypluto" in pypluto.toml;
    - PYPLUTO_TEXT=loud.

    """


class PyPLUTOConflictWarning(PyPLUTOWarning):
    """Two keywords contradict each other, so one of them wins.

    The message says which one is kept.

    Examples
    --------
    - I.contour(var, c="k", cmap="viridis") uses c;
    - I.zoom(right=0.9, width=0.3) sets left from right and width.

    """


class PyPLUTODependencyWarning(PyPLUTOWarning):
    """An optional program or package is missing, so PyPLUTO falls back.

    Examples
    --------
    - pp.Image(LaTeX="pgf") without LaTeX installed uses LaTeX=True instead.

    """


class PyPLUTODeprecationWarning(PyPLUTOWarning, DeprecationWarning):
    """A keyword or a method that will be removed.

    Also a DeprecationWarning, so Python and pytest treat it as one. The
    message names what to use instead.

    Examples
    --------
    - pp.Image(close=True), now replace=True.

    """


class PyPLUTOKeywordWarning(PyPLUTOWarning):
    """A keyword was given that the method never reads.

    Usually a typo; it is raised by the keyword check of every method.

    Examples
    --------
    - I.plot(x, y, colour="r"), where the keyword is c.

    """


class PyPLUTOOptionWarning(PyPLUTOWarning):
    """A value was not accepted as given, so it is replaced or adjusted.

    The drawing goes on with the replacement, which the message names.

    Examples
    --------
    - I.display(var, cscale="logg") is drawn with "linear";
    - I.plot(x, y2d, c=["r", "b"]) for three lines cycles the two colors.

    """


class PPWarn:
    """Raise the warnings of pyPLUTO, written as warnings.warn is.

    Examples
    --------
    - Example #1: a keyword that was not used

        >>> PPWarn.warn("Unused kwargs: {'colour'}", PyPLUTOKeywordWarning)

    """

    @staticmethod
    def warn(message: str, category: type[Warning] = PyPLUTOWarning) -> None:
        """Warn from the first frame outside pyPLUTO, the user's own line.

        From Python 3.12, warnings.warn skips the frames of the package
        itself, through skip_file_prefixes. On 3.11 the frames are walked up
        here from the caller of warn until one lies outside the package, and
        its depth is the stacklevel handed to warnings.warn. There is no
        stacklevel to give, since it is found either way.

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

            >>> PPWarn.warn("Unused kwargs: {'colour'}", PyPLUTOKeywordWarning)

        - Example #2: a keyword that will be removed

            >>> PPWarn.warn("'close' is deprecated", PyPLUTODeprecationWarning)

        """
        # From Python 3.12 the frames of the package are skipped by Python
        if sys.version_info >= (3, 12):
            warnings.warn(message, category, skip_file_prefixes=(_PACKAGE,))
            return

        # On 3.11 they are counted here: level 2 is the caller of warn, and
        # every frame inside the package adds one
        level = 2
        frame = inspect.currentframe()
        frame = frame.f_back if frame is not None else None
        while frame is not None and frame.f_code.co_filename.startswith(
            _PACKAGE
        ):
            frame = frame.f_back
            level += 1
        warnings.warn(message, category, stacklevel=level)
