import re
from pathlib import Path
from typing import Any

try:
    import inifix
except ImportError:
    inifix = None

from pyPLUTO.loadmixin import LoadMixin
from pyPLUTO.loadstate import LoadState


class FiledefpliniManager(LoadMixin):
    def __init__(self, state: LoadState, **kwargs: Any) -> None:
        self.state = state
        defh = kwargs.get("defh")
        if defh is not False:
            pathdefh = self.pathdir / Path("definitions.h")
            defhfile = "definitions.hpp"
            if not pathdefh.exists():
                pathdefh = self.pathdir / Path("definitions.hpp")
                defhfile = "definitions.h"
            try:
                self.defh = self.read_defh(pathdefh)
            except FileNotFoundError:
                print(f"No {defhfile} is read!") if defh is True else ...

        # Try to read the file pluto.ini
        plini = kwargs.get("plini")
        if plini is not False:
            pathplini = self.pathdir / Path("pluto.ini")
            try:
                self.plini = self.read_plini(pathplini)
            except FileNotFoundError:
                print("No pluto.ini is read!") if plini is True else ...

    def read_defh(self, filepath: Path) -> dict:
        """Read a header file and extract definitions.

        This function reads a header file, extracts lines that start with
        '#define', and converts the values to their appropriate types (boolean,
        integer, float, or string).

        Returns
        -------
        dict
            A dictionary where keys are the defined names and values are the
            converted values.

        Parameters
        ----------
        filepath : str
            The path to the header file to read.

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

    def read_plini(self, filepath: Path) -> dict:
        """Read a pluto.ini file and extract settings.

        This function reads a pluto.ini file and extracts key-value pairs,
        converting the values to their appropriate types.

        Returns
        -------
        dict
            A dictionary where keys are the setting names and values are the
            converted values.

        Parameters
        ----------
        filepath : Path
            The path to the pluto.ini file to read.

        """
        if inifix is not None:
            conf = inifix.load(filepath)
            print("used inifix")
            return conf
        else:
            conf, section = {}, None

            with open(filepath) as f:
                for lines in f:
                    line = lines.strip()

                    if not line or line.startswith(("#", ";")):
                        continue

                    if line.startswith("["):
                        section = line.strip("[]")
                        conf[section] = {}
                        continue

                    if section is None:
                        continue

                    parts = line.split()
                    key = parts[0]
                    values = [self.parse_token(x) for x in parts[1:]]

                    conf[section][key] = (
                        values[0] if len(values) == 1 else values
                    )

            return conf

    def parse_token(self, x: str) -> int | float | str:
        try:
            return int(x)
        except ValueError:
            try:
                return float(x)
            except ValueError:
                return x

    def convert_value(self, value: str) -> bool | int | float | str:
        """Convert a string value to its appropriate type.

        This function attempts to convert a string value into a boolean,
        integer, float, or leave it as a string if it cannot be converted.

        Returns
        -------
        bool | int | float | str
            The converted value, which can be a boolean, integer, float, or the
            original string if conversion is not possible.

        Parameters
        ----------
        value : str
            The string value to convert.

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
