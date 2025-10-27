import pytest

import pyPLUTO.image as image_mod
import pyPLUTO.imagemixin as mixin_mod


# ---- Minimal stubs ----
class DummyManager:
    def __init__(self, *_a, **_kw): ...
    def __getattr__(self, name):
        return lambda *a, **kw: name


class DummyState:
    def __init__(self):
        self.ax = []
        self.LaTeX = False
        self.style = "old"
        self.legpar = []
        self.legpos = "right"
        self.nline = 3
        self.nwin = 9
        self.ncol0 = 1
        self.ntext = 0
        self.nrow0 = 1
        self.tight = True
        self.vlims = (0, 1)
        self.xscale = "linear"
        self.yscale = "linear"
        self.setax = []
        self.setay = []
        self.shade = []
        self.tickspar = []


@pytest.fixture(autouse=True)
def patch_all(monkeypatch):
    # replace all managers with simple stubs
    for name in [
        "FigureManager",
        "AxisManager",
        "ColorbarManager",
        "ContourManager",
        "CreateAxesManager",
        "DisplayManager",
        "ImageToolsManager",
        "InteractiveManager",
        "LegendManager",
        "PlotManager",
        "RangeManager",
        "ScatterManager",
        "StreamplotManager",
        "ZoomManager",
    ]:
        monkeypatch.setattr(image_mod, name, DummyManager)
    monkeypatch.setattr(image_mod, "ImageState", lambda *a, **kw: DummyState())


# ------------------------------
# image.py missing lines only
# ------------------------------


def test_init_exit_branch(monkeypatch):
    """Covers the 'exit' path when setting 'state' before it's defined."""
    img = image_mod.Image(text=False)
    # explicitly trigger first 'if name=="state"' branch
    object.__setattr__(img, "state", DummyState())
    img.state.new_field = 42
    assert img.state.new_field == 42


@pytest.mark.parametrize(
    "attr",
    [
        "colorbar",
        "contour",
        "create_axes",
        "display",
        "interactive",
        "legend",
        "plot",
        "savefig",
        "scatter",
        "set_axis",
        "show",
        "text",
        "streamplot",
        "zoom",
    ],
)
def test_property_delegation(attr):
    """Each property returns a callable from the dummy manager."""
    img = image_mod.Image(text=False)
    result = getattr(img, attr)()
    assert result == attr


# ------------------------------
# imagemixin.py missing lines
# ------------------------------


def test_selected_mixin_properties():
    class M(mixin_mod.ImageMixin):
        def __init__(self):
            self.state = DummyState()

    m = M()

    # Only touch the specific missing lines
    m.style = "newstyle"
    assert m.style == "newstyle"

    m.legpos = "left"
    assert m.legpos == "left"

    m.nline = 7
    assert m.nline == 7

    m.ncol0 = 2
    assert m.ncol0 == 2

    m.ntext = 5
    assert m.ntext == 5

    m.nrow0 = 9
    assert m.nrow0 == 9

    m.tight = False
    assert m.tight is False

    m.vlims = (1, 2)
    assert m.vlims == (1, 2)

    m.xscale = "log"
    assert m.xscale == "log"

    m.yscale = "log"
    assert m.yscale == "log"

    m.ax = ["ax1", "ax2"]
    assert m.ax == ["ax1", "ax2"]

    m.legpar = [[0.1, 0.2], [0.3, 0.4]]
    assert m.legpar == [[0.1, 0.2], [0.3, 0.4]]

    m.setax = [0, 1]
    assert m.setax == [0, 1]

    m.setay = [2, 3]
    assert m.setay == [2, 3]

    m.shade = ["shade1", "shade2"]
    assert m.shade == ["shade1", "shade2"]

    m.tickspar = [5, 10]
    assert m.tickspar == [5, 10]
