from pyPLUTO.imagestate import ImageState


def test_image_state_initialization():
    state = ImageState(style="seaborn-v0_8")
    assert state.style == "seaborn-v0_8"


def test_image_state_attributes():
    state = ImageState(style="default", color=["red", "blue"])
    assert state.color == ["red", "blue"]
    state.color = ["green", "yellow"]
    assert state.color == ["green", "yellow"]


def test_image_state_dynamic_attribute():
    state = ImageState(style="default")
    state.custom_attr = 123
    assert state.custom_attr == 123
