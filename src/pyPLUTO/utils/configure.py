"""Module to configure the pyPLUTO package."""

from __future__ import annotations

import importlib
import logging
import sys
import traceback
import warnings
from types import TracebackType
from typing import TYPE_CHECKING, Any, cast

from pyPLUTO.utils.ppwarnings import PyPLUTOWarning

if TYPE_CHECKING:
    from IPython.core.interactiveshell import InteractiveShell


class Configure:
    """Handle the init tools for pyPLUTO.

    Tools include finding the session, setting up the handlers, and other
    initialization tasks.
    """

    greeted = False

    def __init__(
        self,
        version: str = "Unknown",
        colorerr: bool = True,
        colorwarn: bool = True,
        greet: bool = True,
    ) -> None:
        """Initialize the Configure class.

        Parameters
        ----------
        - colorerr: bool, default True
            If True, color the errors in red.
        - colorwarn: bool, default True
            If True, color the warnings in yellow.
        - greet: bool, default True
            If True, print a greeting message with the version and session.
        - version: str, default "Unknown"
            The version of the pyPLUTO package.

        Returns
        -------
        - None

        """
        self.version: str = version
        self.colorerr: bool = colorerr
        self.colorwarn: bool = colorwarn
        self.session: str = self.find_session()
        self.setup_handlers(colorwarn, colorerr)
        if greet and not Configure.greeted:
            print(f"PyPLUTO version: {self.version}   session: {self.session}")
            Configure.greeted = True

    def find_session(self) -> str:
        """Find the session in which the code is running.

        Returns
        -------
        - str

        Examples
        --------
        - Example #1: Standard Python interpreter

            >>> Configure(greet=False).find_session()
            'Standard Python interpreter'

        - Example #2: Jupyter notebook or qtconsole

            >>> Configure(greet=False).find_session()
            'Jupyter notebook or qtconsole'

        - Example #3: Terminal running IPython

            >>> Configure(greet=False).find_session()
            'Terminal running IPython'

        - Example #4: Unknown session

            >>> Configure(greet=False).find_session()
            'Unknown session'

        """

        # Try to get IPython. If not available, it's not an IPython session.
        def get_ipython_wrapper() -> InteractiveShell | None:
            """Return the IPython instance, or None if not available."""
            try:
                ipy_mod = importlib.import_module("IPython.core.getipython")
                get_ipython = ipy_mod.get_ipython
                return get_ipython()
            except (ImportError, AttributeError):
                return None

        # Get the ipython method (from IPthon or from the ImportError)

        ipython = get_ipython_wrapper()

        # Standard Python interpreter
        if ipython is None:
            return "Standard Python interpreter"

        # Find the session name
        shell = ipython.__class__.__name__

        # Jupyter notebook or qtconsole
        if shell == "ZMQInteractiveShell":
            return "Jupyter notebook or qtconsole"
        # Terminal running IPython
        if shell == "TerminalInteractiveShell":
            return "Terminal running IPython"
        # Unknown session
        return "Unknown session"

    def color_warning(
        self,
        message: Warning | str,
        category: type[Warning],
        filename: str,
        lineno: int,
        _line: str | None = None,
    ) -> str:
        """Color the warnings in yellow.

        Parameters
        ----------
        - message: Warning | str
            The warning message.
        - category: type[Warning]
            The category of the warning.
        - filename: str
            The name of the file where the warning occurred.
        - lineno: int
            The line number where the warning occurred.
        - _line: str | None, default None
            The source line, which the colored message does not show.

        Returns
        -------
        - str
            The formatted warning message with color codes.

        """
        # Format the warning message with color codes
        msg = str(message)

        return f"\33[33m{category.__name__}: {msg}[{filename}:{lineno}]\33[0m\n"

    def color_error(
        self,
        exc_type: type[BaseException] | None,
        value: BaseException | None,
        tb: TracebackType | None,
    ) -> None:
        """Color the errors in red.

        The report is Python's own, coloured: the header, the frames, the
        type and the message of the error, and any exception chained to it.

        Parameters
        ----------
        - exc_type: type[BaseException] | None
            The type of the exception.
        - value: BaseException | None
            The exception instance.
        - tb: TracebackType | None
            The traceback object.

        Returns
        -------
        - None

        """
        report = "".join(traceback.format_exception(exc_type, value, tb))
        sys.stderr.write(f"\33[31m{report}\33[0m")

    def setup_handlers(
        self,
        colorwarn: bool = True,
        colorerr: bool = True,
    ) -> None:
        """Set up the handlers for the warnings and errors.

        Parameters
        ----------
        - colorwarn: bool, default True
            If True, color the warnings in yellow.
        - colorerr: bool, default True
            If True, color the errors in red.

        Returns
        -------
        - None

        """
        # Show every pyPLUTO warning every time, wherever it points; other
        # packages keep Python's defaults and the user's own filters. The
        # module filter covers the warnings not raised through ppwarn yet
        warnings.filterwarnings("always", category=PyPLUTOWarning)
        warnings.filterwarnings("always", module="pyPLUTO")

        # Set up the handlers for warnings and errors
        if colorwarn:
            # Python lets formatwarning be replaced, but ty types it as that
            # very function and refuses any other; pyright needs no cast
            warnings.formatwarning = cast("Any", self.color_warning)
        if colorerr:
            sys.excepthook = self.color_error

        # Attach a stdout handler so logger.info() calls are visible,
        # matching the old print() behaviour. The logger lets everything
        # through, since pplog has already decided what is shown
        pkg_logger = logging.getLogger("pyPLUTO")
        if not pkg_logger.handlers:
            _handler = logging.StreamHandler(sys.stdout)
            _handler.setFormatter(logging.Formatter("%(message)s"))
            pkg_logger.addHandler(_handler)
            pkg_logger.setLevel(logging.DEBUG)
