"""Test of the __init__.py file.

`__init__.py` is what `import pyPLUTO as pp` executes, so these tests are
about the package's front door: which names it offers, that each is the real
object rather than a copy, and that the version and greeting are settled
correctly on import.

Two of them reload the package to see what import does differently under
other conditions. That is worth knowing about when reading this file, because
reloading is contagious: a reload that was not undone would leave every later
test in the session importing a different pyPLUTO. Both restore what they
changed, one through a fixture and one through the `Configure` flag.

PUBLIC_API below is written by hand rather than read from `pp.__all__`, so
that adding a name to the package is a deliberate change to its public
surface and not a silent one.
"""

import importlib
import importlib.metadata as md
from collections.abc import Generator
from types import ModuleType

import pytest

import pyPLUTO as pp
import pyPLUTO.image as image_mod
import pyPLUTO.load as load_mod
import pyPLUTO.loadpart as loadpart_mod
from pyPLUTO.utils import configure, examples_api, pytools
from pyPLUTO.utils.configure import Configure

PUBLIC_API = [
    "Image",
    "Load",
    "LoadPart",
    "copy_examples",
    "examples_path",
    "find_example",
    "list_examples",
    "ring",
    "run_example",
    "savefig",
    "set_text",
    "show",
]

# Where each public name is implemented
SOURCE_MODULE = {
    "Image": image_mod,
    "Load": load_mod,
    "LoadPart": loadpart_mod,
    "copy_examples": examples_api,
    "examples_path": examples_api,
    "find_example": pytools,
    "list_examples": examples_api,
    "ring": pytools,
    "run_example": examples_api,
    "savefig": pytools,
    "set_text": configure,
    "show": pytools,
}


@pytest.fixture
def reloaded_without_metadata(
    monkeypatch: pytest.MonkeyPatch,
) -> Generator[ModuleType, None, None]:
    """Re-import pyPLUTO as if its package metadata were missing.

    This is the situation of a source tree that was never installed as the
    py-pluto distribution, which cannot be reproduced in a session where it
    *is* installed -- hence replacing the metadata lookup with one that
    always raises.

    Everything after the yield is teardown and runs even if the test fails:
    the real lookup is put back and pyPLUTO is reloaded once more, so the
    rest of the suite sees the normal package with its real version.
    """

    def missing(name: str) -> str:
        raise md.PackageNotFoundError(name)

    monkeypatch.setattr(md, "version", missing)
    yield importlib.reload(pp)
    monkeypatch.undo()
    importlib.reload(pp)


def test_version_matches_metadata() -> None:
    """Compare the exported version with what the metadata reports.

    The version is read rather than written, so this checks the reading works
    and, with the test below, that both branches of the try/except behave.
    """
    assert pp.__version__ == md.version("py-pluto")


def test_version_fallback(reloaded_without_metadata: ModuleType) -> None:
    """Import with the metadata missing and check the version says so.

    The other branch of the try/except. An unhandled PackageNotFoundError
    here would make `import pyPLUTO` fail outright for anyone working from a
    checkout, which is a normal way to develop and must keep working.
    """
    assert reloaded_without_metadata.__version__ == "unknown"


def test_all_is_the_public_api() -> None:
    """Compare __all__ with the hand-written list at the top of this file.

    An exact comparison in both directions: a name added to the package
    without being intended as public fails here, and so does one removed
    while still being advertised. This is the test that makes the public
    surface a deliberate decision rather than whatever happens to be imported.
    """
    assert sorted(pp.__all__) == PUBLIC_API


@pytest.mark.parametrize("name", pp.__all__)
def test_all_names_exist(name: str) -> None:
    """Check one advertised name actually exists on the package.

    `__all__` is only a list of strings, so nothing stops it naming something
    that was never imported: `from pyPLUTO import *` would then fail on a
    name the package itself advertises.
    """
    assert hasattr(pp, name)


@pytest.mark.parametrize(("name", "module"), SOURCE_MODULE.items())
def test_exports_are_the_real_objects(name: str, module: ModuleType) -> None:
    """Check one exported name is the same object as the implementation.

    `is`, not equality. Re-exporting a copy would mean a user patching
    `pp.Load` in a test, or reading `pp.Load.__doc__`, would be working on
    something other than what the package actually uses.

    The mapping at the top says where each name comes from, so one that moved
    to another module without the import being updated fails here.
    """
    assert getattr(pp, name) is getattr(module, name)


def test_configuration_flags() -> None:
    """Check the three module-level switches start enabled.

    They are read once, while `__init__.py` runs, so their value at import is
    the only one that matters: setting them afterwards has no effect.
    """
    assert (pp.colorerr, pp.colorwarn, pp.greet) == (True, True, True)


def test_greeting_shows_version(
    monkeypatch: pytest.MonkeyPatch,
    capsys: pytest.CaptureFixture[str],
) -> None:
    """Re-import the package and check the greeting names the version.

    The greeting prints once per session, which `Configure.greeted` records,
    so the flag is reset before reloading -- otherwise the reload would print
    nothing and the test would be checking an empty string.

    It uses `capsys` rather than `caplog` because the greeting is printed,
    not logged.
    """
    monkeypatch.setattr(Configure, "greeted", False)
    importlib.reload(pp)
    assert f"PyPLUTO version: {pp.__version__}" in capsys.readouterr().out
