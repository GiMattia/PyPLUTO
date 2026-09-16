"""Test of the loadmixin.py file.

The same checks as test_baseloadmixin.py, run against LoadMixin, and kept
deliberately parallel to it: the same tests in the same order, so neither
mixin is held to a lower standard and a reader who knows one file knows the
other.

The tests are about wiring rather than values -- that each property reaches
the field of the same name, in both directions, for every field. A getter
pointing at its neighbour raises nothing and would be found by a user reading
the wrong grid off their data.

Because LoadMixin inherits from BaseLoadMixin, the properties tested here are
both the grid ones it defines and the base ones it inherits, so the base
pairs are exercised a second time against the subclass.
"""

import pytest
from helper_load import DEFAULTS, WITH_DEFAULT, WITHOUT_DEFAULT

from pyPLUTO.loadmixin import LoadMixin
from pyPLUTO.loadstate import LoadState

# The mixin exposes every LoadState field, so its expected values are the
# state's own table from helper_load.py: DEFAULTS is what every property
# returns on a fresh state, split into WITH_DEFAULT and WITHOUT_DEFAULT. Each
# entry is checked by test_default or by test_unset_until_loaded, and
# test_every_property_is_listed makes sure the properties match the state
# fields: a new state field without a property fails there.


class _Loader(LoadMixin):
    """The smallest object that can use the mixin: it only has a state.

    A mixin cannot be instantiated on its own, since it expects a `state` its
    owner provides. Rather than use a real Load -- which would read files and
    build eight managers -- the tests use this, which supplies a state and
    nothing else, so whatever works here works because of the mixin.
    """

    def __init__(self) -> None:
        """Give the mixin the one thing it needs, a fresh state."""
        self.state = LoadState()


def test_every_property_is_listed() -> None:
    """Compare the properties reachable on the mixin with the helper table.

    The properties are collected along the MRO because LoadMixin defines only
    the grid ones itself and inherits the rest from BaseLoadMixin. Looking at
    `vars(LoadMixin)` alone would see the grid ones only, and the base half
    would go untested with nothing to say so.

    Every other test here is parametrized from that table, which is what makes
    this the test that keeps the rest meaningful.
    """
    defined = {
        name
        for klass in LoadMixin.__mro__
        for name, attribute in vars(klass).items()
        if isinstance(attribute, property)
    }
    missing, stale = defined - set(DEFAULTS), set(DEFAULTS) - defined
    assert not missing, (
        f"not listed in DEFAULTS, so untested: {sorted(missing)}"
    )
    assert not stale, (
        f"listed in DEFAULTS but no LoadMixin property: {sorted(stale)}"
    )


@pytest.mark.parametrize(("name", "expected"), WITH_DEFAULT.items())
def test_default(name: str, expected: object) -> None:
    """Read one property on a fresh loader and check the default it returns.

    The same expectation as the matching test in test_loadstate.py, but
    reached through the property rather than off the dataclass, so a getter
    wired to the wrong field is caught even when both fields have defaults.

    The type is checked too because 0 == 0.0 == False in Python: comparing
    values alone would not notice, e.g., level defaulting to False.
    """
    value = getattr(_Loader(), name)
    assert value == expected
    assert type(value) is type(expected)


@pytest.mark.parametrize("name", WITHOUT_DEFAULT)
def test_unset_until_loaded(name: str) -> None:
    """Read a load-only property on a fresh loader and expect AttributeError.

    The property must not soften the state's behaviour: reading `x1` before a
    load has to fail just as reading `state.x1` does, rather than return None
    because the getter swallowed the error.

    If one of these fields silently gained a default, code could read a
    made-up grid or shape before anything is loaded: this test would catch it.
    """
    with pytest.raises(AttributeError):
        getattr(_Loader(), name)


@pytest.mark.parametrize("name", DEFAULTS)
def test_property_reads_from_state(name: str) -> None:
    """Put a marker on one state field and read it back through its property.

    This is the direction that catches a getter pointing at the wrong field,
    which matters most here: x1, x1c, x1p, x1r, x1rc, x1rp, x1rt and x1t are
    eight names one letter apart.

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

    The opposite direction, catching a setter pointing elsewhere -- and also
    a missing one, since assigning to a property that has only a getter
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
    against each other, so the three together leave no way for a getter and
    a setter to agree on the wrong field.
    """
    loader = _Loader()
    sentinel = object()
    setattr(loader, name, sentinel)
    assert getattr(loader, name) is sentinel


def test_states_are_independent() -> None:
    """Give two loaders different grids and check neither sees the other's.

    The state is shared by reference within one load, which is the design; it
    must not be shared between two. If the mixin held the value itself, or
    the state were built once at class level, opening a second simulation
    would change the grid of the first under the user.
    """
    first, second = _Loader(), _Loader()
    first.nx1 = 128
    second.nx1 = 64
    assert first.state.nx1 == 128
    assert second.state.nx1 == 64
