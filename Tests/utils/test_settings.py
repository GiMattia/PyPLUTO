"""Test of the settings.py file.

Every source is pointed at a folder of the test by the autouse fixture: the
user's configuration folder, the current folder and the PYPLUTO_ variables,
so the settings of the machine running the tests never leak in. The tables
below are written by hand, never read from the module, so a mistake in how
ALLOWED is read from the types cannot hide.
"""

import sys
from pathlib import Path

import pytest

from pyPLUTO.utils import settings
from pyPLUTO.utils.pperrors import PyPLUTOConfigError
from pyPLUTO.utils.ppwarnings import PyPLUTOWarning

# What each setting accepts
ACCEPTED = {
    "greet": (True, False),
    "text": ("default", "verbose", True, False, None),
    "colors": ("PyPLUTO", "always", None),
    "warnings": ("always", "once", "ignore", "error"),
    "errors": ("short", "full"),
}

# The values stored differently from how they are given
STORED = {("text", True): "verbose", ("text", None): "default"}

# Values refused, each for a different reason
REFUSED = [
    ("colors", "pypluto"),
    ("text", 1),
    ("greet", 0),
    ("warnings", None),
    ("errors", "long"),
]


@pytest.fixture(autouse=True)
def isolated(monkeypatch: pytest.MonkeyPatch, tmp_path: Path) -> None:
    """Point every source at the test folder and restore the settings after."""
    monkeypatch.setenv("XDG_CONFIG_HOME", str(tmp_path / "config"))
    monkeypatch.setenv("APPDATA", str(tmp_path / "config"))
    monkeypatch.chdir(tmp_path)
    for name in ACCEPTED:
        monkeypatch.delenv(f"PYPLUTO_{name.upper()}", raising=False)
    monkeypatch.setattr(settings, "SETTINGS", dict(settings.DEFAULTS))


def write(path: Path, text: str) -> Path:
    """Write a setting file, creating its folder, and give back its path."""
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8")
    return path


# ---- What each setting accepts ----
def test_allowed_is_read_from_the_types() -> None:
    """Compare the table read from SettingsKwargs with the hand-written one."""
    assert settings.ALLOWED == ACCEPTED


def test_every_default_is_accepted() -> None:
    """Check each default passes the check unchanged."""
    for name, value in settings.DEFAULTS.items():
        assert settings.check(name, value) == value


@pytest.mark.parametrize(
    ("name", "value"),
    [(name, value) for name, values in ACCEPTED.items() for value in values],
    ids=[
        f"{name}-{value}"
        for name, values in ACCEPTED.items()
        for value in values
    ],
)
def test_an_accepted_value_is_stored(name: str, value: object) -> None:
    """Check every accepted value, and the two that text stores differently."""
    assert settings.check(name, value) == STORED.get((name, value), value)


@pytest.mark.parametrize(
    ("name", "value"),
    REFUSED,
    ids=["wrong-case", "one-for-true", "zero-for-false", "none", "unknown"],
)
def test_a_wrong_value_is_refused(name: str, value: object) -> None:
    """Give a value the setting does not accept and expect the error.

    1 and 0 are refused although they compare equal to True and False; the
    spelling is exact, so "pypluto" is refused too.
    """
    with pytest.raises(PyPLUTOConfigError, match="Unknown value"):
        settings.check(name, value)


def test_an_unknown_setting_is_refused() -> None:
    """Give a setting that does not exist; the message lists the real ones."""
    with pytest.raises(PyPLUTOConfigError, match="greet, text, colors"):
        settings.check("colours", "always")


@pytest.mark.parametrize(
    ("text", "stored"),
    [(None, None), (True, "verbose"), (False, False), ("default", "default")],
    ids=["none-kept", "true", "false", "default"],
)
def test_check_text_keeps_none_and_stores_the_rest(
    text: settings.TextValue, stored: settings.TextValue
) -> None:
    """Check the text of an object: None stays None, since on an object it
    follows the package, and the other values are stored as check does."""
    assert settings.check_text(text) == stored


# ---- The user file ----
def test_the_user_file_follows_xdg(
    monkeypatch: pytest.MonkeyPatch, tmp_path: Path
) -> None:
    """On Linux and macOS, with XDG_CONFIG_HOME set, the file is inside it."""
    monkeypatch.setattr(sys, "platform", "linux")
    expected = tmp_path / "config" / "pypluto" / "pypluto.toml"
    assert settings.user_file() == expected


def test_the_user_file_falls_back_to_dot_config(
    monkeypatch: pytest.MonkeyPatch, tmp_path: Path
) -> None:
    """Without XDG_CONFIG_HOME, the file is in ~/.config."""
    monkeypatch.setattr(sys, "platform", "linux")
    monkeypatch.delenv("XDG_CONFIG_HOME")
    monkeypatch.setattr(Path, "home", lambda: tmp_path)
    expected = tmp_path / ".config" / "pypluto" / "pypluto.toml"
    assert settings.user_file() == expected


def test_the_user_file_on_windows_is_in_appdata(
    monkeypatch: pytest.MonkeyPatch, tmp_path: Path
) -> None:
    """On Windows the file is inside %APPDATA%."""
    monkeypatch.setattr(sys, "platform", "win32")
    expected = tmp_path / "config" / "pypluto" / "pypluto.toml"
    assert settings.user_file() == expected


# ---- Reading the sources ----
def test_a_missing_file_gives_nothing(tmp_path: Path) -> None:
    """Read a file that does not exist: no settings, no warning."""
    assert settings.read_file(tmp_path / "nothing.toml") == {}


def test_a_file_is_read_with_none_written_as_a_word(tmp_path: Path) -> None:
    """Read a file with a native boolean and "none" for None."""
    path = write(tmp_path / "pypluto.toml", 'greet = false\ncolors = "none"\n')
    assert settings.read_file(path) == {"greet": False, "colors": None}


def test_a_broken_file_warns_and_gives_nothing(tmp_path: Path) -> None:
    """Read a file that is not TOML: a warning names it, and nothing is read."""
    path = write(tmp_path / "pypluto.toml", "greet = = false\n")
    with pytest.warns(PyPLUTOWarning, match="cannot be read"):
        assert settings.read_file(path) == {}


def test_the_environment_is_read_with_the_three_words(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """Set three variables, the words true, false and none among them."""
    monkeypatch.setenv("PYPLUTO_GREET", "false")
    monkeypatch.setenv("PYPLUTO_TEXT", "true")
    monkeypatch.setenv("PYPLUTO_COLORS", "none")
    monkeypatch.setenv("PYPLUTO_ERRORS", "full")
    assert settings.read_environment() == {
        "greet": False,
        "text": True,
        "colors": None,
        "errors": "full",
    }


# ---- Merging and loading ----
def test_merge_ignores_a_wrong_value_and_keeps_the_rest() -> None:
    """Merge a valid and a wrong setting: the wrong one warns, naming its
    source, and the valid one is stored."""
    with pytest.warns(PyPLUTOWarning, match="In my file: Unknown value"):
        settings.merge({"greet": False, "colors": "pypluto"}, "my file")
    assert settings.SETTINGS["greet"] is False
    assert settings.SETTINGS["colors"] == "PyPLUTO"


def test_load_lets_each_source_override_the_one_before(
    monkeypatch: pytest.MonkeyPatch, tmp_path: Path
) -> None:
    """Set text in all three sources and check the environment wins.

    The user file also sets greet, which nothing overrides, and the folder
    file sets warnings, so each layer leaves its mark.
    """
    write(
        settings.user_file(),
        'greet = false\ntext = "verbose"\n',
    )
    write(tmp_path / "pypluto.toml", 'text = false\nwarnings = "once"\n')
    monkeypatch.setenv("PYPLUTO_TEXT", "default")

    settings.load()

    assert settings.SETTINGS == {
        "greet": False,
        "text": "default",
        "colors": "PyPLUTO",
        "warnings": "once",
        "errors": "short",
    }


def test_load_starts_again_from_the_defaults() -> None:
    """Change a setting, load with no sources, and find the default back."""
    settings.SETTINGS["greet"] = False
    settings.load()
    assert settings.SETTINGS == settings.DEFAULTS
