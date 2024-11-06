
import os
import pyPLUTO as pp
from PyQt6.QtWidgets import QFileDialog
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

def load_data(self):
    try:

        if self.varstext.text():
            vars = self.varstext.text().replace(' ', '')
            vars = vars.replace('-', ',').split(',')
        else:
            vars = True
        self.amrlev = int(self.amr_selector.text()) if self.amr_selector.text() else 0
        self.full3D = True if self.threed_checkbox.isChecked() else False
        self.D = pp.Load(self.nout, path=self.folder_path,
                                    datatype = self.datatype,
                                    vars = vars,
                                    full3d = self.full3D,
                                    level = self.amrlev)
        self.data_loaded = True
        self.var_selector.clear()
        self.var_selector.addItems(self.D._load_vars)
        self.xaxis_selector.addItems(["x1", "x2", "x3"])
        self.yaxis_selector.addItems(["x2", "x3", "x1"])
        if self.D.geom == 'POLAR':
            self.xaxis_selector.addItems(["x1c", "x2c"])
            self.yaxis_selector.addItems(["x1c", "x2c"])
        #self.info_label.setText(str(self.D))
        #self.info_label.setText(
        #    f"Loaded folder: {self.folder_path}\n"
        #    f"Format file: {self.D.format}\n"
        #    f"Domain:\nnx1 x nx2 x nx3 = {self.D.nx1} x {self.D.nx2} x {self.D.nx3}\n"
        #    f"Loaded step = {self.D.nout[0]}\nPresent Time = {self.D.ntime}\n"
        #    f"Variables: {', '.join(self.D._load_vars)}")
    except Exception as e:
        print(f"Error loading data: {e}")
        self.data_loaded = False

def clearload(self):
    self.folder_path = './'
    self.outtext.clear()
    self.varstext.clear()
    self.amr_selector.clear()
    self.nlp_selector.clear()