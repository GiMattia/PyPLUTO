"""VolumeManager class."""

from __future__ import annotations

import warnings
from typing import Unpack

import numpy as np
from matplotlib.axes import Axes
from mpl_toolkits.mplot3d import Axes3D

from pyPLUTO.imagefuncs.imagetools import ImageToolsManager
from pyPLUTO.imagefuncs.volengine import (
    MPLVolumeRenderer,
    VolumeRenderOptions,
    default_extent_for,
)
from pyPLUTO.imagekwargs import VolumeKwargs
from pyPLUTO.imagemixin import ImageMixin
from pyPLUTO.imagestate import ImageState
from pyPLUTO.utils.inspector import track_kwargs

# Map the PyPLUTO ``cscale`` keyword onto the norms understood by the engine.
_CSCALE_TO_NORM = {
    "norm": "linear",
    "linear": "linear",
    "lin": "linear",
    "log": "log",
    "log10": "log",
    "symlog": "symlog",
}


class VolumeManager(ImageMixin):
    """Manager for ray-marched volume rendering of a 3D Cartesian field.

    The volume is drawn as an RGBA underlay synchronized with a Matplotlib
    Axes3D, which keeps ownership of the camera, box, ticks and labels. The
    renderer is interactive by default (live preview while rotating, full
    quality on release) and honors the active Matplotlib style, so
    ``Image(style="dark_background")`` produces a dark backdrop.

    Only uniform Cartesian grids are supported in this version.
    """

    def __init__(self, state: ImageState) -> None:
        """Initialize the VolumeManager with the given state."""
        self.state = state
        self.ImageToolsManager = ImageToolsManager(state)

    @track_kwargs(
        extra_keys={
            "cmap",
            "cscale",
            "vmin",
            "vmax",
            "opacity",
            "opacity_scale",
            "mode",
            "samples",
            "resolution",
            "background",
            "lut_size",
            "gamma",
            "margin",
            "set_orthographic",
        }
    )
    def volume(
        self,
        var: np.ndarray,
        ax: Axes | int | None = None,
        _check: bool = True,
        **kwargs: Unpack[VolumeKwargs],
    ) -> MPLVolumeRenderer:
        """Volume-render a 3D uniform Cartesian field onto an Axes3D.

        A figure with a single 3D axis is created if none is present.

        Parameters
        ----------
        - var (not optional): np.ndarray
            The 3D scalar field, indexed ``var[i1, i2, i3]`` following the
            PyPLUTO ``(x1, x2, x3)`` convention. It is transposed internally to
            the engine's ``(z, y, x)`` order.
        - ax: ax | int | None, default None
            The 3D axis where to render. If None, the last 3D axis is used (or a
            new one is created). A non-3D axis raises an error.
        - azim: float, default None
            Azimuthal camera angle in degrees. Fixes the view (and the Home
            reset target). If None, the current axis value is kept.
        - background: str | tuple | None, default 'auto'
            Backdrop color. 'auto' follows the active style
            (``rcParams["axes.facecolor"]``), None keeps the volume
            transparent, and an RGBA tuple fixes the color.
        - cmap: str, default 'magma'
            The colormap used for the RGB transfer function.
        - colorbar: bool, default True
            If True, attach a colorbar mapped to the color limits.
        - cscale: {'linear','log','symlog'}, default 'linear'
            The normalization of the scalar values. Other PyPLUTO scales fall
            back to 'linear' with a warning.
        - elev: float, default None
            Elevation camera angle in degrees. Fixes the view (and the Home
            reset target). If None, the current axis value is kept.
        - interactive: bool, default True
            If True, wire mouse rotation/zoom with live preview, full-quality
            render on release, and a Home button that resets both the axes and
            the rendered underlay.
        - margin: float, default 1.05
            Padding factor for the bounding sphere fitted in the view.
        - mode: {'composite','mip','average'}, default 'composite'
            The ray-integration mode.
        - opacity: str | tuple | callable, default ('sigmoid', 0.35, 0.12, 1.0)
            The opacity transfer function on normalized values in [0, 1].
        - opacity_scale: float, default 8.0
            Absorption density scale; higher means more opaque.
        - preview_resolution: int, default 192
            Image resolution used for the live preview while interacting.
        - preview_samples: int, default 64
            Number of ray samples used for the live preview.
        - resolution: int | tuple[int, int], default 512
            Final render resolution in pixels.
        - roll: float, default None
            Roll camera angle in degrees. Fixes the view (and the Home reset
            target). If None, the current axis value is kept.
        - samples: int, default 192
            Number of ray samples for the final render.
        - show_grid: bool, default False
            If True, show the 3D grid.
        - triad: bool, default False
            If True, draw an orientation triad overlay.
        - vmin: float, default None
            Lower color limit. Inferred from robust percentiles if omitted.
        - vmax: float, default None
            Upper color limit. Inferred from robust percentiles if omitted.
        - x1: np.ndarray, default None
            The x1 (x) grid coordinates, used to build the physical extent.
        - x2: np.ndarray, default None
            The x2 (y) grid coordinates, used to build the physical extent.
        - x3: np.ndarray, default None
            The x3 (z) grid coordinates, used to build the physical extent.

        Returns
        -------
        - MPLVolumeRenderer
            The renderer handle, exposing ``set_cmap``, ``set_clim``,
            ``set_opacity``, ``set_quality`` and ``savefig``.

        Examples
        --------
        - Example #1: render a loaded variable

            >>> import pyPLUTO as pp
            >>> I = pp.Image()
            >>> h = I.volume(D.rho, x1=D.x1, x2=D.x2, x3=D.x3)

        - Example #2: dark background with a maximum-intensity projection

            >>> I = pp.Image(style="dark_background")
            >>> h = I.volume(arr, mode="mip", cmap="plasma")

        """
        data = np.asarray(var)
        if data.ndim != 3:
            raise ValueError(
                f"volume expects a 3D array, got shape {data.shape}"
            )

        # Resolve (or create) a 3D axis. ``proj='3d'`` only takes effect when a
        # new axis is created; existing axes are returned as-is.
        kwargs.setdefault("proj", "3d")
        ax, _nax = self.ImageToolsManager.assign_ax(ax, _check=False, **kwargs)
        self.ImageToolsManager.hide_text(_nax, ax.texts)
        if not isinstance(ax, Axes3D):
            raise ValueError(
                "volume requires a 3D axis. Create the image axes with "
                "proj='3d' (e.g. I.create_axes(proj='3d')) before calling it."
            )

        # Fix the camera before the renderer captures it as the home view, so
        # the saved image is reproducible and the Home button returns here.
        elev = kwargs.get("elev")
        azim = kwargs.get("azim")
        roll = kwargs.get("roll")
        if elev is not None or azim is not None or roll is not None:
            ax.view_init(
                elev=elev if elev is not None else ax.elev,
                azim=azim if azim is not None else ax.azim,
                roll=roll if roll is not None else ax.roll,
            )

        # PyPLUTO arrays are indexed (x1, x2, x3) = (x, y, z); the engine wants
        # (z, y, x). Transpose so vol[k, j, i] matches (x, y, z).
        vol = np.ascontiguousarray(data.transpose(2, 1, 0))
        extent = self._build_extent(
            vol,
            kwargs.get("x1"),
            kwargs.get("x2"),
            kwargs.get("x3"),
        )

        options = self._build_options(kwargs)
        renderer = MPLVolumeRenderer(
            vol,
            ax=ax,
            extent=extent,
            options=options,
            interactive=bool(kwargs.get("interactive", True)),
            preview_resolution=int(kwargs.get("preview_resolution", 192)),
            preview_samples=int(kwargs.get("preview_samples", 64)),
            triad=bool(kwargs.get("triad", False)),
            colorbar=bool(kwargs.get("colorbar", True)),
            show_grid=bool(kwargs.get("show_grid", False)),
        )
        self.state.volumes.append(renderer)
        return renderer

    def _build_extent(
        self,
        vol: np.ndarray,
        x1: np.ndarray | None,
        x2: np.ndarray | None,
        x3: np.ndarray | None,
    ) -> tuple[float, float, float, float, float, float]:
        """Build the (xmin, xmax, ...) extent from the grid coordinates.

        ``vol`` is already in engine (z, y, x) order. Missing coordinates fall
        back to integer index ranges. Uniform spacing is assumed.
        """
        default = default_extent_for(vol)
        ranges = []
        for axis, coord in enumerate((x1, x2, x3)):
            if coord is None:
                ranges.append((default[2 * axis], default[2 * axis + 1]))
            else:
                c = np.asarray(coord, dtype=float)
                ranges.append((float(c.min()), float(c.max())))
        (xmin, xmax), (ymin, ymax), (zmin, zmax) = ranges
        return (xmin, xmax, ymin, ymax, zmin, zmax)

    def _build_options(self, kwargs: VolumeKwargs) -> VolumeRenderOptions:
        """Translate PyPLUTO kwargs into a VolumeRenderOptions instance."""
        cscale = kwargs.get("cscale")
        if cscale is not None and str(cscale).lower() not in _CSCALE_TO_NORM:
            warnings.warn(
                f"volume does not support cscale={cscale!r}; "
                "falling back to 'linear'.",
                UserWarning,
                stacklevel=2,
            )
        norm = _CSCALE_TO_NORM.get(str(cscale).lower(), "linear")

        vmin = kwargs.get("vmin")
        vmax = kwargs.get("vmax")
        clim = (
            (float(vmin), float(vmax))
            if vmin is not None and vmax is not None
            else None
        )

        defaults = VolumeRenderOptions()
        return VolumeRenderOptions(
            samples=int(kwargs.get("samples", defaults.samples)),
            resolution=kwargs.get("resolution", defaults.resolution),
            cmap=str(kwargs.get("cmap", defaults.cmap)),
            norm=norm,
            clim=clim,
            opacity=kwargs.get("opacity", defaults.opacity),
            opacity_scale=float(
                kwargs.get("opacity_scale", defaults.opacity_scale)
            ),
            mode=kwargs.get("mode", defaults.mode),
            background=kwargs.get("background", defaults.background),
            lut_size=int(kwargs.get("lut_size", defaults.lut_size)),
            gamma=float(kwargs.get("gamma", defaults.gamma)),
            margin=float(kwargs.get("margin", defaults.margin)),
            set_orthographic=bool(
                kwargs.get("set_orthographic", defaults.set_orthographic)
            ),
        )
