"""Benchmarks for the plotting routines of the Image class."""

import matplotlib.pyplot as plt
import numpy as np
import pytest

import pyPLUTO as pp

X = np.linspace(-1.0, 1.0, 128)
X2D, Y2D = np.meshgrid(X, X, indexing="ij")
VAR = 1.0 / ((X2D**2 + Y2D**2) / 2.0 + 1.0)


@pytest.fixture(autouse=True)
def _close_figures():
    """Close every figure created during a benchmark."""
    yield
    plt.close("all")


def test_image_create(benchmark):
    """Create an empty figure."""
    image = benchmark(pp.Image)
    assert image.fig is not None


def test_image_create_axes(benchmark):
    """Create a figure with a 2x2 grid of axes."""

    def run():
        image = pp.Image()
        image.create_axes(nrow=2, ncol=2)
        return image

    image = benchmark(run)
    assert len(image.ax) == 4


def test_image_plot(benchmark):
    """Draw a set of 1D line plots."""

    def run():
        image = pp.Image()
        for k in range(4):
            image.plot(X, np.sin((k + 1) * np.pi * X), label=f"k={k}")
        image.legend()
        return image

    image = benchmark(run)
    assert len(image.ax[0].lines) == 4


def test_image_display(benchmark):
    """Display a 2D 128x128 field with a colorbar."""

    def run():
        image = pp.Image()
        image.display(VAR, x1=X, x2=X, cpos="right", cmap="magma")
        return image

    image = benchmark(run)
    assert len(image.ax[0].collections) > 0
