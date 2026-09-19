"""Test of the figure.py file.

FigureManager is the one manager built before the others, because it creates
the figure they all draw on. Its work is mostly deciding: which figure this
Image gets, what size and fontsize it carries, which style and LaTeX settings
matplotlib is left in.

Two traps are worth knowing before adding a test here.

`fig.get_tight_layout()` is **not** how to observe the `tight` keyword: the
code calls `fig.tight_layout()` once rather than installing the tight layout
engine, so that method returns False whatever was asked for, and three tests
once asserted on it vacuously. What does change is the layout engine and the
position of the axes.

The LaTeX tests monkeypatch `plt.switch_backend` and `mpl.rcParams`, because
the real thing switches the backend of the whole process and needs XeLaTeX
installed. They re-assert the Agg backend first, so they do not depend on the
order the suite runs in.
"""

import shutil

import matplotlib as mpl
import matplotlib.pyplot as plt
import pytest
from matplotlib.figure import Figure

from pyPLUTO.image import Image
from pyPLUTO.imagefuncs.figure import FigureManager
from pyPLUTO.imagestate import ImageState

# The first four line colours, written out by hand. The palette is ordered so
# that neighbouring colours stay distinguishable with a colour vision
# deficiency, so a reordering is a real change and must fail here.
FIRST_COLORS = ["#0104fe", "#dc050c", "#4eb265", "#ee8026"]

# What the two flags put in front of that palette.
BLACK = "#000000"
WHITE = "#ffffff"


def _drawn_figure(number: int) -> plt.Figure:
    """Build a figure in a given window, with something on it.

    Anything attaching to it can then be checked in both directions: the
    figure is the same object, and what was drawn on it is still there.
    """
    plt.close("all")
    figure = plt.figure(number)
    figure.add_subplot(111).plot([0.0, 1.0], [0.0, 1.0])
    return figure


# ---- Style ----
@pytest.mark.parametrize("through", ["manager", "image"])
def test_a_valid_style_is_kept(through: str) -> None:
    """Ask for a style matplotlib has, and check it survives.

    Checked through the manager and through the facade, since a user reaches
    it by the second and the first is where the work happens: the two must
    agree, and they share one state.
    """
    if through == "manager":
        state = ImageState(style="ggplot", LaTeX=True)
        manager = FigureManager(state)
        assert manager.state.style == "ggplot"
    else:
        image = Image(style="ggplot", text=False)
        assert image.style == "ggplot"
        assert image.FigureManager.state.style == "ggplot"


@pytest.mark.parametrize("through", ["manager", "image"])
def test_an_unknown_style_warns_and_falls_back(through: str) -> None:
    """Ask for a style nothing defines, and check the fallback is recorded.

    A misspelled style must not stop a figure from being drawn, and the
    state has to end up holding what matplotlib is really using, or every
    later read of `style` would be wrong.
    """
    with pytest.warns(UserWarning, match="Style 'nosuchstyle' not found"):
        if through == "manager":
            state = ImageState(style="nosuchstyle", LaTeX=True)
            manager = FigureManager(state)
            assert manager.state.style == "default"
        else:
            image = Image(style="nosuchstyle", text=False)
            assert image.style == "default"
            assert image.FigureManager.state.style == "default"


# ---- Line colours ----
def test_the_colours_are_the_expected_ones() -> None:
    """Ask for a number of colours and check how many, and which, come back.

    The count matters as much as the values: a palette cut short leaves
    later lines without a colour of their own, and the order is what keeps
    neighbouring lines distinguishable.
    """
    image = Image(numcolors=15, text=False)

    assert len(image.color) == 15
    assert image.color[: len(FIRST_COLORS)] == FIRST_COLORS


@pytest.mark.parametrize(
    ("keyword", "expected"), [("withblack", BLACK), ("withwhite", WHITE)]
)
def test_black_or_white_goes_first(keyword: str, expected: str) -> None:
    """Put black or white in front of the palette and check it is first.

    The rest of the palette follows it unchanged, so what the flag does is
    shift everything by one rather than replace a colour.
    """
    image = Image(text=False, **{keyword: True})

    assert image.color[0] == expected
    assert image.color[1] == FIRST_COLORS[0]


# ---- LaTeX ----
@pytest.mark.parametrize("latex", [True, False])
def test_the_latex_flag_is_recorded(latex: bool) -> None:
    """Set the LaTeX flag and read it back off the image and the manager.

    Both read the same state, so this is the plain round trip; the branches
    that do the work are below.
    """
    image = Image(LaTeX=latex, text=False)

    assert image.LaTeX is latex
    assert image.FigureManager.state.LaTeX is latex


def test_pgf_is_kept_when_latex_is_installed(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """Ask for the pgf backend with LaTeX available, and check it is used.

    The backend switch and the rcParams update are replaced: the real ones
    change the backend of the whole process. Agg is reasserted first so the
    test does not depend on what ran before it.
    """
    plt.switch_backend("Agg")
    monkeypatch.setattr(shutil, "which", lambda cmd: "latex")
    monkeypatch.setattr(plt, "switch_backend", lambda *a, **kw: None)
    monkeypatch.setattr(mpl.rcParams, "update", lambda *a, **kw: None)

    image = Image(LaTeX="pgf", text=False)

    assert image.LaTeX == "pgf"
    assert image.FigureManager.state.LaTeX == "pgf"


def test_pgf_falls_back_when_latex_is_missing(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """Ask for pgf on a machine without LaTeX, and check the fallback.

    pgf needs XeLaTeX, which most machines do not have, so the request
    becomes LaTeX=True rather than an error: the figure is still drawn, with
    the LaTeX font instead of the pgf backend.
    """
    plt.switch_backend("Agg")
    monkeypatch.setattr(shutil, "which", lambda cmd: None)
    monkeypatch.setattr(plt, "switch_backend", lambda *a, **kw: None)
    monkeypatch.setattr(mpl.rcParams, "update", lambda *a, **kw: None)

    with pytest.warns(UserWarning, match="LaTeX not installed"):
        image = Image(LaTeX="pgf", text=False)

    assert image.state.LaTeX is True


def test_pgf_falls_back_when_the_backend_is_missing(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """Ask for pgf where LaTeX exists but the backend cannot be imported.

    The other way the request can fail, and it must end in the same place:
    LaTeX=True, a warning, and a usable figure.
    """
    plt.switch_backend("Agg")
    monkeypatch.setattr(shutil, "which", lambda cmd: "fakepath")

    def failing_switch(*_args: object, **_kwargs: object) -> None:
        raise ImportError("Backend pgf not available")

    monkeypatch.setattr(plt, "switch_backend", failing_switch)
    monkeypatch.setattr(mpl.rcParams, "update", lambda *a, **kw: None)

    with pytest.warns(UserWarning, match="pgf backend is not available"):
        image = Image(LaTeX="pgf", text=False)

    assert image.state.LaTeX is True


class _FailingRcParams(dict):
    """rcParams that refuse to be written, to reach the LaTeX=True guard."""

    def __setitem__(self, key: object, value: object) -> None:
        """Refuse every assignment, as a missing font package would."""
        raise ImportError("Simulated failure setting font")


def test_latex_true_warns_when_the_font_is_missing(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """Set the LaTeX font where it cannot be set, and check the warning.

    The STIX font is not always installed. The plot is still drawn with the
    default font, so the user is told rather than stopped.
    """
    image = Image(LaTeX=True, text=False)
    monkeypatch.setattr(mpl, "rcParams", _FailingRcParams(mpl.rcParams))

    with pytest.warns(UserWarning, match="LaTeX = True option is not"):
        image.FigureManager.assign_LaTeX("bold")


def test_latex_true_is_silent_when_it_works(
    recwarn: pytest.WarningsRecorder,
) -> None:
    """Set the LaTeX font where it can be set, and expect no warning.

    The counterpart of the test above: the warning must be the exception,
    not something every figure prints.
    """
    image = Image(LaTeX=True, text=False)

    image.FigureManager.assign_LaTeX("normal")

    assert [str(w.message) for w in recwarn] == []


# ---- The figure itself ----
def test_the_default_figure() -> None:
    """Build an image with no keywords and check what the figure is.

    The defaults a user gets without asking for anything, pinned in full:
    an 8x5 figure, fontsize 17, window 1, and no title over the subplots.
    """
    image = Image(text=False)

    assert image.fig is not None
    assert image.fig.get_figwidth() == 8.0
    assert image.fig.get_figheight() == 5.0
    assert image.fontsize == 17
    assert image.fig.number == 1
    assert image.fig._suptitle is None


def test_the_figure_keywords_are_applied() -> None:
    """Give a size, a window and a fontsize, and check all three arrive.

    `set_size` records that the size was asked for rather than computed,
    which is what stops create_axes from resizing the figure later.
    """
    plt.close("all")
    image = Image(figsize=[10.0, 10.0], nwin=2, fontsize=20, text=False)

    assert list(image.figsize) == [10.0, 10.0]
    assert image.set_size is True
    assert image.nwin == 2
    assert image.fontsize == 20
    assert image.fig is not None
    assert list(image.fig.get_size_inches()) == [10.0, 10.0]


def test_the_suptitle_is_written() -> None:
    """Give a title over all the subplots, and check its text and size.

    It is written on the figure rather than on an axis, so it survives
    whatever happens to the subplots afterwards.
    """
    figure = _drawn_figure(1)
    Image(fig=figure, suptitle="Test Title", suptitlesize=18, text=False)

    assert figure._suptitle is not None
    assert figure._suptitle.get_text() == "Test Title"
    assert figure._suptitle.get_fontsize() == 18


@pytest.mark.parametrize("tight", [True, False])
def test_tight_changes_the_layout(tight: bool) -> None:
    """Draw with and without the tight layout, and compare the axes box.

    Not `fig.get_tight_layout()`, which is False either way: the code calls
    `tight_layout()` once instead of installing the engine. What the
    keyword really does is move the axes, so the box is what is compared --
    tight pulls the plot outwards to use the margins.
    """
    image = Image(tight=tight, text=False)
    image.plot([0.0, 1.0], [0.0, 1.0], title="a title", xtitle="x")

    box = image.ax[0].get_position()

    assert image.tight is tight
    if tight:
        # Pulled outwards, past matplotlib's default margins.
        assert box.x0 < 0.125
        assert box.x1 > 0.900
    else:
        # Left exactly on the defaults.
        assert box.x0 == pytest.approx(0.125)
        assert box.x1 == pytest.approx(0.900)


def test_create_figure_refuses_a_missing_figure(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """Make matplotlib hand back no figure, and check the manager says so.

    It cannot happen through pyplot today, but everything downstream
    dereferences the figure, so the guard turns a None into a sentence
    rather than an AttributeError three calls later.
    """
    state = ImageState(
        fig=None, figsize=[8.0, 5.0], fontsize=17, nwin=1, tight=False
    )
    manager = FigureManager.__new__(FigureManager)
    manager.state = state
    monkeypatch.setattr(plt, "figure", lambda *a, **kw: None)
    monkeypatch.setattr(mpl.rcParams, "update", lambda *a, **kw: None)

    with pytest.raises(ValueError, match="The figure could not be created"):
        manager.create_figure(
            replace=False, suptitle=None, suptitlesize="large"
        )


# ---- Replacing or inheriting ----
def test_a_new_image_replaces_the_window() -> None:
    """Build a second image on the same window, and check it starts clean.

    The default without `fig`: the window is taken over, so a script run
    twice does not draw on top of its own previous figure.
    """
    first = _drawn_figure(1)
    image = Image(text=False)

    assert image.fig is not first
    assert not first.axes


def test_replace_false_inherits_the_window() -> None:
    """Ask not to replace, and check the existing figure is the one used.

    The way to add to a figure that is already there: same object, and
    whatever was drawn on it is still drawn.
    """
    first = _drawn_figure(1)
    image = Image(replace=False, text=False)

    assert image.fig is first
    assert first.axes


def test_an_inherited_window_can_be_resized() -> None:
    """Inherit a figure and ask for a different size at the same time.

    Two things at once, and the second is the reason the size is applied by
    hand afterwards: `plt.figure(nwin, figsize=...)` on a window that exists
    hands the figure back, ignores the size and warns about it. So the
    figure has to be resized once it is in hand -- and what was drawn on it
    survives the resize.
    """
    first = _drawn_figure(1)
    image = Image(replace=False, figsize=[3.0, 7.0], text=False)

    assert image.fig is first
    assert first.axes
    assert list(image.figsize) == [3.0, 7.0]
    assert list(first.get_size_inches()) == [3.0, 7.0]


def test_another_window_is_left_alone() -> None:
    """Build an image on a different window, and check the first survives.

    Replacing is about the window this Image takes, not about every figure
    open at the time.
    """
    first = _drawn_figure(1)
    image = Image(nwin=2, text=False)

    assert image.nwin == 2
    assert first.axes


def test_a_given_figure_is_used_as_it_is() -> None:
    """Hand a drawn figure to an Image and check it is used, not replaced.

    A figure passed with `fig` is one the user already owns, so it is what
    the Image draws on and its contents survive.
    """
    figure = _drawn_figure(3)
    image = Image(fig=figure, text=False)

    assert image.fig is figure
    assert figure.axes


def test_replace_true_replaces_a_given_figure() -> None:
    """Hand a figure over and ask for a replacement anyway.

    The one case where a passed figure is closed: the user asked for a new
    one in that window.
    """
    figure = _drawn_figure(3)
    image = Image(fig=figure, replace=True, text=False)

    assert image.fig is not figure
    assert not figure.axes


def test_check_previous_fig_clears_the_existing_figure(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """Check the old figure is emptied as well as closed.

    `clf()` before `close()` releases the artists at once. Without it a
    stale Image, still holding axes and texts, keeps the whole plot alive in
    memory until it is collected.
    """
    state = ImageState(nwin=3)
    manager = FigureManager.__new__(FigureManager)
    manager.state = state
    cleared: list[str] = []

    class _Figure:
        def clf(self) -> None:
            cleared.append("cleared")

    figure = _Figure()
    closed: list[object] = []
    monkeypatch.setattr(plt, "fignum_exists", lambda n: True)
    monkeypatch.setattr(plt, "figure", lambda n: figure)
    monkeypatch.setattr(plt, "close", closed.append)

    manager.check_previous_fig(replace=True)

    assert cleared == ["cleared"]
    assert closed == [figure]


# ---- Attaching to a figure ----
@pytest.mark.parametrize(
    ("keyword", "read", "given"),
    [("figsize", "figsize", [12.0, 3.0]), ("fontsize", "fontsize", 30.0)],
)
def test_a_keyword_wins_over_the_figure(
    keyword: str, read: str, given: object
) -> None:
    """Attach to a figure and ask for a size, or a fontsize, of your own.

    The figure carries its own values and they are read off it, which used
    to overwrite whatever was asked for here and leave the request silently
    dropped. An explicit keyword is applied again afterwards, and a size
    reaches the figure itself.
    """
    plt.close("all")
    figure = plt.figure(71, figsize=(4.0, 4.0))
    image = Image(fig=figure, text=False, **{keyword: given})

    assert (
        list(getattr(image, read)) == list(given)
        if isinstance(given, list)
        else getattr(image, read) == given
    )


def test_an_attached_figure_supplies_what_was_not_given() -> None:
    """Attach to a figure without asking for anything, and check it decides.

    The other half of the test above: a size, a window number and a layout
    are properties of the figure, so an Image attached to one inherits them
    rather than imposing its own defaults.
    """
    figure = plt.figure(72, figsize=(4.0, 6.0))
    image = Image(fig=figure, text=False)

    assert list(image.figsize) == [4.0, 6.0]
    assert image.nwin == 72


@pytest.mark.parametrize(
    ("layout", "expected"), [("tight", True), (None, True)]
)
def test_the_layout_of_an_attached_figure(
    layout: str | None, expected: bool
) -> None:
    """Attach to a figure with and without matplotlib's tight engine.

    A figure carrying the engine says so, and that is inherited. A figure
    without it says False, which means "no engine installed" rather than "no
    tight layout wanted" -- pyPLUTO lays out by calling `tight_layout()`
    once and installs no engine -- so the default stands instead. Attaching
    used to read that False and silently switch the layout off.
    """
    plt.close("all")
    figure = plt.figure(81, layout=layout)
    image = Image(fig=figure, text=False)

    assert image.tight is expected


def test_a_figure_without_a_window_number() -> None:
    """Attach to a figure pyplot never registered, and check the fallback.

    `plt.Figure()` builds one outside pyplot, so it has no window number and
    reading it raises. The Image falls back to window 1 and says so.
    """
    figure = plt.Figure()

    with pytest.warns(UserWarning, match="not associated to a window number"):
        image = Image(fig=figure, text=False)

    assert image.nwin == 1


class _LabelledFigure(Figure):
    """A figure whose window number is not an integer.

    A subclass rather than a patched attribute: assigning to
    `Figure.number` is deprecated in matplotlib 3.10 and becomes an error in
    3.12, so patching one would warn now and fail later.
    """

    number = "labelled"


def test_a_figure_numbered_with_something_else_is_ignored() -> None:
    """Attach to a figure whose number is not an integer.

    pyplot always numbers with an integer, even for `plt.figure("label")`,
    so this cannot arrive through the public API. The guard is what tells
    the type checkers that `nwin` stays an int, and this is what covers it:
    a number of another type is left where it is rather than stored.
    """
    state = ImageState(nwin=4, fig=_LabelledFigure())
    manager = FigureManager.__new__(FigureManager)
    manager.state = state

    manager.check_previous_fig(replace=False)

    assert state.nwin == 4


def test_a_conflicting_window_number_warns() -> None:
    """Ask for a window number while handing over a figure of another.

    A figure cannot be renumbered, so the number given is dropped; the
    warning is what stops that being silent.
    """
    figure = _drawn_figure(3)

    with pytest.warns(UserWarning, match="nwin=7 is ignored"):
        image = Image(fig=figure, nwin=7, text=False)

    assert image.nwin == 3


def test_a_matching_window_number_is_silent(
    recwarn: pytest.WarningsRecorder,
) -> None:
    """Ask for the window number the figure already has.

    Saying out loud what is already true is not a mistake, so it must not
    warn: only a disagreement does.
    """
    figure = _drawn_figure(3)

    image = Image(fig=figure, nwin=3, text=False)

    assert image.nwin == 3
    assert [str(w.message) for w in recwarn] == []


# ---- The deprecated keyword ----
@pytest.mark.parametrize("close", [True, False])
def test_close_is_deprecated_and_read_as_replace(close: bool) -> None:
    """Use the old `close` keyword and check it warns and still works.

    `close` emptied the window and `replace` decided whether a new figure
    was built, and neither did anything alone. They are one keyword now,
    and the old one keeps working for a release.
    """
    first = _drawn_figure(1)

    with pytest.warns(DeprecationWarning, match="'close' argument is"):
        image = Image(close=close, text=False)

    assert (image.fig is not first) is close
