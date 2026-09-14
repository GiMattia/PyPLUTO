"""Test of the image.py file."""

import inspect
import logging
import re

import matplotlib.pyplot as plt
import pytest
from helper_all import DummyManager
from helper_image import DELEGATION, MANAGERS, NOT_DELEGATED, DummyState

import pyPLUTO as pp
import pyPLUTO.image as image_mod
from pyPLUTO.image import Image
from pyPLUTO.imagefuncs.figure import FigureManager
from pyPLUTO.imagestate import ImageState

# The hand-written tables live in helper_image.py: DELEGATION maps each facade
# method to the manager it hands the call to, NOT_DELEGATED lists the public
# methods that are not facades, and MANAGERS lists the managers that
# Image.__init__ builds on the shared state.


@pytest.fixture
def dummy_managers(monkeypatch: pytest.MonkeyPatch) -> None:
    """Replace the managers and the state with stubs, for one test only."""
    for name in MANAGERS:
        monkeypatch.setattr(image_mod, name, DummyManager)
    monkeypatch.setattr(image_mod, "ImageState", lambda *a, **kw: DummyState())


# ---- Construction ----
def test_default_initialization() -> None:
    """Build an image with its own state and figure manager."""
    img = pp.Image(text=False)
    assert isinstance(img.state, ImageState)
    assert isinstance(img.FigureManager, FigureManager)


def test_custom_arguments() -> None:
    """Keep a given figure and style on the state, readable from the image."""
    fig = plt.figure()
    img = pp.Image(fig=fig, style="dark_background", text=False)
    assert img.state.fig is fig
    assert img.state.style == "dark_background"
    assert img.style == "dark_background"


def test_tight_layout() -> None:
    """Pass the tight option on to the figure."""
    img = pp.Image(tight=False, text=False)
    assert img.fig is not None
    assert img.fig.get_tight_layout() is False


def test_fontweight_default() -> None:
    """Store the default font weight on the state."""
    assert pp.Image(text=False).fontweight == "normal"


def test_fontweight_given() -> None:
    """Store a given font weight on the state, readable from the image."""
    img = pp.Image(fontweight="bold", text=False)
    assert img.state.fontweight == "bold"
    assert img.fontweight == "bold"


@pytest.mark.parametrize(("name"), MANAGERS)
def test_managers_share_the_state(name: str) -> None:
    """Build every manager on the image's own state.

    A manager with a separate state would draw on a different figure, or read
    stale settings, without any error.
    """
    img = pp.Image(text=False)
    assert getattr(img, name).state is img.state


def test_every_manager_is_listed() -> None:
    """Keep MANAGERS in sync with the managers Image.__init__ builds."""
    img = pp.Image(text=False)
    built = {name for name in vars(img.state) if name.endswith("Manager")}
    missing, stale = built - set(MANAGERS), set(MANAGERS) - built
    assert not missing, (
        f"not listed in MANAGERS, so untested: {sorted(missing)}"
    )
    assert not stale, (
        f"listed in MANAGERS but no longer built by Image.__init__: "
        f"{sorted(stale)}"
    )


def test_warn_attr() -> None:
    """Warn about a keyword argument that Image does not know."""
    with pytest.warns(UserWarning, match=r"Unused kwargs: \{'attr'\}"):
        pp.Image(attr=None)  # pyright: ignore[reportCallIssue]


@pytest.mark.parametrize(
    ("text", "logged"), [(None, True), (True, True), (False, False)]
)
def test_Image_prints_message(
    caplog: pytest.LogCaptureFixture, text: bool | None, logged: bool
) -> None:
    """Log the window number unless text=False silences the output."""
    with caplog.at_level(logging.INFO):
        pp.Image(text=text)
    assert ("Image class created at nwin" in caplog.text) is logged


# ---- Attribute access ----
def test_attribute_get_existing() -> None:
    """Read and write the image attributes through the state."""
    img = pp.Image(text=False)
    setattr(img.state, "custom_attr", 123)  # noqa: B010
    assert img.custom_attr == 123
    img.custom_attr = 456
    assert getattr(img.state, "custom_attr") == 456  # noqa: B009


def test_getattr_new() -> None:
    """Raise AttributeError for an attribute the state does not have."""
    img = pp.Image(text=False)
    with pytest.raises(AttributeError):
        img.wrong  # noqa: B018


# ---- Printing ----
def test_repr_default() -> None:
    """Show the window number and the figure size."""
    assert repr(pp.Image(text=False)) == "Image(nwin=1, figsize=[8.0, 5.0])"


def test_repr_follows_the_state() -> None:
    """Show the actual window number and figure size, not the defaults."""
    img = pp.Image(nwin=3, figsize=[4.0, 3.0], text=False)
    assert repr(img) == "Image(nwin=3, figsize=[4.0, 3.0])"


def test_str() -> None:
    """Describe the class, its public methods and its public attributes."""
    s = str(pp.Image(text=False))
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


@pytest.mark.parametrize("method", DELEGATION)
def test_str_lists_every_method(method: str) -> None:
    """List every public method in the description, so it cannot go stale."""
    assert f"- {method}\n" in str(pp.Image(text=False))


def test_str_attributes_exist() -> None:
    """Advertise only attributes that the image really has."""
    img = pp.Image(text=False)
    section = str(img).split("Public attributes available:")[1]
    names = re.findall(r"- (\w+)", section.split("Please do not")[0])
    assert names
    for name in names:
        assert hasattr(img, name), name


# ---- Delegation to the managers ----
def test_every_method_is_listed() -> None:
    """Keep DELEGATION in sync with the public methods Image defines.

    Adding, removing or renaming a method fails here until the table above is
    updated, so no method can go untested.
    """
    public = {
        name
        for name, attribute in vars(Image).items()
        if callable(attribute) and not name.startswith("_")
    }
    listed = set(DELEGATION) | NOT_DELEGATED
    missing, stale = public - listed, listed - public
    assert not missing, (
        f"not listed in DELEGATION, so untested: {sorted(missing)}"
    )
    assert not stale, (
        f"listed in DELEGATION but no longer an Image method: {sorted(stale)}"
    )


@pytest.mark.parametrize(("method", "manager"), DELEGATION.items())
def test_delegation(
    method: str, manager: str, monkeypatch: pytest.MonkeyPatch
) -> None:
    """Hand every argument to the right manager and return its result.

    Each argument is a fresh object(), and must arrive at the manager's
    parameter with the same name, whether the facade passes it by position or
    by keyword. An extra keyword checks that **kwargs are forwarded too. The
    manager signature is unwrapped because track_kwargs hides _check from it.

    LONG TEST: CHECK
    """
    img = pp.Image(text=False)
    target = getattr(img, manager)
    calls: list[tuple[tuple[object, ...], dict[str, object]]] = []
    result = object()

    def record(*args: object, **kwargs: object) -> object:
        calls.append((args, kwargs))
        return result

    monkeypatch.setattr(target, method, record)

    params = inspect.signature(getattr(Image, method)).parameters.values()
    sent = {
        p.name: object()
        for p in params
        if p.name != "self" and p.kind is not p.VAR_KEYWORD
    }
    extra = (
        {"extra": object()}
        if any(p.kind is p.VAR_KEYWORD for p in params)
        else {}
    )

    assert getattr(img, method)(**sent, **extra) is result

    ((args, kwargs),) = calls
    signature = inspect.signature(inspect.unwrap(getattr(type(target), method)))
    received = signature.bind(None, *args, **kwargs).arguments
    var_kw = next(
        (
            p.name
            for p in signature.parameters.values()
            if p.kind is p.VAR_KEYWORD
        ),
        None,
    )
    forwarded = received.pop(var_kw, {}) if var_kw else {}
    for name, value in sent.items():
        assert received[name] is value, name
    for name, value in extra.items():
        assert forwarded[name] is value, name


@pytest.mark.parametrize(("method", "manager"), DELEGATION.items())
def test_docstring_is_copied(method: str, manager: str) -> None:
    """Show the manager's documentation on the facade method."""
    doc = getattr(getattr(image_mod, manager), method).__doc__
    assert doc
    assert getattr(Image, method).__doc__ == doc


def test_oplotbox(monkeypatch: pytest.MonkeyPatch) -> None:
    """Hand oplotbox to the AMR module function, with the image and the args."""
    calls: list[tuple[tuple[object, ...], dict[str, object]]] = []
    monkeypatch.setattr(
        image_mod, "oplotbox", lambda *a, **k: calls.append((a, k))
    )
    img = pp.Image(text=False)
    img.oplotbox([1, 2, 3], [4, 5, 6])
    ((args, kwargs),) = calls
    assert args[0] is img
    assert args[1:] == ([1, 2, 3], [4, 5, 6])
    assert kwargs == {"_check": False}


# ---- Moved from test_imagemixin.py ----
@pytest.mark.usefixtures("dummy_managers")
def test_init_exit_branch() -> None:
    """Covers the 'exit' path when setting 'state' before it's defined."""
    img = image_mod.Image(text=False)
    # explicitly trigger first 'if name=="state"' branch
    object.__setattr__(img, "state", DummyState())
    img.state.new_field = 42  # pyright: ignore[reportAttributeAccessIssue]  # ty: ignore[unresolved-attribute]
    assert img.state.new_field == 42  # pyright: ignore[reportAttributeAccessIssue]  # ty: ignore[unresolved-attribute]


@pytest.mark.usefixtures("dummy_managers")
@pytest.mark.parametrize(
    "attr",
    [
        "colorbar",
        "create_axes",
        "legend",
        "savefig",
        "set_axis",
        "zoom",
    ],
)
def test_property_delegation(attr: str) -> None:
    """Each property returns a callable from the dummy manager."""
    img = image_mod.Image(text=False)
    result = getattr(img, attr)()
    assert result == attr


@pytest.mark.usefixtures("dummy_managers")
def test_text_delegation() -> None:
    """text delegates to the manager (requires a positional text argument)."""
    img = image_mod.Image(text=False)
    result = img.text(text="hello")
    assert result == "text"
