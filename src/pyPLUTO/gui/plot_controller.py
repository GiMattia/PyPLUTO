"""Plot controller for GUI plotting/canvas workflow."""

from __future__ import annotations

import numpy as np
from matplotlib.collections import QuadMesh
from matplotlib.image import AxesImage

import pyPLUTO as pp

from .services import apply_slices, convert_axis_map


class PlotController:
    def __init__(self, app):
        self.app = app

    def update_cmap_selector(self) -> None:
        app = self.app
        from .globals import cmaps_divided as cmaps

        selected_type = app.typecmap_selector.currentText()
        app.cmap_selector.clear()
        app.cmap_selector.addItems(cmaps.get(selected_type, []))

    def plot_data(self) -> None:
        app = self.app
        if not app.data_loaded:
            print("ERROR: No data loaded.")
            return
        var_name = app.var_selector.currentText()
        if not var_name:
            print("ERROR: No variable selected.")
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
        if app.vardim < 1 or app.vardim > 2:
            raise ValueError("ERROR: Variable shape not recognized.")
        self._check_axisparam()

        axis_convert = convert_axis_map(app.Data.geom, app.vardim)
        if app.overplot_checkbox.isChecked() and app.vardim == 1:
            app.numlines = app.numlines + 1 if app.numlines > 0 else 1
        else:
            self.reload_canvas()
            app.numlines = 1

        x1 = getattr(app.Data, axis_convert[app.xaxis_selector.currentText()])
        x2 = getattr(app.Data, axis_convert[app.yaxis_selector.currentText()])
        xlim = [x1.min(), x1.max()]
        ylim = (
            [x2.min(), x2.max()]
            if app.vardim == 2
            else [app.var.min(), app.var.max()]
        )
        self._set_range(xlim, ylim)

        if app.vardim == 1:
            cmap_temp = app.datadict.pop("cmap")
            cscale_temp = app.datadict.pop("cscale")
            ctresh_temp = app.datadict.pop("tresh", None)
            app.Image.plot(x1, app.var, **app.datadict, xtitle=" ", ytitle=" ")
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
            )
        app.firstplot = False
        app.canvas.draw()

    def update_axes(self) -> None:
        app = self.app
        self._check_axisparam()
        cmap = app.datadict.pop("cmap")
        cscale = app.datadict.pop("cscale")
        vmin = app.datadict.pop("vmin", app.var.min())
        vmax = app.datadict.pop("vmax", app.var.max())
        ctresh = app.datadict.pop("tresh", max(np.abs(vmin), vmax) * 0.01)
        norm = app.Image.ImageToolsManager.set_cscale(
            cscale, vmin, vmax, ctresh
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
        app = self.app
        from matplotlib.backends.backend_qtagg import (
            FigureCanvasQTAgg as FigureCanvas,
        )
        from matplotlib.backends.backend_qtagg import (
            NavigationToolbar2QT as NavigationToolbar,
        )

        app.Image = pp.Image(figsize=[10, 6])
        app.firstplot = True
        app.figure = app.Image.fig
        print(app.Image.fontsize, app.Image.figsize)
        app.canvas = FigureCanvas(app.figure)
        app.toolbar = NavigationToolbar(app.canvas, app)
        app.canvas.setFixedWidth(800)
        app.canvas_layout.addWidget(app.toolbar)
        app.canvas_layout.addWidget(app.canvas)

    def reload_canvas(self) -> None:
        app = self.app
        app.canvas_layout.removeWidget(app.toolbar)
        app.toolbar.deleteLater()
        app.canvas_layout.removeWidget(app.canvas)
        app.canvas.deleteLater()
        self.create_new_figure()

    def clear_labels(self) -> None:
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

    def _check_axisparam(self) -> None:
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

    def _set_range(self, xlim, ylim) -> None:
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
                app.ymin, app.ymax, app.yscale_selector.currentText()
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
