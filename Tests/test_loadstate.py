"""Test of the loadstate.py file."""

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
    """Keep DEFAULTS in sync with the fields LoadState declares.

    This covers the inherited fields too, so a new BaseLoadState field shows
    up here as well until the table is updated.
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
    """Hold the expected default, with the expected type, on a fresh state.

    The type is checked too because 0 == 0.0 == False in Python: comparing
    values alone would not notice, e.g., level defaulting to False.
    """
    value = getattr(LoadState(), name)
    assert value == expected
    assert type(value) is type(expected)


@pytest.mark.parametrize("name", WITHOUT_DEFAULT)
def test_unset_until_loaded(name: str) -> None:
    """Raise AttributeError for a field that only a load fills in.

    If one of these fields silently gained a default, code could read a
    made-up grid or shape before anything is loaded: this test would catch it.
    """
    with pytest.raises(AttributeError):
        getattr(LoadState(), name)


def test_constructor_accepts_the_fields_with_a_default() -> None:
    """Accept in the constructor exactly the fields that have a default.

    The fields filled in by a load are declared init=False, so they cannot be
    passed to LoadState(...) and set by mistake before the load.
    """
    accepted = {field.name for field in fields(LoadState) if field.init}
    assert accepted == set(WITH_DEFAULT)


@pytest.mark.parametrize("name", CONTAINERS)
def test_containers_are_not_shared(name: str) -> None:
    """Give every state its own dict, list or set (default_factory).

    Filling the variables, units or offsets of one dataset never leaks into
    another one.
    """
    first, second = LoadState(), LoadState()
    assert getattr(first, name) is not getattr(second, name)


def test_loaded_variables_can_be_attached() -> None:
    """Accept attributes that are not declared fields.

    Load forwards attribute assignments to its state, so loaded variables such
    as rho are stored as extra attributes: the dataclass deliberately does not
    use slots=True.
    """
    state = LoadState()
    state.rho = np.ones(3)  # pyright: ignore[reportAttributeAccessIssue]  # ty: ignore[unresolved-attribute]
    assert state.rho.shape == (3,)  # pyright: ignore[reportAttributeAccessIssue]  # ty: ignore[unresolved-attribute]


def test_repr_on_fresh_state() -> None:
    """Print a fresh state without crashing.

    The load-only fields do not exist before a load. They are declared
    repr=False, so the generated repr skips them instead of raising
    AttributeError on the first one.
    """
    text = repr(LoadState())
    assert text.startswith("LoadState(")
    for name in WITHOUT_DEFAULT:
        assert f"{name}=" not in text
