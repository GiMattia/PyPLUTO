"""Test of the imagestate.py file.

The same checks as the two load state files, run against ImageState, and kept
deliberately parallel to them: the same tests in the same order, so no state
is held to a lower standard than the others.

ImageState differs in one way that shows up throughout. Every field has a
default, because an Image is usable the moment it is built, so there is
nothing that only a later step can fill in. The load states check their
load-only fields one by one; here that half of the table is empty, and
test_no_field_is_unset states so outright rather than leaving a test that
silently checks nothing.
"""

from dataclasses import fields

import pytest
from helper_image import CONTAINERS, DEFAULTS, WITH_DEFAULT, WITHOUT_DEFAULT

from pyPLUTO.imagestate import ImageState

# The hand-written table and its views live in helper_image.py: DEFAULTS is
# what every field holds on a fresh state, WITH_DEFAULT and WITHOUT_DEFAULT
# split it, and CONTAINERS lists the fields built by a default_factory. Each
# entry is checked by test_default or by test_unset_until_loaded, and
# test_every_field_is_listed makes sure no field is missing.


def test_every_field_is_listed() -> None:
    """Compare the fields the class declares with the table in the helper.

    Adding, removing or renaming a field fails here until the table is
    updated, so no field can go untested.

    Every other test in this file is parametrized from that table, so a field
    missing from it would never be exercised and nothing would say so.
    """
    declared = {field.name for field in fields(ImageState)}
    missing, stale = declared - set(DEFAULTS), set(DEFAULTS) - declared
    assert not missing, (
        f"not listed in DEFAULTS, so untested: {sorted(missing)}"
    )
    assert not stale, (
        f"listed in DEFAULTS but no longer an ImageState field: {sorted(stale)}"
    )


@pytest.mark.parametrize(("name", "expected"), WITH_DEFAULT.items())
def test_default(name: str, expected: object) -> None:
    """Build a fresh state and check one field against the expected default.

    One test per field, so a failure names the field rather than the table.
    What it pins is what a user gets from `pp.Image()` before drawing
    anything.

    The type is checked too because 0 == 0.0 == False in Python: comparing
    values alone would not notice, e.g., tight defaulting to 1.
    """
    value = getattr(ImageState(), name)
    assert value == expected
    assert type(value) is type(expected)


def test_no_field_is_unset() -> None:
    """Check that no field is marked as having no default.

    This replaces a test that would otherwise check nothing: parametrizing
    over an empty WITHOUT_DEFAULT produces zero cases, which pytest reports
    as a skip rather than a pass, and a reader would have to work out why.

    States that do have load-only fields check them one by one instead, with
    test_unset_until_loaded (see test_baseloadstate.py). If this fails, a
    field was marked UNSET in the table and that test should come back here.
    """
    assert WITHOUT_DEFAULT == []


def test_constructor_accepts_the_fields_with_a_default() -> None:
    """Compare what the constructor accepts with the fields having defaults.

    For ImageState these are the same set, since every field has a default.
    The test is kept in the same shape as its counterparts in the load state
    files, where the two sets genuinely differ.

    A field declared init=False could not be passed to ImageState(...), and
    would have to move to the WITHOUT_DEFAULT half of the table.
    """
    accepted = {field.name for field in fields(ImageState) if field.init}
    assert accepted == set(WITH_DEFAULT)


@pytest.mark.parametrize("name", CONTAINERS)
def test_containers_are_not_shared(name: str) -> None:
    """Build two states and check they do not share the same container.

    `is not` is the whole test: two empty lists compare equal, so only
    identity distinguishes a shared object from a fresh one. Almost every
    field here is a container, since the per-axis lists all start empty.

    Two images would otherwise share their axes, colors or ranges, and one
    would silently change the other.
    """
    first, second = ImageState(), ImageState()
    assert getattr(first, name) is not getattr(second, name)


def test_repr_on_fresh_state() -> None:
    """Print a fresh state and find a real value in the text.

    Shorter than its counterpart in the load states, because nothing here is
    hidden from the repr: with no load-only fields there is no `repr=False`,
    so a field is expected to appear rather than to be absent.
    """
    text = repr(ImageState())
    assert text.startswith("ImageState(")
    assert "nwin=1" in text


def test_image_state_initialization() -> None:
    """Pass a style to the constructor and read it back.

    The fields with defaults are settings a user may choose, and this is the
    one line that checks the constructor actually honours a choice rather
    than only that it accepts one.
    """
    state = ImageState(style="seaborn-v0_8", LaTeX=True)
    assert state.style == "seaborn-v0_8"


def test_image_state_attributes() -> None:
    """Pass a list to the constructor, then replace it wholesale.

    A field built by a default_factory must still accept a value given
    explicitly, and must still be an ordinary attribute afterwards: the
    factory decides the starting value, not the behaviour.
    """
    state = ImageState(style="default", LaTeX=True, color=["red", "blue"])
    assert state.color == ["red", "blue"]
    state.color = ["green", "yellow"]
    assert state.color == ["green", "yellow"]


def test_image_state_dynamic_attribute() -> None:
    """Attach an attribute that is not a declared field, and read it back.

    Image forwards every attribute assignment to its state, so the state must
    accept names it does not declare: the dataclass has no slots on purpose.

    The type checkers are silenced on these two lines for that reason: the
    name is not a field and cannot be one.
    """
    state = ImageState(style="default", LaTeX=True)
    state.custom_attr = 123  # pyright: ignore[reportAttributeAccessIssue]  # ty: ignore[unresolved-attribute]
    assert state.custom_attr == 123  # pyright: ignore[reportAttributeAccessIssue]  # ty: ignore[unresolved-attribute]
