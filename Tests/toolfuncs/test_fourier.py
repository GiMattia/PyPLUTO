"""Test of the fourier.py file."""

from pathlib import Path

import numpy as np
import numpy.testing as npt
import pytest

import pyPLUTO as pp
from pyPLUTO.toolfuncs.fourier import FourierManager

# A sine wave with a known wavenumber, sampled over a full period
xx = np.linspace(0, 2 * np.pi, 64, endpoint=False)
dx = xx[1] - xx[0]


def _load(data_dir: Path):
    return pp.Load(path=data_dir / "single_file", text=False)


# The transform of a sine peaks at its own wavenumber
def test_fourier_peak_1D(data_dir: Path):
    freqs, ft = _load(data_dir).fourier(np.sin(5 * xx), dx=dx)
    assert freqs[np.argmax(ft)] == pytest.approx(5.0)


# Only the positive half of the spectrum is returned
def test_fourier_shape_1D(data_dir: Path):
    freqs, ft = _load(data_dir).fourier(np.sin(5 * xx), dx=dx)
    assert ft.shape == (33,)
    assert np.asarray(freqs).shape == (33,)


# The amplitude of the transform is always positive
def test_fourier_amplitude_positive(data_dir: Path):
    _, ft = _load(data_dir).fourier(np.sin(5 * xx), dx=dx)
    assert np.all(ft >= 0.0)


# A constant signal has all its power in the zero frequency
def test_fourier_constant_signal(data_dir: Path):
    _, ft = _load(data_dir).fourier(np.ones(64), dx=dx)
    assert np.argmax(ft) == 0
    npt.assert_allclose(ft[1:], 0.0, atol=1e-10)


# In 2D one frequency array per direction is returned
def test_fourier_2D(data_dir: Path):
    field = np.sin(3 * xx)[:, None] * np.ones(32)
    freqs, ft = _load(data_dir).fourier(field, dx=dx, dy=1.0)
    assert len(freqs) == 2
    assert ft.shape == (33, 17)


# In 3D one frequency array per direction is returned
def test_fourier_3D(data_dir: Path):
    freqs, ft = _load(data_dir).fourier(
        np.ones((8, 8, 8)), dx=1.0, dy=1.0, dz=1.0
    )
    assert len(freqs) == 3
    assert ft.shape == (5, 5, 5)


# A float spacing is taken as it is
def test_fourier_spacing_float():
    assert FourierManager._fourier_spacing(4.0) == 4.0


# A list or array spacing uses its first value
def test_fourier_spacing_sequence():
    assert FourierManager._fourier_spacing([2.0, 3.0]) == 2.0
    assert FourierManager._fourier_spacing(np.array([2.5, 3.0])) == 2.5


# A negative spacing is not physical and raises an error
def test_fourier_spacing_negative():
    with pytest.raises(ValueError):
        FourierManager._fourier_spacing(-1.0)
