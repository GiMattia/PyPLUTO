"""Matplotlib-integrated volume rendering for uniform Cartesian grids.

Design goal
-----------
Use Matplotlib's Axes3D as the interactive camera/annotation layer and render
the volume into a synchronized 2-D RGBA underlay.

Data convention
---------------
The input volume is a NumPy array with shape (nz, ny, nx), i.e. ``vol[k, j, i]``
corresponds to physical coordinates (x, y, z).  The physical box is specified as
``extent=(xmin, xmax, ymin, ymax, zmin, zmax)``.

This is a pure-Python reference implementation.  The hot functions intended to
move to Rust later are ``render_volume_*_cpu``, ``_trilinear_sample`` and the
``_ray_box_intersection`` kernels.  ``PyPLUTO`` wraps this module through
``pyPLUTO.imagefuncs.volume.VolumeManager``; it is not part of the public API.
"""

from __future__ import annotations

import time
from collections.abc import Callable, Sequence
from dataclasses import dataclass
from typing import Literal, Union, cast

import matplotlib.pyplot as plt
import numpy as np
from matplotlib import cm, colors
from matplotlib.axes import Axes
from matplotlib.backend_bases import Event
from matplotlib.figure import Figure
from mpl_toolkits.mplot3d import Axes3D, proj3d

ArrayLike3D = Union[np.ndarray, Sequence[Sequence[Sequence[float]]]]
OpacitySpec = Union[
    str,
    tuple[str, float],
    tuple[str, float, float],
    tuple[str, float, float, float],
    Callable[[np.ndarray], np.ndarray],
]
NormSpec = Union[str, colors.Normalize]
BackgroundSpec = Union[str, tuple[float, float, float, float], None]


@dataclass
class VolumeCamera:
    """Orthographic camera derived from a Matplotlib Axes3D view.

    Parameters
    ----------
    center:
        Physical center of the volume box.
    forward:
        Unit vector pointing from the camera into the scene.
    right:
        Unit vector pointing to the right in screen coordinates.
    up:
        Unit vector pointing up in screen coordinates.
    half_height:
        Half-height of the view window in physical units.
    aspect:
        Width / height of the output image.
    ray_length:
        Distance from the camera plane to the volume center.  Must be larger
        than the volume radius.
    """

    center: np.ndarray
    forward: np.ndarray
    right: np.ndarray
    up: np.ndarray
    half_height: float
    aspect: float
    ray_length: float


@dataclass
class VolumeRenderOptions:
    """Quality and transfer-function options for the reference renderer.

    ``background="auto"`` derives the backdrop color from the active Matplotlib
    style (``rcParams["axes.facecolor"]``); ``None`` keeps the volume
    transparent; an explicit RGBA tuple fixes the color.
    """

    samples: int = 192
    resolution: int | tuple[int, int] = 512
    cmap: str = "magma"
    norm: NormSpec = "linear"
    clim: tuple[float, float] | None = None
    opacity: OpacitySpec = ("sigmoid", 0.35, 0.12, 1.0)
    opacity_scale: float = 8.0
    mode: Literal["composite", "mip", "average"] = "composite"
    background: BackgroundSpec = "auto"
    lut_size: int = 1024
    gamma: float = 1.0
    margin: float = 1.05
    set_orthographic: bool = True


# ---------------------------------------------------------------------------
# Basic data and transfer-function utilities
# ---------------------------------------------------------------------------


def as_zyx_volume(data: ArrayLike3D, *, dtype: type = np.float32) -> np.ndarray:
    """Return a finite 3-D C-contiguous array in (z, y, x) order.

    This function does not transpose.  It only validates the dimensionality and
    memory layout.
    """
    arr = np.asarray(data, dtype=dtype)
    if arr.ndim != 3:
        raise ValueError(f"expected a 3-D array, got shape {arr.shape}")
    if not np.isfinite(arr).any():
        raise ValueError("volume contains no finite values")
    return np.ascontiguousarray(arr)


def default_extent_for(
    data: np.ndarray,
) -> tuple[float, float, float, float, float, float]:
    """Return a unit-cell extent for a (nz, ny, nx) volume."""
    nz, ny, nx = data.shape
    return (0.0, float(nx - 1), 0.0, float(ny - 1), 0.0, float(nz - 1))


def extent_center_radius(
    extent: Sequence[float],
) -> tuple[np.ndarray, np.ndarray, float]:
    """Return center, side lengths, and bounding-sphere radius for an extent."""
    xmin, xmax, ymin, ymax, zmin, zmax = map(float, extent)
    center = np.array(
        [(xmin + xmax) / 2.0, (ymin + ymax) / 2.0, (zmin + zmax) / 2.0]
    )
    lengths = np.array([xmax - xmin, ymax - ymin, zmax - zmin], dtype=float)
    radius = 0.5 * float(np.linalg.norm(lengths))
    return center, lengths, radius


def make_mpl_norm(
    norm: NormSpec, clim: tuple[float, float]
) -> colors.Normalize:
    """Create a Matplotlib norm object from a small string API."""
    vmin, vmax = map(float, clim)
    if isinstance(norm, str):
        key = norm.lower()
        if key in ("linear", "lin", "none", "norm"):
            return colors.Normalize(vmin=vmin, vmax=vmax, clip=True)
        if key in ("log", "log10"):
            # Matplotlib LogNorm requires strictly positive vmin.
            tiny = np.nextafter(0.0, 1.0)
            return colors.LogNorm(
                vmin=max(vmin, tiny), vmax=max(vmax, tiny), clip=True
            )
        if key in ("symlog", "symmetric_log"):
            linthresh = max(1.0e-12, 1.0e-3 * max(abs(vmin), abs(vmax), 1.0))
            return colors.SymLogNorm(
                linthresh=linthresh, vmin=vmin, vmax=vmax, clip=True
            )
        raise ValueError(f"unknown norm {norm!r}")
    return norm


def finite_clim(
    data: np.ndarray,
    clim: tuple[float, float] | None,
    norm: NormSpec,
) -> tuple[float, float]:
    """Choose robust finite color limits if none are supplied."""
    if clim is not None:
        return float(clim[0]), float(clim[1])

    finite = np.asarray(data[np.isfinite(data)], dtype=np.float64)
    if finite.size == 0:
        raise ValueError(
            "cannot infer clim from an array with no finite values"
        )

    if isinstance(norm, str) and norm.lower() in ("log", "log10"):
        finite = finite[finite > 0.0]
        if finite.size == 0:
            raise ValueError(
                "log normalization requires at least one positive value"
            )

    # Percentiles avoid a single hot cell making the first image useless.
    vmin, vmax = np.percentile(finite, [1.0, 99.5])
    if not np.isfinite(vmin) or not np.isfinite(vmax) or vmin == vmax:
        vmin, vmax = float(np.nanmin(finite)), float(np.nanmax(finite))
    if vmin == vmax:
        vmax = vmin + 1.0
    return float(vmin), float(vmax)


def _opacity_curve(x: np.ndarray, opacity: OpacitySpec) -> np.ndarray:
    """Evaluate an opacity curve on normalized coordinates x in [0, 1]."""
    x = np.asarray(x, dtype=np.float32)

    if callable(opacity):
        return np.asarray(opacity(x), dtype=np.float32)

    if isinstance(opacity, tuple):
        name = str(opacity[0]).lower()
        args = opacity[1:]
    else:
        name = str(opacity).lower()
        args = ()

    if name in ("linear", "lin"):
        alpha = x
    elif name in ("constant", "flat"):
        alpha = np.ones_like(x) * (float(args[0]) if args else 1.0)
    elif name in ("none", "transparent", "zero"):
        alpha = np.zeros_like(x)
    elif name in ("sigmoid", "logistic"):
        center = float(args[0]) if len(args) >= 1 else 0.5
        width = float(args[1]) if len(args) >= 2 else 0.1
        gain = float(args[2]) if len(args) >= 3 else 1.0
        width = max(width, 1.0e-6)
        alpha = gain / (1.0 + np.exp(-(x - center) / width))
    elif name in ("power", "pow"):
        gamma = float(args[0]) if args else 2.0
        alpha = x**gamma
    elif name in ("window", "gaussian"):
        center = float(args[0]) if len(args) >= 1 else 0.5
        width = float(args[1]) if len(args) >= 2 else 0.15
        gain = float(args[2]) if len(args) >= 3 else 1.0
        width = max(width, 1.0e-6)
        alpha = gain * np.exp(-0.5 * ((x - center) / width) ** 2)
    else:
        raise ValueError(f"unknown opacity specification {opacity!r}")

    return np.clip(alpha, 0.0, 1.0).astype(np.float32)


def make_transfer_lut(
    *,
    cmap: str = "magma",
    opacity: OpacitySpec = ("sigmoid", 0.35, 0.12, 1.0),
    size: int = 1024,
    gamma: float = 1.0,
) -> np.ndarray:
    """Return an RGBA transfer-function lookup table sampled on [0, 1].

    The RGB channels come from a Matplotlib colormap.  The alpha channel is a
    separate opacity curve so colormap and transparency tune independently.
    """
    if size < 2:
        raise ValueError("lut size must be at least 2")
    x = np.linspace(0.0, 1.0, int(size), dtype=np.float32)
    if gamma != 1.0:
        x_for_color = np.clip(x, 0.0, 1.0) ** float(gamma)
    else:
        x_for_color = x

    rgba = plt.get_cmap(cmap)(x_for_color).astype(np.float32)
    rgba[:, 3] = _opacity_curve(x, opacity)
    return np.ascontiguousarray(rgba, dtype=np.float32)


def normalize_values(
    values: np.ndarray, norm_obj: colors.Normalize
) -> np.ndarray:
    """Map physical scalar values to [0, 1] using a Matplotlib norm."""
    out = norm_obj(values)
    # Some Matplotlib norms return masked arrays for invalid entries.
    if np.ma.isMaskedArray(out):
        out = out.filled(np.nan)
    out = np.asarray(out, dtype=np.float32)
    return np.clip(out, 0.0, 1.0)


def resolve_background(background: BackgroundSpec) -> np.ndarray | None:
    """Resolve a background spec to an RGBA tuple (or None for transparent).

    ``"auto"`` reads the active Matplotlib style so the volume matches e.g.
    ``plt.style.use("dark_background")``.
    """
    if background is None:
        return None
    if isinstance(background, str):
        if background.lower() == "auto":
            face = plt.rcParams.get("axes.facecolor", "white")
            return np.array(colors.to_rgba(face), dtype=np.float32)
        return np.array(colors.to_rgba(background), dtype=np.float32)
    return np.array(background, dtype=np.float32)


# ---------------------------------------------------------------------------
# Camera utilities
# ---------------------------------------------------------------------------


def _normalize_vec(
    v: np.ndarray, fallback: np.ndarray | None = None
) -> np.ndarray:
    v = np.asarray(v, dtype=np.float64)
    n = float(np.linalg.norm(v))
    if not np.isfinite(n) or n < 1.0e-14:
        if fallback is None:
            raise ValueError("cannot normalize a near-zero vector")
        return _normalize_vec(np.asarray(fallback, dtype=np.float64))
    return v / n


def mpl_view_basis(
    elev: float, azim: float, roll: float = 0.0
) -> tuple[np.ndarray, np.ndarray, np.ndarray]:
    """Approximate the Matplotlib Axes3D view as forward/right/up vectors.

    This is deliberately simple and orthographic.  It matches Matplotlib's view
    angles closely enough for the triad overlay.  Pixel rays for the actual
    render come from ``projected_rays_from_axes``.
    """
    er = np.deg2rad(float(elev))
    ar = np.deg2rad(float(azim))
    rr = np.deg2rad(float(roll))

    # Direction from scene center to camera.  The ray direction is opposite.
    eye = np.array(
        [np.cos(er) * np.cos(ar), np.cos(er) * np.sin(ar), np.sin(er)],
        dtype=np.float64,
    )
    forward = _normalize_vec(-eye)

    tmp_up = np.array([0.0, 0.0, 1.0], dtype=np.float64)
    if abs(float(np.dot(forward, tmp_up))) > 0.98:
        tmp_up = np.array([0.0, 1.0, 0.0], dtype=np.float64)

    right = _normalize_vec(
        np.cross(forward, tmp_up), fallback=np.array([1.0, 0.0, 0.0])
    )
    up = _normalize_vec(np.cross(right, forward), fallback=tmp_up)

    if rr != 0.0:
        c, s = np.cos(rr), np.sin(rr)
        right0, up0 = right.copy(), up.copy()
        right = c * right0 + s * up0
        up = -s * right0 + c * up0

    return (
        forward.astype(np.float64),
        right.astype(np.float64),
        up.astype(np.float64),
    )


def camera_from_axes(
    ax: Axes3D,
    extent: Sequence[float],
    *,
    width: int,
    height: int,
    margin: float = 1.05,
) -> VolumeCamera:
    """Build an orthographic camera from an Axes3D object."""
    center, _lengths, radius = extent_center_radius(extent)
    aspect = float(width) / max(float(height), 1.0)

    elev = float(getattr(ax, "elev", 30.0))
    azim = float(getattr(ax, "azim", -60.0))
    roll = float(getattr(ax, "roll", 0.0))
    forward, right, up = mpl_view_basis(elev, azim, roll)

    # Fit the full bounding sphere in the output.  This is conservative, which
    # is good because it prevents clipping during rotation.
    half_height = max(radius * float(margin), 1.0e-12)
    ray_length = 4.0 * max(radius, 1.0)

    return VolumeCamera(
        center=center,
        forward=forward,
        right=right,
        up=up,
        half_height=half_height,
        aspect=aspect,
        ray_length=ray_length,
    )


def camera_signature(
    ax: Axes3D, width: int, height: int, samples: int
) -> tuple:
    """Small immutable key used to decide whether a re-render is needed."""
    try:
        proj_key = tuple(
            np.round(np.asarray(ax.get_proj(), dtype=np.float64).ravel(), 10)
        )
    except Exception:
        proj_key = ()

    if (bbox := getattr(ax, "bbox", None)) is not None:
        bbox_key = (
            round(float(bbox.x0), 4),
            round(float(bbox.y0), 4),
            round(float(bbox.width), 4),
            round(float(bbox.height), 4),
        )
    else:
        bbox_key = ()

    return (
        proj_key,
        bbox_key,
        tuple(round(float(v), 8) for v in ax.get_xlim()),
        tuple(round(float(v), 8) for v in ax.get_ylim()),
        tuple(round(float(v), 8) for v in ax.get_zlim()),
        int(width),
        int(height),
        int(samples),
    )


# ---------------------------------------------------------------------------
# Ray marching kernels.  These are the main candidates for Rust.
# ---------------------------------------------------------------------------


def _ray_box_intersection(
    origins: np.ndarray,
    direction: np.ndarray,
    extent: Sequence[float],
) -> tuple[np.ndarray, np.ndarray, np.ndarray]:
    """Vectorized ray/AABB intersection for many origins and one direction."""
    origins = np.asarray(origins, dtype=np.float64)
    direction = np.asarray(direction, dtype=np.float64)
    bmin = np.array([extent[0], extent[2], extent[4]], dtype=np.float64)
    bmax = np.array([extent[1], extent[3], extent[5]], dtype=np.float64)

    t_near = np.full(origins.shape[0], -np.inf, dtype=np.float64)
    t_far = np.full(origins.shape[0], np.inf, dtype=np.float64)
    valid = np.ones(origins.shape[0], dtype=bool)

    for axis in range(3):
        d = float(direction[axis])
        o = origins[:, axis]
        if abs(d) < 1.0e-14:
            valid &= (o >= bmin[axis]) & (o <= bmax[axis])
            continue
        t0 = (bmin[axis] - o) / d
        t1 = (bmax[axis] - o) / d
        lo = np.minimum(t0, t1)
        hi = np.maximum(t0, t1)
        t_near = np.maximum(t_near, lo)
        t_far = np.minimum(t_far, hi)

    valid &= t_far > t_near
    valid &= t_far > 0.0
    t_near = np.maximum(t_near, 0.0)
    return t_near, t_far, valid


def _ray_box_intersection_many(
    origins: np.ndarray,
    directions: np.ndarray,
    extent: Sequence[float],
) -> tuple[np.ndarray, np.ndarray, np.ndarray]:
    """Vectorized ray/AABB intersection for many origins and directions."""
    origins = np.asarray(origins, dtype=np.float64)
    directions = np.asarray(directions, dtype=np.float64)
    if origins.ndim != 2 or origins.shape[1] != 3:
        raise ValueError("origins must have shape (n, 3)")
    if directions.shape != origins.shape:
        raise ValueError("directions must have the same shape as origins")

    bmin = np.array([extent[0], extent[2], extent[4]], dtype=np.float64)
    bmax = np.array([extent[1], extent[3], extent[5]], dtype=np.float64)

    n = origins.shape[0]
    t_near = np.full(n, -np.inf, dtype=np.float64)
    t_far = np.full(n, np.inf, dtype=np.float64)
    valid = np.ones(n, dtype=bool)

    eps = 1.0e-14
    for axis in range(3):
        d = directions[:, axis]
        o = origins[:, axis]
        parallel = np.abs(d) < eps
        valid &= ~(parallel & ((o < bmin[axis]) | (o > bmax[axis])))

        nonpar = ~parallel
        if np.any(nonpar):
            t0 = (bmin[axis] - o[nonpar]) / d[nonpar]
            t1 = (bmax[axis] - o[nonpar]) / d[nonpar]
            lo = np.minimum(t0, t1)
            hi = np.maximum(t0, t1)
            t_near[nonpar] = np.maximum(t_near[nonpar], lo)
            t_far[nonpar] = np.minimum(t_far[nonpar], hi)

    valid &= t_far > t_near
    valid &= t_far > 0.0
    t_near = np.maximum(t_near, 0.0)
    return t_near, t_far, valid


def _projected_box_depth_range(
    ax: Axes3D, extent: Sequence[float]
) -> tuple[float, float]:
    """Return a padded projected z-range for the box in the current view."""
    xmin, xmax, ymin, ymax, zmin, zmax = map(float, extent)
    corners = np.array(
        [
            [x, y, z]
            for x in (xmin, xmax)
            for y in (ymin, ymax)
            for z in (zmin, zmax)
        ],
        dtype=np.float64,
    )

    matrix = ax.get_proj()
    _xp, _yp, zp = proj3d.proj_transform(
        corners[:, 0], corners[:, 1], corners[:, 2], matrix
    )
    zp = np.asarray(zp, dtype=np.float64)
    zp = zp[np.isfinite(zp)]

    if zp.size == 0:
        return 0.0, 1.0

    z0, z1 = float(np.min(zp)), float(np.max(zp))
    if z0 == z1:
        z0 -= 1.0
        z1 += 1.0

    pad = 0.25 * abs(z1 - z0) + 1.0e-6
    return z0 - pad, z1 + pad


def projected_rays_from_axes(
    ax: Axes3D,
    extent: Sequence[float],
    *,
    width: int,
    height: int,
) -> tuple[np.ndarray, np.ndarray]:
    """Build one ray per output pixel from the actual Axes3D projection.

    This follows the same path as Matplotlib in reverse:
    display pixel -> mplot3d projected x/y -> inverse ``ax.get_proj()`` -> ray.
    The returned origins and directions are in data coordinates.
    """
    width = int(width)
    height = int(height)
    if width < 2 or height < 2:
        raise ValueError("width and height must be at least 2")

    matrix = ax.get_proj()
    inv_matrix = np.linalg.inv(matrix)

    bbox = ax.bbox
    disp_x = float(bbox.x0) + (
        np.arange(width, dtype=np.float64) + 0.5
    ) * float(bbox.width) / float(width)
    # Row zero of imshow is the top row.
    disp_y = float(bbox.y1) - (
        np.arange(height, dtype=np.float64) + 0.5
    ) * float(bbox.height) / float(height)
    xx, yy = np.meshgrid(disp_x, disp_y, indexing="xy")

    xy_proj = ax.transData.inverted().transform(
        np.column_stack([xx.ravel(), yy.ravel()])
    )
    xp = xy_proj[:, 0]
    yp = xy_proj[:, 1]

    z_near, z_far = _projected_box_depth_range(ax, extent)

    x0, y0, z0 = proj3d.inv_transform(
        xp, yp, np.full_like(xp, z_near), inv_matrix
    )
    x1, y1, z1 = proj3d.inv_transform(
        xp, yp, np.full_like(xp, z_far), inv_matrix
    )

    origins = np.column_stack([x0, y0, z0]).astype(np.float64, copy=False)
    farpts = np.column_stack([x1, y1, z1]).astype(np.float64, copy=False)

    vec = farpts - origins
    length = np.linalg.norm(vec, axis=1)
    good = np.isfinite(length) & (length > 0.0)

    directions = np.zeros_like(vec)
    directions[good] = vec[good] / length[good, None]

    # Invalid rays are harmless; they will miss the box.
    origins[~good] = 0.0
    directions[~good] = np.array([0.0, 0.0, 1.0])
    return origins, directions


def _composite_background(
    rgba: np.ndarray,
    *,
    height: int,
    width: int,
    background: np.ndarray | None,
) -> np.ndarray:
    """Composite flattened RGBA pixels over a constant background."""
    if background is not None:
        bg = np.asarray(background, dtype=np.float32)
        bg_rgb = bg[:3]
        bg_alpha = bg[3] if bg.size >= 4 else 1.0
        out_rgb = rgba[:, :3] + (1.0 - rgba[:, 3:4]) * bg_rgb[None, :]
        out_alpha = rgba[:, 3] + (1.0 - rgba[:, 3]) * bg_alpha
        rgba[:, :3] = out_rgb
        rgba[:, 3] = out_alpha

    return np.clip(rgba.reshape(height, width, 4), 0.0, 1.0)


def _box_diagonal(extent: Sequence[float]) -> float:
    """Return the bounding-box diagonal length (clamped away from zero)."""
    return max(
        float(
            np.linalg.norm(
                np.array(
                    [
                        extent[1] - extent[0],
                        extent[3] - extent[2],
                        extent[5] - extent[4],
                    ],
                    dtype=float,
                )
            )
        ),
        1.0e-12,
    )


def render_volume_from_rays_cpu(
    volume: np.ndarray,
    *,
    extent: Sequence[float],
    origins: np.ndarray,
    directions: np.ndarray,
    norm_obj: colors.Normalize,
    lut: np.ndarray,
    samples: int = 192,
    mode: Literal["composite", "mip", "average"] = "composite",
    opacity_scale: float = 8.0,
    background: np.ndarray | None = None,
    width: int = 512,
    height: int = 512,
) -> np.ndarray:
    """Render a volume from arbitrary per-pixel rays.

    This is the function to mirror in Rust.  Every pixel may have its own ray
    direction, which is required for exact Matplotlib projection matching.
    """
    vol = as_zyx_volume(volume)
    lut = np.asarray(lut, dtype=np.float32)
    origins = np.asarray(origins, dtype=np.float64)
    directions = np.asarray(directions, dtype=np.float64)

    if lut.ndim != 2 or lut.shape[1] != 4:
        raise ValueError("lut must have shape (n, 4)")
    if (
        origins.shape != directions.shape
        or origins.ndim != 2
        or origins.shape[1] != 3
    ):
        raise ValueError("origins and directions must have shape (n, 3)")
    if origins.shape[0] != int(width) * int(height):
        raise ValueError("number of rays must equal width * height")

    samples = int(samples)
    if samples < 1:
        raise ValueError("samples must be positive")

    t0, t1, valid = _ray_box_intersection_many(origins, directions, extent)
    npix = origins.shape[0]

    rgb_acc = np.zeros((npix, 3), dtype=np.float32)
    alpha_acc = np.zeros(npix, dtype=np.float32)

    if not np.any(valid):
        rgba = np.zeros((npix, 4), dtype=np.float32)
        return _composite_background(
            rgba, height=height, width=width, background=background
        )

    valid_idx = np.flatnonzero(valid)
    ov = origins[valid_idx]
    dv = directions[valid_idx]
    t0v = t0[valid_idx]
    t1v = t1[valid_idx]
    path = np.maximum(t1v - t0v, 1.0e-12)

    diag = _box_diagonal(extent)
    lut_last = lut.shape[0] - 1

    if mode == "mip":
        best_u = np.full(valid_idx.size, -np.inf, dtype=np.float32)
        for isamp in range(samples):
            frac = (isamp + 0.5) / samples
            tt = t0v + frac * path
            pts = ov + tt[:, None] * dv
            vals = _trilinear_sample(vol, pts, extent)
            u = normalize_values(vals, norm_obj)
            u[~np.isfinite(u)] = -np.inf
            best_u = np.maximum(best_u, u)

        best_u = np.clip(best_u, 0.0, 1.0)
        idx = np.asarray(best_u * lut_last, dtype=np.int64)
        rgb_acc[valid_idx] = lut[idx, :3]
        alpha_acc[valid_idx] = 1.0

    elif mode == "average":
        sum_u = np.zeros(valid_idx.size, dtype=np.float32)
        count = np.zeros(valid_idx.size, dtype=np.float32)
        for isamp in range(samples):
            frac = (isamp + 0.5) / samples
            tt = t0v + frac * path
            pts = ov + tt[:, None] * dv
            vals = _trilinear_sample(vol, pts, extent)
            u = normalize_values(vals, norm_obj)
            m = np.isfinite(u)
            sum_u[m] += u[m]
            count[m] += 1.0

        mean_u = np.divide(sum_u, np.maximum(count, 1.0), dtype=np.float32)
        idx = np.asarray(np.clip(mean_u, 0.0, 1.0) * lut_last, dtype=np.int64)
        rgb_acc[valid_idx] = lut[idx, :3]
        alpha_acc[valid_idx] = 1.0

    elif mode == "composite":
        local_rgb = np.zeros((valid_idx.size, 3), dtype=np.float32)
        local_alpha = np.zeros(valid_idx.size, dtype=np.float32)

        for isamp in range(samples):
            alive = local_alpha < 0.995
            if not np.any(alive):
                break

            frac = (isamp + 0.5) / samples
            tt = t0v[alive] + frac * path[alive]
            pts = ov[alive] + tt[:, None] * dv[alive]
            vals = _trilinear_sample(vol, pts, extent)
            u = normalize_values(vals, norm_obj)
            good = np.isfinite(u)
            if not np.any(good):
                continue

            idx = np.asarray(
                np.clip(u[good], 0.0, 1.0) * lut_last, dtype=np.int64
            )
            rgba_i = lut[idx]

            # Interpret opacity as absorption density per unit path.
            ds = path[alive][good] / float(samples)
            alpha_i = 1.0 - np.exp(
                -float(opacity_scale) * rgba_i[:, 3] * ds / diag
            )
            alpha_i = np.clip(alpha_i, 0.0, 1.0).astype(np.float32)

            alive_indices = np.flatnonzero(alive)
            target = alive_indices[good]
            one_minus = 1.0 - local_alpha[target]
            local_rgb[target] += (one_minus * alpha_i)[:, None] * rgba_i[:, :3]
            local_alpha[target] += one_minus * alpha_i

        rgb_acc[valid_idx] = local_rgb
        alpha_acc[valid_idx] = local_alpha

    else:
        raise ValueError(f"unknown render mode {mode!r}")

    rgba = np.zeros((npix, 4), dtype=np.float32)
    rgba[:, :3] = rgb_acc
    rgba[:, 3] = alpha_acc

    return _composite_background(
        rgba, height=height, width=width, background=background
    )


def render_volume_projected_cpu(
    volume: np.ndarray,
    *,
    extent: Sequence[float],
    ax: Axes3D,
    norm_obj: colors.Normalize,
    lut: np.ndarray,
    samples: int = 192,
    mode: Literal["composite", "mip", "average"] = "composite",
    opacity_scale: float = 8.0,
    background: np.ndarray | None = None,
    width: int = 512,
    height: int = 512,
) -> np.ndarray:
    """Render the volume using the exact current Axes3D projection."""
    origins, directions = projected_rays_from_axes(
        ax, extent, width=width, height=height
    )
    return render_volume_from_rays_cpu(
        volume,
        extent=extent,
        origins=origins,
        directions=directions,
        norm_obj=norm_obj,
        lut=lut,
        samples=samples,
        mode=mode,
        opacity_scale=opacity_scale,
        background=background,
        width=width,
        height=height,
    )


def _trilinear_sample(
    volume: np.ndarray,
    points: np.ndarray,
    extent: Sequence[float],
    *,
    fill_value: float = np.nan,
) -> np.ndarray:
    """Sample a (nz, ny, nx) volume at physical points (x, y, z)."""
    vol = volume
    nz, ny, nx = vol.shape
    xmin, xmax, ymin, ymax, zmin, zmax = map(float, extent)

    p = np.asarray(points, dtype=np.float64)
    x, y, z = p[:, 0], p[:, 1], p[:, 2]

    # Convert physical coordinates to fractional cell indices.
    fx = (
        (x - xmin) / (xmax - xmin) * (nx - 1)
        if xmax != xmin
        else np.zeros_like(x)
    )
    fy = (
        (y - ymin) / (ymax - ymin) * (ny - 1)
        if ymax != ymin
        else np.zeros_like(y)
    )
    fz = (
        (z - zmin) / (zmax - zmin) * (nz - 1)
        if zmax != zmin
        else np.zeros_like(z)
    )

    valid = (
        (fx >= 0.0)
        & (fx <= nx - 1)
        & (fy >= 0.0)
        & (fy <= ny - 1)
        & (fz >= 0.0)
        & (fz <= nz - 1)
    )
    out = np.full(p.shape[0], fill_value, dtype=np.float32)
    if not np.any(valid):
        return out

    fxv = fx[valid]
    fyv = fy[valid]
    fzv = fz[valid]

    i0 = np.floor(fxv).astype(np.int64)
    j0 = np.floor(fyv).astype(np.int64)
    k0 = np.floor(fzv).astype(np.int64)
    i1 = np.minimum(i0 + 1, nx - 1)
    j1 = np.minimum(j0 + 1, ny - 1)
    k1 = np.minimum(k0 + 1, nz - 1)

    wx = (fxv - i0).astype(np.float32)
    wy = (fyv - j0).astype(np.float32)
    wz = (fzv - k0).astype(np.float32)

    c000 = vol[k0, j0, i0]
    c100 = vol[k0, j0, i1]
    c010 = vol[k0, j1, i0]
    c110 = vol[k0, j1, i1]
    c001 = vol[k1, j0, i0]
    c101 = vol[k1, j0, i1]
    c011 = vol[k1, j1, i0]
    c111 = vol[k1, j1, i1]

    c00 = c000 * (1.0 - wx) + c100 * wx
    c10 = c010 * (1.0 - wx) + c110 * wx
    c01 = c001 * (1.0 - wx) + c101 * wx
    c11 = c011 * (1.0 - wx) + c111 * wx
    c0 = c00 * (1.0 - wy) + c10 * wy
    c1 = c01 * (1.0 - wy) + c11 * wy
    c = c0 * (1.0 - wz) + c1 * wz

    out[valid] = c.astype(np.float32)
    return out


def _resolve_resolution(
    resolution: int | tuple[int, int],
) -> tuple[int, int]:
    """Return (width, height) from an integer or tuple."""
    if isinstance(resolution, tuple):
        width, height = int(resolution[0]), int(resolution[1])
    else:
        width = height = int(resolution)
    if width < 2 or height < 2:
        raise ValueError(
            "resolution must be at least 2 pixels in each direction"
        )
    return width, height


def render_volume_cpu(
    volume: np.ndarray,
    *,
    extent: Sequence[float],
    camera: VolumeCamera,
    norm_obj: colors.Normalize,
    lut: np.ndarray,
    samples: int = 192,
    mode: Literal["composite", "mip", "average"] = "composite",
    opacity_scale: float = 8.0,
    background: np.ndarray | None = None,
    width: int = 512,
    height: int = 512,
) -> np.ndarray:
    """Render a volume to an RGBA image using a fixed orthographic camera.

    This is the simpler reference path that does not depend on a live Axes3D
    projection.  It favors clarity over speed.
    """
    vol = as_zyx_volume(volume)
    lut = np.asarray(lut, dtype=np.float32)
    if lut.ndim != 2 or lut.shape[1] != 4:
        raise ValueError("lut must have shape (n, 4)")

    samples = int(samples)
    if samples < 1:
        raise ValueError("samples must be positive")

    # Pixel centers in camera-screen coordinates.  Row 0 is the top of imshow.
    xs = np.linspace(
        -camera.half_height * camera.aspect,
        camera.half_height * camera.aspect,
        width,
        dtype=np.float64,
    )
    ys = np.linspace(
        camera.half_height, -camera.half_height, height, dtype=np.float64
    )
    xx, yy = np.meshgrid(xs, ys, indexing="xy")

    origins = (
        camera.center[None, :]
        + xx.reshape(-1, 1) * camera.right[None, :]
        + yy.reshape(-1, 1) * camera.up[None, :]
        - camera.ray_length * camera.forward[None, :]
    )
    direction = camera.forward.astype(np.float64)

    t0, t1, valid = _ray_box_intersection(origins, direction, extent)
    npix = origins.shape[0]

    rgb_acc = np.zeros((npix, 3), dtype=np.float32)
    alpha_acc = np.zeros(npix, dtype=np.float32)

    if not np.any(valid):
        rgba = np.zeros((npix, 4), dtype=np.float32)
        return _composite_background(
            rgba, height=height, width=width, background=background
        )

    valid_idx = np.flatnonzero(valid)
    ov = origins[valid_idx]
    t0v = t0[valid_idx]
    t1v = t1[valid_idx]
    path = np.maximum(t1v - t0v, 1.0e-12)
    diag = _box_diagonal(extent)
    lut_last = lut.shape[0] - 1

    if mode == "mip":
        best_u = np.full(valid_idx.size, -np.inf, dtype=np.float32)
        for isamp in range(samples):
            frac = (isamp + 0.5) / samples
            tt = t0v + frac * path
            pts = ov + tt[:, None] * direction[None, :]
            vals = _trilinear_sample(vol, pts, extent)
            u = normalize_values(vals, norm_obj)
            u[~np.isfinite(u)] = -np.inf
            best_u = np.maximum(best_u, u)
        best_u = np.clip(best_u, 0.0, 1.0)
        idx = np.asarray(best_u * lut_last, dtype=np.int64)
        rgb_acc[valid_idx] = lut[idx, :3]
        alpha_acc[valid_idx] = 1.0

    elif mode == "average":
        sum_u = np.zeros(valid_idx.size, dtype=np.float32)
        count = np.zeros(valid_idx.size, dtype=np.float32)
        for isamp in range(samples):
            frac = (isamp + 0.5) / samples
            tt = t0v + frac * path
            pts = ov + tt[:, None] * direction[None, :]
            vals = _trilinear_sample(vol, pts, extent)
            u = normalize_values(vals, norm_obj)
            m = np.isfinite(u)
            sum_u[m] += u[m]
            count[m] += 1.0
        mean_u = np.divide(sum_u, np.maximum(count, 1.0), dtype=np.float32)
        idx = np.asarray(np.clip(mean_u, 0.0, 1.0) * lut_last, dtype=np.int64)
        rgb_acc[valid_idx] = lut[idx, :3]
        alpha_acc[valid_idx] = 1.0

    elif mode == "composite":
        local_rgb = np.zeros((valid_idx.size, 3), dtype=np.float32)
        local_alpha = np.zeros(valid_idx.size, dtype=np.float32)

        for isamp in range(samples):
            alive = local_alpha < 0.995
            if not np.any(alive):
                break

            frac = (isamp + 0.5) / samples
            tt = t0v[alive] + frac * path[alive]
            pts = ov[alive] + tt[:, None] * direction[None, :]
            vals = _trilinear_sample(vol, pts, extent)
            u = normalize_values(vals, norm_obj)
            good = np.isfinite(u)
            if not np.any(good):
                continue

            idx = np.asarray(
                np.clip(u[good], 0.0, 1.0) * lut_last, dtype=np.int64
            )
            rgba_i = lut[idx]

            ds = path[alive][good] / float(samples)
            alpha_i = 1.0 - np.exp(
                -float(opacity_scale) * rgba_i[:, 3] * ds / diag
            )
            alpha_i = np.clip(alpha_i, 0.0, 1.0).astype(np.float32)

            alive_indices = np.flatnonzero(alive)
            target = alive_indices[good]
            one_minus = 1.0 - local_alpha[target]
            local_rgb[target] += (one_minus * alpha_i)[:, None] * rgba_i[:, :3]
            local_alpha[target] += one_minus * alpha_i

        rgb_acc[valid_idx] = local_rgb
        alpha_acc[valid_idx] = local_alpha

    else:
        raise ValueError(f"unknown render mode {mode!r}")

    rgba = np.zeros((npix, 4), dtype=np.float32)
    rgba[:, :3] = rgb_acc
    rgba[:, 3] = alpha_acc

    return _composite_background(
        rgba, height=height, width=width, background=background
    )


# ---------------------------------------------------------------------------
# Matplotlib integration
# ---------------------------------------------------------------------------


def _make_transparent_3d_axes(ax: Axes3D) -> None:
    """Let a 2-D underlay image show through an Axes3D."""
    try:
        ax.patch.set_alpha(0.0)
    except Exception:
        pass
    edge = colors.to_rgba(plt.rcParams.get("axes.edgecolor", "0.6"), 0.35)
    for axis_name in ("xaxis", "yaxis", "zaxis"):
        axis = getattr(ax, axis_name, None)
        if axis is None:
            continue
        pane = getattr(axis, "pane", None)
        if pane is not None:
            try:
                pane.set_facecolor((1.0, 1.0, 1.0, 0.0))
                pane.set_edgecolor(edge)
                pane.set_alpha(0.0)
            except Exception:
                pass


def _sync_axes_position(overlay_ax: Axes3D, underlay_ax: Axes) -> None:
    """Make the image underlay occupy exactly the same bbox as the 3D axes."""
    underlay_ax.set_position(overlay_ax.get_position())


def _fig_add_underlay_axes(ax3d: Axes3D) -> Axes:
    fig = ax3d.figure
    pos = ax3d.get_position()
    image_ax = fig.add_axes(
        pos.bounds,
        label=f"_volume_underlay_{id(ax3d)}",
        zorder=ax3d.get_zorder() - 1,
    )
    image_ax.set_axis_off()
    image_ax.set_xlim(0, 1)
    image_ax.set_ylim(0, 1)
    image_ax.patch.set_alpha(0.0)
    ax3d.set_zorder(image_ax.get_zorder() + 1)
    _make_transparent_3d_axes(ax3d)
    return image_ax


class MPLVolumeRenderer:
    """Attach a software volume renderer to a Matplotlib Axes3D.

    The volume is an RGBA image drawn in a 2-D axes underneath the 3-D axes.
    The 3-D axes remain responsible for camera manipulation, box, ticks,
    labels, and view state.
    """

    def __init__(
        self,
        data: ArrayLike3D,
        *,
        ax: Axes3D | None = None,
        extent: Sequence[float] | None = None,
        options: VolumeRenderOptions | None = None,
        interactive: bool = True,
        preview_resolution: int = 192,
        preview_samples: int = 64,
        triad: bool = False,
        colorbar: bool = True,
        show_grid: bool = False,
        throttle_s: float = 0.05,
    ) -> None:
        """Initialize the renderer and draw the first frame."""
        self.volume = as_zyx_volume(data)
        self.extent = tuple(
            map(
                float,
                extent
                if extent is not None
                else default_extent_for(self.volume),
            )
        )
        self.options = options if options is not None else VolumeRenderOptions()
        self.interactive = bool(interactive)
        self.preview_resolution = int(preview_resolution)
        self.preview_samples = int(preview_samples)
        self.triad_enabled = bool(triad)
        self.colorbar_enabled = bool(colorbar)
        self.show_grid = bool(show_grid)
        self.throttle_s = float(throttle_s)

        if ax is None:
            fig = plt.figure()
            ax = fig.add_subplot(111, projection="3d")
        self.ax3d = ax
        self.fig = cast(Figure, ax.figure)
        # tight/constrained layout is incompatible with Axes3D and would warn
        # on every draw; the underlay/overlay/triad positions are synced
        # manually, so a fixed layout is what we want here anyway.
        try:
            self.fig.set_layout_engine("none")
        except Exception:
            pass
        self.image_ax = _fig_add_underlay_axes(ax)
        self.image_artist = None
        self.colorbar = None
        self.triad_ax = None
        self._connections: list[int] = []
        self._last_signature: tuple | None = None
        self._last_view_sig: tuple | None = None
        self._last_t = 0.0
        self._dragging = False
        self._is_rendering = False
        self._home_view: dict | None = None
        self._orig_home = None

        self.clim = finite_clim(
            self.volume, self.options.clim, self.options.norm
        )
        self.norm_obj = make_mpl_norm(self.options.norm, self.clim)
        self.lut = make_transfer_lut(
            cmap=self.options.cmap,
            opacity=self.options.opacity,
            size=self.options.lut_size,
            gamma=self.options.gamma,
        )

        xmin, xmax, ymin, ymax, zmin, zmax = self.extent
        self.ax3d.set_xlim(xmin, xmax)
        self.ax3d.set_ylim(ymin, ymax)
        self.ax3d.set_zlim(zmin, zmax)
        try:
            self.ax3d.set_box_aspect((xmax - xmin, ymax - ymin, zmax - zmin))
        except Exception:
            pass
        if self.options.set_orthographic:
            try:
                self.ax3d.set_proj_type("ortho")
            except Exception:
                pass

        try:
            self.ax3d.grid(self.show_grid)
        except Exception:
            pass

        if self.colorbar_enabled:
            self._make_colorbar()
        if self.triad_enabled:
            self._make_triad_axes()

        self._store_home_view()

        if self.interactive:
            self.connect()
            self._install_home_hook()

        self.render(final=True, force=True)

    # ---------------- public API ----------------

    def connect(self) -> MPLVolumeRenderer:
        """Connect the Matplotlib event handlers for interactivity."""
        canvas = self.fig.canvas
        self._connections.extend(
            [
                canvas.mpl_connect("button_press_event", self._on_button_press),
                canvas.mpl_connect(
                    "button_release_event", self._on_button_release
                ),
                canvas.mpl_connect("motion_notify_event", self._on_motion),
                canvas.mpl_connect("scroll_event", self._on_scroll),
                canvas.mpl_connect("resize_event", self._on_resize),
                canvas.mpl_connect("draw_event", self._on_draw),
            ]
        )
        return self

    def disconnect(self) -> None:
        """Disconnect all Matplotlib event handlers."""
        for cid in self._connections:
            try:
                self.fig.canvas.mpl_disconnect(cid)
            except Exception:
                pass
        self._connections.clear()

    def set_clim(self, vmin: float, vmax: float) -> MPLVolumeRenderer:
        """Set the color limits and re-render."""
        self.clim = (float(vmin), float(vmax))
        self.norm_obj = make_mpl_norm(self.options.norm, self.clim)
        if self.colorbar is not None:
            self.colorbar.mappable.set_norm(self.norm_obj)
            self.colorbar.update_normal(self.colorbar.mappable)
        self.render(final=True, force=True)
        self.fig.canvas.draw_idle()
        return self

    def set_cmap(self, cmap: str) -> MPLVolumeRenderer:
        """Set the colormap and re-render."""
        self.options.cmap = str(cmap)
        self.lut = make_transfer_lut(
            cmap=self.options.cmap,
            opacity=self.options.opacity,
            size=self.options.lut_size,
            gamma=self.options.gamma,
        )
        if self.colorbar is not None:
            self.colorbar.mappable.set_cmap(self.options.cmap)
            self.colorbar.update_normal(self.colorbar.mappable)
        self.render(final=True, force=True)
        self.fig.canvas.draw_idle()
        return self

    def set_opacity(
        self,
        opacity: OpacitySpec,
        *,
        opacity_scale: float | None = None,
    ) -> MPLVolumeRenderer:
        """Set the opacity transfer function and re-render."""
        self.options.opacity = opacity
        if opacity_scale is not None:
            self.options.opacity_scale = float(opacity_scale)
        self.lut = make_transfer_lut(
            cmap=self.options.cmap,
            opacity=self.options.opacity,
            size=self.options.lut_size,
            gamma=self.options.gamma,
        )
        self.render(final=True, force=True)
        self.fig.canvas.draw_idle()
        return self

    def set_quality(
        self,
        *,
        resolution: int | tuple[int, int] | None = None,
        samples: int | None = None,
        preview_resolution: int | None = None,
        preview_samples: int | None = None,
    ) -> MPLVolumeRenderer:
        """Set render resolution / sample counts and re-render."""
        if resolution is not None:
            self.options.resolution = resolution
        if samples is not None:
            self.options.samples = int(samples)
        if preview_resolution is not None:
            self.preview_resolution = int(preview_resolution)
        if preview_samples is not None:
            self.preview_samples = int(preview_samples)
        self.render(final=True, force=True)
        self.fig.canvas.draw_idle()
        return self

    def set_grid(self, visible: bool = False) -> MPLVolumeRenderer:
        """Toggle the 3-D grid."""
        self.show_grid = bool(visible)
        try:
            self.ax3d.grid(self.show_grid)
        except Exception:
            pass
        self.fig.canvas.draw_idle()
        return self

    def render(self, *, final: bool = True, force: bool = False) -> np.ndarray:
        """Render and update the underlay image.  Returns the RGBA buffer."""
        if self._is_rendering:
            # Avoid recursive rendering from draw callbacks.
            return (
                np.asarray(self.image_artist.get_array(), dtype=np.float32)
                if self.image_artist is not None
                else np.zeros((2, 2, 4))
            )

        self._is_rendering = True
        try:
            _sync_axes_position(self.ax3d, self.image_ax)
            self._sync_triad_position()

            if final:
                width, height = _resolve_resolution(self.options.resolution)
                samples = int(self.options.samples)
            else:
                width, height = _resolve_resolution(self.preview_resolution)
                samples = int(self.preview_samples)

            sig = camera_signature(self.ax3d, width, height, samples)
            if not force and sig == self._last_signature:
                return (
                    np.asarray(self.image_artist.get_array(), dtype=np.float32)
                    if self.image_artist is not None
                    else np.zeros((height, width, 4))
                )

            rgba = render_volume_projected_cpu(
                self.volume,
                extent=self.extent,
                ax=self.ax3d,
                norm_obj=self.norm_obj,
                lut=self.lut,
                samples=samples,
                mode=self.options.mode,
                opacity_scale=self.options.opacity_scale,
                background=resolve_background(self.options.background),
                width=width,
                height=height,
            )

            if self.image_artist is None:
                self.image_artist = self.image_ax.imshow(
                    rgba,
                    origin="upper",
                    interpolation="bilinear" if not final else "nearest",
                    aspect="auto",
                    extent=(0, 1, 0, 1),
                )
            else:
                self.image_artist.set_data(rgba)
                self.image_artist.set_interpolation(
                    "nearest" if final else "bilinear"
                )

            self._last_signature = sig
            self._last_view_sig = self._view_signature()
            if self.triad_enabled:
                self.update_triad()
            return rgba
        finally:
            self._is_rendering = False

    def savefig(
        self, path: str, *, dpi: int = 200, final: bool = True
    ) -> MPLVolumeRenderer:
        """Render at full quality and save the figure."""
        self.render(final=final, force=True)
        self.fig.savefig(path, dpi=dpi)
        return self

    # ---------------- colorbar and triad ----------------

    def _make_colorbar(self) -> None:
        sm = cm.ScalarMappable(norm=self.norm_obj, cmap=self.options.cmap)
        sm.set_array([])
        self.colorbar = self.fig.colorbar(
            sm, ax=self.ax3d, fraction=0.046, pad=0.04
        )

    def _make_triad_axes(self) -> None:
        pos = self.ax3d.get_position()
        size = 0.16 * min(pos.width, pos.height)
        self.triad_ax = self.fig.add_axes(
            (
                pos.x0 + 0.035 * pos.width,
                pos.y0 + 0.035 * pos.height,
                size,
                size,
            ),
            label=f"_volume_triad_{id(self.ax3d)}",
            zorder=self.ax3d.get_zorder() + 2,
        )
        self.triad_ax.set_axis_off()
        self.triad_ax.set_xlim(-1.05, 1.05)
        self.triad_ax.set_ylim(-1.05, 1.05)
        self.triad_ax.set_aspect("equal")
        self.triad_ax.patch.set_alpha(0.0)
        self.update_triad()

    def _sync_triad_position(self) -> None:
        if self.triad_ax is None:
            return
        pos = self.ax3d.get_position()
        size = 0.16 * min(pos.width, pos.height)
        self.triad_ax.set_position(
            (
                pos.x0 + 0.035 * pos.width,
                pos.y0 + 0.035 * pos.height,
                size,
                size,
            )
        )

    def update_triad(self) -> None:
        """Redraw the orientation triad to match the current view."""
        if self.triad_ax is None:
            return
        self.triad_ax.clear()
        self.triad_ax.set_axis_off()
        self.triad_ax.set_xlim(-1.05, 1.05)
        self.triad_ax.set_ylim(-1.05, 1.05)
        self.triad_ax.set_aspect("equal")
        self.triad_ax.patch.set_alpha(0.0)

        elev = float(getattr(self.ax3d, "elev", 30.0))
        azim = float(getattr(self.ax3d, "azim", -60.0))
        roll = float(getattr(self.ax3d, "roll", 0.0))
        _forward, right, up = mpl_view_basis(elev, azim, roll)

        basis = {
            "X": np.array([1.0, 0.0, 0.0]),
            "Y": np.array([0.0, 1.0, 0.0]),
            "Z": np.array([0.0, 0.0, 1.0]),
        }
        # Conventional axis colors, but local to this overlay only.
        color_map = {"X": "tab:red", "Y": "gold", "Z": "tab:green"}
        text_color = plt.rcParams.get("text.color", "k")
        projected = []
        for label, vec in basis.items():
            sx = float(np.dot(vec, right))
            sy = float(np.dot(vec, up))
            depth = float(np.dot(vec, _forward))
            projected.append((depth, label, sx, sy))

        # Draw farthest first so front-facing arrows sit above.
        for _depth, label, sx, sy in sorted(projected):
            length = max(np.hypot(sx, sy), 1.0e-12)
            sx, sy = 0.75 * sx / length, 0.75 * sy / length
            self.triad_ax.annotate(
                "",
                xy=(sx, sy),
                xytext=(0.0, 0.0),
                arrowprops=dict(
                    arrowstyle="-|>",
                    lw=1.4,
                    color=color_map[label],
                    shrinkA=0,
                    shrinkB=0,
                ),
            )
            self.triad_ax.text(
                1.12 * sx,
                1.12 * sy,
                label,
                ha="center",
                va="center",
                fontsize=8,
                color=color_map[label],
            )
        self.triad_ax.plot([0], [0], marker="o", ms=3, color=text_color)

    # ---------------- view reset (toolbar Home) ----------------

    def _view_signature(self) -> tuple:
        """View-only signature (projection + limits), ignoring resolution."""
        try:
            proj_key = tuple(
                np.round(
                    np.asarray(self.ax3d.get_proj(), dtype=np.float64).ravel(),
                    10,
                )
            )
        except Exception:
            proj_key = ()
        return (
            proj_key,
            tuple(round(float(v), 8) for v in self.ax3d.get_xlim()),
            tuple(round(float(v), 8) for v in self.ax3d.get_ylim()),
            tuple(round(float(v), 8) for v in self.ax3d.get_zlim()),
        )

    def _store_home_view(self) -> None:
        """Remember the initial view so Home can restore it exactly."""
        self._home_view = {
            "elev": float(getattr(self.ax3d, "elev", 30.0)),
            "azim": float(getattr(self.ax3d, "azim", -60.0)),
            "roll": float(getattr(self.ax3d, "roll", 0.0)),
            "xlim": tuple(self.ax3d.get_xlim()),
            "ylim": tuple(self.ax3d.get_ylim()),
            "zlim": tuple(self.ax3d.get_zlim()),
        }

    def _restore_home_view(self) -> None:
        """Restore the stored initial view onto the Axes3D."""
        v = self._home_view
        if v is None:
            return
        try:
            self.ax3d.view_init(elev=v["elev"], azim=v["azim"], roll=v["roll"])
        except TypeError:
            # Older Matplotlib without a roll argument.
            self.ax3d.view_init(elev=v["elev"], azim=v["azim"])
        self.ax3d.set_xlim(*v["xlim"])
        self.ax3d.set_ylim(*v["ylim"])
        self.ax3d.set_zlim(*v["zlim"])

    def _install_home_hook(self) -> None:
        """Wrap the navigation toolbar Home so it also resets the underlay.

        ``draw_event`` already re-renders on any view change, so this is mainly
        a guarantee that the 3-D axes themselves snap back to the initial view
        regardless of backend/Matplotlib version.
        """
        toolbar = getattr(self.fig.canvas, "toolbar", None)
        if toolbar is None or not hasattr(toolbar, "home"):
            return
        orig_home = toolbar.home

        def home(*args: object, **kwargs: object) -> object:
            result = orig_home(*args, **kwargs)
            self._restore_home_view()
            self.render(final=True, force=True)
            self.fig.canvas.draw_idle()
            return result

        toolbar.home = home
        self._orig_home = orig_home

    # ---------------- event handlers ----------------

    def _event_is_relevant(self, event: Event) -> bool:
        # event.inaxes may be None during an Axes3D drag depending on backend.
        inaxes = getattr(event, "inaxes", None)
        return inaxes in (self.ax3d, self.image_ax, None)

    def _on_button_press(self, event: Event) -> None:
        if self._event_is_relevant(event):
            self._dragging = True

    def _on_button_release(self, event: Event) -> None:
        if not self._dragging:
            return
        self._dragging = False
        self.render(final=True, force=True)
        self.fig.canvas.draw_idle()

    def _on_motion(self, event: Event) -> None:
        if not self._dragging or not self._event_is_relevant(event):
            return
        now = time.monotonic()
        if now - self._last_t < self.throttle_s:
            return
        self._last_t = now
        self.render(final=False, force=False)
        self.fig.canvas.draw_idle()

    def _on_scroll(self, event: Event) -> None:
        if not self._event_is_relevant(event):
            return
        self.render(final=False, force=True)
        self.fig.canvas.draw_idle()

    def _on_resize(self, event: Event) -> None:
        _sync_axes_position(self.ax3d, self.image_ax)
        self._sync_triad_position()
        self.render(final=True, force=True)
        self.fig.canvas.draw_idle()

    def _on_draw(self, event: Event) -> None:
        # Keep axes aligned during layout changes, but do not recursively draw.
        _sync_axes_position(self.ax3d, self.image_ax)
        self._sync_triad_position()
        if self.triad_enabled:
            self.update_triad()

        # Re-render when the view changed outside of an active drag, e.g. the
        # toolbar Home/Back/Forward buttons or a programmatic ``view_init``.
        # During a drag the motion/release handlers own the rendering.
        if self._is_rendering or self._dragging:
            return
        view_sig = self._view_signature()
        if view_sig != self._last_view_sig:
            self.render(final=True, force=True)
            self.fig.canvas.draw_idle()


def synthetic_plume(
    n: int = 96,
) -> tuple[np.ndarray, tuple[float, float, float, float, float, float]]:
    """Make a simple volume with a torus-like shell and a central plume."""
    z, y, x = np.mgrid[
        -1 : 1 : complex(n), -1 : 1 : complex(n), -1 : 1 : complex(n)
    ]
    rxy = np.sqrt(x * x + y * y)
    torus = np.exp(-((rxy - 0.55) ** 2 / 0.018 + (z - 0.15) ** 2 / 0.035))
    plume = np.exp(-(x * x + y * y) / 0.035) * np.exp(-((z + 0.35) ** 2) / 0.45)
    clumps = 0.22 * np.exp(
        -((x - 0.38) ** 2 + (y + 0.2) ** 2 + (z - 0.2) ** 2) / 0.04
    )
    data = (
        0.15 * np.random.default_rng(2).random((n, n, n))
        + torus
        + 1.4 * plume
        + clumps
    ).astype(np.float32)
    return data, (-1.0, 1.0, -1.0, 1.0, -1.0, 1.0)
