import numpy as np
import pyPLUTO as pp

x = np.linspace(0, 1, 101)
y = np.linspace(1, 10, 101)
z = np.logspace(0, 1, 101)


# Simple legend with custom label
def test_custo_label():
    Image = pp.Image()
    Image.plot(x, y)
    Image.legend(label=["a"])
    assert Image.ax[0].get_legend().get_lines()[0].get_label() == "a"


# Simple legend with custom label and different parameters
def test_custom_params():
    Image = pp.Image()
    Image.plot(x, y)
    Image.plot(x, z)
    Image.legend(label=["a", "b"], c=["k", "r"])
    lines = Image.ax[0].get_legend().get_lines()
    assert lines[0].get_label() == "a"
    assert lines[1].get_label() == "b"
    assert lines[0].get_color() == "k"
    assert lines[1].get_color() == "r"


# Simple legend with custom label and different parameters
def test_more_custom_params():
    Image = pp.Image()
    Image.plot(x, y, label="111")
    Image.plot(x, z, label="222")
    Image.legend(c=["k", "r"])
    lines = Image.ax[0].get_legend().get_lines()
    assert lines[0].get_label() == "111"
    assert lines[1].get_label() == "222"
    assert lines[0].get_color() == Image.color[0]
    assert lines[1].get_color() == Image.color[1]
