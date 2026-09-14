"""Test of the imagekwargs.py file."""

import typing
from importlib import import_module
from typing import get_args, get_type_hints

import pytest
from helper_image import DELEGATION, KWARGS, NO_KWARGS, OTHER_KWARGS

import pyPLUTO.imagekwargs as kwargs_mod
from pyPLUTO.image import Image

# The TypedDicts declared in imagekwargs.py. This list is read from the module
# on purpose: the tests below check properties that must hold for every one of
# them, so a newly added TypedDict is covered without touching this file. The
# hand-written expectations live in helper_image.py (KWARGS, NO_KWARGS).
TYPED_DICTS = sorted(
    name for name, obj in vars(kwargs_mod).items() if typing.is_typeddict(obj)
)


def _chain(typed_dict: type) -> list[type]:
    """Return a TypedDict and every TypedDict it extends, parents last.

    A TypedDict subclass does not keep its parents in __mro__, which is always
    (cls, dict, object): the real chain is recorded in __orig_bases__, so that
    is what has to be followed.
    """
    chain = [typed_dict]
    for base in getattr(typed_dict, "__orig_bases__", ()):
        if typing.is_typeddict(base):
            chain.extend(_chain(base))
    return chain


def test_module_declares_typed_dicts() -> None:
    """Find the kwargs TypedDicts, so the tests below are not vacuous."""
    assert TYPED_DICTS


@pytest.mark.parametrize("name", TYPED_DICTS)
def test_every_typeddict_is_total_false(name: str) -> None:
    """Make every kwarg optional, with total=False.

    A required key would make every call that omits it a type error, so the
    whole point of these tables is that they are optional.
    """
    typed_dict = getattr(kwargs_mod, name)
    assert typed_dict.__required_keys__ == frozenset()


@pytest.mark.parametrize("name", TYPED_DICTS)
def test_no_conflicting_key_types(name: str) -> None:
    """Declare a kwarg with one type only, along the whole inheritance chain.

    Several tables inherit from two parents at once (PlotKwargs from
    LegendKwargs and SetAxisKwargs), so the same key can arrive twice. If the
    two declarations disagreed, the winner would depend on the order of the
    bases rather than on intent.
    """
    seen: dict[str, object] = {}
    conflicts = []
    for base in reversed(_chain(getattr(kwargs_mod, name))):
        for key, annotation in getattr(base, "__annotations__", {}).items():
            if key in seen and seen[key] != annotation:
                conflicts.append(key)
            seen[key] = annotation
    assert not conflicts, f"{name} declares with two types: {sorted(conflicts)}"


@pytest.mark.parametrize(("method", "expected"), KWARGS.items())
def test_method_kwargs_typeddict(method: str, expected: str) -> None:
    """Annotate each facade method's **kwargs with its own TypedDict.

    The annotation is what pyright checks a call against, so a method pointed
    at the wrong table would accept the wrong keywords and reject its own.
    """
    hints = get_type_hints(getattr(Image, method), include_extras=True)
    unpacked = get_args(hints["kwargs"])
    assert unpacked, f"{method} does not unpack a TypedDict"
    assert unpacked[0].__name__ == expected


@pytest.mark.parametrize("method", sorted(NO_KWARGS))
def test_method_without_kwargs(method: str) -> None:
    """Take explicit parameters only, with no **kwargs at all."""
    hints = get_type_hints(getattr(Image, method), include_extras=True)
    assert "kwargs" not in hints


@pytest.mark.parametrize(("name", "where"), OTHER_KWARGS.items())
def test_non_facade_kwargs_typeddict(name: str, where: str) -> None:
    """Unpack the two tables no facade method uses at their own place.

    FigureKwargs belongs to the constructor and SetLocKwargs to a manager
    method Image never exposes, so they are pinned here by name and place
    rather than left unchecked.
    """
    module_name, _, path = where.partition(":")
    target: object = import_module(module_name)
    for part in path.split("."):
        target = getattr(target, part)

    hints = get_type_hints(target, include_extras=True)
    unpacked = get_args(hints["kwargs"])
    assert unpacked, f"{where} does not unpack a TypedDict"
    assert unpacked[0].__name__ == name


def test_every_typeddict_is_reachable() -> None:
    """Attach every declared TypedDict to a method, directly or as a base.

    A table nobody unpacks documents keywords that no call can ever use, so
    it would silently rot. ImageKwargs is reached through the tables that
    extend it, which is why the bases count too.
    """
    used = set(KWARGS.values()) | set(OTHER_KWARGS)
    reachable = {
        base.__name__
        for name in used
        for base in _chain(getattr(kwargs_mod, name))
    }
    orphans = set(TYPED_DICTS) - reachable
    assert not orphans, f"declared but never unpacked: {sorted(orphans)}"


def test_every_method_is_listed() -> None:
    """Keep KWARGS and NO_KWARGS in sync with the facade methods of Image.

    A new method fails here until it is listed in one of the two, so its
    kwargs table cannot go unchecked.
    """
    listed = set(KWARGS) | NO_KWARGS
    missing, stale = set(DELEGATION) - listed, listed - set(DELEGATION)
    assert not missing, (
        f"not listed in KWARGS or NO_KWARGS, so untested: {sorted(missing)}"
    )
    assert not stale, (
        f"listed in KWARGS or NO_KWARGS but not an Image facade method: "
        f"{sorted(stale)}"
    )
