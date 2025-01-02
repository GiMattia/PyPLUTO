from matplotlib.backends.backend_qtagg import FigureCanvasQTAgg as FigureCanvas, NavigationToolbar2QT as NavigationToolbar
import pyPLUTO as pp
import numpy as np
from globals import cmaps
import matplotlib.pyplot as plt

def update_cmap_selector(self):
    selected_type = self.typecmap_selector.currentText()
    self.cmap_selector.clear()
    self.cmap_selector.addItems(cmaps.get(selected_type, []))

def clear_labels(self):
    self.var_selector.setCurrentIndex(0)
    self.transpose_checkbox.setChecked(False)
    self.xaxis_selector.setCurrentIndex(0)
    self.yaxis_selector.setCurrentIndex(0)
    self.xslicetext.clear()
    self.yslicetext.clear()
    self.zslicetext.clear()
    self.plot_title.clear()
    self.xrange_min.clear()
    self.xrange_max.clear()
    self.yrange_min.clear()
    self.yrange_max.clear()
    self.vrange_min.clear()
    self.vrange_max.clear()
    self.xscale_selector.setCurrentIndex(0)
    self.yscale_selector.setCurrentIndex(0)
    self.vscale_selector.setCurrentIndex(0)
    self.xscale_tresh.clear()
    self.yscale_tresh.clear()
    self.vscale_tresh.clear()
    self.typecmap_selector.setCurrentIndex(0)
    self.cmap_selector.setCurrentIndex(0)
    self.reverse_checkbox.setChecked(False)
    self.overplot_checkbox.setChecked(False)

def update_axes(self):
    self.check_axisparam()
    cmap   = self.datadict.pop('cmap')
    cscale = self.datadict.pop('cscale')
    vmin   = self.datadict.pop('vmin',self.var.min()) 
    vmax   = self.datadict.pop('vmax',self.var.max()) 
    ctresh = self.datadict.pop('tresh',max(np.abs(vmin),vmax)*0.01)
    norm        = self.I._set_cscale(cscale, vmin, vmax, ctresh)
    for artist in self.I.ax[0].get_children():
        if isinstance(artist, (plt.matplotlib.image.AxesImage,
                               plt.matplotlib.collections.QuadMesh)):
            artist.set_cmap(cmap)
            artist.set_norm(norm)

    self.set_range(xlim = None, ylim = None)
    self.I.set_axis(self.I.ax[0],**self.datadict)
    self.datadict['cmap']   = cmap
    self.datadict['cscale'] = cscale
    self.datadict['tresh']  = ctresh
    self.canvas.figure = self.I.fig
    self.canvas.draw() 

def plot_data(self):
    
    if not self.data_loaded:
        print("ERROR: No data loaded.")
        return

    var_name = self.var_selector.currentText()
    if not var_name:
        print("ERROR: No variable selected.")
        return
    
    self.var = getattr(self.D, var_name)
    
    self.var = self.var.T if self.transpose_checkbox.isChecked() else self.var
    if self.zslicetext.text() and len(np.shape(self.var)) == 3:
        self.var = self.var[:,:,int(self.zslicetext.text())]
    if self.yslicetext.text() and len(np.shape(self.var)) > 1:
        self.var = self.var[:,int(self.yslicetext.text())]
    if self.xslicetext.text():
        self.var = self.var[int(self.xslicetext.text())]

    self.vardim = len(np.shape(self.var))
    if self.vardim < 1 or self.vardim > 2:
        raise ValueError("ERROR: Variable shape not recognized.")
    self.check_axisparam()

    if self.D.geom == 'POLAR':
        convert_axis = {"R": "x1", "phi": "x2", "z": "x3", 
                        "x": "x1c", "y": "x2c"}
    elif self.D.geom == 'SPHERICAL':
        convert_axis = {"r": "x1", "theta": "x2", "phi": "x3", 
                        "R": "x1p", "z": "x2p"}
    else:
        convert_axis = {"x": "x1", "y": "x2", "z": "x3"}

    axis_convert = {key: (val if self.vardim == 1 else val[:2] + "r" + val[2:]) 
                for key, val in convert_axis.items()}
    
    if self.overplot_checkbox.isChecked() and self.vardim == 1: 
        self.numlines = self.numlines + 1 if self.numlines > 0 else 1
    else:
        self.reload_canvas()
        self.numlines = 1

    x1 = getattr(self.D, axis_convert[self.xaxis_selector.currentText()])
    x2 = getattr(self.D, axis_convert[self.yaxis_selector.currentText()])

    xlim = [x1.min(), x1.max()]
    ylim = [x2.min(), x2.max()] if self.vardim == 2 else [self.var.min(), self.var.max()]

    self.set_range(xlim, ylim)

    if self.vardim == 1:
        cmap_temp   = self.datadict.pop('cmap')
        cscale_temp = self.datadict.pop('cscale')
        ctresh_temp = self.datadict.pop('tresh', None)
        self.I.plot(x1, self.var, **self.datadict, 
                    xtitle = " ", ytitle = "var")
        self.datadict['cmap']   = cmap_temp
        self.datadict['cscale'] = cscale_temp
        if ctresh_temp is not None: self.datadict['tresh'] = ctresh_temp
    elif self.vardim == 2:
        self.I.display(self.var, x1 = x1, x2 = x2, cpos='right', 
                                 aspect = "equal", **self.datadict, 
                                 xtitle = " ", ytitle = " ", clabel = " ")

    self.firstplot = False
    self.canvas.draw()


def create_new_figure(self):
    self.I = pp.Image(figsize=[10, 6])
    self.firstplot = True
    self.figure = self.I.fig

    self.canvas = FigureCanvas(self.figure)
    self.toolbar = NavigationToolbar(self.canvas, self)
    self.canvas.setFixedWidth(800)   

    # Add new toolbar and canvas to layout
    self.canvas_layout.addWidget(self.toolbar)
    self.canvas_layout.addWidget(self.canvas)

def reload_canvas(self):
    # Remove old toolbar and canvas
    self.canvas_layout.removeWidget(self.toolbar)
    self.toolbar.deleteLater()
    self.canvas_layout.removeWidget(self.canvas)
    self.canvas.deleteLater()
    self.create_new_figure()

def check_axisparam(self):

    self.datadict = {}
    if self.vrange_min.text():
        self.datadict['vmin'] = float(self.vrange_min.text())
    if self.vrange_max.text():
        self.datadict['vmax'] = float(self.vrange_max.text())

    self.datadict['cmap']   = self.cmap_selector.currentText()
    if self.reverse_checkbox.isChecked():
        if self.datadict['cmap'][-2:] == '_r':
            self.datadict['cmap'] = self.datadict['cmap'][:-2]
        else:
            self.datadict['cmap'] += '_r'

    self.datadict['title']  = self.plot_title.text()  if self.plot_title.text()  else "" 

    self.datadict['xscale'] = self.xscale_selector.currentText()
    if self.xscale_tresh.text():
        self.datadict['xtresh'] = float(self.xscale_tresh.text())

    self.datadict['yscale'] = self.yscale_selector.currentText()
    if self.yscale_tresh.text():
        self.datadict['ytresh'] = float(self.yscale_tresh.text())

    self.datadict['cscale'] = self.vscale_selector.currentText()
    if self.vscale_tresh.text():
        self.datadict['tresh'] = float(self.vscale_tresh.text())

def set_range(self, xlim, ylim):

    # FIX RANGE!

    

    if xlim is None:
        xlim = [self.xmin, self.xmax]
    if ylim is None:
        ylim = [self.ymin, self.ymax]

    if self.firstplot is True:
        self.xmin, self.xmax = xlim
        self.ymin, self.ymax = ylim
    else:
        self.xmin = np.minimum(xlim[0], self.xmin)
        self.xmax = np.maximum(xlim[1], self.xmax)
        self.ymin = np.minimum(ylim[0], self.ymin)
        self.ymax = np.maximum(ylim[1], self.ymax)
    
    axtmax = 0.01*(self.ymax - self.ymin) if self.vardim == 1 else 0

    self.datadict['xrange'] = [
        float(self.xrange_min.text()) if self.xrange_min.text() else self.xmin,
        float(self.xrange_max.text()) if self.xrange_max.text() else self.xmax
    ]

    self.datadict['yrange'] = [
        float(self.yrange_min.text()) if self.yrange_min.text() else self.ymin - axtmax,
        float(self.yrange_max.text()) if self.yrange_max.text() else self.ymax + axtmax
    ]
