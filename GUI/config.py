from PyQt6.QtWidgets import QFileDialog
import os
import pyPLUTO as pp

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
        self.xaxis_selector.clear()
        self.yaxis_selector.clear()
        self.var_selector.addItems(self.D._load_vars)
        xaxis_labels = ["x1", "x2", "x3"]
        yaxis_labels = ["x2", "x3", "x1"]
        if self.D.geom == 'POLAR':
            xaxis_labels.extend(["x1c", "x2c"])
            yaxis_labels.extend(["x1c", "x2c"])
        if self.D.geom == 'SPHERICAL':
            xaxis_labels.extend(["x1p", "x2p"])
            yaxis_labels.extend(["x1p", "x2p"])
        
        self.xaxis_selector.addItems(xaxis_labels)
        self.yaxis_selector.addItems(yaxis_labels)
            
        self.info_label.setText(str(self.D))
        self.info_label.setText(
            f"Loaded folder: {self.folder_path}\n"
            f"Format file: {self.D.format}\n"
            f"Geometry: {self.D.geom}\n"
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