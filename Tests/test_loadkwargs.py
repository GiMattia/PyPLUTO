"""Test of the loadkwargs.py file."""

import typing
from typing import get_args, get_type_hints

import helper_load
import helper_loadpart
import pytest

import pyPLUTO.loadkwargs as kwargs_mod
from pyPLUTO.load import Load
from pyPLUTO.loadpart import LoadPart

# The TypedDicts declared in loadkwargs.py. This list is read from the module
# on purpose: the tests below check properties that must hold for every one of
# them, so a newly added TypedDict is covered without touching this file. The
# hand-written expectations live in helper_load.py and helper_loadpart.py
# (KWARGS, NO_KWARGS).
TYPED_DICTS = sorted(
    name for name, obj in vars(kwargs_mod).items() if typing.is_typeddict(obj)
)

# The two classes whose keywords loadkwargs.py declares, each with its own
# hand-written tables. Both are covered by the same tests, so neither can be
# held to a lower standard than the other.
CLASSES = [(Load, helper_load), (LoadPart, helper_loadpart)]

# (class, method, TypedDict name) for every method that takes **kwargs, and
# (class, method) for every method that takes none.
WITH_KWARGS = [
    (cls, method, expected)
    for cls, helper in CLASSES
    for method, expected in helper.KWARGS.items()
]
WITHOUT_KWARGS = [
    (cls, method)
    for cls, helper in CLASSES
    for method in sorted(helper.NO_KWARGS)
]


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

    LoadKwargs and LoadPartKwargs both extend BaseLoadKwargs, so the same key
    can arrive twice. If a subclass redeclared an inherited key with another
    type, the winner would depend on the order of the bases rather than on
    intent.
    """
    seen: dict[str, object] = {}
    conflicts = []
    for base in reversed(_chain(getattr(kwargs_mod, name))):
        for key, annotation in getattr(base, "__annotations__", {}).items():
            if key in seen and seen[key] != annotation:
                conflicts.append(key)
            seen[key] = annotation
    assert not conflicts, f"{name} declares with two types: {sorted(conflicts)}"


@pytest.mark.parametrize(("cls", "method", "expected"), WITH_KWARGS)
def test_method_kwargs_typeddict(cls: type, method: str, expected: str) -> None:
    """Annotate each method's **kwargs with its own TypedDict.

    The annotation is what pyright checks a call against, so a method pointed
    at the wrong table would accept the wrong keywords and reject its own.
    """
    hints = get_type_hints(getattr(cls, method), include_extras=True)
    unpacked = get_args(hints["kwargs"])
    assert unpacked, f"{cls.__name__}.{method} does not unpack a TypedDict"
    assert unpacked[0].__name__ == expected


@pytest.mark.parametrize(("cls", "method"), WITHOUT_KWARGS)
def test_method_without_kwargs(cls: type, method: str) -> None:
    """Take explicit parameters only, with no **kwargs at all."""
    hints = get_type_hints(getattr(cls, method), include_extras=True)
    assert "kwargs" not in hints


@pytest.mark.parametrize(("cls", "helper"), CLASSES)
def test_every_method_is_listed(cls: type, helper: object) -> None:
    """Keep KWARGS and NO_KWARGS in sync with the methods of each class.

    A new method fails here until it is listed in one of the two, so its
    kwargs table cannot go unchecked. The constructor is added by hand: it is
    not in DELEGATION, since it delegates to nobody.

    LONG TEST: CHECK
    """
    kwargs: dict[str, str] = helper.KWARGS  # type: ignore[attr-defined]
    no_kwargs: set[str] = helper.NO_KWARGS  # type: ignore[attr-defined]
    delegation: dict[str, str] = helper.DELEGATION  # type: ignore[attr-defined]

    listed = set(kwargs) | no_kwargs
    expected = set(delegation) | {"__init__"}
    missing, stale = expected - listed, listed - expected
    assert not missing, (
        f"{cls.__name__}: not listed in KWARGS or NO_KWARGS, so untested: "
        f"{sorted(missing)}"
    )
    assert not stale, (
        f"{cls.__name__}: listed in KWARGS or NO_KWARGS but not a method: "
        f"{sorted(stale)}"
    )


def test_every_typeddict_is_reachable() -> None:
    """Attach every declared TypedDict to a method, directly or as a base.

    A table nobody unpacks documents keywords that no call can ever use, so
    it would silently rot. BaseLoadKwargs is reached through LoadKwargs and
    LoadPartKwargs, which is why the bases count too.
    """
    used = {expected for _, _, expected in WITH_KWARGS}
    reachable = {
        base.__name__
        for name in used
        for base in _chain(getattr(kwargs_mod, name))
    }
    orphans = set(TYPED_DICTS) - reachable
    assert not orphans, f"declared but never unpacked: {sorted(orphans)}"
