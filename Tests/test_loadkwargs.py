"""Test of the loadkwargs.py file.

The loading twin of test_imagekwargs.py, kept parallel to it. The file under
test is pure declaration, so it is at 100% line coverage before a single test
exists; what these tests check is the contract instead.

One difference in shape: two classes are covered here rather than one, since
Load and LoadPart each have their own tables, and the tests are parametrized
over both so neither is held to a lower standard.
"""

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

    LoadKwargs and LoadPartKwargs both extend BaseLoadKwargs, so the same key
    can arrive twice. If a subclass redeclared an inherited key with another
    type, the winner would depend on the order of the bases rather than on
    intent.

    The chain is followed through `_chain`, not `__mro__`: a TypedDict does
    not keep its parents there, so a version of this test using `__mro__`
    could never fail.
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
    """Check one method unpacks the table the helper says it should.

    The annotation is what pyright checks a call against, so a method pointed
    at the wrong table would accept the wrong keywords and reject its own.
    Both classes are covered, so `Load.__init__` and `LoadPart.__init__`
    cannot end up sharing a table by accident.
    """
    hints = get_type_hints(getattr(cls, method), include_extras=True)
    unpacked = get_args(hints["kwargs"])
    assert unpacked, f"{cls.__name__}.{method} does not unpack a TypedDict"
    assert unpacked[0].__name__ == expected


@pytest.mark.parametrize(("cls", "method"), WITHOUT_KWARGS)
def test_method_without_kwargs(cls: type, method: str) -> None:
    """Check one method takes no **kwargs at all.

    Listed by hand rather than left out, so every method is accounted for by
    one table or the other and none can be forgotten.
    """
    hints = get_type_hints(getattr(cls, method), include_extras=True)
    assert "kwargs" not in hints


@pytest.mark.parametrize(("cls", "helper"), CLASSES)
def test_every_method_is_listed(cls: type, helper: object) -> None:
    """Compare the two helper tables against the methods of one class.

    A new method fails here until it is listed in KWARGS or NO_KWARGS, so its
    keywords cannot go unchecked. The tests above are parametrized from those
    tables, which is what makes this the one that keeps them meaningful.

    The constructor is added by hand because it is not in DELEGATION: it
    delegates to nobody, yet it is where most keywords are actually given.
    """
    kwargs: dict[str, str] = helper.KWARGS  # type: ignore[attr-defined]  # ty: ignore[unresolved-attribute]
    no_kwargs: set[str] = helper.NO_KWARGS  # type: ignore[attr-defined]  # ty: ignore[unresolved-attribute]
    delegation: dict[str, str] = helper.DELEGATION  # type: ignore[attr-defined]  # ty: ignore[unresolved-attribute]

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
    """Check every declared table is reachable from some method.

    A table nobody unpacks documents keywords that no call can ever use, so
    it would silently rot. Bases count as reached: BaseLoadKwargs exists to
    be inherited by LoadKwargs and LoadPartKwargs rather than unpacked.
    """
    used = {expected for _, _, expected in WITH_KWARGS}
    reachable = {
        base.__name__
        for name in used
        for base in _chain(getattr(kwargs_mod, name))
    }
    orphans = set(TYPED_DICTS) - reachable
    assert not orphans, f"declared but never unpacked: {sorted(orphans)}"
