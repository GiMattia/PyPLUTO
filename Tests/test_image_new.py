import matplotlib.pyplot as plt
import pyPLUTO as pp
import pytest
from pyPLUTO.imagestate import ImageState


def test_default_initialization():
    img = pp.Image_new()
    assert isinstance(img.state, ImageState)
    assert isinstance(img._figure_manager, object)


def test_custom_arguments():
    fig = plt.figure()
    img = pp.Image_new(fig=fig, style="dark_background")
    assert img.state.fig is fig
    assert img.state.style == "dark_background"
    assert img.style == "dark_background"


def test_attribute_get_existing():
    img = pp.Image_new()
    img.state.custom_attr = 123
    assert img.custom_attr == 123
    img.custom_attr = 456
    assert img.state.custom_attr == 456
    img.another_attr = 789
    with pytest.raises(AttributeError):
        print(img.state.another_attr)


def test_assign_existing_attribute():
    img = pp.Image_new()
    img.assign(style="seaborn")
    assert img.style == "seaborn"
    assert img.state.style == "seaborn"


def test_assign_new_custom_attribute():
    img = pp.Image_new()
    img.assign(title="Jet Plot")
    assert img.title == "Jet Plot"
    assert hasattr(img.state, "title")
    assert img.state.title == "Jet Plot"


def test_assign_multiple_attributes():
    img = pp.Image_new()
    img.assign(style="ggplot", color=["red", "green"], label="Shock Front")
    assert img.style == "ggplot"
    assert img.color == ["red", "green"]
    assert img.label == "Shock Front"
    assert img.state.label == "Shock Front"


def test_assign_chainability():
    img = pp.Image_new()
    result = img.assign(a=1, b=2)
    assert result is img
    assert img.a == 1
    assert img.b == 2


def test_image_new_prints_message(capfd):
    I = pp.Image_new(text=True)
    captured = capfd.readouterr()
    assert "Image class created at nwin" in captured.out


# Check if the __str__ method works
def test_str():
    Image = pp.Image_new()
    s = str(Image)
    assert "Image properties:" in s
    assert "Adds a set of [nrow,ncol] subplots to the figure." in s
    assert "Plots one line in a subplot." in s
    assert "Image class." in s
    assert "Public methods available:" in s
    assert "- display" in s
    assert "- savefig" in s
    assert "Public attributes available:" in s
    assert "- fig" in s
    assert "Please do not use 'private'" in s


# Check if raises an error with wrong attribute
def test_getattr_new():
    with pytest.raises(AttributeError):
        Image = pp.Image_new()
        Image.wrong
