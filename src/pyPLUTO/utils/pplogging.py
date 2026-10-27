"""Messages of pyPLUTO, shown at the verbosity of the object sending them.

PPLog.info is the ordinary information, shown by default; PPLog.debug is a
detail, shown only with text=True or "verbose". The verbosity is read from
self.state.classlog of the method calling them, where every object keeps the
text it was built with: None, or a caller without one, follows the package,
whose text is the setting of the same name (see settings.py). Every object
built with text=None therefore follows the package, and one given its own
text decides for its messages alone, with the same meaning.
"""

from __future__ import annotations

import inspect
import logging

from pyPLUTO.utils.settings import SETTINGS, TextValue, check

# The level each text value shows, for the package and for each object
LEVELS = {
    False: logging.WARNING,
    "default": logging.INFO,
    True: logging.DEBUG,
    "verbose": logging.DEBUG,
}


class PPLog:
    """Send the messages of pyPLUTO.

    Examples
    --------
    - Example #1: The ordinary information

        >>> PPLog.info("Loaded output %s", 3)

    - Example #2: A detail

        >>> PPLog.debug("Final step number: %s", 120)

    """

    @staticmethod
    def info(msg: str, *args: object) -> None:
        """Log the ordinary information, shown by default.

        Parameters
        ----------
        - msg: str
            The message, with a %s for each of the args.
        - *args: object
            The values put in the message.

        Returns
        -------
        - None

        """
        PPLog.send(logging.INFO, msg, *args)

    @staticmethod
    def debug(msg: str, *args: object) -> None:
        """Log a detail, shown only with text=True or "verbose".

        Parameters
        ----------
        - msg: str
            The message, with a %s for each of the args.
        - *args: object
            The values put in the message.

        Returns
        -------
        - None

        """
        PPLog.send(logging.DEBUG, msg, *args)

    @staticmethod
    def send(level: int, msg: str, *args: object) -> None:
        """Log the message if the text of the calling object allows it.

        Parameters
        ----------
        - level: int
            The level of the message, logging.INFO or logging.DEBUG.
        - msg: str
            The message, with a %s for each of the args.
        - *args: object
            The values put in the message.

        Returns
        -------
        - None

        """
        # Two frames up: info or debug, then the method that called it
        frame = inspect.currentframe()
        for _ in range(2):
            frame = frame.f_back if frame is not None else None
        caller = frame.f_locals.get("self") if frame is not None else None
        text = getattr(getattr(caller, "state", None), "classlog", None)
        if level >= LEVELS[SETTINGS["text"] if text is None else text]:
            # The record points at the method that called info or debug
            logging.getLogger("pyPLUTO").log(level, msg, *args, stacklevel=3)


def set_text(text: TextValue = None) -> None:
    """Set the verbosity of pyPLUTO logging, the text setting.

    A shortcut for pp.configure(text=...). Every object built with text=None
    follows it; an object given its own text decides for its messages alone.

    Parameters
    ----------
    - text: TextValue, default None
        False shows only the warnings, "default" (or None) the ordinary
        information, True or "verbose" also the debug details.

    Returns
    -------
    - None

    Raises
    ------
    - PyPLUTOConfigError
        If text is not one of the values above.

    Examples
    --------
    - Example #1: Only the warnings

        >>> set_text(False)

    - Example #2: The ordinary information

        >>> set_text("default")

    - Example #3: Also the debug details

        >>> set_text("verbose")

    """
    SETTINGS["text"] = check("text", text)
