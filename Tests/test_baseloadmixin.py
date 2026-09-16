"""Test of the baseloadmixin.py file.

BaseLoadMixin is thirty-odd property pairs, each two lines long, each reading
or writing one field of the state. Nothing in it is hard; what is easy is
getting one of them wrong -- a getter pointing at the neighbouring field, a
setter that was never written, a property left behind when its field was
renamed. None of that raises, and all of it would be found by a user reading
the wrong number off their data.

The tests are therefore mostly about *wiring* rather than values: that each
property reaches the field of the same name, in both directions, for every
field. They are parametrized over the table in helper_baseload.py, so the
same list drives the state tests and these, and the two cannot drift apart.

test_baseloadstate.py checks the same table against the dataclass itself, and
these two files are deliberately kept in step: a state test and a mixin test
for the same property, so neither side is held to a lower standard.
"""

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
    """The smallest object that can use the mixin: it only has a state.

    A mixin cannot be instantiated on its own, since it expects a `state` its
    owner provides. Rather than use a real Load -- which would read files and
    drag in eight managers -- the tests use this, which supplies a state and
    nothing else. Anything that works here therefore works because of the
    mixin, not because of something Load does around it.
    """

    def __init__(self) -> None:
        """Give the mixin the one thing it needs, a fresh state."""
        self.state = BaseLoadState()


def test_every_property_is_listed() -> None:
    """Compare the properties the mixin defines with the table in the helper.

    Adding, removing or renaming a property fails here until the table above
    is updated, so no property can go untested.

    Since every other test in this file is parametrized from that table, a
    property missing from it would simply never be exercised, with nothing
    failing to say so. This is the test that makes the rest meaningful.
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
    """Read one property on a fresh loader and check the default it returns.

    The same expectation as the matching test in test_baseloadstate.py, but
    reached through the property rather than off the dataclass, so a getter
    wired to the wrong field is caught even when both fields have defaults.

    The type is checked too because 0 == 0.0 == False in Python: comparing
    values alone would not notice, e.g., multiple defaulting to 0.
    """
    value = getattr(_Loader(), name)
    assert value == expected
    assert type(value) is type(expected)


@pytest.mark.parametrize("name", WITHOUT_DEFAULT)
def test_unset_until_loaded(name: str) -> None:
    """Read a load-only property on a fresh loader and expect AttributeError.

    The property must not soften the state's behaviour: reading `nout` before
    a load has to fail just as reading `state.nout` does, rather than return
    None because the getter caught the error.

    If one of these fields silently gained a default, code could read a
    made-up value before anything is loaded: this test would catch it.
    """
    with pytest.raises(AttributeError):
        getattr(_Loader(), name)


@pytest.mark.parametrize("name", DEFAULTS)
def test_property_reads_from_state(name: str) -> None:
    """Put a marker on one state field and read it back through its property.

    This is the direction that catches a getter pointing at the wrong field.

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
    """Write a marker through one property and find it on the state field.

    The opposite direction, which catches a setter pointing elsewhere -- and
    also a missing one, since assigning to a property that has only a getter
    raises AttributeError here rather than passing quietly.
    """
    loader = _Loader()
    sentinel = object()
    setattr(loader, name, sentinel)
    assert getattr(loader.state, name) is sentinel


@pytest.mark.parametrize("name", DEFAULTS)
def test_property_roundtrip(name: str) -> None:
    """Write through a property and read back through the same property.

    The two tests above pin each direction against the state; this pins them
    against each other. A getter and a setter both pointing at the *same*
    wrong field would pass both of those and fail nothing -- except that the
    read test would then not see its marker, which is what keeps the trio
    honest together.
    """
    loader = _Loader()
    sentinel = object()
    setattr(loader, name, sentinel)
    assert getattr(loader, name) is sentinel


def test_states_are_independent() -> None:
    """Give two loaders different values and check neither sees the other's.

    The state is shared by reference within one load, which is the whole
    design; it must not be shared between two. If the mixin held the value
    itself, or the state were built once at class level, opening a second
    dataset would change the first one under the user.
    """
    first, second = _Loader(), _Loader()
    first.datatype = "dbl"
    second.datatype = "vtk"
    assert first.state.datatype == "dbl"
    assert second.state.datatype == "vtk"
