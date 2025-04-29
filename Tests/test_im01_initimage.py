import matplotlib as mpl
import pyPLUTO as pp


# Test the default values of the figure created in the __init__
def test_default_image():
    Image = pp.Image()
    assert isinstance(Image.fig, mpl.figure.Figure)
    assert Image.fig.get_figwidth() == 8.0
    assert Image.fig.get_figheight() == 5.0
    assert Image.fig._suptitle is None
    assert Image.fontsize == 17
    assert Image.fig.get_tight_layout() is False
    assert Image.fig.number == 1


# Test the window number
def test_window_number():
    Image = pp.Image(nwin=2)
    assert Image.fig.number == 2


# Test the figure size
def test_figsize():
    Image = pp.Image(figsize=(6, 7))
    assert Image.fig.get_figwidth() == 6.0
    assert Image.fig.get_figheight() == 7.0


# Test the suptitle
def test_suptitle():
    Image = pp.Image(suptitle="This is a title")
    assert Image.fig._suptitle.get_text() == "This is a title"


# Test the fontsize
def test_fontsize():
    Image = pp.Image(fontsize=20)
    assert Image.fontsize == 20



# Test the tight layout
def test_tight_layout():
    Image = pp.Image(tight=False)
    assert Image.fig.get_tight_layout() is False


# Test the LaTeX
def test_LaTeX():
    pass


# Test the colorlines
def test_colorlines():
    pass
