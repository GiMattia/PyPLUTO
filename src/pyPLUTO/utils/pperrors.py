"""Errors of pyPLUTO: the categories it raises on purpose.

Every error the package raises on purpose is a PyPLUTOError, so a user can
catch all of them with one except, while an error from numpy or matplotlib
still stops the code. This is also what the settings read: colors="PyPLUTO"
colors only these, and errors="short" hides the frames inside the package
only for these. The exception is PyPLUTOInternalError, a guard that only a
bug in pyPLUTO can trip: it is always shown in full, with a line asking to
report it.

A subclass is named after what went wrong, not after the built-in it
resembles, and it also derives from the closest built-in, so code catching
that built-in keeps working: PyPLUTOConfigError is a ValueError too. The
classes take a message and nothing else, so they survive being pickled back
from a worker process. The base itself is never raised: every error uses
the subclass that says what went wrong.
"""

from __future__ import annotations


class PyPLUTOError(Exception):
    """Base category of every error raised by pyPLUTO on purpose.

    Only for catching: every error raised is one of the subclasses below.

    Examples
    --------
    - try: ... except pp.PyPLUTOError: catches every error of PyPLUTO.

    """


class PyPLUTOAttributeError(PyPLUTOError, AttributeError):
    """The attribute or variable asked for does not exist.

    Still an AttributeError, so hasattr and getattr with a default work as
    usual.

    Examples
    --------
    - D.rho2 on a Load that holds rho, prs and vx1.

    """


class PyPLUTOAxisError(PyPLUTOError, ValueError):
    """The axis asked for cannot be used.

    Raised when ax does not point to an axis of this image, or when axes
    are asked to share in a way that cannot work.

    Examples
    --------
    - I.plot(x, y, ax=5) on an image with two axes;
    - I.create_axes(sharex="diagonal").

    """


class PyPLUTOConfigError(PyPLUTOError, ValueError):
    """A setting was given an unknown name or an unknown value.

    Raised by pp.configure, which checks every value before storing any,
    so a wrong one changes nothing.

    Examples
    --------
    - pp.configure(colors="pypluto"), where the value is "PyPLUTO";
    - pp.configure(colours="always").

    """


class PyPLUTOCopyError(PyPLUTOError, TypeError):
    """An Image, Load or LoadPart was asked to be copied or pickled.

    They are refused on purpose: a load maps its files in memory, and a copy
    would either share them or read them whole.

    Examples
    --------
    - copy.deepcopy(D);
    - sending D to a worker process: send the output number instead, and
      call pp.Load in the worker.

    """


class PyPLUTODataError(PyPLUTOError, ValueError):
    """The data or the grid given cannot be drawn.

    Raised when arrays do not fit together, or when a method needs data
    that is not there.

    Examples
    --------
    - I.streamplot(vx, vy) with vx and vy of different shapes;
    - I.colorbar() on an axis with only lines, nothing colored by data.

    """


class PyPLUTOInternalError(PyPLUTOError, RuntimeError):
    """A guard that only a bug in PyPLUTO can trip.

    It never comes from what the user wrote, so it is always shown in full,
    with a line asking to report it.

    Examples
    --------
    - a drawing method reached before the Image has a figure.

    """


class PyPLUTOOptionError(PyPLUTOError, ValueError):
    """A keyword was given a value it does not accept.

    Raised when the value has no sensible fallback, so drawing cannot go on.

    Examples
    --------
    - I.text("a", xycoords="pixels"), where only "fraction", "points" and
      "figure" exist.

    """
