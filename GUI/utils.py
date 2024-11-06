import os
import numpy as np
import pyPLUTO as pp
from PyQt6.QtWidgets import QFileDialog
import matplotlib.pyplot as plt
import matplotlib.scale as mscale

scales = list(mscale.get_scale_names())
scales = [scales[3]] + [scales[0]] + scales[4:]

cmaps = [('Perceptually Uniform Sequential', [
            'viridis', 'plasma', 'inferno', 'magma', 'cividis']),
         ('Sequential', [
            'Greys', 'Purples', 'Blues', 'Greens', 'Oranges', 'Reds',
            'YlOrBr', 'YlOrRd', 'OrRd', 'PuRd', 'RdPu', 'BuPu',
            'GnBu', 'PuBu', 'YlGnBu', 'PuBuGn', 'BuGn', 'YlGn']),
         ('Sequential (2)', [
            'binary', 'gist_yarg', 'gist_gray', 'gray', 'bone', 'pink',
            'spring', 'summer', 'autumn', 'winter', 'cool', 'Wistia',
            'hot', 'afmhot', 'gist_heat', 'copper']),
         ('Diverging', [
            'PiYG', 'PRGn', 'BrBG', 'PuOr', 'RdGy', 'RdBu',
            'RdYlBu', 'RdYlGn', 'Spectral', 'coolwarm', 'bwr', 'seismic']),
         ('Cyclic', ['twilight', 'twilight_shifted', 'hsv']),
         ('Qualitative', [
            'Pastel1', 'Pastel2', 'Paired', 'Accent',
            'Dark2', 'Set1', 'Set2', 'Set3',
            'tab10', 'tab20', 'tab20b', 'tab20c']),
         ('Miscellaneous', [
            'flag', 'prism', 'ocean', 'gist_earth', 'terrain', 'gist_stern',
            'gnuplot', 'gnuplot2', 'CMRmap', 'cubehelix', 'brg',
            'gist_rainbow', 'rainbow', 'jet', 'turbo', 'nipy_spectral',
            'gist_ncar'])]


def check_axisparam(self):
    # Create datadict with yrange and optionally xrange
    self.datadict = {}
    if self.xrange_min.text() or self.xrange_max.text():
        self.datadict['xrange'] = [
            float(self.xrange_min.text()) if self.xrange_min.text() else self.D.x1.min(),
            float(self.xrange_max.text()) if self.xrange_max.text() else self.D.x1.max()
        ]
    if self.yrange_min.text() or self.yrange_max.text():
        self.datadict['yrange'] = [
            float(self.yrange_min.text()) if self.yrange_min.text() else self.D.x2.min(),
            float(self.yrange_max.text()) if self.yrange_max.text() else self.D.x2.max()
        ]
    if self.vrange_min.text():
        self.datadict['vmin'] = float(self.vrange_min.text())
    if self.vrange_max.text():
        self.datadict['vmax'] = float(self.vrange_max.text())

    self.datadict['clabel'] = self.clabel_label.text() if self.clabel_label.text() else " "
    self.datadict['title'] = self.title_label.text() if self.title_label.text() else ""
    self.datadict['xtitle'] = self.xlabel_label.text() if self.xlabel_label.text() else ""
    self.datadict['ytitle'] = self.ylabel_label.text() if self.ylabel_label.text() else ""
    self.datadict['cmap'] = self.cmap_selector.currentText()
    self.datadict['xscale'] = self.xscale_selector.currentText()
    self.datadict['yscale'] = self.yscale_selector.currentText()
    self.datadict['cscale'] = self.varscale_selector.currentText()
    if self.cmapreverse_checkbox.isChecked():
        if self.datadict['cmap'][-2:] == '_r':
            self.datadict['cmap'] = self.datadict['cmap'][:-2]
        else:
            self.datadict['cmap'] += '_r'
    if self.transpose_checkbox.isChecked():
        self.datadict['transpose'] = True


    # Modify the plot_selected_variable function
def plot_selected_variable(self):
    if not self.data_loaded:
        print("ERROR: No data loaded.")
        return

    var_name = self.var_selector.currentText()
    if not var_name:
        print("ERROR: No variable selected.")
        return

    axis_convert = {"x1": "x1r", "x2": "x2r", "x3": "x3r", "x1p": "x1rp", "x2p": "x2rp", "x3p": "x3rp",
                    "x1c": "x1rc", "x2c": "x2rc", "x3c": "x3rc"}
    self.var    = getattr(self.D, var_name)
    self.vardim = len(np.shape(self.var))
    if not self.overplot_checkbox.isChecked(): self.plot_window.canvas.figure.clear()
    self.I = pp.Image(figsize=[7.5, 6.3]) if not self.overplot_checkbox.isChecked() else self.I
    self.datadict = {}
    self.check_axisparam()
    x1 = getattr(self.D, axis_convert[self.xaxis_selector.currentText()])
    x2 = getattr(self.D, axis_convert[self.yaxis_selector.currentText()])
    if self.vardim == 1:
        temp_clabel = self.datadict.pop('clabel')
        temp_cmap   = self.datadict.pop('cmap')
        temp_cscale = self.datadict.pop('cscale')
        self.I.plot(x1, self.var, **self.datadict)
        self.datadict['clabel'] = temp_clabel
        self.datadict['cmap']   = temp_cmap
        self.datadict['cscale'] = temp_cscale
    elif self.vardim == 2:
        self.I.display(self.var, x1 = x1, x2 = x2, cpos='right', **self.datadict)
    else:
        print("ERROR: Variable shape not recognized.")

    self.plot_window.canvas.figure = self.I.fig
    self.plot_window.canvas.draw()

def update_axes(self):
    self.check_axisparam()
    temp_clabel = self.datadict.pop('clabel')
    temp_cmap   = self.datadict.pop('cmap')
    temp_cscale = self.datadict.pop('cscale')
    self.I.set_axis(self.I.ax[0],**self.datadict)
    if len(self.I.fig.axes) > 1:
        self.I.fig.axes[-1].set_ylabel(temp_clabel)
        for artist in self.I.ax[0].get_children():
            if isinstance(artist, (plt.matplotlib.image.AxesImage,
                                   plt.matplotlib.collections.QuadMesh)):
                artist.set_cmap(temp_cmap)
    self.datadict['clabel'] = temp_clabel
    self.datadict['cmap']   = temp_cmap
    self.datadict['cscale'] = temp_cscale
    self.plot_window.canvas.figure = self.I.fig
    self.plot_window.canvas.draw()

def clear_labels(self):
    self.xrange_min.clear()
    self.xrange_max.clear()
    self.yrange_min.clear()
    self.yrange_max.clear()
    self.vrange_min.clear()
    self.vrange_max.clear()
    self.xlabel_label.clear()
    self.ylabel_label.clear()
    self.title_label.clear()
    self.clabel_label.clear()
    self.var_selector.clear()
    self.var_selector.addItems(self.D._load_vars)
    self.cmap_selector.clear()
    self.cmap_selector.addItems(self.cmaps_avail)
    self.xscale_selector.clear()
    self.xscale_selector.addItems(scales)
    self.yscale_selector.clear()
    self.yscale_selector.addItems(scales)
    self.cmapreverse_checkbox.setChecked(False)
    self.transpose_checkbox.setChecked(False) # fix

def save_figure(self):
    file_path, _ = QFileDialog.getSaveFileName(self, "Save Plot", os.getcwd(), "PNG Files (*.png);;All Files (*)")
    if file_path:
        self.I.savefig(file_path)
        print(f"Figure saved to {file_path}")