"""Plot controller for GUI plotting/canvas workflow."""

from __future__ import annotations

import logging
from typing import TYPE_CHECKING, Any

import numpy as np
from matplotlib.backends.backend_qt import (
    NavigationToolbar2QT as NavigationToolbar,
)
from matplotlib.backends.backend_qtagg import (
    FigureCanvasQTAgg as FigureCanvas,
)
from matplotlib.collections import QuadMesh
from matplotlib.image import AxesImage

import pyPLUTO as pp

if TYPE_CHECKING:
    from pyPLUTO.gui.main_window import PyPLUTOApp

from pyPLUTO.gui.globals import cmaps_divided as cmaps
from pyPLUTO.gui.services import apply_slices, convert_axis_map

logger = logging.getLogger(__name__)


class PlotController:
    """Orchestrate GUI plotting actions and canvas lifecycle."""

    def __init__(self, app: PyPLUTOApp) -> None:
        """Bind the controller to the main application window.

        Parameters
        ----------
        - app: PyPLUTOApp
            The main application window instance that owns this controller.

        Returns
        -------
        - None

        """
        self.app = app

    def update_cmap_selector(self) -> None:
        """Repopulate the colormap selector based on the chosen colormap type.

        Reads the current colormap-type combo box and replaces the items in the
        colormap combo box with the matching subset from the global
        ``cmaps_divided`` registry.

        Returns
        -------
        - None

        """
        app = self.app

        selected_type = app.typecmap_selector.currentText()
        app.cmap_selector.clear()
        app.cmap_selector.addItems(cmaps.get(selected_type, []))

    def plot_data(self) -> None:
        """Read the current GUI state, slice the selected var, and render it.

        Dispatches to ``Image.plot`` for 1-D data and ``Image.display`` for 2-D
        data. When the *overplot* checkbox is active and the variable is 1-D the
        existing canvas is reused; otherwise the canvas is rebuilt from scratch.

        Returns
        -------
        - None

        """
        twod = 2
        app = self.app
        if not app.data_loaded:
            logger.error("No data loaded.")
            return
        var_name = app.var_selector.currentText()
        if not var_name:
            logger.error("No variable selected.")
            return

        app.var = getattr(app.Data, var_name)
        app.var = app.var.T if app.transpose_checkbox.isChecked() else app.var
        app.var, app.xslice, app.yslice, app.zslice = apply_slices(
            app.var,
            app.xslicetext.text(),
            app.yslicetext.text(),
            app.zslicetext.text(),
        )
        app.vardim = len(np.shape(app.var))
        if app.vardim < 1 or app.vardim > twod:
            raise ValueError("ERROR: Variable shape not recognized.")
        self._check_axisparam()

        axis_convert = convert_axis_map(app.Data.geom, app.vardim)
        if app.overplot_checkbox.isChecked() and app.vardim == 1:
            app.numlines = app.numlines + 1 if app.numlines > 0 else 1
        else:
            self.reload_canvas()
            app.numlines = 1
            app.frozen_lines.clear()

        x1 = getattr(app.Data, axis_convert[app.xaxis_selector.currentText()])
        x2 = getattr(app.Data, axis_convert[app.yaxis_selector.currentText()])
        xlim = [x1.min(), x1.max()]
        ylim = (
            [x2.min(), x2.max()]
            if app.vardim == twod
            else [app.var.min(), app.var.max()]
        )
        self._set_range(xlim, ylim)

        # Capture the spec after ranges are set, before datadict is mutated.
        spec = self._capture_spec()
        if app.overplot_checkbox.isChecked() and app.vardim == 1:
            app.live_specs.append(spec)
        else:
            app.live_specs.clear()
            app.live_specs.append(spec)

        if app.vardim == 1:
            cmap_temp = app.datadict.pop("cmap")
            cscale_temp = app.datadict.pop("cscale")
            ctresh_temp = app.datadict.pop("tresh", None)
            app.Image.plot(
                x1,
                app.var,
                **app.datadict,
                xtitle=" ",
                ytitle=" ",
            )
            # Capture the actual color assigned so replay stays in sync.
            if app.Image.ax:
                plotted = app.Image.ax[0].get_lines()
                if plotted:
                    app.live_specs[-1]["color"] = plotted[-1].get_color()
            app.figure.set_size_inches(
                app.Image.state.figsize[0],
                app.Image.state.figsize[1],
                forward=False,
            )
            app.datadict["cmap"] = cmap_temp
            app.datadict["cscale"] = cscale_temp
            if ctresh_temp is not None:
                app.datadict["tresh"] = ctresh_temp
        else:
            app.Image.display(
                app.var,
                x1=x1,
                x2=x2,
                cpos="right",
                **app.datadict,
                xtitle=" ",
                ytitle=" ",
                clabel=" ",
                figsize=app.Image.state.figsize,
            )
        app.firstplot = False
        app.canvas.draw()

    def lock_lines(self) -> None:
        """Freeze all current live lines into static snapshots.

        Reads every ``Line2D`` from the active axes, stores its data and style,
        then clears ``live_specs`` so subsequent overplots become the new live
        lines followed by the slider.

        Returns
        -------
        - None

        """
        app = self.app
        if not app.data_loaded:
            app.info_label.append("[Lock Lines] No data loaded.")
            return
        if not app.live_specs:
            app.info_label.append(
                "[Lock Lines] Nothing to lock — plot a line first."
            )
            return
        if not app.Image.ax:
            app.info_label.append("[Lock Lines] No active axes found.")
            return
        ax = app.Image.ax[0]
        lines = ax.get_lines()
        if not lines:
            app.info_label.append(
                "[Lock Lines] No lines found on the current axes."
            )
            return
        n_before = len(app.frozen_lines)
        for line in lines:
            app.frozen_lines.append(
                {
                    "xdata": line.get_xdata().copy(),
                    "ydata": line.get_ydata().copy(),
                    "color": line.get_color(),
                    "linewidth": line.get_linewidth(),
                    "linestyle": line.get_linestyle(),
                    "marker": line.get_marker(),
                    "markersize": line.get_markersize(),
                }
            )
        n_locked = len(app.frozen_lines) - n_before
        app.live_specs.clear()
        app.numlines = 0
        app.overplot_checkbox.setChecked(True)
        app.info_label.append(
            f"[Lock Lines] {n_locked} line(s) frozen. "
            "Overplot a new line to enable slider replay."
        )

    def replay_all(self) -> None:
        """Redraw frozen snapshots then re-execute all live specs.

        Called by the time slider. Clears the canvas, repaints every frozen
        line from its stored arrays, then re-plots each live spec against the
        freshly loaded ``Data`` at the current nout.

        Returns
        -------
        - None

        """
        app = self.app
        # Clear the figure without disturbing the Qt widget layout.
        app.figure.clear()
        app.Image = pp.Image(fig=app.figure, text=False)
        app.firstplot = True
        app.numlines = 0

        # Re-execute live specs (creates the axis via pp.Image).
        for spec in app.live_specs:
            try:
                self._execute_spec(spec)
            except Exception as exc:
                app.info_label.append(f"[Replay] Error executing spec: {exc}")
                logger.exception("Error in _execute_spec")
                continue
            app.firstplot = False
            app.numlines += 1

        # Paint frozen lines directly onto the existing axis.
        if app.frozen_lines and app.Image.ax:
            ax = app.Image.ax[0]
            for fl in app.frozen_lines:
                style = {
                    k: v for k, v in fl.items() if k not in ("xdata", "ydata")
                }
                ax.plot(fl["xdata"], fl["ydata"], **style)

        # Advance nline so any subsequent plot_data() overplot picks up the
        # right next color (frozen + live lines already occupy the palette).
        if app.Image.ax:
            app.Image.state.nline[0] = len(app.frozen_lines) + len(
                app.live_specs
            )

        app.canvas.draw()

    def update_axes(self) -> None:
        """Apply colormap, normalisation, and axis-range changes.

        Such changes are done without re-plotting.
        Updates every ``AxesImage`` and ``QuadMesh`` artist on the current axes
        in place, then calls ``set_axis`` to propagate scale and range settings.

        Returns
        -------
        - None

        """
        app = self.app
        self._check_axisparam()
        cmap = app.datadict.pop("cmap")
        cscale = app.datadict.pop("cscale")
        vmin = app.datadict.pop("vmin", app.var.min())
        vmax = app.datadict.pop("vmax", app.var.max())
        ctresh = app.datadict.pop("tresh", max(np.abs(vmin), vmax) * 0.01)
        norm = app.Image.ImageToolsManager.set_cscale(
            cscale,
            vmin,
            vmax,
            ctresh,
        )
        for artist in app.Image.ax[0].get_children():
            if isinstance(artist, (AxesImage, QuadMesh)):
                artist.set_cmap(cmap)
                artist.set_norm(norm)
        self._set_range(xlim=None, ylim=None)
        app.Image.set_axis(app.Image.ax[0], **app.datadict)
        app.datadict["cmap"] = cmap
        app.datadict["cscale"] = cscale
        app.datadict["tresh"] = ctresh
        app.canvas.draw()

    def create_new_figure(self) -> None:
        """Instantiate fresh Image, canvas, and toolbar attached to the layout.

        Creates a new ``FigureCanvasQTAgg`` and ``NavigationToolbar2QT`` from
        the new figure and appends both to ``app.canvas_layout``.

        Returns
        -------
        - None

        """
        app = self.app

        app.Image = pp.Image(figsize=[10, 6], text=False)
        app.firstplot = True
        app.figure = app.Image.fig
        app.canvas = FigureCanvas(app.figure)
        app.toolbar = NavigationToolbar(app.canvas, app)
        app.canvas.setFixedWidth(800)
        app.canvas_layout.addWidget(app.toolbar)
        app.canvas_layout.addWidget(app.canvas)

    def reload_canvas(self) -> None:
        """Clear the figure content in-place without touching the Qt widgets.

        Clears all axes and artists from the existing figure, then re-attaches
        a fresh ``pp.Image`` to it. The canvas and toolbar widgets stay in the
        layout, so no geometry shift occurs.

        Returns
        -------
        - None

        """
        app = self.app
        app.figure.clear()
        app.Image = pp.Image(fig=app.figure, text=False)
        app.firstplot = True
        app.canvas.draw()

    def clear_labels(self) -> None:
        """Reset every plot-panel widget to its default state.

        Clears text inputs, resets combo box selections to index 0, and unchecks
        all checkboxes except *ratio* which is restored to its checked default.

        Returns
        -------
        - None

        """
        app = self.app
        app.var_selector.setCurrentIndex(0)
        app.ratio_checkbox.setChecked(True)
        app.transpose_checkbox.setChecked(False)
        app.xaxis_selector.setCurrentIndex(0)
        app.yaxis_selector.setCurrentIndex(0)
        app.xslicetext.clear()
        app.yslicetext.clear()
        app.zslicetext.clear()
        app.plot_title.clear()
        app.xrange_min.clear()
        app.xrange_max.clear()
        app.yrange_min.clear()
        app.yrange_max.clear()
        app.vrange_min.clear()
        app.vrange_max.clear()
        app.xscale_selector.setCurrentIndex(0)
        app.yscale_selector.setCurrentIndex(0)
        app.vscale_selector.setCurrentIndex(0)
        app.xscale_tresh.clear()
        app.yscale_tresh.clear()
        app.vscale_tresh.clear()
        app.typecmap_selector.setCurrentIndex(0)
        app.cmap_selector.setCurrentIndex(0)
        app.reverse_checkbox.setChecked(False)
        app.overplot_checkbox.setChecked(False)

    def _capture_spec(self) -> dict[str, Any]:
        """Snapshot the current GUI state as a replayable plot specification.

        Called inside ``plot_data`` after ``_check_axisparam`` and
        ``_set_range`` have both run, so ``app.datadict`` already contains
        the full set of plot kwargs including computed axis ranges.

        Returns
        -------
        - dict[str, Any]
            Mapping with all information needed to reproduce the plot at a
            different nout via ``_execute_spec``.

        """
        app = self.app
        # Strip computed ranges — _execute_spec recomputes them from fresh data.
        datadict = {
            k: v
            for k, v in app.datadict.items()
            if k not in ("xrange", "yrange")
        }
        return {
            "var_name": app.var_selector.currentText(),
            "xslice": app.xslicetext.text(),
            "yslice": app.yslicetext.text(),
            "zslice": app.zslicetext.text(),
            "axis_x": app.xaxis_selector.currentText(),
            "axis_y": app.yaxis_selector.currentText(),
            "transpose": app.transpose_checkbox.isChecked(),
            "yscale": app.yscale_selector.currentText(),
            "xrange_min": app.xrange_min.text(),
            "xrange_max": app.xrange_max.text(),
            "yrange_min": app.yrange_min.text(),
            "yrange_max": app.yrange_max.text(),
            "datadict": datadict,
        }

    def _execute_spec(self, spec: dict[str, Any]) -> None:
        """Re-plot one live spec against the current loaded Data.

        Fetches the variable, applies the stored slices, recomputes axis
        ranges from the new data (honouring any stored manual overrides),
        and calls the appropriate ``Image`` method.

        Parameters
        ----------
        - spec: dict[str, Any]
            A spec dict previously produced by ``_capture_spec``.

        Returns
        -------
        - None

        """
        twod = 2
        app = self.app
        try:
            var = getattr(app.Data, spec["var_name"])
        except AttributeError:
            logger.warning("Variable %s not found in Data", spec["var_name"])
            return
        var = var.T if spec["transpose"] else var
        var, _, _, _ = apply_slices(
            var, spec["xslice"], spec["yslice"], spec["zslice"]
        )
        vardim = len(np.shape(var))
        if vardim < 1 or vardim > twod:
            return

        axis_convert = convert_axis_map(app.Data.geom, vardim)
        x1 = getattr(app.Data, axis_convert[spec["axis_x"]])

        # Recompute ranges from fresh data, apply any stored manual overrides.
        xlim = [float(x1.min()), float(x1.max())]
        if vardim == twod:
            x2 = getattr(app.Data, axis_convert[spec["axis_y"]])
            ylim = [float(x2.min()), float(x2.max())]
            ymin_r, ymax_r = ylim
        else:
            x2 = None
            ylim = [float(var.min()), float(var.max())]
            ymin_r, ymax_r = app.Image.RangeManager.range_offset(
                ylim[0], ylim[1], spec["yscale"]
            )

        datadict: dict[str, Any] = dict(spec["datadict"])
        datadict["xrange"] = [
            float(spec["xrange_min"]) if spec["xrange_min"] else xlim[0],
            float(spec["xrange_max"]) if spec["xrange_max"] else xlim[1],
        ]
        datadict["yrange"] = [
            float(spec["yrange_min"]) if spec["yrange_min"] else ymin_r,
            float(spec["yrange_max"]) if spec["yrange_max"] else ymax_r,
        ]

        if vardim == 1:
            datadict.pop("cmap", None)
            datadict.pop("cscale", None)
            datadict.pop("tresh", None)
            # Pin the color so replay always uses the same hue regardless of
            # how many lines the fresh Image has already drawn.
            if "color" in spec:
                datadict["c"] = spec["color"]
            app.Image.plot(x1, var, **datadict, xtitle=" ", ytitle=" ")
            app.figure.set_size_inches(
                app.Image.state.figsize[0],
                app.Image.state.figsize[1],
                forward=False,
            )
        else:
            app.Image.display(
                var,
                x1=x1,
                x2=x2,
                cpos="right",
                **datadict,
                xtitle=" ",
                ytitle=" ",
                clabel=" ",
                figsize=app.Image.state.figsize,
            )

    def _check_axisparam(self) -> None:
        """Rebuild ``app.datadict`` from the current plot-panel widget values.

        Reads every relevant GUI field (value/color-scale range, aspect ratio,
        colormap, axis scales, and their symmetry thresholds) and stores the
        results in the ``app.datadict`` mapping, which is forwarded to the
        ``Image`` rendering calls.

        Returns
        -------
        - None

        """
        app = self.app
        app.datadict = {}
        if app.vrange_min.text():
            app.datadict["vmin"] = float(app.vrange_min.text())
        if app.vrange_max.text():
            app.datadict["vmax"] = float(app.vrange_max.text())
        app.datadict["aspect"] = (
            "equal" if not app.ratio_checkbox.isChecked() else "auto"
        )
        app.datadict["cmap"] = app.cmap_selector.currentText()
        if app.reverse_checkbox.isChecked():
            app.datadict["cmap"] = (
                app.datadict["cmap"][:-2]
                if app.datadict["cmap"].endswith("_r")
                else app.datadict["cmap"] + "_r"
            )
        app.datadict["title"] = (
            app.plot_title.text() if app.plot_title.text() else ""
        )
        app.datadict["xscale"] = app.xscale_selector.currentText()
        if app.xscale_tresh.text():
            app.datadict["xtresh"] = float(app.xscale_tresh.text())
        app.datadict["yscale"] = app.yscale_selector.currentText()
        if app.yscale_tresh.text():
            app.datadict["ytresh"] = float(app.yscale_tresh.text())
        app.datadict["cscale"] = app.vscale_selector.currentText()
        if app.vscale_tresh.text():
            app.datadict["tresh"] = float(app.vscale_tresh.text())

    def _set_range(
        self,
        xlim: list[float] | None,
        ylim: list[float] | None,
    ) -> None:
        """Update the axis extents and write them into ``app.datadict``.

        On the first plot the stored limits are initialised from
        ``xlim``/``ylim``. On subsequent calls the stored limits are grown to
        encompass the new data. Any user-supplied range overrides in the text
        fields take precedence over the computed limits when writing ``xrange``
        and ``yrange``.

        Parameters
        ----------
        - xlim: list[float] or None
            [xmin, xmax] for the current data; None reuses the stored values.
        - ylim: list[float] or None
            [ymin, ymax] for the current data; None reuses the stored values.

        Returns
        -------
        - None

        """
        app = self.app
        if xlim is None:
            xlim = [app.xmin, app.xmax]
        if ylim is None:
            ylim = [app.ymin, app.ymax]
        if app.firstplot:
            app.xmin, app.xmax = xlim
            app.ymin, app.ymax = ylim
        else:
            app.xmin = np.minimum(xlim[0], app.xmin)
            app.xmax = np.maximum(xlim[1], app.xmax)
            app.ymin = np.minimum(ylim[0], app.ymin)
            app.ymax = np.maximum(ylim[1], app.ymax)
        ymin, ymax = (
            app.Image.RangeManager.range_offset(
                app.ymin,
                app.ymax,
                app.yscale_selector.currentText(),
            )
            if app.vardim == 1
            else (app.ymin, app.ymax)
        )
        app.datadict["xrange"] = [
            float(app.xrange_min.text()) if app.xrange_min.text() else app.xmin,
            float(app.xrange_max.text()) if app.xrange_max.text() else app.xmax,
        ]
        app.datadict["yrange"] = [
            float(app.yrange_min.text()) if app.yrange_min.text() else ymin,
            float(app.yrange_max.text()) if app.yrange_max.text() else ymax,
        ]
