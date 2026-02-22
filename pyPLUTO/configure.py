"""Module to configure the pyPLUTO package."""

import importlib
import sys
import traceback
import warnings
from collections.abc import Callable
from types import TracebackType
from typing import TYPE_CHECKING, cast

if TYPE_CHECKING:
    from IPython.core.interactiveshell import InteractiveShell

FormatWarning = Callable[
    [Warning | str, type[Warning], str, int, str | None], str
]


class Configure:
    """Handle the init tools for pyPLUTO.

    Tools include finding the session, setting up the handlers, and other
    initialization tasks.
    """

    greeted = False

    def __init__(
        self, colorerr: bool = True, colorwarn: bool = True, greet: bool = True
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

        Returns
        -------
        - None

        """
        self.version: str = "1.1.1"
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
        # Note the quotes around the return type of the get_ipython_wrapper
        # function. This is because pylint would throw an error.
        def get_ipython_wrapper() -> "InteractiveShell | None":
            """Return the IPython instance, or None if not available."""
            warnings.filterwarnings(
                "ignore",
                message=r".*importing 'Const' from 'astroid' is deprecated.*",
                category=DeprecationWarning,
            )

            try:
                ipy_mod = importlib.import_module("IPython.core.getipython")
                get_ipython = ipy_mod.get_ipython
                return cast("InteractiveShell | None", get_ipython())
            except (ImportError, AttributeError):
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
        message: Warning | str,
        category: type[Warning],
        filename: str,
        lineno: int,
        _file: str | None = None,
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
        msg = str(message)

        return f"\33[33m{category.__name__}: {msg}[{filename}:{lineno}]\33[0m\n"

    def color_error(
        self,
        _type: type[BaseException] | None,
        value: BaseException | None,
        tb: TracebackType | None,
    ) -> None:
        """Color the errors in red.

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

    def _setup_handlers(
        self, colorwarn: bool = True, colorerr: bool = True
    ) -> None:
        """Set up the handlers for the warnings and errors.

        Note that a type ignore is placed on the line where the warning handler
        is set up because mypy and pyrefly would throw the following error:

        (Warning | str, type[Warning], str, int, str | None) -> str is not
        assignable to attribute formatwarning with type (message: Warning | str,
        category: type[Warning], filename: str, lineno: int, line: str |
        None = None) -> str
        Incompatible types in assignment (expression has type
        "Callable[[Warning | str, type[Warning], str, int, str | None], str]",
        variable has type "Callable[[Arg(Warning | str, 'message'),
        Arg(type[Warning], 'category'), Arg(str, 'filename'),
        Arg(int, 'lineno'), DefaultArg(str | None, 'line')], str]")

        This is because the signature of the color_warning method does not
        exactly match the expected signature of the formatwarning attribute.
        However, since the color_warning method is designed to be compatible
        with the formatwarning attribute, we can safely ignore this type error.

        The correct approach would be to use the following piece of code:

        if colorwarn:
            def _formatwarning(
                message: Warning | str,
                category: type[Warning],
                filename: str,
                lineno: int,
                line: str | None = None,
            ) -> str:
                return self.color_warning(
                    message,
                    category,
                    filename,
                    lineno,
                    line
                )

            warnings.formatwarning = _formatwarning

        but, for simplicity, we directly assign the color_warning method to the
        formatwarning attribute and ignore the type error.

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
