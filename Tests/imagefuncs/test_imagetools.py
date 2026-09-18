"""Test of the imagetools.py file.

ImageToolsManager is the helper the other image managers are built on: each of
them holds one, and every plotting call starts by asking `assign_ax` which
axis to draw on. So a fault here surfaces far from this file, as a plot drawn
on the wrong axis or a colormap silently replaced, and these tests are the
only ones that check its pieces directly.

The colormap lookup is the part that reaches outside the package. It searches
the optional packages in `CMAP_PROVIDERS`, of which a machine may have all,
some or none, so the tests never search the real ones: they install fake
provider modules and point `CMAP_PROVIDERS` at those. The one test that uses
the real table asserts only the fallback, which holds either way.

Most tests build a real Image, because what is being checked is a real figure:
which axis was picked, what was drawn on it, what was written to disk.
"""

import sys
from pathlib import Path
from types import ModuleType

import matplotlib
import matplotlib.colors as mcol
import pytest

import pyPLUTO as pp
from pyPLUTO.imagefuncs import imagetools
from pyPLUTO.imagefuncs.imagetools import ImageToolsManager
from pyPLUTO.imagestate import ImageState

# Hand-written expectations. Each colour scale name maps to the matplotlib
# normalization it must produce, and to the attribute that carries the
# threshold: the four scales that use it read it as a different quantity, and
# a scale wired to the wrong normalization would still return a Normalize.
CSCALES: dict[str, tuple[type[mcol.Normalize], str | None]] = {
    "linear": (mcol.Normalize, None),
    "log": (mcol.LogNorm, None),
    "symlog": (mcol.SymLogNorm, "linthresh"),
    "twoslope": (mcol.TwoSlopeNorm, "vcenter"),
    "2slope": (mcol.TwoSlopeNorm, "vcenter"),
    "power": (mcol.PowerNorm, "gamma"),
    "asinh": (mcol.AsinhNorm, "linear_width"),
}


def _image() -> pp.Image:
    """Build a quiet image, the starting point of nearly every test here.

    text=False keeps the creation line out of the captured log: the managers
    are what is under test, not the greeting.
    """
    return pp.Image(text=False)


def _manager() -> tuple[ImageToolsManager, pp.Image]:
    """Build an image and a manager reading the same state.

    The manager an Image already holds would do just as well; building one
    explicitly is what the other imagefuncs managers do, and it keeps the
    tests honest about which object they are calling.
    """
    image = _image()
    return ImageToolsManager(image.state), image


def _stateless_manager() -> ImageToolsManager:
    """Build a manager on a fresh state, so it has no figure.

    ImageState starts with `fig` set to None, which is the "no figure yet"
    case each of the three guards below is written for.
    """
    return ImageToolsManager(ImageState())


def _fake_module(name: str, **attributes: object) -> ModuleType:
    """Build a module object carrying the given attributes.

    Used both for a fake package and for the attribute a package keeps its
    colormaps on, which is a module of its own in cmocean and seaborn.
    """
    fake = ModuleType(name)
    for attribute, value in attributes.items():
        setattr(fake, attribute, value)
    return fake


def _fake_provider(
    monkeypatch: pytest.MonkeyPatch,
    module: str,
    **attributes: object,
) -> ModuleType:
    """Install a fake colormap package for the duration of one test.

    A module put into sys.modules is what `importlib.import_module` finds, so
    find_cmap imports it without anything being installed. monkeypatch removes
    it again when the test ends.

    The tests that use this also repoint CMAP_PROVIDERS at their fakes, so no
    result depends on which real colormap packages the machine has.
    """
    fake = _fake_module(module, **attributes)
    monkeypatch.setitem(sys.modules, module, fake)
    return fake


def _cmap(name: str) -> mcol.ListedColormap:
    """Build a two-colour colormap, red first, so reversal is visible.

    Reversing it puts blue at 0.0, which is what the reversal tests assert on:
    a colormap returned unreversed cannot pass by having the right name alone.
    """
    return mcol.ListedColormap(["red", "blue"], name=name)


# ---- Colour scales ----
@pytest.mark.parametrize(("cscale", "expected"), CSCALES.items())
def test_set_cscale_returns_the_matching_norm(
    cscale: str, expected: tuple[type[mcol.Normalize], str | None]
) -> None:
    """Ask for one colour scale and check the normalization it returns.

    Each scale draws the same data differently, so a scale wired to the wrong
    normalization is a wrong plot with no error. Where the scale uses the
    threshold, the value is checked too: symlog, twoslope, power and asinh
    each read the same argument as a different quantity, and passing it to the
    wrong parameter would go unnoticed by a type check.
    """
    norm_type, threshold_attr = expected
    manager, _ = _manager()
    vmin = 0.1 if cscale == "log" else -1.0

    norm = manager.set_cscale(cscale, vmin, 1.0, 0.5)

    assert isinstance(norm, norm_type)
    if threshold_attr is not None:
        assert getattr(norm, threshold_attr) == 0.5


def test_set_cscale_unknown_scale_warns_and_falls_back() -> None:
    """Ask for a scale nothing defines and check it warns and draws linearly.

    A misspelled scale must not raise in the middle of a plot, so the plot is
    still drawn; without the warning the typo would go unnoticed and the
    figure would silently use the wrong scale.
    """
    manager, _ = _manager()
    with pytest.warns(UserWarning, match="'nosuchscale' not found"):
        norm = manager.set_cscale("nosuchscale", 0.0, 1.0, 0.5)

    assert isinstance(norm, mcol.Normalize)


@pytest.mark.parametrize("cscale", ["linear", "lin", "norm", None])
def test_set_cscale_linear_is_silent(
    cscale: str, recwarn: pytest.WarningsRecorder
) -> None:
    """Ask for the linear scale by any of its names and expect no warning.

    All of these mean the linear scale on purpose, so none may be reported as
    unknown. `norm` is what the managers pass when the user set nothing, and
    `volume` passes None, so warning on either would fire on every plot.
    """
    manager, _ = _manager()
    assert isinstance(manager.set_cscale(cscale, 0.0, 1.0, 0.5), mcol.Normalize)
    assert [str(w.message) for w in recwarn] == []


def test_set_cscale_keeps_the_limits() -> None:
    """Check the limits given are the limits of the returned normalization.

    The scale decides the shape of the mapping, but the two ends are the
    user's: a normalization that lost them would rescale every plot.
    """
    manager, _ = _manager()
    norm = manager.set_cscale("linear", 0.0, 2.0, 0.5)
    assert (norm.vmin, norm.vmax) == (0.0, 2.0)


# ---- Colormaps ----
def test_find_cmap_none_is_returned_unchanged() -> None:
    """Pass None and get None back.

    Three of the four callers pass the user's `cmap` keyword straight through,
    which is None when they did not set one. Turning that into a colormap here
    would override matplotlib's own default for every one of them.
    """
    manager, _ = _manager()
    assert manager.find_cmap(None) is None


def test_find_cmap_colormap_is_returned_unchanged() -> None:
    """Pass a colormap object and get the same object back.

    A user who built a colormap themselves, or passed `plt.get_cmap(...)`,
    must get exactly it: `is`, not merely one of the same name.
    """
    manager, _ = _manager()
    cmap = _cmap("handmade")
    assert manager.find_cmap(cmap) is cmap


def test_find_cmap_matplotlib_name() -> None:
    """Look up a matplotlib colormap by name.

    The ordinary case, and the one that must cost nothing: it is answered
    before any optional package is imported.
    """
    manager, _ = _manager()
    found = manager.find_cmap("viridis")
    assert found is not None
    assert found.name == "viridis"


def test_find_cmap_matplotlib_reversed_name() -> None:
    """Look up a reversed matplotlib colormap by name.

    matplotlib registers its own reversed colormaps, so `viridis_r` is found
    whole and never reversed by hand here.
    """
    manager, _ = _manager()
    found = manager.find_cmap("viridis_r")
    assert found is not None
    assert found.name == "viridis_r"


def test_find_cmap_from_a_provider_module(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """Find a colormap that only a provider package has.

    The point of the provider list: a name matplotlib does not know is looked
    for in the optional packages rather than being replaced by plasma.
    """
    cmap = _cmap("fakemap")
    _fake_provider(monkeypatch, "fakepkg", fakemap=cmap)
    monkeypatch.setattr(imagetools, "CMAP_PROVIDERS", {"fakepkg": ""})

    manager, _ = _manager()
    assert manager.find_cmap("fakemap") is cmap


def test_find_cmap_from_a_provider_attribute(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """Find a colormap kept on an attribute of the package, not on the module.

    The packages disagree about where their colormaps live -- pastamarkers
    keeps them on `salsa`, cmocean on `cm` -- which is what the value in
    CMAP_PROVIDERS says. A lookup that ignored it would find nothing in either.
    """
    cmap = _cmap("fakemap")
    holder = _fake_module("fakepkg.cm", fakemap=cmap)
    _fake_provider(monkeypatch, "fakepkg", cm=holder)
    monkeypatch.setattr(imagetools, "CMAP_PROVIDERS", {"fakepkg": "cm"})

    manager, _ = _manager()
    assert manager.find_cmap("fakemap") is cmap


def test_find_cmap_reverses_a_provider_colormap(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """Ask for `_r` from a package that ships no reversed colormaps.

    pastamarkers is such a package, and this is the path that reverses the
    base colormap here instead. Checking the colour at 0.0 rather than the
    name: a reversal that returned the original would keep a plausible name.
    """
    _fake_provider(monkeypatch, "fakepkg", fakemap=_cmap("fakemap"))
    monkeypatch.setattr(imagetools, "CMAP_PROVIDERS", {"fakepkg": ""})

    manager, _ = _manager()
    found = manager.find_cmap("fakemap_r")

    assert found is not None
    assert found.name == "fakemap_r"
    assert found(0.0) == mcol.to_rgba("blue")


def test_find_cmap_prefers_the_provider_own_reversed_colormap(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """Ask for `_r` from a package that ships its own reversed colormap.

    The name is looked for as written before anything is reversed here, so a
    package that took care to ship a reversed version is not second-guessed.
    Their colours may differ: a hand reversal only flips the list.
    """
    shipped = _cmap("fakemap_r")
    _fake_provider(
        monkeypatch, "fakepkg", fakemap=_cmap("fakemap"), fakemap_r=shipped
    )
    monkeypatch.setattr(imagetools, "CMAP_PROVIDERS", {"fakepkg": ""})

    manager, _ = _manager()
    assert manager.find_cmap("fakemap_r") is shipped


def test_find_cmap_from_a_provider_that_registers_with_matplotlib(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """Find a colormap a package registers with matplotlib when imported.

    cblind works this way: it exposes no colormap attributes at all, and its
    names exist only once the import has registered them. Looking only at the
    module attributes would find nothing.

    The fake registers on import, as cblind does, and unregisters afterwards
    so matplotlib's registry is left as it was found.
    """
    cmap = _cmap("fakeregistered")
    matplotlib.colormaps.register(cmap)
    monkeypatch.setattr(imagetools, "CMAP_PROVIDERS", {"fakepkg": ""})
    _fake_provider(monkeypatch, "fakepkg")

    manager, _ = _manager()
    try:
        found = manager.find_cmap("fakeregistered")
        assert found is not None
        assert found.name == "fakeregistered"
    finally:
        matplotlib.colormaps.unregister("fakeregistered")


def test_find_cmap_takes_the_first_provider_that_has_the_name(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """Give two packages the same colormap name and check which one wins.

    The order of CMAP_PROVIDERS is the documented tie-break, so this pins it:
    without an order, the same script would draw differently depending on
    which packages happen to be installed.
    """
    first, second = _cmap("first"), _cmap("second")
    _fake_provider(monkeypatch, "fakepkg1", shared=first)
    _fake_provider(monkeypatch, "fakepkg2", shared=second)
    monkeypatch.setattr(
        imagetools, "CMAP_PROVIDERS", {"fakepkg1": "", "fakepkg2": ""}
    )

    manager, _ = _manager()
    assert manager.find_cmap("shared") is first


def test_find_cmap_skips_a_provider_that_is_not_installed(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """List a package nobody has and check the search carries on past it.

    Every provider is optional, so a missing one must be an ordinary outcome
    rather than an ImportError in the middle of a plot.
    """
    cmap = _cmap("fakemap")
    _fake_provider(monkeypatch, "fakepkg", fakemap=cmap)
    monkeypatch.setattr(
        imagetools,
        "CMAP_PROVIDERS",
        {"pypluto_absent_provider": "", "fakepkg": ""},
    )

    manager, _ = _manager()
    assert manager.find_cmap("fakemap") is cmap


def test_find_cmap_skips_a_provider_without_the_expected_attribute(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """Point a provider at an attribute its package does not have.

    A package that reorganises its colormaps must be skipped like a missing
    one, not raise: the entry in CMAP_PROVIDERS is a guess about someone
    else's package, and it can go out of date.
    """
    _fake_provider(monkeypatch, "fakepkg", fakemap=_cmap("fakemap"))
    monkeypatch.setattr(imagetools, "CMAP_PROVIDERS", {"fakepkg": "nosuchattr"})

    manager, _ = _manager()
    with pytest.warns(UserWarning, match="not found"):
        found = manager.find_cmap("fakemap")

    assert found is not None
    assert found.name == "plasma"


def test_find_cmap_ignores_an_attribute_that_is_not_a_colormap(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """Ask for a name that exists in the package but is not a colormap.

    Every attribute answers to getattr, and pastamarkers keeps its colormaps
    on a named tuple, so `find_cmap("count")` used to return its `count`
    method and hand it to matplotlib as a colormap. The result must be the
    plasma fallback, as for any other name the package does not have.
    """
    _fake_provider(monkeypatch, "fakepkg", count=len)
    monkeypatch.setattr(imagetools, "CMAP_PROVIDERS", {"fakepkg": ""})

    manager, _ = _manager()
    with pytest.warns(UserWarning, match="not found"):
        found = manager.find_cmap("count")

    assert found is not None
    assert found.name == "plasma"


def test_find_cmap_unknown_name_warns_and_falls_back() -> None:
    """Ask for a name nothing has, against the real provider list.

    The one test that uses the packages actually installed, so it asserts only
    what holds either way: a warning naming the colormap, and a usable
    colormap back, because a typo must not stop a plot from being drawn.
    """
    manager, _ = _manager()
    with pytest.warns(UserWarning, match="'nosuchcmap' not found"):
        found = manager.find_cmap("nosuchcmap")

    assert found is not None
    assert found.name == "plasma"


# ---- Axis assignment ----
def test_assign_ax_creates_the_first_axis() -> None:
    """Ask for an axis on an empty figure and check one is created.

    This is what makes `I.plot(x, y)` work on a new Image without the user
    creating axes first.
    """
    manager, image = _manager()
    ax, nax = manager.assign_ax(None, _check=False)
    assert nax == 0
    assert ax is image.ax[0]


def test_assign_ax_by_index() -> None:
    """Select an axis by its number and check both what and where it is.

    The index is what a user passes as `ax=1`, and it is also what the return
    value's second half reports, so the two are checked against each other.
    """
    image = _image()
    image.create_axes(ncol=2)
    manager = ImageToolsManager(image.state)

    ax, nax = manager.assign_ax(1, _check=False)

    assert nax == 1
    assert ax is image.ax[1]


def test_assign_ax_none_takes_the_current_axis() -> None:
    """Leave the axis out and check the current one is used.

    A user who selected an axis expects the next plot to land there. The
    current axis is set here to the first of two, so the answer cannot
    coincide with "the last axis" below.
    """
    image = _image()
    image.create_axes(ncol=2)
    assert image.fig is not None
    image.fig.sca(image.ax[0])
    manager = ImageToolsManager(image.state)

    ax, nax = manager.assign_ax(None, _check=False)

    assert nax == 0
    assert ax is image.ax[0]


def test_assign_ax_none_takes_the_last_axis_when_the_current_is_foreign() -> (
    None
):
    """Leave the axis out while the current axis is one the Image never made.

    matplotlib's current axis is figure-wide, so anything drawn on the figure
    can become it -- here an axis added directly. Falling back to the last
    axis the Image knows keeps the plot inside the layout it built.
    """
    image = _image()
    image.create_axes(ncol=2)
    assert image.fig is not None
    image.fig.add_axes((0.1, 0.1, 0.2, 0.2))
    manager = ImageToolsManager(image.state)

    ax, nax = manager.assign_ax(None, _check=False)

    assert nax == 1
    assert ax is image.ax[1]


def test_assign_ax_takes_the_first_of_a_list() -> None:
    """Pass a list of axes and check the first is used.

    create_axes returns a list, so this is what a user gets by passing its
    result straight back in.
    """
    image = _image()
    image.create_axes(ncol=2)
    manager = ImageToolsManager(image.state)

    ax, nax = manager.assign_ax(list(image.ax), _check=False)

    assert nax == 0
    assert ax is image.ax[0]


def test_assign_ax_rejects_an_axis_of_another_figure() -> None:
    """Pass an axis belonging to a different Image and expect a refusal.

    Drawing on it would silently fill a figure the user is not looking at,
    which is worse than an error naming the mistake.
    """
    first, second = _image(), _image()
    other_ax = second.create_axes()
    manager = ImageToolsManager(first.state)

    with pytest.raises(ValueError, match="does not belong"):
        manager.assign_ax(other_ax, _check=False)


def test_assign_ax_rejects_something_that_is_not_an_axis() -> None:
    """Pass a string and expect a refusal.

    The keyword is typed, but nothing stops a plain call, and every later line
    assumes a real axis.
    """
    manager, _ = _manager()
    with pytest.raises(ValueError, match="not valid"):
        manager.assign_ax("nosuchaxis", _check=False)  # pyright: ignore[reportArgumentType]  # ty: ignore[invalid-argument-type]


def test_assign_ax_without_a_figure() -> None:
    """Ask for an axis on a manager whose state has no figure.

    Every manager is built on the state, so one built before the figure --
    or after it was closed -- must say so rather than fail further in.
    """
    with pytest.raises(ValueError, match="No figure is present"):
        _stateless_manager().assign_ax(None, _check=False)


# ---- Hidden text ----
def test_hide_text_hides_the_axis_label() -> None:
    """Hide the label create_axes writes, and check it is marked as hidden.

    Each axis is created carrying its own number as a text, which every plot
    then hides. The flag is what stops it being hidden twice.
    """
    image = _image()
    image.create_axes()
    manager = ImageToolsManager(image.state)
    image.state.ntext[0] = None
    texts = image.ax[0].texts

    manager.hide_text(0, texts)

    assert image.state.ntext[0] == 1
    assert all(not text.get_visible() for text in texts)


def test_hide_text_does_nothing_twice() -> None:
    """Hide the label of an axis already marked as hidden.

    A user's own text goes into the same list, so hiding again once the label
    is gone would make their text disappear instead.
    """
    image = _image()
    image.create_axes()
    manager = ImageToolsManager(image.state)
    image.state.ntext[0] = 1
    own_text = image.ax[0].text(0.5, 0.5, "mine")

    manager.hide_text(0, image.ax[0].texts)

    assert own_text.get_visible()


def test_hide_text_accepts_no_texts() -> None:
    """Call it with no texts at all and check nothing happens.

    An axis may hold none, and the flag must stay untouched so the real label
    is still hidden the first time one appears.
    """
    image = _image()
    image.create_axes()
    manager = ImageToolsManager(image.state)
    image.state.ntext[0] = None

    manager.hide_text(0, None)

    assert image.state.ntext[0] is None


# ---- Text ----
def test_text_is_added_to_the_axis() -> None:
    """Write a text and find it on the axis.

    The plain case: what the user asked for is on the plot.
    """
    image = _image()
    image.plot([0, 1], [0, 1])
    image.text(text="hello", x=0.5, y=0.5)
    assert any(text.get_text() == "hello" for text in image.ax[0].texts)


def test_text_uses_the_given_style() -> None:
    """Write a text with a colour, a size and an alignment, and read them back.

    Each of these is a separate keyword read out of **kwargs, so one of them
    dropped would leave the text drawn in the default style, which is easy to
    miss in a figure.
    """
    image = _image()
    image.plot([0, 1], [0, 1])

    image.text(
        text="styled",
        x=0.5,
        y=0.5,
        c="r",
        textsize=20,
        horalign="center",
        veralign="top",
    )

    written = next(t for t in image.ax[0].texts if t.get_text() == "styled")
    assert written.get_color() == "r"
    assert written.get_fontsize() == 20
    assert written.get_horizontalalignment() == "center"
    assert written.get_verticalalignment() == "top"


@pytest.mark.parametrize("xycoords", ["fraction", "points"])
def test_text_in_axis_coordinates_hides_the_axis_label(xycoords: str) -> None:
    """Write a text inside the axis and check the axis label is hidden.

    Both coordinate systems place the text in the axis, so both hide the
    number create_axes wrote there; the text below, placed on the figure,
    is the one case that does not.
    """
    image = _image()
    image.create_axes()
    image.text(text="inside", x=0.5, y=0.5, xycoords=xycoords)
    assert image.state.ntext[0] == 1


def test_text_in_figure_coordinates_keeps_the_axis_label() -> None:
    """Write a text on the figure and check the axis label is left alone.

    A text placed on the figure is not in any axis, so hiding an axis label
    because of it would remove a label the user can still see.
    """
    image = _image()
    image.create_axes()
    image.text(text="outside", x=0.5, y=0.5, xycoords="figure")
    assert image.state.ntext[0] is None


def test_text_does_not_warn_about_its_own_keywords(
    recwarn: pytest.WarningsRecorder,
) -> None:
    """Write a text with its documented keywords and expect no warning.

    Regression test. `text` called `assign_ax` without marking it as a nested
    call, so the inner call restarted the keyword tracking and reported every
    keyword `text` itself consumes: `I.text("hi", textsize=20)` warned about
    `textsize`, which its own docstring documents.

    recwarn collects whatever is warned rather than requiring a warning, which
    is what lets a test assert that nothing was said.
    """
    image = _image()
    image.plot([0, 1], [0, 1])

    image.text(text="hello", x=0.5, y=0.5, textsize=20, horalign="center")

    assert [str(warning.message) for warning in recwarn] == []


def test_text_warns_about_an_unknown_keyword() -> None:
    """Write a text with a misspelled keyword and check the warning names it.

    The other half of the regression: silencing the spurious warnings must not
    silence the real one. The message has to name `text`, since the same bug
    reported the user's keyword against `assign_ax`, which they never called.
    """
    image = _image()
    image.plot([0, 1], [0, 1])

    with pytest.warns(UserWarning, match=r"Unused kwargs: \{'nosuchkeyword'\}"):
        image.text(text="hello", x=0.5, y=0.5, nosuchkeyword=1)  # pyright: ignore[reportCallIssue]


# ---- Saving ----
def test_savefig_writes_the_file(tmp_path: Path) -> None:
    """Save a figure and check the file is there.

    The end of most sessions, and the only method here whose result lives
    outside the process.
    """
    image = _image()
    image.plot([0, 1], [0, 1])
    out = tmp_path / "figure.png"

    image.savefig(str(out))

    assert out.exists()


def test_savefig_passes_the_options_to_matplotlib(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    """Save with a different box and resolution and check both are forwarded.

    Neither can be read back from the file without decoding it, so the
    figure's own savefig records what it was given. A dropped dpi would only
    show as a blurry figure much later.
    """
    image = _image()
    image.plot([0, 1], [0, 1])
    assert image.fig is not None
    calls: list[dict[str, object]] = []
    monkeypatch.setattr(image.fig, "savefig", lambda *a, **kw: calls.append(kw))

    image.savefig(str(tmp_path / "figure.png"), bbox=None, dpi=72)

    assert calls == [{"bbox_inches": None, "dpi": 72}]


def test_savefig_script_relative_saves_next_to_the_caller(
    tmp_path: Path,
) -> None:
    """Save with script_relative and check the file lands beside the caller.

    The option is for scripts run from elsewhere: the figure belongs next to
    the script, not in whatever directory the user happened to be in. The
    path is found by walking the call stack, which is why this goes through a
    real module written into tmp_path: calling the manager directly would
    count a different number of frames and answer with this test file's own
    folder.
    """
    script = tmp_path / "plotting_script.py"
    script.write_text(
        "import pyPLUTO as pp\n\n\n"
        "def draw() -> None:\n"
        "    image = pp.Image(text=False)\n"
        "    image.plot([0, 1], [0, 1])\n"
        "    image.savefig('relative.png', script_relative=True)\n"
    )
    sys.path.insert(0, str(tmp_path))
    try:
        module = __import__("plotting_script")
        module.draw()
    finally:
        sys.path.remove(str(tmp_path))
        sys.modules.pop("plotting_script", None)

    assert (tmp_path / "relative.png").exists()


def test_savefig_without_a_figure() -> None:
    """Save from a manager whose state has no figure.

    Saving nothing would write an empty file, or fail inside matplotlib; the
    message says which of the two mistakes the user made.
    """
    with pytest.raises(ValueError, match="No figure to save"):
        _stateless_manager().savefig("nosuchfigure.png")
