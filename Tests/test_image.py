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
    comp1, comp2 = 123, 456
    img = pp.Image()
    img.state.custom_attr = comp1
    assert img.custom_attr == comp1
    img.custom_attr = comp2
    assert img.state.custom_attr == comp2


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


def test_no_text_suppresses_print(capfd):
    img = pp.Image(text=False)
    captured = capfd.readouterr()
    assert "Image class created at nwin" not in captured.out


def test___setattr__existing_attribute_branch():
    img = pp.Image()
    old_ref = img.AxisManager
    img.AxisManager = old_ref  # exercises super().__setattr__ path
    assert img.AxisManager is old_ref


def test_property_proxies_are_callable():
    img = pp.Image()
    assert callable(img.animate)
    assert callable(img.colorbar)
    assert callable(img.contour)
    assert callable(img.interactive)
    assert callable(img.savefig)
    assert callable(img.scatter)
    assert callable(img.show)
    assert callable(img.text)
    assert callable(img.streamplot)


def test_oplotbox_delegates(monkeypatch):
    called = {
        "flag": False,
        "args": None,
        "kwargs": None,
        "self_is_image": None,
    }

    def fake_oplotbox(self, *args, **kwargs):
        called["flag"] = True
        called["args"] = args
        called["kwargs"] = kwargs
        called["self_is_image"] = isinstance(self, pp.Image)

    monkeypatch.setattr(pp.image, "oplotbox", fake_oplotbox, raising=True)
    img = pp.Image()
    img.oplotbox(1, a=2)
    assert called["flag"] is True
    assert called["args"] == (1,)
    assert called["kwargs"] == {"a": 2}
    assert called["self_is_image"] is True


def test_imagemixin_setters_write_through_to_state():
    img = pp.Image()
    img.ax = [None]
    assert img.state.ax == [None]
    img.legpar = {"fontsize": 8}
    assert img.state.legpar == {"fontsize": 8}
    img.legpos = "upper right"
    assert img.state.legpos == "upper right"
    img.nline = 3
    assert img.state.nline == 3
    img.ntext = 2
    assert img.state.ntext == 2
    img.setax = [0, 1]
    assert img.state.setax == [0, 1]
    img.setay = [0, 1]
    assert img.state.setay == [0, 1]
    img.shade = True
    assert img.state.shade is True
    img.tickspar = {"direction": "in"}
    assert img.state.tickspar == {"direction": "in"}
    img.vlims = (0.0, 1.0)
    assert img.state.vlims == (0.0, 1.0)
    img.xscale = "log"
    assert img.state.xscale == "log"
    img.yscale = "linear"
    assert img.state.yscale == "linear"
