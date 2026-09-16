"""Test of the loadstate.py file.

The same checks as test_baseloadstate.py, run against LoadState. The pair is
kept deliberately parallel: the same tests, in the same order, so neither
state is held to a lower standard than the other and a reader who knows one
file knows the other.

What differs is only the table they are parametrized from. This one comes
from helper_load.py, which is the inherited base table plus the grid fields,
so every inherited field is checked here too -- against the subclass, where
a careless override would show up.
"""

from dataclasses import fields

import numpy as np
import pytest
from helper_load import CONTAINERS, DEFAULTS, WITH_DEFAULT, WITHOUT_DEFAULT

from pyPLUTO.loadstate import LoadState

# The hand-written table and its views live in helper_load.py, shared with
# test_loadmixin.py: DEFAULTS is what every field holds on a fresh state (the
# fields inherited from BaseLoadState plus the ones LoadState adds),
# WITH_DEFAULT and WITHOUT_DEFAULT split it, and CONTAINERS lists the fields
# built by a default_factory. Each entry is checked by test_default or by
# test_unset_until_loaded, and test_every_field_is_listed makes sure no field
# is missing.


def test_every_field_is_listed() -> None:
    """Compare the fields the class declares with the table in the helper.

    `fields()` reports the inherited fields as well as the new ones, so a
    field added to BaseLoadState shows up here until the table is updated.
    That is intended: the helper table is the union, and both state test
    files read it.

    Every other test in this file is parametrized from that table, so a field
    missing from it would never be tested and nothing would say so.
    """
    declared = {field.name for field in fields(LoadState)}
    missing, stale = declared - set(DEFAULTS), set(DEFAULTS) - declared
    assert not missing, (
        f"not listed in DEFAULTS, so untested: {sorted(missing)}"
    )
    assert not stale, (
        f"listed in DEFAULTS but no longer a LoadState field: {sorted(stale)}"
    )


@pytest.mark.parametrize(("name", "expected"), WITH_DEFAULT.items())
def test_default(name: str, expected: object) -> None:
    """Build a fresh state and check one field against the expected default.

    One test per field with a default, so a failure names the field rather
    than the table.

    The type is checked too because 0 == 0.0 == False in Python: comparing
    values alone would not notice, e.g., level defaulting to False.
    """
    value = getattr(LoadState(), name)
    assert value == expected
    assert type(value) is type(expected)


@pytest.mark.parametrize("name", WITHOUT_DEFAULT)
def test_unset_until_loaded(name: str) -> None:
    """Read a load-only field on a fresh state and expect AttributeError.

    Nearly every LoadState field is of this kind, because a grid has no
    meaningful value until a simulation has been read: its size, its geometry
    and its very shape all come from the files.

    If one of these fields silently gained a default, code could read a
    made-up grid or shape before anything is loaded: this test would catch it.
    """
    with pytest.raises(AttributeError):
        getattr(LoadState(), name)


def test_constructor_accepts_the_fields_with_a_default() -> None:
    """Compare what the constructor accepts with the fields having defaults.

    Only full3D and level can be chosen at construction; everything else is a
    result of reading the files.

    The fields filled in by a load are declared init=False, so they cannot be
    passed to LoadState(...) and set by mistake before the load.
    """
    accepted = {field.name for field in fields(LoadState) if field.init}
    assert accepted == set(WITH_DEFAULT)


@pytest.mark.parametrize("name", CONTAINERS)
def test_containers_are_not_shared(name: str) -> None:
    """Build two states and check they do not share the same container.

    `is not` is the whole test: two empty dicts compare equal, so only
    identity distinguishes a shared object from a fresh one. The containers
    are all inherited from BaseLoadState, since the grid fields have no
    defaults at all.

    Filling the variables, units or offsets of one dataset never leaks into
    another one.
    """
    first, second = LoadState(), LoadState()
    assert getattr(first, name) is not getattr(second, name)


def test_loaded_variables_can_be_attached() -> None:
    """Attach a variable that is not a declared field, and read it back.

    Load forwards attribute assignments to its state, so loaded variables such
    as rho are stored as extra attributes: the dataclass deliberately does not
    use slots=True.

    The names cannot be declared in advance, since they come from whatever the
    simulation wrote, and users attach composite variables of their own on
    top. The type checkers are told to ignore these two lines for the same
    reason: rho is not a field, and cannot be.
    """
    state = LoadState()
    state.rho = np.ones(3)  # pyright: ignore[reportAttributeAccessIssue]  # ty: ignore[unresolved-attribute]
    assert state.rho.shape == (3,)  # pyright: ignore[reportAttributeAccessIssue]  # ty: ignore[unresolved-attribute]


def test_repr_on_fresh_state() -> None:
    """Print a fresh state and check it neither crashes nor invents values.

    The load-only fields do not exist before a load. They are declared
    repr=False, so the generated repr skips them instead of raising
    AttributeError on the first one.

    This is not hypothetical: it used to raise on dx1, the first such field,
    and was fixed by marking all twenty of them repr=False. The loop checks
    every one is absent rather than only that the call returned something.
    """
    text = repr(LoadState())
    assert text.startswith("LoadState(")
    for name in WITHOUT_DEFAULT:
        assert f"{name}=" not in text
