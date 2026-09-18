"""Test of the image.py file.

The plotting twin of test_load.py and test_loadpart.py, and kept parallel to
them: the shared sections (managers, attribute access, printing, delegation)
hold the same tests under the same names, so no facade is held to a lower
standard than the others. What only an Image has -- the figure keywords, the
signature checks, oplotbox -- sits in sections of its own.

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

Some tests build a real Image and some replace its managers with the stub in
helper_all.py. The rule of thumb is that anything checking the *figure*
needs real managers, while anything checking *which manager answered* is
better off with a stub, which cannot draw and so cannot be slow or flaky.
"""

import inspect
import logging
import re
from collections.abc import Callable

import matplotlib.pyplot as plt
import pytest
from helper_all import DummyManager
from helper_image import DELEGATION, MANAGERS, NOT_DELEGATED

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
    """Replace the managers with stubs, for one test only.

    monkeypatch undoes the replacement when the test ends, so this cannot
    leak into anything else. The stubs make the tests that use it fast and
    figure-free: DummyManager answers any method with its own name, so the
    test can see which one was called without anything being drawn.

    The state stays real. ImageState is a plain dataclass that builds no
    figure, so there is nothing to gain from a stand-in, and a stand-in would
    be one more thing that could drift from the class it imitates.
    """
    for name in MANAGERS:
        monkeypatch.setattr(image_mod, name, DummyManager)


# ---- Managers ----
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

    The managers are looked for on the *state*, not on the image: they are
    assigned in `__init__` as `self.XManager = ...`, and `__setattr__`
    forwards every assignment but "state" itself, so that is where they end
    up.
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


# ---- Attribute access ----
def test_attribute_reads_and_writes_the_state() -> None:
    """Set a name on the state, read it off the image, and the reverse.

    The forwarding that makes the facade transparent: everything a user sets
    on the Image is stored where the sixteen managers read from.
    """
    img = pp.Image(text=False)
    setattr(img.state, "custom_attr", 123)  # noqa: B010
    assert img.custom_attr == 123
    img.custom_attr = 456
    assert getattr(img.state, "custom_attr") == 456  # noqa: B009


def test_unknown_attribute_raises() -> None:
    """Read a name nothing ever set, and expect AttributeError.

    Reaching through to the state must not turn a missing name into None, or
    a misspelled attribute would read as empty rather than as a mistake.
    """
    img = pp.Image(text=False)
    with pytest.raises(AttributeError):
        img.wrong  # noqa: B018


@pytest.mark.usefixtures("dummy_managers")
def test_replaced_state_receives_assignments() -> None:
    """Swap the state through the facade, then assign a name on the image.

    `__setattr__` has one exception, the name "state": it is stored on the
    Image itself instead of being forwarded, which is the path taken by the
    first line of `__init__`. Every other name goes to whatever the state is
    *now*, so after the swap a new name must land on the new state and not
    on the Image.

    `vars()` rather than attribute access: it reads the instance dictionary
    directly, so the value cannot be found by some other route. A failure on
    the first assert means "state" was forwarded instead of kept (the state
    would try to hold itself); on the others, that assignments no longer
    reach the state the managers read from.
    """
    img = image_mod.Image(text=False)
    new_state = ImageState()

    img.state = new_state
    assert vars(img)["state"] is new_state

    img.new_field = 42
    assert vars(new_state).get("new_field") == 42
    assert "new_field" not in vars(img)


# ---- Printing ----
def test_repr_shows_the_state() -> None:
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


def test_str_describes_the_image() -> None:
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


def test_str_properties_exist() -> None:
    """Read the property names out of the description and check each exists.

    The same check as the test above, for the other section that names
    attributes: "Image properties:" gives each line a name in brackets, and
    "Number of subplots" names two, `(nrow0 x ncol0)`. A renamed field would
    leave the old name advertised here with nothing to say so.

    The pattern wants a space before the bracket, so words such as "time(s)"
    in the load facades' twin of this test are not read as names.
    """
    img = pp.Image(text=False)
    section = str(img).split("Image properties:")[1]
    section = section.split("Public methods available:")[0]
    names = [
        name
        for pair in re.findall(r"\s\((\w+)(?: x (\w+))?\)", section)
        for name in pair
        if name
    ]
    assert names
    for name in names:
        assert hasattr(img, name), name


# ---- Construction ----
def test_default_builds_state_and_figure_manager() -> None:
    """Build an image with no arguments and check what it is made of.

    The simplest possible construction, and the one that would fail first if
    the constructor stopped building either the state or the figure manager.
    """
    img = pp.Image(text=False)
    assert isinstance(img.state, ImageState)
    assert isinstance(img.FigureManager, FigureManager)


def test_figure_and_style_keywords_reach_the_state() -> None:
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


def test_tight_keyword_reaches_matplotlib() -> None:
    """Pass tight=False and check matplotlib actually received it.

    Unlike the test above this reads the answer off the *figure* rather than
    off the state, so it checks the setting reached matplotlib rather than
    merely being recorded.
    """
    img = pp.Image(tight=False, text=False)
    assert img.fig is not None
    assert img.fig.get_tight_layout() is False


def test_fontweight_defaults_to_normal() -> None:
    """Build an image without the keyword and check the default weight.

    fontweight used to be advertised by `__str__` but never stored anywhere,
    so it silently did nothing. It now lives on the state like fontsize, and
    this test and the next are what keep it there.
    """
    assert pp.Image(text=False).fontweight == "normal"


def test_fontweight_keyword_is_stored() -> None:
    """Pass a font weight and find it on the state and on the image.

    The other half of the pair above: the default exists and a choice is
    honoured.
    """
    img = pp.Image(fontweight="bold", text=False)
    assert img.state.fontweight == "bold"
    assert img.fontweight == "bold"


def test_unknown_keyword_warns() -> None:
    """Pass a keyword nothing reads and check the user is told.

    This is track_kwargs working end to end through a real constructor: the
    whole point is that a misspelled keyword says so instead of being
    silently ignored. See utils/inspector.py.
    """
    with pytest.warns(UserWarning, match=r"Unused kwargs: \{'attr'\}"):
        pp.Image(attr=None)  # pyright: ignore[reportCallIssue]


# ---- Logging ----
@pytest.mark.parametrize(
    ("text", "logged"), [(None, True), (True, True), (False, False)]
)
def test_text_logs_the_window(
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


# ---- Delegation to the managers ----
def test_every_method_is_listed() -> None:
    """Compare the public methods Image defines with the tables in the helper.

    Adding, removing or renaming a method fails here until DELEGATION or
    NOT_DELEGATED is updated, so no method can go untested.

    The five tests below that are parametrized from DELEGATION would
    otherwise skip a missing method with nothing to say so: its wiring, its
    arguments, its signature and its documentation would all go unchecked.
    """
    public = {
        name
        for name, attribute in vars(Image).items()
        if callable(attribute) and not name.startswith("_")
    }
    listed = set(DELEGATION) | NOT_DELEGATED
    missing, stale = public - listed, listed - public
    assert not missing, (
        f"in neither DELEGATION nor NOT_DELEGATED, so untested: "
        f"{sorted(missing)}"
    )
    assert not stale, (
        f"listed in DELEGATION or NOT_DELEGATED but no longer an Image "
        f"method: {sorted(stale)}"
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
def test_signature_matches_the_manager(method: str, manager: str) -> None:
    """Compare the signature of one facade method with its manager's.

    test_delegation passes every parameter explicitly, so it cannot see a
    facade and a manager that *disagree* about their parameters. This test
    compares the two signatures directly: the same names, in the same order,
    of the same kind, with the same defaults.

    Each part guards a quiet failure. A parameter the facade does not declare
    still works at runtime, because it falls into **kwargs and is forwarded,
    but the type checkers reject it and `help()` does not show it -- this is
    how `interactive` lost `ax`. The order matters because a user may pass by
    position: `interactive` once had `_check` where the manager has `limfix`,
    so a third positional argument silently switched off the kwargs check. A
    different default means the facade and the manager behave differently
    when the same call is made on each.

    Annotations are not compared: they are strings under `from __future__
    import annotations`, and the facade may legitimately spell a type
    differently. The manager is unwrapped because track_kwargs replaces its
    signature with one that hides _check.
    """

    def shape(func: Callable[..., object]) -> list[tuple[str, object, object]]:
        """Reduce a signature to the name, kind and default of each part."""
        params = inspect.signature(func).parameters.values()
        return [(p.name, p.kind, p.default) for p in params if p.name != "self"]

    facade = shape(getattr(Image, method))
    real = shape(inspect.unwrap(getattr(getattr(image_mod, manager), method)))
    assert facade == real, f"\nfacade:  {facade}\nmanager: {real}"


@pytest.mark.usefixtures("dummy_managers")
@pytest.mark.parametrize(("method", "manager"), DELEGATION.items())
def test_required_arguments_reach_the_manager(
    method: str, manager: str
) -> None:
    """Call one facade method with its required arguments only.

    The counterpart of test_delegation, which passes everything: here the
    facade has to fill in every optional parameter from its own defaults and
    still reach the manager. A facade that needed an argument its manager
    does not, or broke on one of its own defaults before forwarding, fails
    here.

    The managers are stubs, so nothing is drawn and a required argument can
    be any object. DummyManager returns the name of the method it was asked
    for, so the result says which method answered; the manager is read back
    off the image to check the call went through the stub the facade holds.
    """
    img = image_mod.Image(text=False)
    params = inspect.signature(getattr(Image, method)).parameters.values()
    required = {
        p.name: object()
        for p in params
        if p.name != "self"
        and p.default is p.empty
        and p.kind not in (p.VAR_POSITIONAL, p.VAR_KEYWORD)
    }
    assert isinstance(getattr(img, manager), DummyManager)
    assert getattr(img, method)(**required) == method


@pytest.mark.parametrize(("method", "manager"), DELEGATION.items())
def test_docstring_is_copied(method: str, manager: str) -> None:
    """Compare the docstring of the facade method with the manager's.

    Each facade method carries a one-line placeholder in the source, replaced
    at class creation by `method.__doc__ = Manager.method.__doc__`. Without
    that line, `help(I.plot)` would show "Plot method." instead of the real
    documentation, and the keywords would be documented nowhere a user can
    reach.

    `assert doc` first, so a manager method that lost its own docstring fails
    as itself rather than as a mismatch between two empty strings.
    """
    doc = getattr(getattr(image_mod, manager), method).__doc__
    assert doc
    assert getattr(Image, method).__doc__ == doc


# ---- Not delegated ----
def test_oplotbox_calls_the_amr_function(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
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
