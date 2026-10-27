"""Configure the pyPLUTO package: the handlers, the greeting, pp.configure.

The settings themselves, their values and where they are read from, live in
settings.py; this module applies them. Configure runs once while pyPLUTO is
imported: it installs the handlers that show errors and warnings, attaches
the printer of the messages, and greets. pp.configure changes the settings
while the program runs.

The handlers are installed once and read the settings each time they show
something, so a change made with pp.configure takes effect at once. What
they show:

- an uncaught error: red when colors is "always", or when it is "PyPLUTO"
  and the error is a PyPLUTOError. With errors="short", a PyPLUTOError loses
  the frames inside pyPLUTO, leaving the user's own lines and the message;
  any other error is shown in full, since it may be a real bug.
- a warning: yellow by the same rule, for a PyPLUTOWarning; any warning not
  colored keeps Python's own format.
"""

from __future__ import annotations

import importlib
import logging
import sys
import traceback
import warnings
from pathlib import Path
from types import TracebackType
from typing import TYPE_CHECKING, Any, Unpack, cast

from pyPLUTO.utils.pperrors import PyPLUTOError, PyPLUTOInternalError
from pyPLUTO.utils.ppwarnings import PyPLUTOWarning
from pyPLUTO.utils.settings import SETTINGS, SettingsKwargs, check

if TYPE_CHECKING:
    from IPython.core.interactiveshell import InteractiveShell

# Every frame whose file lies under this folder belongs to pyPLUTO
PACKAGE = str(Path(__file__).resolve().parent.parent)

# Python's own format of a warning, kept for the warnings not colored
PYTHON_FORMATWARNING = warnings.formatwarning

# The line that ends the report of a PyPLUTOInternalError
BUG_REPORT = (
    "This is a bug in PyPLUTO: please report it at "
    "https://github.com/GiMattia/PyPLUTO/issues\n"
)


class Configure:
    """Handle the init tools for pyPLUTO.

    Tools include finding the session, setting up the handlers, and other
    initialization tasks.
    """

    greeted = False

    def __init__(self, version: str = "Unknown") -> None:
        """Initialize the Configure class.

        The greeting is printed once per process, and only if the greet
        setting is on.

        Parameters
        ----------
        - version: str, default "Unknown"
            The version of the pyPLUTO package.

        Returns
        -------
        - None

        """
        self.version: str = version
        self.session: str = self.find_session()
        self.setup_handlers()
        if SETTINGS["greet"] and not Configure.greeted:
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

            >>> Configure().find_session()
            'Standard Python interpreter'

        - Example #2: Jupyter notebook or qtconsole

            >>> Configure().find_session()
            'Jupyter notebook or qtconsole'

        - Example #3: Terminal running IPython

            >>> Configure().find_session()
            'Terminal running IPython'

        - Example #4: Unknown session

            >>> Configure().find_session()
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
        """Color a warning in yellow, if the colors setting asks for it.

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
            The warning colored, or in Python's own format when the colors
            setting leaves it out.

        """
        colors = SETTINGS["colors"]
        ours = issubclass(category, PyPLUTOWarning)
        if colors == "always" or (colors == "PyPLUTO" and ours):
            text = f"{category.__name__}: {message}[{filename}:{lineno}]"
            return f"\33[33m{text}\33[0m\n"
        return PYTHON_FORMATWARNING(message, category, filename, lineno, _line)

    def color_error(
        self,
        exc_type: type[BaseException] | None,
        value: BaseException | None,
        tb: TracebackType | None,
    ) -> None:
        """Report an uncaught error, colored and shortened as the settings ask.

        The report is Python's own: the header, the frames, the type and the
        message of the error, and any exception chained to it. With
        errors="short", a PyPLUTOError loses the frames inside pyPLUTO; a
        PyPLUTOInternalError never does, and its report ends with a line
        asking to report the bug.

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
        ours = exc_type is not None and issubclass(exc_type, PyPLUTOError)
        internal = exc_type is not None and issubclass(
            exc_type, PyPLUTOInternalError
        )
        if ours and not internal and SETTINGS["errors"] == "short":
            tb = self.user_frames(tb)
        report = "".join(traceback.format_exception(exc_type, value, tb))
        if internal:
            report += BUG_REPORT

        colors = SETTINGS["colors"]
        if colors == "always" or (colors == "PyPLUTO" and ours):
            report = f"\33[31m{report}\33[0m"
        sys.stderr.write(report)

    @staticmethod
    def user_frames(tb: TracebackType | None) -> TracebackType | None:
        """Drop the frames inside pyPLUTO from a traceback.

        The frames left are linked to each other again, so the traceback
        reads as if the error had been raised from the user's last line.

        Parameters
        ----------
        - tb: TracebackType | None
            The traceback of an uncaught error.

        Returns
        -------
        - TracebackType | None
            The first frame outside pyPLUTO, or None if there is none.

        Examples
        --------
        - Example #1: the traceback of a PyPLUTOError

            >>> Configure.user_frames(error.__traceback__)

        """
        frames = []
        while tb is not None:
            if not tb.tb_frame.f_code.co_filename.startswith(PACKAGE):
                frames.append(tb)
            tb = tb.tb_next
        if not frames:
            return None
        for frame, after in zip(frames, [*frames[1:], None], strict=True):
            frame.tb_next = after
        return frames[0]

    def setup_handlers(self) -> None:
        """Set up the handlers for the warnings and errors.

        Returns
        -------
        - None

        """
        # The warnings not raised through PPWarn yet are shown every time;
        # this filter goes once they all are
        warnings.filterwarnings("always", module="pyPLUTO")
        apply_warnings()

        # Installed always: they read the settings each time they show
        # something. Python lets formatwarning be replaced, but ty types it
        # as that very function and refuses any other; pyright needs no cast
        warnings.formatwarning = cast("Any", self.color_warning)
        sys.excepthook = self.color_error

        # Attach a stdout handler so logger.info() calls are visible,
        # matching the old print() behaviour. The logger lets everything
        # through, since PPLog has already decided what is shown
        pkg_logger = logging.getLogger("pyPLUTO")
        if not pkg_logger.handlers:
            _handler = logging.StreamHandler(sys.stdout)
            _handler.setFormatter(logging.Formatter("%(message)s"))
            pkg_logger.addHandler(_handler)
            pkg_logger.setLevel(logging.DEBUG)


def apply_warnings() -> None:
    """Install the filter the warnings setting asks for on PyPLUTOWarning.

    The filter goes in front of every other, so the setting holds over the
    filter of the old warnings and over earlier calls.

    Returns
    -------
    - None

    """
    warnings.filterwarnings(SETTINGS["warnings"], category=PyPLUTOWarning)


class Settings(dict[str, Any]):
    """The settings in use, as pp.configure gives them back.

    It reads and prints as a dict. Used in a with statement, it puts the
    settings back as they were before the call that made it.
    """

    def __init__(self, previous: dict[str, Any]) -> None:
        """Copy the settings in use, and keep the ones to put back.

        Parameters
        ----------
        - previous: dict[str, Any]
            The settings before the call, restored at the end of a with.

        Returns
        -------
        - None

        """
        super().__init__(SETTINGS)
        self.previous = previous

    def __enter__(self) -> Settings:
        """Enter the with statement, the settings already in use."""
        return self

    def __exit__(self, *_exc: object) -> None:
        """Put back the settings as they were before the call."""
        store(self.previous)


def store(values: dict[str, Any]) -> None:
    """Store settings already checked, and apply the warnings filter.

    Parameters
    ----------
    - values: dict[str, Any]
        The settings to store, by name.

    Returns
    -------
    - None

    """
    SETTINGS.update(values)
    apply_warnings()


def configure(**kwargs: Unpack[SettingsKwargs]) -> Settings:
    """Change the settings of pyPLUTO, and give back the ones in use.

    Called without keywords it only gives them back. Every value is checked
    before any is stored, so a wrong one changes nothing. Used in a with
    statement, the change lasts until the end of the block.

    Parameters
    ----------
    - colors: "PyPLUTO" | "always" | None
        Which errors and warnings are colored: pyPLUTO's, all, or none.
    - errors: "short" | "full"
        How a pyPLUTO error is shown: the user's own lines and the message,
        or the whole traceback.
    - greet: bool
        Whether importing pyPLUTO prints the greeting; read at import, so
        it matters in a file or a variable, not here.
    - text: "default" | "verbose" | bool | None
        False shows only the warnings, "default" (or None) the ordinary
        information, True or "verbose" also the debug details.
    - warnings: "always" | "once" | "ignore" | "error"
        What happens to pyPLUTO's warnings.

    Returns
    -------
    - Settings
        Every setting in use after the call, as a dict.

    Raises
    ------
    - PyPLUTOConfigError
        If a setting does not exist or a value is not one it accepts.

    Examples
    --------
    - Example #1: read the settings

        >>> pp.configure()
        {'greet': True, 'text': 'default', 'colors': 'PyPLUTO', ...}

    - Example #2: color every error and warning

        >>> pp.configure(colors="always")

    - Example #3: silence pyPLUTO inside a block only

        >>> with pp.configure(text=False, warnings="ignore"):
        ...     D = pp.Load()

    """
    previous = dict(SETTINGS)
    store({name: check(name, value) for name, value in kwargs.items()})
    return Settings(previous)
