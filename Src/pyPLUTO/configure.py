import sys
import traceback
import warnings
from types import TracebackType
from typing import Any


class Configure:
    """Class to handle the init tools for pyPLUTO. Tools include finding the
    session, setting up the handlers, and other initialization tasks."""

    greeted = False

    def __init__(
        self, colorerr: bool = True, colorwarn: bool = True, greet: bool = True
    ) -> None:
        """Initialize the Configure class."""
        self.version: str = "1.0"
        self.colorerr: bool = colorerr
        self.colorwarn: bool = colorwarn
        self.session: str = self._find_session()
        self._setup_handlers(colorwarn, colorerr)
        if greet and not Configure.greeted:
            print(f"PyPLUTO version: {self.version}   session: {self.session}")
            Configure.greeted = True

    def _find_session(self) -> str:
        """Find the session in which the code is running.

        Returns
        -------
        - session: str
            The name of the session.

        Parameters
        ----------
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
        def get_ipython_wrapper() -> Any:
            """Wrapper to get the IPython instance. Try to import get_ipython
            from IPython.core.getipython. If it fails, return None.
            This is useful for standard Python interpreter sessions where
            IPython is not available.
            """
            try:
                from IPython.core.getipython import get_ipython

                return get_ipython()  # type: ignore
            except ImportError:
                return None

        # Get the ipython method (from IPthon or from the ImportError)

        ipython = get_ipython_wrapper()

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

    def color_warning(
        self,
        message: str,
        category: type[Warning],
        filename: str,
        lineno: int,
        _file: str | None = None,
        _line: str | None = None,
    ) -> str:
        """Method to color the warnings in yellow.

        Parameters
        ----------
        - message: str
            The warning message.
        - category: type[Warning]
            The category of the warning.
        - filename: str
            The name of the file where the warning occurred.
        - lineno: int
            The line number where the warning occurred.
        - _file: str | None, optional
            Not used, kept for compatibility.
        - _line: str | None, optional
            Not used, kept for compatibility.

        Returns
        -------
        - str
            The formatted warning message with color codes.

        """
        # Format the warning message with color codes
        message = (
            f"\33[33m{category.__name__}: {message}"
            f"[{filename}:{lineno}]\33[0m\n"
        )

        # Return the colored message
        return message

    def color_error(
        self,
        _type: type[BaseException] | None,
        value: BaseException | None,
        tb: TracebackType | None,
    ) -> None:
        """Method to color the errors in red.

        Parameters
        ----------
        - _type: type[BaseException] | None
            The type of the exception.
        - value: BaseException | None
            The exception instance.
        - tb: TracebackType | None
            The traceback object.

        Returns
        -------
        - None

        """
        # Traces the error and writes it in red
        traceback_str = "".join(traceback.format_tb(tb))
        sys.stderr.write(f"\033[91m{traceback_str}\033[0m")
        sys.stderr.write(f"\33[31m{value}\33[0m\n")  # Red color for errors

        # End of the function

    def _setup_handlers(
        self, colorwarn: bool = True, colorerr: bool = True
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
        # Set up the "always" filter for warnings
        warnings.simplefilter("always")

        # Set up the handlers for warnings and errors
        if colorwarn:
            warnings.formatwarning = self.color_warning  # type: ignore
        if colorerr:
            sys.excepthook = self.color_error

        # End of the function
