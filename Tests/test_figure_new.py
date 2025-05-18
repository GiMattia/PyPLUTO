import shutil
import warnings

import matplotlib as mpl
import matplotlib.pyplot as plt
import pytest
from pyPLUTO.figure_new import FigureManager
from pyPLUTO.image_new import Image_new
from pyPLUTO.imagestate import ImageState


# Test when the style is valid and can be applied
def test_setup_style_with_valid_style():
    # Given
    state = ImageState(
        style="ggplot", LaTeX=True
    )  # Use a valid style available in matplotlib
    _ = FigureManager(state)
    assert state.style == "ggplot"  # style should remain the same


# Test when the style is invalid and falls back to default
def test_setup_style_with_invalid_style():
    state = ImageState(style="non_existent_style", LaTeX=True)
    with pytest.warns(
        UserWarning, match="Style 'non_existent_style' not found."
    ) as warning:
        _ = FigureManager(state)
    assert state.style == "default"  # Ensure the style was set to 'default'


# Test interaction with Image_new to check delegation and style fallback
def test_interaction_with_image_new():
    # Given
    with pytest.warns(
        UserWarning, match="Style 'non_existent_style' not found."
    ) as warning:
        img = Image_new(
            style="non_existent_style"
        )  # Initialize Image_new with invalid style

    assert img.state.LaTeX == True
    assert img.state.style == "default"  # style should fallback to default
    assert (
        img._figure_manager.state.style == "default"
    )  # Same for the figure manager


# Test interaction when a valid style is used via Image_new
def test_interaction_with_image_new_valid_style():
    # Given
    img = Image_new(style="ggplot")  # Use a valid style available in matplotlib
    assert (
        img.state.style == "ggplot"
    )  # style should remain as seaborn-darkgrid
    assert (
        img._figure_manager.state.style == "ggplot"
    )  # Same for the figure manager


def test_number_colors():
    # Given
    img = Image_new(numcolors=15)
    assert img._figure_manager.state.color[0] == "#0104fe"
    assert img._figure_manager.color[0] == "#0104fe"
    with pytest.warns(
        DeprecationWarning,
        match="numcolor is deprecated. Use numcolors instead.",
    ) as warning:
        _ = Image_new(numcolor=15)


def test_latex():
    # Given
    img = Image_new(LaTeX=False)
    assert img.LaTeX == False
    assert img.state.LaTeX == False
    assert img._figure_manager.state.LaTeX == False

    img = Image_new(LaTeX=True)
    assert img.LaTeX == True
    assert img.state.LaTeX == True
    assert img._figure_manager.state.LaTeX == True


def test_latex_pgf(monkeypatch):
    monkeypatch.setattr(
        shutil, "which", lambda cmd: "latex"
    )  # simulate installed
    monkeypatch.setattr(plt, "switch_backend", lambda *args, **kwargs: None)
    monkeypatch.setattr(mpl.rcParams, "update", lambda *args, **kwargs: None)

    img = Image_new(LaTeX="pgf")

    # Now this should pass
    assert img.LaTeX == "pgf"
    assert img.state.LaTeX == "pgf"
    assert img._figure_manager.state.LaTeX == "pgf"


def test_latex_pgf_latex_not_installed(monkeypatch):
    monkeypatch.setattr(
        shutil, "which", lambda cmd: None
    )  # simulate missing latex
    monkeypatch.setattr(plt, "switch_backend", lambda *args, **kwargs: None)
    monkeypatch.setattr(mpl.rcParams, "update", lambda *args, **kwargs: None)

    with pytest.warns(UserWarning, match="LaTeX not installed"):
        img = Image_new(LaTeX="pgf")  # triggers fallback inside constructor
    #    img._figure_manager._assign_LaTeX("normal")

    assert img.state.LaTeX is True  # fallback occurred
    img = Image_new(LaTeX=True)
    assert img.LaTeX is True


def test_latex_pgf_backend_import_error(monkeypatch):
    monkeypatch.setattr(
        shutil, "which", lambda cmd: "fakepath"
    )  # simulate installed

    def fake_switch_backend(*args, **kwargs):
        raise ImportError("Backend pgf not available")

    monkeypatch.setattr(plt, "switch_backend", fake_switch_backend)
    monkeypatch.setattr(mpl.rcParams, "update", lambda *args, **kwargs: None)

    with pytest.warns(UserWarning, match="pgf backend is not available"):
        img = Image_new(LaTeX="pgf")  # moved inside

    assert img.state.LaTeX is True


class FakeRcParams(dict):
    def __setitem__(self, key, value):
        raise ImportError("Simulated failure setting font")


# suppress unrelated warnings
def test_latex_true_font_missing(monkeypatch):
    img = Image_new(LaTeX=True)

    # Replace mpl.rcParams with a fake object that raises on set
    monkeypatch.setattr(mpl, "rcParams", FakeRcParams(mpl.rcParams))

    with pytest.warns(
        UserWarning, match="LaTeX = True option is not available"
    ):
        img._figure_manager._assign_LaTeX("bold")


def test_latex_true_success(monkeypatch):
    img = Image_new(LaTeX=True)

    # No warning expected if assignment is valid
    with warnings.catch_warnings(record=True) as w:
        warnings.simplefilter("always")
        img._figure_manager._assign_LaTeX("normal")
        assert len(w) == 0


def test_figure_created():
    # Given
    img = Image_new()

    # Then
    assert img.fig is not None
    assert img._figure_manager.fig is not None
    assert isinstance(img.fig, mpl.figure.Figure)
    assert img.fig.get_figwidth() == 8.0
    assert img.fig.get_figheight() == 5.0
    assert img.fig._suptitle is None
    assert img.fontsize == 17
    assert img.fig.get_tight_layout() is False
    assert img.fig.number == 1


def test_figure_replaced():
    # Given
    fig = plt.figure()
    img = Image_new(fig=fig, replace=True)

    # Then
    assert img.fig is not fig
    assert img.fig is not None


def test_figure_not_replaced():
    # Given
    fig = plt.figure()
    img = Image_new(fig=fig)

    # Then
    assert img.fig is fig


def test_figure_params():
    # Given
    img = Image_new(figsize=[10, 10], nwin=2, fontsize=20)

    # Then
    assert img.figsize == [10, 10]
    assert img._set_size is True
    assert img.nwin == 2
    assert img.fontsize == 20


def test_suptitle_and_tightlayout():
    fig = plt.figure()
    img = Image_new(fig=fig, suptitle="Test Title", suptitlesize=18, tight=True)

    # Test suptitle
    assert fig._suptitle is not None
    assert fig._suptitle.get_text() == "Test Title"
    assert fig._suptitle.get_fontsize() == 18


# Test the tight layout
def test_tight_layout():
    img = Image_new(tight=False)
    assert img.fig.get_tight_layout() is False


def test_image_new_fig_no_number():
    fig = plt.Figure()

    with pytest.warns(
        UserWarning, match="The figure is not associated to a window number"
    ):
        img = Image_new(fig=fig)

    assert img.state.nwin == 1
