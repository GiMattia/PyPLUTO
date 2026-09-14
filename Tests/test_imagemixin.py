"""Test of the imagemixin.py file."""

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
    """The smallest object that can use the mixin: it only has a state."""

    def __init__(self) -> None:
        self.state = ImageState()


def test_every_property_is_listed() -> None:
    """Keep DEFAULTS in sync with the properties ImageMixin defines.

    Adding, removing or renaming a property fails here until the table is
    updated, so no property can go untested.
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
    """Return the expected default, with the expected type, on a fresh state.

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
    """Read each property from the state field with the same name.

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
    """Write each property to the state field with the same name.

    A property without a setter raises AttributeError here, so this also
    checks that every property can be written.
    """
    image = _Image()
    sentinel = object()
    setattr(image, name, sentinel)
    assert getattr(image.state, name) is sentinel


@pytest.mark.parametrize("name", DEFAULTS)
def test_property_roundtrip(name: str) -> None:
    """Read back through each property what was written through it."""
    image = _Image()
    sentinel = object()
    setattr(image, name, sentinel)
    assert getattr(image, name) is sentinel


def test_states_are_independent() -> None:
    """Keep the state of two images separate."""
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
