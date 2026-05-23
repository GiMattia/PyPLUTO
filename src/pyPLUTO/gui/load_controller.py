"""Load controller for GUI data loading workflow."""

from __future__ import annotations

import os

from PySide6.QtWidgets import QFileDialog

import pyPLUTO as pp

from .custom_var import setup_var_selector
from .services import (
    axis_labels_for_geom,
    build_info_text,
    filtered_loaded_vars,
    parse_selected_file,
    parse_vars_text,
)


class LoadController:
    def __init__(self, app):
        self.app = app

    def load_data(self) -> None:
        app = self.app
        try:
            var = parse_vars_text(app.varstext.text())
            app.Data = pp.Load(
                app.nout,
                path=app.folder_path,
                datatype=app.datatype,
                var=var,
                full3D=False,
            )
            app.data_loaded = True

            app.var_selector.clear()
            app.xaxis_selector.clear()
            app.yaxis_selector.clear()

            keep = filtered_loaded_vars(app.Data)
            app.Data._load_vars = keep
            app.var_selector.addItems(list(map(str, app.Data._load_vars)))
            app.var_selector.addItems(["Custom var..."])
            setup_var_selector(app.var_selector, app.Data)

            xlabels, ylabels = axis_labels_for_geom(app.Data.geom)
            app.xaxis_selector.addItems(xlabels)
            app.yaxis_selector.addItems(ylabels)

            defs = app.var_selector.property("_cv_defs") or []
            app.info_label.setPlainText(
                build_info_text(str(app.folder_path or "./"), app.Data, defs)
            )
        except Exception as e:
            print(f"Error loading data: {e}")
            app.data_loaded = False

    def select_folder(self) -> None:
        app = self.app
        format_name = app.format_selector.currentText()
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
        starting_dir = app.folder_path if app.folder_path else os.getcwd()
        bigstr += (
            "PLUTO Files (*.dbl *.vtk *.flt *.dbl.h5 *.flt.h5 *.out "
            "*.hdf5 *.tab);;All Files (*)"
        )
        dialog = QFileDialog(
            app, "Select a File or Folder", starting_dir, bigstr
        )
        dialog.setOption(QFileDialog.Option.DontUseNativeDialog, True)
        dialog.setFileMode(QFileDialog.FileMode.ExistingFile)

        def on_accept():
            if selected := dialog.selectedFiles():
                self.finalize_load_path(selected[0])

        dialog.accepted.connect(on_accept)
        dialog.open()
        app._file_dialog = dialog

    def reload_data(self) -> None:
        app = self.app
        var_name = app.var_selector.currentText()
        app.nout = int(app.outtext.text()) if app.outtext.text() else "last"
        app.folder_path = "./" if app.folder_path is None else app.folder_path
        self.load_data()
        defs = app.var_selector.property("_cv_defs") or []
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
            app.Data, "load_vars", getattr(app.Data, "_load_vars", [])
        )
        if var_name in loaded_vars or var_name in custom_names:
            app.var_selector.setCurrentText(var_name)

    def clearload(self) -> None:
        app = self.app
        app.folder_path = "./"
        app.format_selector.setCurrentIndex(0)
        app.outtext.clear()
        app.varstext.clear()

    def finalize_load_path(self, file_path: str) -> None:
        app = self.app
        app.folder_path, app.datatype, app.nout = parse_selected_file(file_path)
        self.load_data()
