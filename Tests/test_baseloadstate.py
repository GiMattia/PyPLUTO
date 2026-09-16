"""Test of the baseloadstate.py file.

BaseLoadState stores everything a load produces, and does nothing else, so
there is no behaviour to test here: what these tests check is the shape of the
class. What each field starts as, which fields may be passed to the
constructor, which raise until a load fills them in, and which must be a fresh
object per instance.

That sounds like small print, and it is exactly where a dataclass goes wrong
in ways nothing else notices: a mutable default shared between loads, a field
that silently gains a default and reads as zero before anything was loaded, a
field added to the class with nothing checking it. Every test below is aimed
at one of those.
"""

from dataclasses import fields

import numpy as np
import pytest
from helper_baseload import CONTAINERS, DEFAULTS, WITH_DEFAULT, WITHOUT_DEFAULT

from pyPLUTO.baseloadstate import BaseLoadState

# The hand-written table and its views live in helper_baseload.py, shared with
# test_baseloadmixin.py: DEFAULTS is what every field holds on a fresh state,
# WITH_DEFAULT and WITHOUT_DEFAULT split it, and CONTAINERS lists the fields
# built by a default_factory. Each entry is checked by test_default or by
# test_unset_until_loaded, and test_every_field_is_listed makes sure no field
# is missing.


def test_every_field_is_listed() -> None:
    """Compare the fields the class declares with the table in the helper.

    Adding, removing or renaming a field fails here until the table above is
    updated, so no field can go untested.

    This is what makes the rest of the file trustworthy: the tests below are
    parametrized from the table, so a field missing from it would simply not
    be tested, silently and with no failure anywhere. The two assertions are
    kept apart so the message says which way the two drifted.
    """
    declared = {field.name for field in fields(BaseLoadState)}
    missing, stale = declared - set(DEFAULTS), set(DEFAULTS) - declared
    assert not missing, (
        f"not listed in DEFAULTS, so untested: {sorted(missing)}"
    )
    assert not stale, (
        f"listed in DEFAULTS but no longer a BaseLoadState field: "
        f"{sorted(stale)}"
    )


@pytest.mark.parametrize(("name", "expected"), WITH_DEFAULT.items())
def test_default(name: str, expected: object) -> None:
    """Build a fresh state and check one field against the expected default.

    One test per field with a default, so a failure names the field rather
    than the table. What it pins is the value a user gets from `pp.Load()`
    before doing anything, which is the starting point of every load.

    The type is checked too because 0 == 0.0 == False in Python: comparing
    values alone would not notice, e.g., multiple defaulting to 0.
    """
    value = getattr(BaseLoadState(), name)
    assert value == expected
    assert type(value) is type(expected)


@pytest.mark.parametrize("name", WITHOUT_DEFAULT)
def test_unset_until_loaded(name: str) -> None:
    """Read a load-only field on a fresh state and expect AttributeError.

    These fields describe what was read from the files, so before a load
    there is no honest answer for them. Raising is the honest answer.

    If one of these fields silently gained a default, code could read a
    made-up value before anything is loaded: this test would catch it. The
    failure that prevents is quiet -- a grid shape of zero, a time of None --
    and would surface far from the cause.
    """
    with pytest.raises(AttributeError):
        getattr(BaseLoadState(), name)


def test_constructor_accepts_the_fields_with_a_default() -> None:
    """Compare what the constructor accepts with the fields having defaults.

    The two groups must line up exactly: a setting can be chosen at
    construction, a result cannot.

    The fields filled in by a load are declared init=False, so they cannot be
    passed to BaseLoadState(...) and set by mistake before the load. A field
    that drifted into the constructor would let a caller hand the loader a
    grid shape or a time of their own, which nothing downstream expects.
    """
    accepted = {field.name for field in fields(BaseLoadState) if field.init}
    assert accepted == set(WITH_DEFAULT)


@pytest.mark.parametrize("name", CONTAINERS)
def test_containers_are_not_shared(name: str) -> None:
    """Build two states and check they do not share the same container.

    This is the classic dataclass trap: a mutable default written as `= {}`
    is built once when the class is defined, so every instance would share
    one object. `is not` is the whole test -- two empty dicts compare equal,
    so only identity can tell a shared one from a fresh one.

    Filling the variables, units or offsets of one dataset never leaks into
    another one. Without this, loading a second simulation would appear to
    add its variables to the first.
    """
    first, second = BaseLoadState(), BaseLoadState()
    assert getattr(first, name) is not getattr(second, name)


def test_loaded_variables_can_be_attached() -> None:
    """Attach a variable that is not a declared field, and read it back.

    Load, LoadPart and Image forward attribute assignments to their state, so
    loaded variables such as rho are stored as extra attributes: the dataclass
    deliberately does not use slots=True.

    The names cannot be declared in advance, since they come from whatever
    the simulation wrote, and users attach composite variables of their own
    on top. The type checkers are told to ignore these two lines for the
    same reason: rho is not a field, and cannot be.
    """
    state = BaseLoadState()
    state.rho = np.ones(3)  # pyright: ignore[reportAttributeAccessIssue]  # ty: ignore[unresolved-attribute]
    assert state.rho.shape == (3,)  # pyright: ignore[reportAttributeAccessIssue]  # ty: ignore[unresolved-attribute]


def test_repr_on_fresh_state() -> None:
    """Print a fresh state and check it neither crashes nor invents values.

    The load-only fields do not exist before a load. They are declared
    repr=False, so the generated repr skips them instead of raising
    AttributeError on the first one.

    This is not hypothetical: it used to raise, and was fixed by marking all
    fourteen of them repr=False. The loop is the part that matters, since it
    checks every load-only field is absent rather than just that the call
    returned something.
    """
    text = repr(BaseLoadState())
    assert text.startswith("BaseLoadState(")
    for name in WITHOUT_DEFAULT:
        assert f"{name}=" not in text
