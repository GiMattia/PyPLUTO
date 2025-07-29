import matplotlib.pyplot as plt
import pytest

import pyPLUTO as pp
from pyPLUTO.imagestate import ImageState


def test_default_initialization():
    img = pp.Image()
    assert isinstance(img.state, ImageState)
    assert isinstance(img._figure_manager, object)


def test_custom_arguments():
    fig = plt.figure()
    img = pp.Image(fig=fig, style="dark_background")
    assert img.state.fig is fig
    assert img.state.style == "dark_background"
    assert img.style == "dark_background"


def test_attribute_get_existing():
    img = pp.Image()
    img.state.custom_attr = 123
    assert img.custom_attr == 123
    img.custom_attr = 456
    assert img.state.custom_attr == 456
    img.another_attr = 789
    assert img.state.another_attr == 789
    img.another_attr = 101112
    assert img.state.another_attr == 101112


def test_Image_prints_message(capfd):
    I = pp.Image(text=True)
    captured = capfd.readouterr()
    assert "Image class created at nwin" in captured.out


# Check if the __str__ method works
def test_str():
    Image = pp.Image()
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
        Image = pp.Image()
        Image.wrong


def test_tight_layout():
    Image = pp.Image(tight=False)
    assert Image.fig.get_tight_layout() is False
