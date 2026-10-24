"""Messages of pyPLUTO, shown at the verbosity of the object sending them.

pplog.info is the ordinary information, shown by default; pplog.debug is a
detail, shown only with text=True. The verbosity is read from
self.state.classlog of the method calling them, where every object keeps the
text it was built with: None, or a caller without one, follows the package,
set with set_text. Every object built with text=None therefore follows
set_text, and one given its own text decides for its messages alone, with
the same meaning.
"""

from __future__ import annotations

import inspect
import logging

# The level each text value shows, for the package and for each object
LEVELS = {False: logging.WARNING, None: logging.INFO, True: logging.DEBUG}


class PPLog:
    """Send the messages of pyPLUTO.

    Examples
    --------
    - Example #1: The ordinary information

        >>> pplog.info("Loaded output %s", 3)

    - Example #2: A detail

        >>> pplog.debug("Final step number: %s", 120)

    """

    # The text of the package, set by set_text
    text: bool | None = None

    def info(self, msg: str, *args: object) -> None:
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
        self.send(logging.INFO, msg, *args)

    def debug(self, msg: str, *args: object) -> None:
        """Log a detail, shown only with text=True.

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
        self.send(logging.DEBUG, msg, *args)

    def send(self, level: int, msg: str, *args: object) -> None:
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
        if level >= LEVELS[self.text if text is None else text]:
            # The record points at the method that called info or debug
            logging.getLogger("pyPLUTO").log(level, msg, *args, stacklevel=3)


# The one instance, used as pplog.info(...) and pplog.debug(...)
pplog = PPLog()


def set_text(text: bool | None = None) -> None:
    """Set the verbosity of pyPLUTO logging.

    Every object built with text=None follows it; an object given its own
    text decides for its messages alone.

    Parameters
    ----------
    - text: bool | None
        None (default) enables standard INFO messages. False silences all
        output (WARNING level). True enables full debug output (DEBUG level).

    Returns
    -------
    - None

    Examples
    --------
    - Example #1: Silence all output

        >>> set_text(False)

    - Example #2: Default INFO output

        >>> set_text(None)

    - Example #3: Full debug output

        >>> set_text(True)

    """
    pplog.text = text
