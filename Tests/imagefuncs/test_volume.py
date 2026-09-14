"""Test of the volume.py / volengine.py volume rendering."""

import numpy as np
import pytest

import pyPLUTO as pp
from pyPLUTO.imagefuncs.volengine import MPLVolumeRenderer, synthetic_plume

data, _extent = synthetic_plume(32)


def test_volume_basic() -> None:
    """A basic render returns an RGBA buffer and registers the renderer."""
    image = pp.Image()
    h = image.volume(data, resolution=48, samples=16, interactive=False)

    assert isinstance(h, MPLVolumeRenderer)
    assert image.state.volumes == [h]

    rgba = h.render(final=True, force=True)
    assert rgba.shape == (48, 48, 4)
    assert rgba.dtype == np.float32
    assert np.all(rgba >= 0.0) and np.all(rgba <= 1.0)


def test_volume_dark_background() -> None:
    """The 'dark_background' style yields a dark backdrop, default a light one."""
    # plt.style.use is global and the backdrop is read from rcParams at render
    # time, so capture each render right after its figure is created.
    light = pp.Image().volume(
        data, resolution=32, samples=12, interactive=False
    )
    light_corner = light.render(force=True)[0, 0, :3]

    dark = pp.Image(style="dark_background").volume(
        data, resolution=32, samples=12, interactive=False
    )
    dark_corner = dark.render(force=True)[0, 0, :3]

    assert light_corner.min() > 0.8
    assert dark_corner.max() < 0.2


def test_volume_extent_from_grid() -> None:
    """The physical extent is built from the x1/x2/x3 grid coordinates."""
    arr = np.random.default_rng(0).random((40, 30, 20)).astype(np.float32)
    x1 = np.linspace(-1.0, 1.0, 40)
    x2 = np.linspace(-2.0, 2.0, 30)
    x3 = np.linspace(0.0, 5.0, 20)

    h = pp.Image().volume(arr, x1=x1, x2=x2, x3=x3, resolution=32, samples=8)
    assert h.extent == (-1.0, 1.0, -2.0, 2.0, 0.0, 5.0)
    # PyPLUTO (x1, x2, x3) order is transposed to engine (z, y, x).
    assert h.volume.shape == (20, 30, 40)


def test_volume_view_change_triggers_rerender() -> None:
    """A view change (e.g. toolbar Home) re-renders the underlay via draw."""
    h = pp.Image().volume(data, resolution=32, samples=8, interactive=True)
    first_sig = h._last_view_sig

    # Programmatically change the camera, as the Home button would.
    h.ax3d.view_init(elev=10.0, azim=10.0)
    h._on_draw(None)
    assert h._last_view_sig != first_sig

    # Restoring the stored home view snaps the camera back.
    h._restore_home_view()
    assert h.ax3d.elev == pytest.approx(h._home_view["elev"])


def test_volume_requires_3d_axis() -> None:
    """Rendering onto a non-3D axis raises an informative error."""
    image = pp.Image()
    image.create_axes()  # default 2D axis
    with pytest.raises(ValueError, match="3D axis"):
        image.volume(data, ax=0, resolution=16, samples=4)
