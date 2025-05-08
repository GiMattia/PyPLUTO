import pytest
from pyPLUTO.figure_new import FigureManager
from pyPLUTO.image_new import Image_new
from pyPLUTO.imagestate import ImageState


# Test when the style is valid and can be applied
def test_setup_style_with_valid_style():
    # Given
    state = ImageState(
        style="ggplot"
    )  # Use a valid style available in matplotlib
    _ = FigureManager(state)
    assert state.style == "ggplot"  # style should remain the same


# Test when the style is invalid and falls back to default
def test_setup_style_with_invalid_style():
    state = ImageState(style="non_existent_style")
    with pytest.warns(
        UserWarning, match="Style 'non_existent_style' not found."
    ) as warning:
        _ = FigureManager(state)
    assert state.style == "default"  # Ensure the style was set to 'default'


# Test interaction with Image_new to check delegation and style fallback
def test_interaction_with_image_new():
    # Given
    with pytest.warns(
        UserWarning, match="Style 'non_existent_style' not found."
    ) as warning:
        img = Image_new(
            style="non_existent_style"
        )  # Initialize Image_new with invalid style

    assert img.state.style == "default"  # style should fallback to default
    assert (
        img.figure_manager.state.style == "default"
    )  # Same for the figure manager


# Test interaction when a valid style is used via Image_new
def test_interaction_with_image_new_valid_style():
    # Given
    img = Image_new(style="ggplot")  # Use a valid style available in matplotlib
    assert (
        img.state.style == "ggplot"
    )  # style should remain as seaborn-darkgrid
    assert (
        img.figure_manager.state.style == "ggplot"
    )  # Same for the figure manager
