import pytest
from pyPLUTO.imagestate import ImageState


def test_image_state_initialization():
    state = ImageState(style="seaborn-v0_8", LaTeX=True)
    assert state.style == "seaborn-v0_8"


def test_image_state_attributes():
    state = ImageState(style="default", LaTeX=True, color=["red", "blue"])
    assert state.color == ["red", "blue"]
    state.color = ["green", "yellow"]
    assert state.color == ["green", "yellow"]


def test_image_state_dynamic_attribute():
    state = ImageState(style="default", LaTeX=True)
    state.custom_attr = 123
    assert state.custom_attr == 123


def test_image_state_missing_attribute():
    with pytest.raises(TypeError):
        state = ImageState(style="default")
