"""Test of the imagetools.py file."""

from types import SimpleNamespace

import matplotlib.colors as mcol
import pytest

import pyPLUTO as pp
from pyPLUTO.imagefuncs import imagetools
from pyPLUTO.imagefuncs.imagetools import ImageToolsManager


def _manager():
    Image = pp.Image()
    return ImageToolsManager(Image.state), Image


# Each color scale name maps to its matplotlib normalization
@pytest.mark.parametrize(
    ("cscale", "expected"),
    [
        ("linear", mcol.Normalize),
        ("log", mcol.LogNorm),
        ("symlog", mcol.SymLogNorm),
        ("twoslope", mcol.TwoSlopeNorm),
        ("power", mcol.PowerNorm),
        ("asinh", mcol.AsinhNorm),
    ],
)
def test_set_cscale_known_scales(cscale, expected):
    manager, _ = _manager()
    vmin = 0.1 if cscale == "log" else -1.0
    assert isinstance(manager.set_cscale(cscale, vmin, 1.0, 0.5), expected)


# An unknown scale falls back to the linear normalization
def test_set_cscale_unknown_scale():
    manager, _ = _manager()
    norm = manager.set_cscale("nosuchscale", 0.0, 1.0, 0.5)
    assert isinstance(norm, mcol.Normalize)


# The limits are kept in the returned normalization
def test_set_cscale_keeps_limits():
    manager, _ = _manager()
    norm = manager.set_cscale("linear", 0.0, 2.0, 0.5)
    assert (norm.vmin, norm.vmax) == (0.0, 2.0)


# A matplotlib colormap is found by its name
def test_find_cmap_matplotlib():
    manager, _ = _manager()
    assert manager.find_cmap("viridis").name == "viridis"


# None means "no colormap" and is returned as it is
def test_find_cmap_none():
    manager, _ = _manager()
    assert manager.find_cmap(None) is None


# An already built colormap is returned unchanged
def test_find_cmap_colormap_object():
    manager, _ = _manager()
    cmap = mcol.ListedColormap(["red", "blue"])
    assert manager.find_cmap(cmap) is cmap


# salsa is an optional dependency, so find_cmap warns differently depending on
# whether it is installed. Both tests below pin it by hand: otherwise each of
# them checks a different branch depending on the machine running the suite.


# An unknown name warns and falls back to a default colormap
def test_find_cmap_unknown_name(monkeypatch):
    manager, _ = _manager()
    monkeypatch.setattr(imagetools, "salsa", SimpleNamespace())
    with pytest.warns(UserWarning, match="not found"):
        assert manager.find_cmap("nosuchcmap").name == "plasma"


# Without salsa the fallback is the same, but the warning says why
def test_find_cmap_without_salsa(monkeypatch):
    manager, _ = _manager()
    monkeypatch.setattr(imagetools, "salsa", None)
    with pytest.warns(UserWarning, match="not installed"):
        assert manager.find_cmap("nosuchcmap").name == "plasma"


# A text is added to the axis
def test_text_is_added():
    _, Image = _manager()
    Image.plot([0, 1], [0, 1])
    Image.text(text="hello", x=0.5, y=0.5)
    assert any(t.get_text() == "hello" for t in Image.ax[0].texts)


# The figure can be saved to a file
def test_savefig(tmp_path):
    _, Image = _manager()
    Image.plot([0, 1], [0, 1])
    out = tmp_path / "figure.png"
    Image.savefig(str(out))
    assert out.exists()


# A new axis is created when none exists yet
def test_assign_ax_creates_axis():
    manager, Image = _manager()
    ax, nax = manager.assign_ax(None, _check=False)
    assert nax == 0
    assert ax is Image.ax[0]


# An axis can be selected by its index
def test_assign_ax_by_index():
    _, Image = _manager()
    Image.create_axes(ncol=2)
    manager = ImageToolsManager(Image.state)
    ax, nax = manager.assign_ax(1, _check=False)
    assert nax == 1
    assert ax is Image.ax[1]
