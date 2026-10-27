"""Settings of pyPLUTO: their values, and where they come from.

Five settings control how the package behaves, not what it computes:

- greet: True or False, whether importing pyPLUTO prints the greeting.
- text: False shows only the warnings, "default" the ordinary information,
  True or "verbose" also the debug details. None means the default here; on
  an object, None follows the package.
- colors: "PyPLUTO" colors only pyPLUTO's errors and warnings, "always"
  every error and warning, None nothing.
- warnings: what happens to pyPLUTO's warnings, "always", "once", "ignore"
  or "error".
- errors: how a pyPLUTO error is shown, "short" (the user's own lines and
  the message) or "full" (the whole traceback).

The settings and their values are written once, in SettingsKwargs: the type
checkers read it for pp.configure, and ALLOWED is read from it for the
check at runtime. Values are exact, "PyPLUTO" and not "pypluto".

Each source below overrides the one before, and the first four are read
while pyPLUTO is imported, so they can silence the greeting:

1. the defaults, in DEFAULTS;
2. the user file, pypluto/pypluto.toml in the user's configuration folder
   (~/.config on Linux and macOS, %APPDATA% on Windows);
3. the folder file, pypluto.toml in the current folder;
4. the environment variables, PYPLUTO_GREET, PYPLUTO_TEXT and so on;
5. pp.configure(...) while the program runs.

In a file or a variable, True, False and None are written true, false and
none. A wrong value there warns and is ignored, so a typo never makes the
import fail; a wrong value given to pp.configure raises a
PyPLUTOConfigError.
"""

from __future__ import annotations

import os
import sys
import tomllib
from pathlib import Path
from typing import (
    Any,
    Literal,
    TypedDict,
    cast,
    get_args,
    get_origin,
    get_type_hints,
)

from pyPLUTO.utils.pperrors import PyPLUTOConfigError
from pyPLUTO.utils.ppwarnings import PPWarn, PyPLUTOConfigWarning

# The values each setting accepts, exactly as written here
TextValue = Literal["default", "verbose"] | bool | None
ColorsValue = Literal["PyPLUTO", "always"] | None
WarningsValue = Literal["always", "once", "ignore", "error"]
ErrorsValue = Literal["short", "full"]


class SettingsKwargs(TypedDict, total=False):
    """The keywords of pp.configure, each optional."""

    greet: bool
    text: TextValue
    colors: ColorsValue
    warnings: WarningsValue
    errors: ErrorsValue


# The value of every setting when nothing else sets it
DEFAULTS: dict[str, Any] = {
    "greet": True,
    "text": "default",
    "colors": "PyPLUTO",
    "warnings": "always",
    "errors": "short",
}

# The name of both setting files, the user's and the folder's
FILENAME = "pypluto.toml"

# How True, False and None are written in a file or a variable
WORDS = {"true": True, "false": False, "none": None}

# The settings in use, filled by load() at import and changed by configure
SETTINGS: dict[str, Any] = dict(DEFAULTS)


def values_of(hint: object) -> tuple[Any, ...]:
    """List the values a type made of literals, bool and None accepts.

    Parameters
    ----------
    - hint (not optional): object
        A type such as Literal["a", "b"] | bool | None.

    Returns
    -------
    - tuple[Any, ...]
        Every value the type accepts, in the order it is written.

    Examples
    --------
    - Example #1: the values of text

        >>> values_of(TextValue)
        ('default', 'verbose', True, False, None)

    """
    if get_origin(hint) is Literal:
        return get_args(hint)
    if hint is bool:
        return (True, False)
    if hint is type(None):
        return (None,)

    # A union: the values of each of its parts
    return tuple(value for part in get_args(hint) for value in values_of(part))


# What each setting accepts at runtime, read from the types of SettingsKwargs
# so that every value is written once
ALLOWED: dict[str, tuple[Any, ...]] = {
    name: values_of(hint)
    for name, hint in get_type_hints(SettingsKwargs).items()
}


def check(name: str, value: object) -> object:
    """Return the value a setting is stored as, or raise if it is unknown.

    Parameters
    ----------
    - name (not optional): str
        The name of the setting, one of ALLOWED.
    - value (not optional): object
        The value given.

    Returns
    -------
    - object
        The value as stored. text keeps one spelling per meaning: True is
        stored as "verbose" and None as "default".

    Raises
    ------
    - PyPLUTOConfigError
        If the setting does not exist or the value is not one it accepts.

    Examples
    --------
    - Example #1: a value stored as it is

        >>> check("colors", "always")
        'always'

    - Example #2: True as a synonym

        >>> check("text", True)
        'verbose'

    """
    if name not in ALLOWED:
        known = ", ".join(ALLOWED)
        msg = f"Unknown setting {name!r}: use one of {known}."
        raise PyPLUTOConfigError(msg)

    # "is" for True, False and None, so that 1 and 0 are not taken for them
    allowed = ALLOWED[name]
    if not any(
        value is choice or (isinstance(choice, str) and value == choice)
        for choice in allowed
    ):
        choices = ", ".join(repr(choice) for choice in allowed)
        msg = f"Unknown value {value!r} for {name!r}: use one of {choices}."
        raise PyPLUTOConfigError(msg)

    if name == "text" and value is True:
        return "verbose"
    if name == "text" and value is None:
        return "default"
    return value


def check_text(text: TextValue) -> TextValue:
    """Return the text of an object as stored, or raise if it is unknown.

    The text given to Image, Load or LoadPart. None is kept, since on an
    object it means following the package; any other value is checked and
    stored as check stores the text setting.

    Parameters
    ----------
    - text (not optional): bool | "default" | "verbose" | None
        The text given to the object.

    Returns
    -------
    - bool | "default" | "verbose" | None
        None, or the text as stored: True becomes "verbose".

    Raises
    ------
    - PyPLUTOConfigError
        If the text is not one of the values above.

    Examples
    --------
    - Example #1: True as a synonym

        >>> check_text(True)
        'verbose'

    - Example #2: None, which follows the package

        >>> check_text(None)

    """
    if text is None:
        return None
    # check only lets through the values of TextValue, which no checker sees
    return cast("TextValue", check("text", text))


def user_file() -> Path:
    """Return the path of the user's setting file, existing or not.

    Returns
    -------
    - Path
        pypluto/pypluto.toml inside %APPDATA% on Windows, and inside
        $XDG_CONFIG_HOME, or ~/.config when it is not set, elsewhere.

    Examples
    --------
    - Example #1: on Linux, with no XDG_CONFIG_HOME

        >>> user_file()
        PosixPath('/home/user/.config/pypluto/pypluto.toml')

    """
    if sys.platform == "win32":
        base = os.environ.get(
            "APPDATA", str(Path.home() / "AppData" / "Roaming")
        )
    else:
        base = os.environ.get("XDG_CONFIG_HOME", str(Path.home() / ".config"))
    return Path(base) / "pypluto" / FILENAME


def read_file(path: Path) -> dict[str, Any]:
    """Read the settings written in a TOML file.

    A missing file gives no settings. A file that cannot be read or parsed
    warns and gives no settings either, so the import goes on. The string
    "none" is read as None, since TOML has no way to write it.

    Parameters
    ----------
    - path (not optional): Path
        The file to read.

    Returns
    -------
    - dict[str, Any]
        The settings as written, not checked yet.

    Examples
    --------
    - Example #1: the file of the current folder

        >>> read_file(Path("pypluto.toml"))
        {'greet': False}

    """
    if not path.is_file():
        return {}
    try:
        with path.open("rb") as file:
            found = tomllib.load(file)
    except (OSError, tomllib.TOMLDecodeError) as error:
        PPWarn.warn(
            f"{path} cannot be read, so it is ignored: {error}",
            PyPLUTOConfigWarning,
        )
        return {}
    return {
        name: WORDS.get(value, value) if isinstance(value, str) else value
        for name, value in found.items()
    }


def read_environment() -> dict[str, Any]:
    """Read the settings given as PYPLUTO_<NAME> environment variables.

    A variable is always text, so true, false and none are read as True,
    False and None; any other text is kept as it is.

    Returns
    -------
    - dict[str, Any]
        The settings found, not checked yet.

    Examples
    --------
    - Example #1: with PYPLUTO_GREET=false and PYPLUTO_TEXT=verbose

        >>> read_environment()
        {'greet': False, 'text': 'verbose'}

    """
    found = {}
    for name in ALLOWED:
        text = os.environ.get(f"PYPLUTO_{name.upper()}")
        if text is not None:
            found[name] = WORDS.get(text, text)
    return found


def merge(values: dict[str, Any], source: str) -> None:
    """Check each setting of one source and store the valid ones.

    Parameters
    ----------
    - values (not optional): dict[str, Any]
        The settings read from the source.
    - source (not optional): str
        Where they come from, named in the warning about a wrong one.

    Returns
    -------
    - None

    Examples
    --------
    - Example #1: the settings of the environment

        >>> merge(read_environment(), "the environment")

    """
    for name, value in values.items():
        try:
            SETTINGS[name] = check(name, value)
        except PyPLUTOConfigError as error:
            PPWarn.warn(
                f"In {source}: {error} It is ignored.", PyPLUTOConfigWarning
            )


def load() -> None:
    """Fill SETTINGS from the defaults, the two files and the environment.

    Called once while pyPLUTO is imported, before anything is printed.

    Returns
    -------
    - None

    Examples
    --------
    - Example #1: read everything again

        >>> load()

    """
    SETTINGS.clear()
    SETTINGS.update(DEFAULTS)
    for path in (user_file(), Path.cwd() / FILENAME):
        merge(read_file(path), str(path))
    merge(read_environment(), "the environment")
