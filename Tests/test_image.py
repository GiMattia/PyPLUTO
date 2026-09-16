"""Test of the image.py file.

The plotting twin of test_load.py and test_loadpart.py, and kept parallel to
them: the same tests in the same order, so no facade is held to a lower
standard than the others.

Image implements almost nothing -- it builds a state, builds sixteen managers
on it, and hands every public call to one of them -- so these tests are about
the wiring rather than about drawing. The failures they are aimed at are
quiet: a method wired to the wrong manager, a manager built on a state of its
own, an argument dropped between facade and manager, a `__str__` describing a
class that has since changed.

That last one is not hypothetical. `__str__` here once advertised `tg` for
`tight` and a `fontweight` that was never stored, and omitted three methods
that did exist; the two tests that check it in both directions were written
for that.

Some tests build a real Image and some use the stubs in helper_all.py and
helper_image.py. The rule of thumb is that anything checking the *figure*
needs a real one, while anything checking *which manager answered* is better
off with a stub, which cannot draw and so cannot be slow or flaky.
"""

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
    """Replace the managers and the state with stubs, for one test only.

    monkeypatch undoes the replacement when the test ends, so this cannot
    leak into anything else. The stubs make the tests that use it fast and
    figure-free: DummyManager answers any method with its own name, so the
    test can see which one was called without anything being drawn.
    """
    for name in MANAGERS:
        monkeypatch.setattr(image_mod, name, DummyManager)
    monkeypatch.setattr(image_mod, "ImageState", lambda *a, **kw: DummyState())


# ---- Construction ----
def test_default_initialization() -> None:
    """Build an image with no arguments and check what it is made of.

    The simplest possible construction, and the one that would fail first if
    the constructor stopped building either the state or the figure manager.
    """
    img = pp.Image(text=False)
    assert isinstance(img.state, ImageState)
    assert isinstance(img.FigureManager, FigureManager)


def test_custom_arguments() -> None:
    """Pass a figure and a style and find both on the state and the image.

    Two things at once: the constructor honours what it was given, and the
    value is readable through the facade as well as off the state, which is
    the mixin property doing its job.
    """
    fig = plt.figure()
    img = pp.Image(fig=fig, style="dark_background", text=False)
    assert img.state.fig is fig
    assert img.state.style == "dark_background"
    assert img.style == "dark_background"


def test_tight_layout() -> None:
    """Pass tight=False and check matplotlib actually received it.

    Unlike the test above this reads the answer off the *figure* rather than
    off the state, so it checks the setting reached matplotlib rather than
    merely being recorded.
    """
    img = pp.Image(tight=False, text=False)
    assert img.fig is not None
    assert img.fig.get_tight_layout() is False


def test_fontweight_default() -> None:
    """Build an image without the keyword and check the default weight.

    fontweight used to be advertised by `__str__` but never stored anywhere,
    so it silently did nothing. It now lives on the state like fontsize, and
    these two tests are what keep it there.
    """
    assert pp.Image(text=False).fontweight == "normal"


def test_fontweight_given() -> None:
    """Pass a font weight and find it on the state and on the image.

    The other half of the pair above: the default exists and a choice is
    honoured.
    """
    img = pp.Image(fontweight="bold", text=False)
    assert img.state.fontweight == "bold"
    assert img.fontweight == "bold"


@pytest.mark.parametrize(("name"), MANAGERS)
def test_managers_share_the_state(name: str) -> None:
    """Check one manager holds the same state object as the image itself.

    `is` rather than equality: two states with the same contents would pass
    an equality check and still be two objects.

    A manager with a separate state would draw on a different figure, or read
    stale settings, without any error.
    """
    img = pp.Image(text=False)
    assert getattr(img, name).state is img.state


def test_every_manager_is_listed() -> None:
    """Compare the managers Image builds with the list in the helper.

    The test above is parametrized from that list, so a manager missing from
    it would never be checked for sharing the state. Sixteen is enough that
    one going unnoticed is a real possibility.
    """
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
    """Pass a keyword nothing reads and check the user is told.

    This is track_kwargs working end to end through a real constructor: the
    whole point is that a misspelled keyword says so instead of being
    silently ignored. See utils/inspector.py.
    """
    with pytest.warns(UserWarning, match=r"Unused kwargs: \{'attr'\}"):
        pp.Image(attr=None)  # pyright: ignore[reportCallIssue]


@pytest.mark.parametrize(
    ("text", "logged"), [(None, True), (True, True), (False, False)]
)
def test_Image_prints_message(
    caplog: pytest.LogCaptureFixture, text: bool | None, logged: bool
) -> None:
    """Build an image at each verbosity and check whether it logged.

    Three cases in one test: the default and True both print the creation
    line, False silences it. A user who asked for quiet and got output would
    have no way to stop it.
    """
    with caplog.at_level(logging.INFO):
        pp.Image(text=text)
    assert ("Image class created at nwin" in caplog.text) is logged


# ---- Attribute access ----
def test_attribute_get_existing() -> None:
    """Set a name on the state, read it off the image, and the reverse.

    The forwarding that makes the facade transparent: everything a user sets
    on the Image is stored where the sixteen managers read from.
    """
    img = pp.Image(text=False)
    setattr(img.state, "custom_attr", 123)  # noqa: B010
    assert img.custom_attr == 123
    img.custom_attr = 456
    assert getattr(img.state, "custom_attr") == 456  # noqa: B009


def test_getattr_new() -> None:
    """Read a name nothing ever set, and expect AttributeError.

    Reaching through to the state must not turn a missing name into None, or
    a misspelled attribute would read as empty rather than as a mistake.
    """
    img = pp.Image(text=False)
    with pytest.raises(AttributeError):
        img.wrong  # noqa: B018


# ---- Printing ----
def test_repr_default() -> None:
    """Compare the repr of a default image with the exact expected text.

    An exact match rather than a substring, because the repr is short enough
    to state in full, and it is what a user sees at the prompt.
    """
    assert repr(pp.Image(text=False)) == "Image(nwin=1, figsize=[8.0, 5.0])"


def test_repr_follows_the_state() -> None:
    """Build an image with non-default settings and check the repr follows.

    The counterpart of the test above: a repr that printed the defaults
    regardless would pass that one and be useless here.
    """
    img = pp.Image(nwin=3, figsize=[4.0, 3.0], text=False)
    assert repr(img) == "Image(nwin=3, figsize=[4.0, 3.0])"


def test_str() -> None:
    """Print the description and check its sections and some of its lines.

    `__str__` here carries a line of prose per method, unlike the load
    facades, so this checks a couple of those lines survive as well as the
    section headings. The two tests below check the description against the
    class in both directions.
    """
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
    """Look for one public method in the description, one test per method.

    Parametrized over DELEGATION, so a method added to the class fails here
    until it is also advertised. This is the test that caught `__str__`
    omitting animate, showgrid and volume.
    """
    assert f"- {method}\n" in str(pp.Image(text=False))


def test_str_attributes_exist() -> None:
    """Read the attribute names out of the description and check each exists.

    The other direction: not "is every method listed" but "is everything
    listed real". This is what caught `tg` being advertised for `tight`, and
    a `fontweight` that was described but never stored.
    """
    img = pp.Image(text=False)
    section = str(img).split("Public attributes available:")[1]
    names = re.findall(r"- (\w+)", section.split("Please do not")[0])
    assert names
    for name in names:
        assert hasattr(img, name), name


# ---- Delegation to the managers ----
def test_every_method_is_listed() -> None:
    """Compare the public methods Image defines with the helper tables.

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
    """Call one facade method and check the manager received it intact.

    The strongest test in the file, and the one that would catch a facade
    method quietly dropping or reordering an argument -- which produces a
    wrong plot rather than an error, since most of these parameters are
    optional.

    It works by replacing the manager's method with a recorder, calling the
    facade, then binding what was recorded against the manager's real
    signature. Binding is what makes the check independent of *how* the
    facade passes things: by position or by keyword, the argument has to land
    on the parameter of the same name.

    Each argument is a fresh object(), so an argument that ended up on the
    wrong parameter cannot coincidentally look right. An extra keyword checks
    that **kwargs are forwarded too, and the return value is the same object
    the manager produced, so the facade is not post-processing anything.

    The manager signature is unwrapped because track_kwargs replaces it with
    one that hides _check, and binding needs the real one.
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
    """Compare the docstring of the facade method with the manager's.

    Each facade method carries a one-line placeholder in the source, replaced
    at class creation by `method.__doc__ = Manager.method.__doc__`. Without
    that line, `help(I.plot)` would show "Plot method." instead of the real
    documentation, and the keywords would be documented nowhere a user can
    reach.
    """
    doc = getattr(getattr(image_mod, manager), method).__doc__
    assert doc
    assert getattr(Image, method).__doc__ == doc


def test_oplotbox(monkeypatch: pytest.MonkeyPatch) -> None:
    """Call oplotbox and check it reached the AMR function, not a manager.

    The one public method that is not delegation: it calls a module function
    and passes the image itself as the first argument. It is listed in
    NOT_DELEGATED rather than in DELEGATION for that reason, and this test is
    what keeps that exception honest.

    The `_check=False` in the expected kwargs is track_kwargs being told this
    is not the outermost call.
    """
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
    """Replace the state outright and check assignments still forward to it.

    `__setattr__` treats the name "state" as its one exception, and
    `object.__setattr__` is used here to bypass the facade entirely and put a
    stub in place. What follows checks the forwarding still works afterwards,
    which is the path taken by the very first line of `__init__`.
    """
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
    """Call a facade method against a stubbed manager and see which answered.

    DummyManager returns the name of whatever method was called, so the
    assertion is that the name comes back: the facade reached the method it
    meant to. Cheaper than test_delegation and covering a different thing --
    that the call arrives at all, with no figure in the way.
    """
    img = image_mod.Image(text=False)
    result = getattr(img, attr)()
    assert result == attr


@pytest.mark.usefixtures("dummy_managers")
def test_text_delegation() -> None:
    """Call text against a stubbed manager, which needs its argument named.

    Separate from the parametrized test above only because `text` will not
    accept an empty call: it needs the text itself.
    """
    img = image_mod.Image(text=False)
    result = img.text(text="hello")
    assert result == "text"
