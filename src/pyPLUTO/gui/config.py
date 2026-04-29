"""Configure the Load object for th GUI."""

import os
import re

import numpy as np
from PySide6.QtWidgets import QFileDialog

import pyPLUTO as pp

from .custom_var import setup_var_selector


def load_data(self):
    """Load the data from the selected folder."""
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
            full3D=False,
        )
        self.data_loaded = True

        self.var_selector.clear()
        self.xaxis_selector.clear()
        self.yaxis_selector.clear()

        keep = []
        raw_nshp = getattr(self.D, "nshp", ())
        if isinstance(raw_nshp, tuple):
            grid_shape = raw_nshp
        elif isinstance(raw_nshp, int):
            grid_shape = (raw_nshp,)
        else:
            try:
                grid_shape = tuple(raw_nshp)
            except TypeError:
                grid_shape = ()

        # Keep compatibility across old/new loaders and transposed layouts.
        grid_shape_candidates = {grid_shape}
        if len(grid_shape) > 1:
            grid_shape_candidates.add(tuple(reversed(grid_shape)))

        loaded_vars = getattr(
            self.D, "load_vars", getattr(self.D, "_load_vars", [])
        )
        if not loaded_vars:
            loaded_vars = list(getattr(self.D, "d_vars", {}).keys())

        for v in list(map(str, loaded_vars)):
            a = getattr(self.D, v, None)

            # keep only full-grid arrays
            if isinstance(a, np.ndarray) and (a.shape in grid_shape_candidates):
                keep.append(v)

        # Fallback: avoid empty selector if loader shape conventions differ.
        if not keep:
            keep = [
                v
                for v in map(str, loaded_vars)
                if isinstance(getattr(self.D, v, None), np.ndarray)
            ]
        self.D._load_vars = keep
        self.var_selector.addItems(self.D._load_vars)

        self.var_selector.addItems(["Custom var..."])
        setup_var_selector(self.var_selector, self.D)

        if self.D.geom == "POLAR":
            xaxis_labels = ["R", "phi", "z", "x", "y"]
            yaxis_labels = ["phi", "z", "R", "x", "y"]
        elif self.D.geom == "SPHERICAL":
            xaxis_labels = ["r", "theta", "phi", "R", "z", "Rt", "zt"]
            yaxis_labels = ["theta", "phi", "r", "R", "z", "Rt", "zt"]
        else:
            xaxis_labels = ["x", "y", "z"]
            yaxis_labels = ["y", "z", "x"]

        self.xaxis_selector.addItems(xaxis_labels)
        self.yaxis_selector.addItems(yaxis_labels)

        # Base info
        base = (
            f"Loaded folder: {self.folder_path}\n"
            f"Format file: {getattr(self.D, 'datatype', 'Unknown')}\n"
            f"Geometry: {self.D.geom}\n"
            f"Domain: {self.D.nx1} x {self.D.nx2} x {self.D.nx3}\n"
            f"Loaded step = "
            f"{self.D.nout[0] if np.ndim(self.D.nout) else self.D.nout}\n"
            f"Present Time = {self.D.ntime}\n"
            f"Variables: {', '.join(self.D._load_vars)}"
        )

        # Append custom vars defined in this session (if any)
        defs = self.var_selector.property("_cv_defs") or []
        CUSTOM_VAR_TUPLE_LENGTH = 3
        if defs:
            lines = []
            for tup in defs:
                if len(tup) == CUSTOM_VAR_TUPLE_LENGTH:
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
    """Open a dialog to select the folder containing the data."""
    format_name = self.format_selector.currentText()
    formats_list = {
        "dbl": "*.dbl",
        "flt": "*.flt",
        "vtk": "*.vtk",
        "dbl.h5": "*.dbl.h5",
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
    bigstr += (
        "PLUTO Files (*.dbl *.vtk *.flt *.dbl.h5 *.flt.h5 *.out "
        "*.hdf5 *.tab);;All Files (*)"
    )
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
    """Reload the data from the selected folder."""
    var_name = self.var_selector.currentText()
    self.nout = int(self.outtext.text()) if self.outtext.text() else "last"
    self.folder_path = "./" if self.folder_path is None else self.folder_path
    self.load_data()
    defs = self.var_selector.property("_cv_defs") or []
    custom_names = []
    for item in defs:
        display_name = item[0]
        clean_name = (
            display_name[1:]
            if str(display_name).startswith("!")
            else display_name
        )
        custom_names.append(clean_name)

    loaded_vars = getattr(
        self.D, "load_vars", getattr(self.D, "_load_vars", [])
    )
    if var_name in loaded_vars or var_name in custom_names:
        self.var_selector.setCurrentText(var_name)


def clearload(self):
    """Clear the loaded data and reset the GUI fields."""
    self.folder_path = "./"
    self.format_selector.setCurrentIndex(0)
    self.outtext.clear()
    self.varstext.clear()


def _finalize_load_path(self, file_path):
    """Finalize the load path and extract relevant information."""
    self.folder_path = os.path.dirname(file_path)
    filename = os.path.basename(file_path)
    if filename.endswith(".dbl.h5"):
        self.datatype = "dbl.h5"
    elif filename.endswith(".flt.h5"):
        self.datatype = "flt.h5"
    else:
        parts = filename.rsplit(".", maxsplit=1)
        self.datatype = parts[-1] if len(parts) == 2 else None
    try:
        match = re.search(r"\.(\d+)\.", filename)
        self.nout = int(match.group(1)) if match else "last"
    except Exception:
        self.nout = "last"
    self.load_data()
