"""Module for reading definitions and pluto.ini files."""

from __future__ import annotations

import logging
import re
from pathlib import Path

import inifix

from pyPLUTO.loadmixin import LoadMixin
from pyPLUTO.loadstate import LoadState

logger = logging.getLogger(__name__)


class FiledefpliniManager(LoadMixin):
    """Manage loading of definitions headers and the pluto.ini file.

    Parameters
    ----------
    - state: LoadState
        The load state object.
    - defh: bool | str | None
        The path to the definitions header file.
    - plini: bool | str | None
        The path to the pluto.ini file.
    """

    def __init__(
        self,
        state: LoadState,
        defh: bool | str | None,
        plini: bool | str | None,
    ) -> None:
        """Initialize the FiledefpliniManager."""
        self.state = state
        if defh is not False:
            pathdefh = self.state.pathdir / Path("definitions.h")
            defhfile = "definitions.hpp"
            if not pathdefh.exists():
                pathdefh = self.state.pathdir / Path("definitions.hpp")
                defhfile = "definitions.h"
            try:
                self.state.defh = self.read_defh(pathdefh)
            except FileNotFoundError:
                logger.info("No %s is read!", defhfile) if defh is True else ...

        # Try to read the file pluto.ini
        if isinstance(plini, str):
            pathplini = self.state.pathdir / Path(plini)
        elif plini is not False:
            pathplini = self.state.pathdir / Path("pluto.ini")
        try:
            self.state.plini = inifix.load(pathplini, sections="require")
        except FileNotFoundError:
            logger.info("No pluto.ini is read!") if plini is True else ...

    def read_defh(self, filepath: Path) -> dict:
        """Read a header file and extract definitions.

        This function reads a header file, extracts lines that start with
        '#define', and converts the values to their appropriate types (boolean,
        integer, float, or string).

        Parameters
        ----------
        - filepath: str
            The path to the header file to read.

        Returns
        -------
        - dict

        """
        # Read the file, check if a line starts with '#define',
        # and split the line into key and value.
        # Convert the value using _convert_value function.
        with open(filepath) as file:
            # Return a dictionary comprehension that processes each line
            return {
                key: self.convert_value(value)
                for line in file
                if line.strip().startswith("#define")
                for _, key, value in [
                    re.split(r"\s+", line.strip(), maxsplit=2)
                ]
            }

    def convert_value(self, value: str) -> bool | int | float | str:
        """Convert a string value to its appropriate type.

        This function attempts to convert a string value into a boolean,
        integer, float, or leave it as a string if it cannot be converted.

        Parameters
        ----------
        - value: str
            The string value to convert.

        Returns
        -------
        - bool | int | float | str

        """
        # Convert the value to uppercase to handle case-insensitive comparisons
        value_upper = value.upper()

        # Check for boolean values first
        if value_upper in {"YES", "TRUE"}:
            return True
        if value_upper in {"NO", "FALSE"}:
            return False

        # Try to convert to an integer or float, if possible
        try:
            return float(value) if "." in value or "e" in value else int(value)
        except ValueError:
            return value
