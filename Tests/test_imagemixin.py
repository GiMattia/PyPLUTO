"""Test of the imagemixin.py file.

The same checks as the two load mixin files, run against ImageMixin, and kept
deliberately parallel to them: the same tests in the same order, so no mixin
is held to a lower standard than the others.

The tests are about wiring rather than values -- that each property reaches
the field of the same name, in both directions, for every field. A getter
pointing at its neighbour raises nothing, and would surface as a plot drawn
with the wrong limits or the wrong scale.

As in imagestate.py every field has a default, so the load-only half of the
table is empty and test_no_property_is_unset says so outright instead of
leaving a test that silently checks nothing.
"""

import pytest
from helper_image import DEFAULTS, WITH_DEFAULT, WITHOUT_DEFAULT, DummyState

from pyPLUTO.imagemixin import ImageMixin
from pyPLUTO.imagestate import ImageState

# The mixin exposes every ImageState field, so its expected values are the
# state's own table from helper_image.py: DEFAULTS is what every property
# returns on a fresh state, split into WITH_DEFAULT and WITHOUT_DEFAULT. Each
# entry is checked by test_default or by test_unset_until_loaded, and
# test_every_property_is_listed makes sure the properties match the state
# fields: a new state field without a property fails there.


class _Image(ImageMixin):
    """The smallest object that can use the mixin: it only has a state.

    A mixin cannot be instantiated on its own, since it expects a `state` its
    owner provides. Rather than use a real Image -- which would open a figure
    and build sixteen managers -- the tests use this, which supplies a state
    and nothing else, so whatever works here works because of the mixin.
    """

    def __init__(self) -> None:
        """Give the mixin the one thing it needs, a fresh state."""
        self.state = ImageState()


def test_every_property_is_listed() -> None:
    """Compare the properties the mixin defines with the table in the helper.

    Adding, removing or renaming a property fails here until the table is
    updated, so no property can go untested.

    Every other test here is parametrized from that table, which is what
    makes this the test that keeps the rest meaningful.
    """
    defined = {
        name
        for name, attribute in vars(ImageMixin).items()
        if isinstance(attribute, property)
    }
    missing, stale = defined - set(DEFAULTS), set(DEFAULTS) - defined
    assert not missing, (
        f"not listed in DEFAULTS, so untested: {sorted(missing)}"
    )
    assert not stale, (
        f"listed in DEFAULTS but no ImageMixin property: {sorted(stale)}"
    )


@pytest.mark.parametrize(("name", "expected"), WITH_DEFAULT.items())
def test_default(name: str, expected: object) -> None:
    """Read one property on a fresh image and check the default it returns.

    The same expectation as the matching test in test_imagestate.py, but
    reached through the property rather than off the dataclass, so a getter
    wired to the wrong field is caught even when both fields have defaults.

    The type is checked too because 0 == 0.0 == False in Python: comparing
    values alone would not notice, e.g., tight defaulting to 1.
    """
    value = getattr(_Image(), name)
    assert value == expected
    assert type(value) is type(expected)


def test_no_property_is_unset() -> None:
    """Give every ImageMixin property a default, so WITHOUT_DEFAULT is empty.

    Mixins over a state with load-only fields check them one by one instead,
    with test_unset_until_loaded (see test_baseloadmixin.py). If this fails, a
    field was marked UNSET in the table and that test should come back here.
    """
    assert WITHOUT_DEFAULT == []


@pytest.mark.parametrize("name", DEFAULTS)
def test_property_reads_from_state(name: str) -> None:
    """Put a marker on one state field and read it back through its property.

    This is the direction that catches a getter pointing at the wrong field,
    which matters here because so many fields are per-axis lists that all
    start as an empty list: setax and setay, xscale and yscale, legpar and
    legpos are indistinguishable by value.

    The value is a fresh object(): only the right field can hold it, so a
    property wired to a different field always fails. Plain values such as
    False or True could coincide with another field's default and hide it.
    """
    image = _Image()
    sentinel = object()
    setattr(image.state, name, sentinel)
    assert getattr(image, name) is sentinel


@pytest.mark.parametrize("name", DEFAULTS)
def test_property_writes_to_state(name: str) -> None:
    """Write a marker through one property and find it on the state field.

    The opposite direction, catching a setter pointing elsewhere -- and also
    a missing one, since assigning to a property that has only a getter
    raises AttributeError here rather than passing quietly.
    """
    image = _Image()
    sentinel = object()
    setattr(image, name, sentinel)
    assert getattr(image.state, name) is sentinel


@pytest.mark.parametrize("name", DEFAULTS)
def test_property_roundtrip(name: str) -> None:
    """Write through a property and read back through the same property.

    The two tests above pin each direction against the state; this pins them
    against each other, so the three together leave no way for a getter and
    a setter to agree on the wrong field.
    """
    image = _Image()
    sentinel = object()
    setattr(image, name, sentinel)
    assert getattr(image, name) is sentinel


def test_states_are_independent() -> None:
    """Give two images different styles and check neither sees the other's.

    The state is shared by reference within one image, which is the design;
    it must not be shared between two. If the mixin held the value itself, or
    the state were built once at class level, opening a second figure would
    restyle the first under the user.
    """
    first, second = _Image(), _Image()
    first.style = "dark_background"
    second.style = "classic"
    assert first.state.style == "dark_background"
    assert second.state.style == "classic"


def test_selected_mixin_properties() -> None:
    """Read and write a selection of properties through a dummy state.

    Kept from the first version of this file. The values are deliberately of
    the wrong type for several properties, so the type checkers are silenced
    on those lines.
    """

    class M(ImageMixin):
        def __init__(self) -> None:
            self.state = DummyState()  # pyright: ignore[reportAttributeAccessIssue]  # ty: ignore[invalid-assignment]

    m = M()

    # Only touch the specific missing lines
    m.style = "newstyle"
    assert m.style == "newstyle"

    m.legpos = "left"  # pyright: ignore[reportAttributeAccessIssue]  # ty: ignore[invalid-assignment]
    assert m.legpos == "left"

    m.nline = 7  # pyright: ignore[reportAttributeAccessIssue]  # ty: ignore[invalid-assignment]
    assert m.nline == 7

    m.ncol0 = 2
    assert m.ncol0 == 2

    m.ntext = 5  # pyright: ignore[reportAttributeAccessIssue]  # ty: ignore[invalid-assignment]
    assert m.ntext == 5

    m.nrow0 = 9
    assert m.nrow0 == 9

    m.tight = False
    assert m.tight is False

    m.vlims = (1, 2)  # pyright: ignore[reportAttributeAccessIssue]  # ty: ignore[invalid-assignment]
    assert m.vlims == (1, 2)

    m.xscale = "log"  # pyright: ignore[reportAttributeAccessIssue]  # ty: ignore[invalid-assignment]
    assert m.xscale == "log"

    m.yscale = "log"  # pyright: ignore[reportAttributeAccessIssue]  # ty: ignore[invalid-assignment]
    assert m.yscale == "log"

    m.ax = ["ax1", "ax2"]  # pyright: ignore[reportAttributeAccessIssue]  # ty: ignore[invalid-assignment]
    assert m.ax == ["ax1", "ax2"]

    m.legpar = [[0.1, 0.2], [0.3, 0.4]]
    assert m.legpar == [[0.1, 0.2], [0.3, 0.4]]

    m.setax = [0, 1]
    assert m.setax == [0, 1]

    m.setay = [2, 3]
    assert m.setay == [2, 3]

    m.shade = ["shade1", "shade2"]
    assert m.shade == ["shade1", "shade2"]

    m.tickspar = [5, 10]
    assert m.tickspar == [5, 10]
