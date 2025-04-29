import numpy as np
import numpy.testing as npt
import pyPLUTO as pp


# Check the default values of the set_axes
def test_setaxis_default():
    Image = pp.Image()
    ax = Image.create_axes()
    Image.set_axis()
    assert ax.get_aspect() == "auto"
    xlim = ax.get_xlim()
    assert np.isclose(xlim[0], 0.0)
    assert np.isclose(xlim[1], 1.0)
    ylim = ax.get_ylim()
    assert np.isclose(ylim[0], 0.0)
    assert np.isclose(ylim[1], 1.0)
    assert ax.get_title() == ""
    assert ax.get_xlabel() == ""
    assert ax.get_ylabel() == ""
    assert ax.get_xscale() == "linear"
    assert ax.get_yscale() == "linear"
    assert ax.get_alpha() is None


# Aspect ratio
def test_aspect_ratio():
    Image = pp.Image()
    ax = Image.create_axes()
    Image.set_axis(aspect="equal", fontsize=20)
    assert np.isclose(ax.get_aspect(), 1.0)
    assert Image.fontsize == 20
    Image.set_axis(aspect=2.0)
    assert np.isclose(ax.get_aspect(), 2.0)


# xrange and yrange
def test_ranges():
    Image = pp.Image()
    ax = Image.create_axes()
    Image.set_axis(xrange=[-1, 1], yrange=[1, 10])
    xlim = ax.get_xlim()
    assert np.isclose(xlim[0], -1.0)
    assert np.isclose(xlim[1], 1.0)
    ylim = ax.get_ylim()
    assert np.isclose(ylim[0], 1.0)
    assert np.isclose(ylim[1], 10.0)


# labels
def test_labels():
    Image = pp.Image()
    ax = Image.create_axes()
    Image.set_axis(title="this is a title", xtitle="x", ytitle="y")
    assert ax.get_title() == "this is a title"
    assert ax.get_xlabel() == "x"
    assert ax.get_ylabel() == "y"


# ticks
def test_ticks():
    Image = pp.Image()
    ax = Image.create_axes()
    Image.set_axis(xticks=[0, 0.5, 1], yticks=None)
    x, y = ax.get_xticks(), ax.get_yticks()
    npt.assert_array_equal(x, [0, 0.5, 1])
    assert len(y) == 0
    Image.set_axis(xticks=None, yticks=[0, 0.2, 1.0])
    x, y = ax.get_xticks(), ax.get_yticks()
    assert len(x) == 0
    npt.assert_array_equal(y, [0, 0.2, 1.0])


# tickslabels
def test_tickslabels():
    Image = pp.Image()
    ax = Image.create_axes()
    yy = ["a", "b", "c"]
    Image.set_axis(
        xticks=[0, 0.5, 1],
        yticks=[0, 0.5, 1],
        xtickslabels=None,
        ytickslabels=yy,
    )
    x, y = ax.get_xticklabels(), ax.get_yticklabels()
    for i in x:
        assert i.get_text() == ""
    for i, j in enumerate(y):
        assert j.get_text() == yy[i]
    Image.set_axis(
        xticks=[0, 0.5, 1],
        yticks=[0, 0.5, 1],
        xtickslabels=yy,
        ytickslabels=None,
    )
    x, y = ax.get_xticklabels(), ax.get_yticklabels()
    for i, j in enumerate(x):
        assert j.get_text() == yy[i]
    for i in y:
        assert i.get_text() == ""


# scales and alpha
def test_scales_alpha():
    Image = pp.Image()
    ax = Image.create_axes()
    Image.set_axis(xscale="log", yscale="log", alpha=0.5)
    assert ax.get_xscale() == "log"
    assert ax.get_yscale() == "log"
    assert np.isclose(ax.get_alpha(), 0.5)
