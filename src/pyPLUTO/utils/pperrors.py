"""Errors of pyPLUTO: the categories it raises on purpose.

Every error the package raises on purpose is a PyPLUTOError, so a user can
catch all of them with one except, while a real bug, or an error from numpy
or matplotlib, still stops the code. This is also what the settings read:
colors="PyPLUTO" colors only these, and errors="short" hides the frames
inside the package only for these.

A subclass is named after what went wrong, not after the built-in it
resembles, and it also derives from the closest built-in, so code catching
that built-in keeps working: PyPLUTOConfigError is a ValueError too. The
classes take a message and nothing else, so they survive being pickled back
from a worker process. A new one is added when a file first needs it.
"""

from __future__ import annotations


class PyPLUTOError(Exception):
    """Base category of every error raised by pyPLUTO on purpose."""


class PyPLUTOConfigError(PyPLUTOError, ValueError):
    """A setting of pyPLUTO given an unknown name or an unknown value."""
