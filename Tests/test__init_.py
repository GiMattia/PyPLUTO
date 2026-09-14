"""Test of the __init__.py file."""

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

    The real metadata lookup is restored and pyPLUTO is re-imported again
    afterwards, so the rest of the suite sees the normal package.
    """

    def missing(name: str) -> str:
        raise md.PackageNotFoundError(name)

    monkeypatch.setattr(md, "version", missing)
    yield importlib.reload(pp)
    monkeypatch.undo()
    importlib.reload(pp)


def test_version_matches_metadata() -> None:
    """Take the version from the installed package metadata."""
    assert pp.__version__ == md.version("py-pluto")


def test_version_fallback(reloaded_without_metadata: ModuleType) -> None:
    """Fall back to "unknown" when the package metadata cannot be found.

    This happens when pyPLUTO is imported from a source tree that was never
    installed as the py-pluto distribution.
    """
    assert reloaded_without_metadata.__version__ == "unknown"


def test_all_is_the_public_api() -> None:
    """Expose exactly the expected public API through __all__."""
    assert sorted(pp.__all__) == PUBLIC_API


@pytest.mark.parametrize("name", pp.__all__)
def test_all_names_exist(name: str) -> None:
    """Make every name listed in __all__ available on the package."""
    assert hasattr(pp, name)


@pytest.mark.parametrize(("name", "module"), SOURCE_MODULE.items())
def test_exports_are_the_real_objects(name: str, module: ModuleType) -> None:
    """Re-export the implementation objects themselves, not copies."""
    assert getattr(pp, name) is getattr(module, name)


def test_configuration_flags() -> None:
    """Enable colored errors, colored warnings and the greeting by default."""
    assert (pp.colorerr, pp.colorwarn, pp.greet) == (True, True, True)


def test_greeting_shows_version(
    monkeypatch: pytest.MonkeyPatch,
    capsys: pytest.CaptureFixture[str],
) -> None:
    """Greet with the package version when pyPLUTO is imported."""
    monkeypatch.setattr(Configure, "greeted", False)
    importlib.reload(pp)
    assert f"PyPLUTO version: {pp.__version__}" in capsys.readouterr().out
