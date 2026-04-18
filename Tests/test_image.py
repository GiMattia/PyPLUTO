import matplotlib.pyplot as plt
import pytest

import pyPLUTO as pp
import pyPLUTO.image as image_mod
from pyPLUTO.imagestate import ImageState


def test_default_initialization():
    img = pp.Image()
    assert isinstance(img.state, ImageState)
    assert isinstance(img.FigureManager, object)


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


def test_warn_attr():
    with pytest.warns(UserWarning, match=r"Unused kwargs: \{'attr'\}"):
        obj = pp.Image(attr=None)


def test_tight_layout():
    Image = pp.Image(tight=False)
    assert Image.fig.get_tight_layout() is False


def test_animate_property(monkeypatch):
    # Patch before Image() is instantiated
    monkeypatch.setattr(
        image_mod,
        "InteractiveManager",
        lambda state: type(
            "DummyInteractive", (), {"animate": lambda self=None: "animate"}
        )(),
    )

    # Prevent any matplotlib figure creation
    monkeypatch.setattr(image_mod, "FigureManager", lambda state, **kw: None)
    monkeypatch.setattr(
        image_mod, "ImageState", lambda *a, **kw: type("S", (), {})()
    )

    img = image_mod.Image(text=False)
    assert img.animate() == "animate"


def test_oplotbox(monkeypatch):
    called = {}

    def fake_oplotbox(self, *a, **kw):
        called["yes"] = True

    # ✅ patch the module-level function, not the instance
    monkeypatch.setattr(image_mod, "oplotbox", fake_oplotbox)

    img = image_mod.Image(text=False)
    img.oplotbox([1, 2, 3], [4, 5, 6])
    assert "yes" in called
