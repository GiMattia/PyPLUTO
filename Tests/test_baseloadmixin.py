"""Test of the baseloadmixin.py file."""

import pytest
from helper_baseload import DEFAULTS, WITH_DEFAULT, WITHOUT_DEFAULT

from pyPLUTO.baseloadmixin import BaseLoadMixin
from pyPLUTO.baseloadstate import BaseLoadState

# The mixin exposes every BaseLoadState field, so its expected values are the
# state's own table from helper_baseload.py: DEFAULTS is what every property
# returns on a fresh state, split into WITH_DEFAULT and WITHOUT_DEFAULT. Each
# entry is checked by test_default or by test_unset_until_loaded, and
# test_every_property_is_listed makes sure the properties match the state
# fields: a new state field without a property fails there.


class _Loader(BaseLoadMixin[BaseLoadState]):
    """The smallest object that can use the mixin: it only has a state."""

    def __init__(self) -> None:
        self.state = BaseLoadState()


def test_every_property_is_listed() -> None:
    """Keep DEFAULTS in sync with the properties BaseLoadMixin defines.

    Adding, removing or renaming a property fails here until the table above
    is updated, so no property can go untested.
    """
    defined = {
        name
        for name, attribute in vars(BaseLoadMixin).items()
        if isinstance(attribute, property)
    }
    missing, stale = defined - set(DEFAULTS), set(DEFAULTS) - defined
    assert not missing, (
        f"not listed in DEFAULTS, so untested: {sorted(missing)}"
    )
    assert not stale, (
        f"listed in DEFAULTS but no BaseLoadMixin property: {sorted(stale)}"
    )


@pytest.mark.parametrize(("name", "expected"), WITH_DEFAULT.items())
def test_default(name: str, expected: object) -> None:
    """Return the expected default, with the expected type, on a fresh state.

    The type is checked too because 0 == 0.0 == False in Python: comparing
    values alone would not notice, e.g., multiple defaulting to 0.
    """
    value = getattr(_Loader(), name)
    assert value == expected
    assert type(value) is type(expected)


@pytest.mark.parametrize("name", WITHOUT_DEFAULT)
def test_unset_until_loaded(name: str) -> None:
    """Raise AttributeError for a field that only a load fills in.

    If one of these fields silently gained a default, code could read a
    made-up value before anything is loaded: this test would catch it.
    """
    with pytest.raises(AttributeError):
        getattr(_Loader(), name)


@pytest.mark.parametrize("name", DEFAULTS)
def test_property_reads_from_state(name: str) -> None:
    """Read each property from the state field with the same name.

    The value is a fresh object(): only the right field can hold it, so a
    property wired to a different field always fails. Plain values such as
    False or True could coincide with another field's default and hide it.
    """
    loader = _Loader()
    sentinel = object()
    setattr(loader.state, name, sentinel)
    assert getattr(loader, name) is sentinel


@pytest.mark.parametrize("name", DEFAULTS)
def test_property_writes_to_state(name: str) -> None:
    """Write each property to the state field with the same name.

    A property without a setter raises AttributeError here, so this also
    checks that every property can be written.
    """
    loader = _Loader()
    sentinel = object()
    setattr(loader, name, sentinel)
    assert getattr(loader.state, name) is sentinel


@pytest.mark.parametrize("name", DEFAULTS)
def test_property_roundtrip(name: str) -> None:
    """Read back through each property what was written through it."""
    loader = _Loader()
    sentinel = object()
    setattr(loader, name, sentinel)
    assert getattr(loader, name) is sentinel


def test_states_are_independent() -> None:
    """Keep the state of two loaders separate."""
    first, second = _Loader(), _Loader()
    first.datatype = "dbl"
    second.datatype = "vtk"
    assert first.state.datatype == "dbl"
    assert second.state.datatype == "vtk"
