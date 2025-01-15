import pyPLUTO as pp
import matplotlib as mpl
import numpy as np


# Test the default values of the figure created in the __init__
def test_default_image():
    I = pp.Image()
    assert type(I.fig) == mpl.figure.Figure
    assert I.fig.get_figwidth() == 8.0
    assert I.fig.get_figheight() == 5.0
    assert I.fig._suptitle == None
    assert I.fontsize == 17
    assert I.fig.get_tight_layout() == False
    assert I.fig.number == 1


# Test the window number
def test_window_number():
    I = pp.Image(nwin=2)
    assert I.fig.number == 2


# Test the figure size
def test_figsize():
    I = pp.Image(figsize=(6, 7))
    assert I.fig.get_figwidth() == 6.0
    assert I.fig.get_figheight() == 7.0


# Test the suptitle
def test_suptitle():
    I = pp.Image(suptitle="This is a title")
    assert I.fig._suptitle.get_text() == "This is a title"


# Test the fontsize
def test_fontsize():
    I = pp.Image(fontsize=20)
    assert I.fontsize == 42


# Test the tight layout
def test_tight_layout():
    I = pp.Image(tight=False)
    assert I.fig.get_tight_layout() == False


# Test the LaTeX
def test_LaTeX():
    pass


# Test the colorlines
def test_colorlines():
    pass
