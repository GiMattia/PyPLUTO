"""Test of the imagekwargs.py file.

The file under test is pure declaration, so it is at 100% line coverage
before a single test exists. What these tests check is the contract instead:
that every table is optional, that no key is declared twice with two types,
that each method points at its own table, and that no table is orphaned.

None of that can fail at runtime -- a wrong annotation simply makes the type
checker accept or reject the wrong calls -- which is exactly why it needs
tests.
"""

import inspect
import re
import typing
from importlib import import_module
from pathlib import Path
from typing import Literal, get_args, get_type_hints

import pytest
from helper_image import (
    DELEGATION,
    DOCUMENTED_KWARGS,
    GHOST_KWARGS,
    KWARGS,
    NO_KWARGS,
    OTHER_KWARGS,
    UNDECLARED_KWARGS,
)

import pyPLUTO.image as image_mod
import pyPLUTO.imagekwargs as kwargs_mod
from pyPLUTO.image import Image
from pyPLUTO.utils.inspector import find_kwargs_keys

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


def _documented_names(function: object) -> set[str]:
    """Return the names listed in the Parameters section of a docstring.

    Each entry is written as `- name: type, default value`, one per parameter
    or keyword. Only that section is read: the Examples below it mention
    names too, and a name shown in an example is not documentation of it.
    """
    doc = getattr(function, "__doc__", None) or ""
    if "Parameters" not in doc:
        return set()
    section = doc.split("Parameters")[1].split("Returns")[0]
    return set(re.findall(r"^\s*- (\w+)", section, re.MULTILINE))


def _keys_read_by_the_managers() -> set[str]:
    """Return every keyword any image manager reads from its **kwargs.

    A method documents what its whole chain accepts, not only what it reads
    itself: `interactive` documents the plot keywords because it hands them
    to PlotManager.plot. So the check below needs the keys of the package,
    not of one method.
    """
    keys: set[str] = set()
    folder = Path(kwargs_mod.__file__).parent / "imagefuncs"
    for path in sorted(folder.glob("*.py")):
        module = import_module(f"pyPLUTO.imagefuncs.{path.stem}")
        for obj in vars(module).values():
            if not isinstance(obj, type):
                continue
            for attribute in vars(obj).values():
                if not callable(attribute):
                    continue
                try:
                    keys |= find_kwargs_keys(inspect.unwrap(attribute))
                except (OSError, TypeError, SyntaxError):
                    # Not every class attribute has readable source.
                    continue
    return keys


# Read once: every method below is checked against the same set.
KEYS_READ = _keys_read_by_the_managers()


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


@pytest.mark.parametrize(("method", "expected"), KWARGS.items())
def test_declared_keys_cover_what_the_manager_reads(
    method: str, expected: str
) -> None:
    """Check every keyword a manager reads is declared in its table.

    A keyword read but not declared works at runtime and is rejected by the
    type checkers, so the table and the code disagree with nobody noticing.

    The keys read come from the scanner track_kwargs uses, so the table must
    declare whatever the manager accounts for at runtime. Parameters are
    subtracted, `ax` being one rather than a keyword.

    The reverse is not a fault: `text` declares the create_axes keywords
    because it forwards them. Known faults are listed in UNDECLARED_KWARGS,
    read in both directions so a new one fails and a fixed one must be
    removed.
    """
    manager = getattr(image_mod, DELEGATION[method])
    function = inspect.unwrap(getattr(manager, method))
    declared = set(get_type_hints(getattr(kwargs_mod, expected)))
    parameters = set(inspect.signature(function).parameters)

    undeclared = find_kwargs_keys(function) - declared - parameters
    known = UNDECLARED_KWARGS.get(method, set())
    missing, stale = undeclared - known, known - undeclared

    assert not missing, (
        f"{manager.__name__}.{method} reads {sorted(missing)}, declared "
        f"nowhere in {expected}"
    )
    assert not stale, (
        f"{expected} now declares {sorted(stale)}: remove it from "
        f"UNDECLARED_KWARGS"
    )


@pytest.mark.parametrize(("method", "manager"), DELEGATION.items())
def test_every_parameter_is_documented(method: str, manager: str) -> None:
    """Check each manager method documents every parameter it takes.

    The keywords have their own table to declare them; a parameter has only
    the docstring, which is also all a user has to find out that `fromplot`
    or `limfix` exists.

    Read from the Parameters section alone, so a name mentioned in an example
    does not count as documented. `self` and the internal `_check` are left
    out, and `kwargs` names the table rather than a parameter.
    """
    function = inspect.unwrap(getattr(getattr(image_mod, manager), method))
    parameters = set(inspect.signature(function).parameters)
    parameters -= {"self", "_check", "kwargs"}

    documented = _documented_names(function)
    undocumented = parameters - documented

    assert not undocumented, (
        f"{manager}.{method} does not document {sorted(undocumented)}"
    )


@pytest.mark.parametrize(("method", "expected"), KWARGS.items())
def test_documented_keywords_exist(method: str, expected: str) -> None:
    """Check each documented keyword is one the package accepts.

    The opposite of the test above: not "is what we read declared" but "is
    what we promise real". A documented keyword nothing reads warns as
    unused, so the documentation itself produces the warning.

    Accepted are the method's parameters, the keys of its table, and every
    key read anywhere in imagefuncs, since a method documents what it
    forwards. Known faults live in GHOST_KWARGS, read in both directions.
    """
    manager = getattr(image_mod, DELEGATION[method])
    function = inspect.unwrap(getattr(manager, method))
    known = (
        set(get_type_hints(getattr(kwargs_mod, expected)))
        | set(inspect.signature(function).parameters)
        | KEYS_READ
    )

    ghosts = _documented_names(function) - known
    listed = GHOST_KWARGS.get(method, set())
    missing, stale = ghosts - listed, listed - ghosts

    assert not missing, (
        f"{method} documents {sorted(missing)}, which nothing declares or reads"
    )
    assert not stale, (
        f"{method} no longer documents {sorted(stale)}: remove it from "
        f"GHOST_KWARGS"
    )


def test_grid_declares_every_value_it_accepts() -> None:
    """Check the values `set_axis` handles for `grid` are all declared.

    A missing Literal value is rejected by the checkers while working at
    runtime, which is how `"both"` was found: `set_axis(grid="both")` draws
    both grids and warned about nothing, and pyright refused the call.

    The values are written out by hand; `set_axis.py` reads them as `"x"`,
    `"y"` and `"both"`, with a bool for all or nothing.
    """
    declared = get_type_hints(kwargs_mod.SetAxisKwargs)["grid"]
    literal = next(
        arg for arg in get_args(declared) if typing.get_origin(arg) is Literal
    )

    assert set(get_args(literal)) == {"x", "y", "both"}


@pytest.mark.parametrize("method", sorted(DOCUMENTED_KWARGS))
def test_declared_keywords_are_documented(method: str) -> None:
    """Check one written-up method still documents every keyword it declares.

    The keywords are the whole interface of these methods, so an
    undocumented one is unreachable in practice. The figure-level keywords
    are documented on `Image.__init__` instead and left out here.

    Only the methods in DOCUMENTED_KWARGS are checked; the rest are expected
    failures in test_with_issues.py until their manager is reviewed.
    """
    manager = getattr(image_mod, DELEGATION[method])
    function = inspect.unwrap(getattr(manager, method))
    declared = set(get_type_hints(getattr(kwargs_mod, KWARGS[method])))
    figure_level = set(get_type_hints(kwargs_mod.FigureKwargs))

    undocumented = declared - _documented_names(function) - figure_level

    assert not undocumented, (
        f"{method} declares but does not document {sorted(undocumented)}"
    )


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
