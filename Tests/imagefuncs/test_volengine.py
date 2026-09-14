"""Test of the volengine.py file."""

import matplotlib.colors as mcol
import matplotlib.pyplot as plt
import numpy as np
import numpy.testing as npt
import pytest

import pyPLUTO.imagefuncs.volengine as ve

# The unit cube, used as the bounding box of most tests
unit_box = (0.0, 1.0, 0.0, 1.0, 0.0, 1.0)


# A 3D array is accepted and converted to single precision
def test_as_zyx_volume():
    volume = ve.as_zyx_volume(np.ones((2, 3, 4)))
    assert volume.shape == (2, 3, 4)
    assert volume.dtype == np.float32
    assert volume.flags["C_CONTIGUOUS"]


# Only 3D arrays are volumes
@pytest.mark.parametrize("shape", [(4,), (4, 4), (2, 2, 2, 2)])
def test_as_zyx_volume_wrong_dimension(shape):
    with pytest.raises(ValueError, match="3-D array"):
        ve.as_zyx_volume(np.ones(shape))


# A volume made only of NaNs carries no information
def test_as_zyx_volume_all_nan():
    with pytest.raises(ValueError, match="no finite values"):
        ve.as_zyx_volume(np.full((2, 2, 2), np.nan))


# The default extent spans one unit per cell, in (x, y, z) order
def test_default_extent_for():
    assert ve.default_extent_for(np.ones((2, 3, 4))) == (
        0.0,
        3.0,
        0.0,
        2.0,
        0.0,
        1.0,
    )


# The center, side lengths and bounding-sphere radius follow from the extent
def test_extent_center_radius():
    center, lengths, radius = ve.extent_center_radius((0, 2, 0, 2, 0, 2))
    npt.assert_allclose(center, [1.0, 1.0, 1.0])
    npt.assert_allclose(lengths, [2.0, 2.0, 2.0])
    assert radius == pytest.approx(0.5 * np.sqrt(12.0))


# The diagonal of the unit cube is the square root of three
def test_box_diagonal():
    assert ve._box_diagonal(unit_box) == pytest.approx(np.sqrt(3.0))


# A flat box still gets a positive diagonal, so nothing divides by zero
def test_box_diagonal_degenerate():
    assert ve._box_diagonal((0, 0, 0, 0, 0, 0)) > 0.0


# A single number means a square image
def test_resolve_resolution_square():
    assert ve._resolve_resolution(8) == (8, 8)


# A pair means width and height
def test_resolve_resolution_rectangle():
    assert ve._resolve_resolution((4, 6)) == (4, 6)


# An image needs at least two pixels per side
@pytest.mark.parametrize("resolution", [1, 0, (1, 8)])
def test_resolve_resolution_too_small(resolution):
    with pytest.raises(ValueError, match="at least 2 pixels"):
        ve._resolve_resolution(resolution)


# The linear opacity curve is the identity
def test_opacity_linear():
    x = np.linspace(0.0, 1.0, 5)
    npt.assert_allclose(ve._opacity_curve(x, "linear"), x)


# The power curve raises the input to the given exponent
def test_opacity_power():
    x = np.linspace(0.0, 1.0, 5)
    npt.assert_allclose(ve._opacity_curve(x, ("power", 2.0)), x**2)


# The constant curve ignores the input
def test_opacity_constant():
    x = np.linspace(0.0, 1.0, 5)
    npt.assert_allclose(ve._opacity_curve(x, ("constant", 0.3)), 0.3)


# The transparent curve is zero everywhere
def test_opacity_none():
    x = np.linspace(0.0, 1.0, 5)
    npt.assert_allclose(ve._opacity_curve(x, "none"), 0.0)


# The sigmoid curve increases and is centered where it is asked to be
def test_opacity_sigmoid():
    x = np.linspace(0.0, 1.0, 21)
    alpha = ve._opacity_curve(x, ("sigmoid", 0.5, 0.1, 1.0))
    assert np.all(np.diff(alpha) >= 0.0)
    assert alpha[10] == pytest.approx(0.5, abs=1e-3)


# The window curve peaks at its center
def test_opacity_window():
    x = np.linspace(0.0, 1.0, 21)
    alpha = ve._opacity_curve(x, ("window", 0.5, 0.15, 1.0))
    assert np.argmax(alpha) == 10


# Any curve can be given as a function
def test_opacity_callable():
    x = np.linspace(0.0, 1.0, 5)
    npt.assert_allclose(ve._opacity_curve(x, lambda v: v * 0.5), x * 0.5)


# Every curve stays between fully transparent and fully opaque
@pytest.mark.parametrize(
    "opacity", ["linear", ("power", 0.5), ("constant", 5.0), ("window", 0.5)]
)
def test_opacity_is_clipped(opacity):
    alpha = ve._opacity_curve(np.linspace(0.0, 1.0, 11), opacity)
    assert np.all((alpha >= 0.0) & (alpha <= 1.0))


# An unknown curve name cannot be used
def test_opacity_unknown():
    with pytest.raises(ValueError, match="unknown opacity"):
        ve._opacity_curve(np.linspace(0.0, 1.0, 5), "nosuchcurve")


# The lookup table holds one RGBA entry per sample
def test_transfer_lut_shape():
    lut = ve.make_transfer_lut(size=16)
    assert lut.shape == (16, 4)
    assert lut.dtype == np.float32


# The alpha channel of the table is the opacity curve
def test_transfer_lut_alpha():
    lut = ve.make_transfer_lut(size=8, opacity="linear")
    npt.assert_allclose(lut[:, 3], np.linspace(0.0, 1.0, 8), atol=1e-6)


# The color channels come from the requested colormap
def test_transfer_lut_colors():
    lut = ve.make_transfer_lut(size=8, cmap="viridis")
    expected = plt.get_cmap("viridis")(
        np.linspace(0.0, 1.0, 8, dtype=np.float32)
    )
    npt.assert_allclose(lut[:, :3], expected[:, :3], atol=1e-6)


# A table needs at least two entries to interpolate between
def test_transfer_lut_too_small():
    with pytest.raises(ValueError, match="at least 2"):
        ve.make_transfer_lut(size=1)


# Explicit color limits are used as they are
def test_finite_clim_explicit():
    assert ve.finite_clim(np.ones((2, 2)), (0.0, 5.0), None) == (0.0, 5.0)


# Without limits they are inferred from the data
def test_finite_clim_inferred():
    vmin, vmax = ve.finite_clim(np.linspace(0.0, 10.0, 101), None, None)
    assert vmin < vmax
    assert vmin >= 0.0
    assert vmax <= 10.0


# A constant array still gets two different limits
def test_finite_clim_constant():
    vmin, vmax = ve.finite_clim(np.ones((4, 4)), None, None)
    assert vmax > vmin


# Limits cannot be inferred when nothing is finite
def test_finite_clim_all_nan():
    with pytest.raises(ValueError, match="no finite values"):
        ve.finite_clim(np.full((2, 2), np.nan), None, None)


# A logarithmic norm only considers the positive values
def test_finite_clim_log():
    vmin, _ = ve.finite_clim(np.array([-5.0, 1.0, 10.0]), None, "log")
    assert vmin > 0.0


# A logarithmic norm needs at least one positive value
def test_finite_clim_log_without_positives():
    with pytest.raises(ValueError, match="at least one positive"):
        ve.finite_clim(np.array([-5.0, -1.0]), None, "log")


# Normalized values always end up between zero and one
def test_normalize_values():
    norm = mcol.Normalize(vmin=0.0, vmax=10.0)
    out = ve.normalize_values(np.array([-5.0, 0.0, 5.0, 10.0, 20.0]), norm)
    npt.assert_allclose(out, [0.0, 0.0, 0.5, 1.0, 1.0])


# No background at all means a transparent image
def test_resolve_background_none():
    assert ve.resolve_background(None) is None


# A named color is turned into its RGBA values
def test_resolve_background_named():
    npt.assert_allclose(ve.resolve_background("red"), [1.0, 0.0, 0.0, 1.0])


# The automatic background follows the active matplotlib style
def test_resolve_background_auto():
    assert ve.resolve_background("auto").shape == (4,)


# RGBA values can also be given directly
def test_resolve_background_tuple():
    npt.assert_allclose(
        ve.resolve_background((0.0, 0.0, 1.0, 1.0)), [0.0, 0.0, 1.0, 1.0]
    )


# A normalized vector keeps its direction and has unit length
def test_normalize_vec():
    out = ve._normalize_vec(np.array([3.0, 0.0, 0.0]))
    npt.assert_allclose(out, [1.0, 0.0, 0.0])
    assert np.linalg.norm(out) == pytest.approx(1.0)


# A ray aimed at the box enters and leaves it at the box faces
def test_ray_box_intersection_hit():
    """LONG TEST: CHECK"""
    origins = np.array([[-5.0, 0.5, 0.5]])
    direction = np.array([1.0, 0.0, 0.0])

    t_near, t_far, valid = ve._ray_box_intersection(
        origins, direction, unit_box
    )

    assert valid[0]
    assert t_near[0] == pytest.approx(5.0)
    assert t_far[0] == pytest.approx(6.0)


# A ray passing beside the box never enters it
def test_ray_box_intersection_miss():
    origins = np.array([[-5.0, 5.0, 0.5]])
    direction = np.array([1.0, 0.0, 0.0])
    assert not ve._ray_box_intersection(origins, direction, unit_box)[2][0]


# A ray starting inside the box enters it immediately
def test_ray_box_intersection_from_inside():
    origins = np.array([[0.5, 0.5, 0.5]])
    direction = np.array([1.0, 0.0, 0.0])
    t_near, _, valid = ve._ray_box_intersection(origins, direction, unit_box)
    assert valid[0]
    assert t_near[0] == pytest.approx(0.0)


# Sampling a volume at its corners gives back the corner values
def test_trilinear_sample_corners():
    volume = np.arange(8.0).reshape(2, 2, 2)
    points = np.array([[0.0, 0.0, 0.0], [1.0, 1.0, 1.0]])
    npt.assert_allclose(
        ve._trilinear_sample(volume, points, unit_box), [0.0, 7.0]
    )


# Sampling a constant volume gives that constant everywhere
def test_trilinear_sample_constant():
    volume = np.full((4, 4, 4), 2.5)
    points = np.array([[0.25, 0.5, 0.75], [0.1, 0.2, 0.3]])
    npt.assert_allclose(ve._trilinear_sample(volume, points, unit_box), 2.5)


# Halfway between two cells the value is their average
def test_trilinear_sample_midpoint():
    volume = np.zeros((2, 2, 2))
    volume[0, 0, 1] = 1.0
    value = ve._trilinear_sample(volume, np.array([[0.5, 0.0, 0.0]]), unit_box)
    assert value[0] == pytest.approx(0.5)


# The synthetic test volume is a cube of finite values
def test_synthetic_plume():
    data, extent = ve.synthetic_plume(8)
    assert data.shape == (8, 8, 8)
    assert np.all(np.isfinite(data))
    assert extent == (-1.0, 1.0, -1.0, 1.0, -1.0, 1.0)
