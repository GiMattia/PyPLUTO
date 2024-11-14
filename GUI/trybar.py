from PyQt6.QtWidgets import QApplication, QMainWindow, QVBoxLayout, QFileDialog, QWidget, QPushButton, QHBoxLayout, QLineEdit, QFrame, QLabel, QComboBox, QCheckBox
from matplotlib.backends.backend_qtagg import FigureCanvasQTAgg as FigureCanvas, NavigationToolbar2QT as NavigationToolbar
from matplotlib import colormaps as cmaps
import sys
import os
import pyPLUTO as pp
import numpy as np
import matplotlib.scale as mscale

scales = list(mscale.get_scale_names())
scales = [scales[3]] + [scales[0]] + scales[4:]
cmaps_avail = [list(cmaps)[2]] + list(cmaps)[0:2] + list(cmaps)[3:83]

cmaps = {'All': cmaps_avail,
         'Uniform': ['plasma', 'viridis', 'inferno', 'magma', 'cividis'],
         'Sequential': [
            'YlOrRd', 'Greys', 'Purples', 'Blues', 'Greens', 'Oranges', 'Reds',
            'YlOrBr', 'OrRd', 'PuRd', 'RdPu', 'BuPu',
            'GnBu', 'PuBu', 'YlGnBu', 'PuBuGn', 'BuGn', 'YlGn'],
         'Sequential (2)': [
            'afmhot', 'binary', 'gist_yarg', 'gist_gray', 'gray', 'bone', 
            'pink', 'spring', 'summer', 'autumn', 'winter', 'cool', 'Wistia',
            'hot', 'gist_heat', 'copper'],
         'Diverging': [
            'RdBu', 'PiYG', 'PRGn', 'BrBG', 'PuOr', 'RdGy', 
            'RdYlBu', 'RdYlGn', 'Spectral', 'coolwarm', 'bwr', 'seismic'],
         'Cyclic': ['twilight', 'twilight_shifted', 'hsv'],
         'Qualitative': [
            'Pastel1', 'Pastel2', 'Paired', 'Accent',
            'Dark2', 'Set1', 'Set2', 'Set3',
            'tab10', 'tab20', 'tab20b', 'tab20c'],
         'Miscellaneous': [
            'flag', 'prism', 'ocean', 'gist_earth', 'terrain', 'gist_stern',
            'gnuplot', 'gnuplot2', 'CMRmap', 'cubehelix', 'brg',
            'gist_rainbow', 'rainbow', 'jet', 'turbo', 'nipy_spectral',
            'gist_ncar']}

format_avail = ["None", "dbl", "flt", "vtk", "dbl.h5", "flt.h5", "hdf5", "tab"]

class PyPLUTOApp(QMainWindow):
    def __init__(self, code):
        super().__init__()     
        codestr = f" ({self.code := code})" if code != "PLUTO" else ""
        self.setWindowTitle(f"PyPLUTO GUI{codestr}")
        if code != "PLUTO":
            raise NotImplementedError(f"Code {code} not yet implemented")

        self.folder_path = None
        self.datatype    = None
        self.data_loaded = False

        main_widget = QWidget()
        self.setCentralWidget(main_widget)
        main_layout = QHBoxLayout(main_widget)

        # Left control panel
        button_layout = QVBoxLayout()

        layout = QHBoxLayout()
        self.add_combobox("datatype_selector", layout, ["fluid"])
        self.add_label("Preferred format:", layout)
        self.add_combobox("format_selector", layout, format_avail)
        button_layout.addLayout(layout)

        layout = QHBoxLayout()
        self.add_label("nout:", layout)
        self.add_lineedit("outtext", layout, "nout")
        self.add_label("vars:", layout)
        self.add_lineedit("varstext", layout, "vars")
        button_layout.addLayout(layout)

        layout = QHBoxLayout()
        self.add_pushbutton("Select Folder", layout, self.select_folder)
        self.add_pushbutton("Clear", layout, self.clearload)
        self.add_pushbutton("Reload Data", layout, self.reload_data)
        button_layout.addLayout(layout)

        self.add_line(button_layout)

        layout = QHBoxLayout()
        self.add_label("Select the variable to plot:", layout)
        self.add_combobox("var_selector", layout, [])
        self.add_checkbox("Transpose", layout)
        button_layout.addLayout(layout)

        layout = QHBoxLayout()
        self.add_label("Select the x-axis:", layout)
        self.add_combobox("xaxis_selector", layout, [], 100)
        self.add_label("y-axis:", layout)
        self.add_combobox("yaxis_selector", layout, [], 100)
        button_layout.addLayout(layout)

        layout = QHBoxLayout()
        self.add_label("Slices: x", layout)
        self.add_lineedit("xslicetext", layout, "x-slice")
        self.add_label("y", layout)
        self.add_lineedit("yslicetext", layout, "y-slice")
        self.add_label("z", layout)
        self.add_lineedit("zslicetext", layout, "z-slice")
        button_layout.addLayout(layout)

        self.add_line(button_layout)

        layout = QHBoxLayout()
        self.add_label("Insert Title:", layout)
        self.add_lineedit("plot_title", layout, "title")
        button_layout.addLayout(layout)

        layout = QHBoxLayout()
        self.add_label("xrange:", layout)
        self.add_lineedit("xrange_min", layout, "xmin")
        self.add_lineedit("xrange_max", layout, "xmax")
        self.add_label("x-scale:", layout)
        self.add_combobox("xscale_selector", layout, scales)
        self.add_lineedit("xscale_tresh", layout, "x-tresh")
        button_layout.addLayout(layout)

        layout = QHBoxLayout()
        self.add_label("yrange:", layout)
        self.add_lineedit("yrange_min", layout, "ymin")
        self.add_lineedit("yrange_max", layout, "ymax")
        self.add_label("y-scale:", layout)
        self.add_combobox("yscale_selector", layout, scales)
        self.add_lineedit("yscale_tresh", layout, "y-tresh")
        button_layout.addLayout(layout)

        layout = QHBoxLayout()
        self.add_label("vrange:", layout)
        self.add_lineedit("vrange_min", layout, "vmin")
        self.add_lineedit("vrange_max", layout, "vmax")
        self.add_label("v-scale:", layout)
        self.add_combobox("vscale_selector", layout, scales)
        self.add_lineedit("vscale_tresh", layout, "v-tresh")
        button_layout.addLayout(layout)

        layout = QHBoxLayout()
        self.add_label("cmap:", layout)
        self.add_combobox("typecmap_selector", layout, cmaps.keys())
        self.add_combobox("cmap_selector", layout, cmaps_avail)
        self.add_checkbox("reverse", layout)
        button_layout.addLayout(layout) 

        layout = QHBoxLayout()
        self.add_pushbutton("Plot", layout, self.plot_data)
        self.add_checkbox("Overplot       ", layout, "overplot_checkbox")
        button_layout.addLayout(layout)

        layout = QHBoxLayout()
        self.add_pushbutton("Update plot", layout, self.update_axes)
        self.add_pushbutton("Clear", layout, self.clear_labels)
        self.add_pushbutton("Reload Canvas", layout, self.reload_canvas)
        button_layout.addLayout(layout)

        self.add_line(button_layout)

        self.info_label = QLabel("Information:")
        self.info_label.setFixedHeight(170)
        self.info_label.setFixedWidth(250)
        button_layout.addWidget(self.info_label)
        self.info_label.setWordWrap(True) 

        self.add_line(button_layout)    

        main_layout.addLayout(button_layout)

        self.typecmap_selector.currentIndexChanged.connect(self.update_cmap_selector)

        # Right panel for Matplotlib canvas
        self.create_new_figure()
        self.canvas = FigureCanvas(self.figure)
        self.canvas.setFixedWidth(800) 
        self.canvas_layout = QVBoxLayout()
        self.toolbar = NavigationToolbar(self.canvas, self)
        self.canvas_layout.addWidget(self.toolbar)
        self.canvas_layout.addWidget(self.canvas)
        main_layout.addLayout(self.canvas_layout)

    def update_cmap_selector(self):
        selected_type = self.typecmap_selector.currentText()
        self.cmap_selector.clear()
        self.cmap_selector.addItems(cmaps.get(selected_type, []))

    def clear_labels(self):
        """
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
        """

    def update_axes(self):
        """
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
        """       

    def plot_data(self):

        if not self.data_loaded:
            print("ERROR: No data loaded.")
            return

        var_name = self.var_selector.currentText()
        if not var_name:
            print("ERROR: No variable selected.")
            return
        
        axis_convert = {"x1":  "x1r",  "x2":  "x2r",  "x3":  "x3r", 
                        "x1p": "x1rp", "x2p": "x2rp", "x3p": "x3rp",
                        "x1c": "x1rc", "x2c": "x2rc", "x3c": "x3rc"}
        self.var    = getattr(self.D, var_name)
        self.vardim = len(np.shape(self.var))
        if not self.overplot_checkbox.isChecked(): self.reload_canvas()

        self.datadict = {}
        self.check_axisparam()
        x1 = getattr(self.D, axis_convert[self.xaxis_selector.currentText()])
        x2 = getattr(self.D, axis_convert[self.yaxis_selector.currentText()])

        self.changerange = False
        if self.vardim == 1:

            self.I.plot(self.D.x1, self.var, ytitle = ' ')
        elif self.vardim == 2:
            self.I.display(self.var, x1 = self.D.x1, x2 = self.D.x2, cpos='right', aspect = "equal")
        else:
            print("ERROR: Variable shape not recognized.")

        if self.firstplot is True:
            self.original_xlim = self.I.ax[0].get_xlim()
            self.original_ylim = self.I.ax[0].get_ylim()
            self.firstplot = False
        self.canvas.draw()
        self.changerange = True

    def create_new_figure(self):
        self.I = pp.Image(figsize=[10, 6])
        self.firstplot = True
        self.figure = self.I.fig

    def reload_canvas(self):
        # Remove old toolbar and canvas
        self.canvas_layout.removeWidget(self.toolbar)
        self.toolbar.deleteLater()
        self.canvas_layout.removeWidget(self.canvas)
        self.canvas.deleteLater()

        # Re-create canvas and toolbar
        self.create_new_figure()
        self.canvas = FigureCanvas(self.figure)
        self.toolbar = NavigationToolbar(self.canvas, self)
        self.canvas.setFixedWidth(800)   

        # Add new toolbar and canvas to layout
        self.canvas_layout.insertWidget(0, self.toolbar)
        self.canvas_layout.addWidget(self.canvas)

    def load_data(self):
        try:

            if self.varstext.text():
                vars = self.varstext.text().replace(' ', '')
                vars = vars.replace('-', ',').split(',')
            else:
                vars = True
            self.D = pp.Load(self.nout, path     = self.folder_path,
                                        datatype = self.datatype,
                                        vars     = vars,
                                        full3d   = None)
            self.data_loaded = True

            
            self.var_selector.clear()
            self.var_selector.addItems(self.D._load_vars)
            self.xaxis_selector.addItems(["x1", "x2", "x3"])
            self.yaxis_selector.addItems(["x2", "x3", "x1"])
            if self.D.geom == 'POLAR':
                self.xaxis_selector.addItems(["x1c", "x2c"])
                self.yaxis_selector.addItems(["x1c", "x2c"])
            
            self.info_label.setText(str(self.D))
            self.info_label.setText(
                f"Loaded folder: {self.folder_path}\n"
                f"Format file: {self.D.format}\n"
                f"Domain:\nnx1 x nx2 x nx3 = {self.D.nx1} x {self.D.nx2} x {self.D.nx3}\n"
                f"Loaded step = {self.D.nout[0]}\nPresent Time = {self.D.ntime}\n"
                f"Variables: {', '.join(self.D._load_vars)}")
        except Exception as e:
            print(f"Error loading data: {e}")
            self.data_loaded = False

    def select_folder(self):
        format_name = self.format_selector.currentText()
        formats_list = {"dbl": "*.dbl", "flt": "*.flt", "vtk": "*.vtk",
                        "dbl,h5": "*.dbl,h5", "flt.h5": "*.flt.h5",
                        "hdf5": "*.hdf5", "tab": "*.tab", "None": None}
        bigstr = f"Preferred format: {format_name} Files ({formats_list[format_name]});;" if format_name != "None" else ""
        bigstr += "PLUTO Files (*.dbl *.vtk *.flt *.dbl.h5 *.flt.h5 *.out *.hdf5 *.tab);;All Files (*)"
        file_path, _ = QFileDialog.getOpenFileName(self, "Select a File or Folder", os.getcwd(), bigstr)
        if file_path:
            self.folder_path = os.path.dirname(file_path)
            datatype = file_path.split('/')[-1].split('.')[-1]
            datatype = datatype if datatype in formats_list.keys() else None
            datatry  = file_path.split('/')[-1].split('.')[0]
            self.datatype = datatry if datatry in formats_list.keys() and datatype is None else datatype
            self.nout = 'last'
            try:
                self.nout = int(file_path.split('/')[-1].split('.')[1])
            except:
                pass
            self.load_data()

    def reload_data(self):
        self.nout = int(self.outtext.text()) if self.outtext.text() else 'last'
        self.folder_path = "./" if self.folder_path is None else self.folder_path
        self.load_data()

    def clearload(self):
        self.folder_path = './'
        self.format_selector.setCurrentIndex(0)
        self.outtext.clear()
        self.varstext.clear()

    def check_axisparam(self):
    # Create datadict with yrange and optionally xrange
        self.datadict = {}
        """
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

        self.datadict['title']  = self.title_label.text()  if self.title_label.text()  else ""
        self.datadict['cmap']   = self.cmap_selector.currentText()
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
        """

    def add_line(self, control_layout):

        line = QFrame()
        line.setFrameShape(QFrame.Shape.HLine)
        line.setFrameShadow(QFrame.Shadow.Sunken)
        control_layout.addWidget(line)

    # Create a QComboBox and set it as an attribute of the instance
    def add_combobox(self, label, control_layout, data, width = None):

        combo_box = QComboBox()
        setattr(self, label, combo_box)
        combo_box.addItems(data)
        if isinstance(width, int):
            combo_box.setMinimumWidth(width)
        control_layout.addWidget(combo_box)

    def add_label(self, label, control_layout, data = None, width = None):

        labelgui = QLabel(label)
        if isinstance(width, int):
            labelgui.setMinimumWidth(width)
        control_layout.addWidget(labelgui)

    def add_lineedit(self, label, control_layout, data = None, width = None):

        lineedit = QLineEdit()
        setattr(self, label, lineedit)
        lineedit.setPlaceholderText(data)
        if isinstance(width, int):
            lineedit.setMinimumWidth(width)
        control_layout.addWidget(lineedit)

    def add_checkbox(self, label, control_layout, data = None, width = None):

        checkbox = QCheckBox(label)
        if data is not None:
            setattr(self, data, checkbox)
        control_layout.addWidget(checkbox)

    def add_pushbutton(self, label, control_layout, data = None, width = None):

        pushbutton = QPushButton(label)
        setattr(self, label, pushbutton)
        if isinstance(width, int):
            pushbutton.setMinimumWidth(width)
        pushbutton.clicked.connect(data)
        control_layout.addWidget(pushbutton)

def main():
    app = QApplication(sys.argv)
    window = PyPLUTOApp(code = "PLUTO")
    window.resize(1150, 720)
    window.show()
    sys.exit(app.exec())

if __name__ == "__main__":
    main()