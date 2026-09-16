"""Test of the imagekwargs.py file.

The file under test is pure declaration, so it is at 100% line coverage
before a single test exists. What these tests check is the contract instead:
that every table is optional, that no key is declared twice with two types,
that each method points at its own table, and that no table is orphaned.

None of that can fail at runtime -- a wrong annotation simply makes the type
checker accept or reject the wrong calls -- which is exactly why it needs
tests.
"""

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
    """Check the module really declares tables, so the rest is not vacuous.

    TYPED_DICTS is read from the module, so if that ever came back empty the
    parametrized tests would silently become zero tests.
    """
    assert TYPED_DICTS


@pytest.mark.parametrize("name", TYPED_DICTS)
def test_every_typeddict_is_total_false(name: str) -> None:
    """Check one table declares no required key.

    A required key would make every call that omits it a type error, so the
    whole point of these tables is that they are optional. `total=False` on
    the class is what sets this, and it is easy to leave off a new table.
    """
    typed_dict = getattr(kwargs_mod, name)
    assert typed_dict.__required_keys__ == frozenset()


@pytest.mark.parametrize("name", TYPED_DICTS)
def test_no_conflicting_key_types(name: str) -> None:
    """Walk one table's whole chain and check no key is declared twice.

    Several tables inherit from two parents at once (PlotKwargs from
    LegendKwargs and SetAxisKwargs), so the same key can arrive twice. If the
    two declarations disagreed, the winner would depend on the order of the
    bases rather than on intent.

    The chain is followed through `_chain`, not `__mro__`: a TypedDict does
    not keep its parents there, which is why this test could not fail at all
    until that was fixed.
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
    """Check one facade method unpacks the table the helper says it should.

    The annotation is what pyright checks a call against, so a method pointed
    at the wrong table would accept the wrong keywords and reject its own --
    and it is an easy mistake, since the tables are near-identical in shape
    and several methods sit next to each other.
    """
    hints = get_type_hints(getattr(Image, method), include_extras=True)
    unpacked = get_args(hints["kwargs"])
    assert unpacked, f"{method} does not unpack a TypedDict"
    assert unpacked[0].__name__ == expected


@pytest.mark.parametrize("method", sorted(NO_KWARGS))
def test_method_without_kwargs(method: str) -> None:
    """Check one method takes no **kwargs at all.

    Listed by hand rather than left out, so that every facade method is
    accounted for by one table or the other and none can be forgotten.
    """
    hints = get_type_hints(getattr(Image, method), include_extras=True)
    assert "kwargs" not in hints


@pytest.mark.parametrize(("name", "where"), OTHER_KWARGS.items())
def test_non_facade_kwargs_typeddict(name: str, where: str) -> None:
    """Resolve a table's declared home and check it is unpacked there.

    Two tables belong to no facade method: FigureKwargs to the constructor
    and SetLocKwargs to a manager method Image never exposes. Rather than
    excuse them from the reachability test below, they are pinned here by
    name and place, and resolved from the "module:Class.method" string in the
    helper so a rename is caught.
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
    """Check every declared table is reachable from some method.

    A table nobody unpacks documents keywords that no call can ever use, so
    it would silently rot. Bases count as reached, since a table like
    ImageKwargs exists precisely to be inherited rather than unpacked.
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
    """Compare the two helper tables against the facade methods of Image.

    A new method fails here until it is listed in KWARGS or NO_KWARGS, so its
    keywords cannot go unchecked. The tests above are parametrized from those
    tables, which is what makes this the one that keeps them meaningful.
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
