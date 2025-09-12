import os

from PyQt6.QtWidgets import QFileDialog

import pyPLUTO as pp

from .custom_var import setup_var_selector


def load_data(self):
    try:
        if self.varstext.text():
            vars = self.varstext.text().replace(" ", "")
            vars = vars.replace("-", ",").split(",")
        else:
            vars = True
        self.D = pp.Load(
            self.nout,
            path=self.folder_path,
            datatype=self.datatype,
            vars=vars,
            full3d=None,
        )
        self.data_loaded = True

        self.var_selector.clear()
        self.xaxis_selector.clear()
        self.yaxis_selector.clear()
        self.var_selector.addItems(self.D._load_vars)
        self.var_selector.addItems(["Custom var..."])
        setup_var_selector(self.var_selector, self.D)

        if self.D.geom == "POLAR":
            xaxis_labels = ["R", "phi", "z", "x", "y"]
            yaxis_labels = ["phi", "z", "R", "x", "y"]
        elif self.D.geom == "SPHERICAL":
            xaxis_labels = ["r", "theta", "phi", "R", "z"]
            yaxis_labels = ["theta", "phi", "r", "R", "z"]
        else:
            xaxis_labels = ["x", "y", "z"]
            yaxis_labels = ["y", "z", "x"]

        self.xaxis_selector.addItems(xaxis_labels)
        self.yaxis_selector.addItems(yaxis_labels)

        # Base info
        base = (
            f"Loaded folder: {self.folder_path}\n"
            f"Format file: {self.D.format}\n"
            f"Geometry: {self.D.geom}\n"
            f"Domain:\nnx1 x nx2 x nx3 = {self.D.nx1} x {self.D.nx2} x {self.D.nx3}\n"
            f"Loaded step = {self.D.nout[0]}\nPresent Time = {self.D.ntime}\n"
            f"Variables: {', '.join(self.D._load_vars)}"
        )

        # Append custom vars defined in this session (if any)
        defs = self.var_selector.property("_cv_defs") or []
        if defs:
            lines = []
            for tup in defs:
                if len(tup) == 3:
                    name, _clean, disp = tup
                    lines.append(f"{name} = {disp}")
                else:
                    # backward-compat: (name, expr)
                    name, expr = tup
                    lines.append(f"{name} = {expr}")
            base += "\n\nCustom variables:\n" + "\n".join(lines)

        self.info_label.setPlainText(base)

    except Exception as e:
        print(f"Error loading data: {e}")
        self.data_loaded = False


def select_folder(self):
    format_name = self.format_selector.currentText()
    formats_list = {
        "dbl": "*.dbl",
        "flt": "*.flt",
        "vtk": "*.vtk",
        "dbl,h5": "*.dbl,h5",
        "flt.h5": "*.flt.h5",
        "hdf5": "*.hdf5",
        "tab": "*.tab",
        "None": None,
    }
    bigstr = (
        f"Preferred format: {format_name} Files ({formats_list[format_name]});;"
        if format_name != "None"
        else ""
    )
    starting_dir = self.folder_path if self.folder_path else os.getcwd()
    bigstr += "PLUTO Files (*.dbl *.vtk *.flt *.dbl.h5 *.flt.h5 *.out *.hdf5 *.tab);;All Files (*)"
    dialog = QFileDialog(self, "Select a File or Folder", starting_dir, bigstr)
    dialog.setOption(QFileDialog.Option.DontUseNativeDialog, True)
    dialog.setFileMode(QFileDialog.FileMode.ExistingFile)

    def on_accept():
        selected = dialog.selectedFiles()
        if selected:
            file_path = selected[0]
            self._finalize_load_path(file_path)

    dialog.accepted.connect(on_accept)
    dialog.open()
    self._file_dialog = dialog  # Save for automation access


def reload_data(self):
    var_name = self.var_selector.currentText()
    self.nout = int(self.outtext.text()) if self.outtext.text() else "last"
    self.folder_path = "./" if self.folder_path is None else self.folder_path
    self.load_data()
    if var_name in self.D._load_vars:
        self.var_selector.setCurrentText(var_name)


def clearload(self):
    self.folder_path = "./"
    self.format_selector.setCurrentIndex(0)
    self.outtext.clear()
    self.varstext.clear()


def _finalize_load_path(self, file_path):
    self.folder_path = os.path.dirname(file_path)
    filename = os.path.basename(file_path)
    parts = filename.split(".")
    self.datatype = parts[-1]
    try:
        self.nout = int(parts[1])
    except Exception:
        self.nout = "last"
    self.load_data()
