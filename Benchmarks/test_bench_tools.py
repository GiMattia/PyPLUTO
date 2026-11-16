"""Benchmarks for the analysis tools of the Load class."""

from pathlib import Path

import numpy as np
import pytest

import pyPLUTO as pp

DATA_DIR = Path(__file__).resolve().parent.parent / "Tests" / "Test_load"


@pytest.fixture(scope="module")
def data():
    """Load a 2D 128x128 dataset once for all the benchmarks."""
    return pp.Load(0, path=DATA_DIR / "single_file", text=False)


@pytest.fixture(scope="module")
def smooth_field():
    """Build a smooth 2D vector field on a 128x128 grid."""
    x = np.linspace(0.0, 2.0 * np.pi, 128)
    xx, yy = np.meshgrid(x, x, indexing="ij")
    return x, -np.sin(yy), np.sin(xx), np.sin(xx) * np.cos(yy)


def test_gradient(benchmark, data):
    """Compute the gradient of the density."""
    result = benchmark(data.gradient, data.rho)
    assert result.shape[-2:] == (128, 128)


def test_divergence(benchmark, data):
    """Compute the divergence of the velocity field."""
    result = benchmark(data.divergence, data.vx1, data.vx2)
    assert result.shape == (128, 128)


def test_curl(benchmark, data):
    """Compute the curl of the velocity field."""
    result = benchmark(data.curl, data.vx1, data.vx2, data.vx3)
    assert result is not None


def test_fourier(benchmark, data):
    """Compute the 2D Fourier transform of the density."""
    result = benchmark(data.fourier, data.rho, dx=1.0, dy=1.0)
    assert result is not None


def test_slices_diagonal(benchmark, data):
    """Extract the main diagonal of the density."""
    result = benchmark(data.slices, data.rho, diag=True)
    assert result.shape == (128,)


def test_find_contour(benchmark, smooth_field):
    """Find the contour lines of a smooth scalar field."""
    x, _, _, scalar = smooth_field
    d = pp.Load(0, path=DATA_DIR / "single_file", text=False)
    d.x1, d.x2 = x, x

    lines = benchmark(d.find_contour, scalar, levels=[-0.5, 0.0, 0.5])
    assert len(lines) > 0


def test_find_fieldlines(benchmark, smooth_field):
    """Integrate field lines of a smooth 2D vector field."""
    x, vx, vy, _ = smooth_field
    d = pp.Load(0, path=DATA_DIR / "single_file", text=False)
    d.x1, d.x2 = x, x

    lines = benchmark(
        d.find_fieldlines,
        vx,
        vy,
        x0=[1.0, 2.0],
        y0=[1.0, 2.0],
        x1=x,
        x2=x,
        numsteps=256,
    )
    assert len(lines) == 2
