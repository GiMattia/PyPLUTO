import matplotlib as mpl
import numpy as np

import pyPLUTO as pp

x = np.linspace(0, 1, 101)
y = np.linspace(1, 10, 101)
z = np.logspace(0, 1, 101)


# Simple legend with custom label
def test_custo_label():
    I = pp.Image()
    I.plot(x, y)
    I.legend(label=["a"])
    assert I.ax[0].get_legend().get_lines()[0].get_label() == "a"


# Simple legend with custom label and different parameters
def test_custom_params():
    I = pp.Image()
    I.plot(x, y)
    I.plot(x, z)
    I.legend(label=["a", "b"], c=["k", "r"])
    lines = I.ax[0].get_legend().get_lines()
    assert lines[0].get_label() == "a"
    assert lines[1].get_label() == "b"
    assert lines[0].get_color() == "k"
    assert lines[1].get_color() == "r"


# Simple legend with custom label and different parameters
def test_more_custom_params():
    I = pp.Image()
    I.plot(x, y, label="111")
    I.plot(x, z, label="222")
    I.legend(c=["k", "r"])
    lines = I.ax[0].get_legend().get_lines()
    assert lines[0].get_label() == "111"
    assert lines[1].get_label() == "222"
    assert lines[0].get_color() == I.color[0]
    assert lines[1].get_color() == I.color[1]
