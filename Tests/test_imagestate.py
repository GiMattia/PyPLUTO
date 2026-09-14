"""Test of the imagestate.py file."""

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
    """Keep DEFAULTS in sync with the fields ImageState declares.

    Adding, removing or renaming a field fails here until the table is
    updated, so no field can go untested.
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
    """Hold the expected default, with the expected type, on a fresh state.

    The type is checked too because 0 == 0.0 == False in Python: comparing
    values alone would not notice, e.g., tight defaulting to 1.
    """
    value = getattr(ImageState(), name)
    assert value == expected
    assert type(value) is type(expected)


def test_no_field_is_unset() -> None:
    """Give every ImageState field a default, so WITHOUT_DEFAULT is empty.

    States that do have load-only fields check them one by one instead, with
    test_unset_until_loaded (see test_baseloadstate.py). If this fails, a
    field was marked UNSET in the table and that test should come back here.
    """
    assert WITHOUT_DEFAULT == []


def test_constructor_accepts_the_fields_with_a_default() -> None:
    """Accept in the constructor exactly the fields that have a default.

    A field declared init=False could not be passed to ImageState(...), and
    would have to move to the WITHOUT_DEFAULT half of the table.
    """
    accepted = {field.name for field in fields(ImageState) if field.init}
    assert accepted == set(WITH_DEFAULT)


@pytest.mark.parametrize("name", CONTAINERS)
def test_containers_are_not_shared(name: str) -> None:
    """Give every state its own dict or list (default_factory).

    Two images would otherwise share their axes, colors or ranges, and one
    would silently change the other.
    """
    first, second = ImageState(), ImageState()
    assert getattr(first, name) is not getattr(second, name)


def test_repr_on_fresh_state() -> None:
    """Print a fresh state without crashing, showing its fields."""
    text = repr(ImageState())
    assert text.startswith("ImageState(")
    assert "nwin=1" in text


def test_image_state_initialization() -> None:
    """Take the style given to the constructor."""
    state = ImageState(style="seaborn-v0_8", LaTeX=True)
    assert state.style == "seaborn-v0_8"


def test_image_state_attributes() -> None:
    """Take a list field from the constructor, and let it be replaced."""
    state = ImageState(style="default", LaTeX=True, color=["red", "blue"])
    assert state.color == ["red", "blue"]
    state.color = ["green", "yellow"]
    assert state.color == ["green", "yellow"]


def test_image_state_dynamic_attribute() -> None:
    """Accept attributes that are not declared fields.

    Image forwards every attribute assignment to its state, so the state must
    accept names it does not declare: the dataclass has no slots on purpose.
    """
    state = ImageState(style="default", LaTeX=True)
    state.custom_attr = 123  # pyright: ignore[reportAttributeAccessIssue]  # ty: ignore[unresolved-attribute]
    assert state.custom_attr == 123  # pyright: ignore[reportAttributeAccessIssue]  # ty: ignore[unresolved-attribute]
