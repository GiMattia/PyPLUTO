"""Load controller for GUI data loading workflow."""

from __future__ import annotations

import logging
import os
from typing import TYPE_CHECKING, cast

from PySide6.QtWidgets import QFileDialog

if TYPE_CHECKING:
    from pyPLUTO.gui.main_window import PyPLUTOApp

import pyPLUTO as pp
from pyPLUTO.gui.custom_var import setup_var_selector
from pyPLUTO.gui.services import (
    axis_labels_for_geom,
    build_info_text,
    filtered_loaded_vars,
    parse_selected_file,
    parse_vars_text,
)

logger = logging.getLogger(__name__)


class LoadController:
    """Handle GUI actions for selecting paths and loading/reloading data."""

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
        self.app: PyPLUTOApp = app

    def load_data(self) -> None:
        """Read data from disk and populate all variable/axis selectors.

        Returns
        -------
        - None

        """
        app = self.app
        try:
            # parse the vars text field, then load the dataset from disk
            var = parse_vars_text(app.varstext.text())
            app.Data = pp.Load(
                app.nout,
                path=cast(
                    "str", app.folder_path
                ),  # always set before this call
                datatype=app.datatype,
                var=var,
                full3D=False,
            )
            app.data_loaded = True

            # clear all selectors before repopulating with the new dataset
            app.var_selector.clear()
            app.xaxis_selector.clear()
            app.yaxis_selector.clear()

            # drop coordinate arrays; keep only plottable variables
            keep = filtered_loaded_vars(app.Data)
            app.Data._load_vars = keep
            app.var_selector.addItems(list(map(str, app.Data._load_vars)))
            app.var_selector.addItems(["Custom var..."])
            setup_var_selector(app.var_selector, app.Data)

            # axis labels depend on the grid geometry (cartesian, polar, …)
            xlabels, ylabels = axis_labels_for_geom(app.Data.geom)
            app.xaxis_selector.addItems(xlabels)
            app.yaxis_selector.addItems(ylabels)

            # refresh the info panel including any custom-variable definitions
            defs = app.var_selector.property("_cv_defs") or []
            app.info_label.setPlainText(
                build_info_text(str(app.folder_path or "./"), app.Data, defs),
            )
        except Exception as e:
            logger.error("Error loading data: %s", e)
            app.data_loaded = False

    def select_folder(self) -> None:
        """Open a non-native file dialog and trigger a load on accept.

        Returns
        -------
        - None

        """
        app = self.app
        format_name = app.format_selector.currentText()

        # map each format name to its glob pattern for the dialog filter
        formats_list: dict[str, str | None] = {
            "dbl": "*.dbl",
            "flt": "*.flt",
            "vtk": "*.vtk",
            "dbl.h5": "*.dbl.h5",
            "flt.h5": "*.flt.h5",
            "hdf5": "*.hdf5",
            "tab": "*.tab",
            "None": None,
        }

        # preferred format appears first in the filter string when selected
        bigstr = (
            (
                f"Preferred format: {format_name} "
                f"Files ({formats_list[format_name]});;"
            )
            if format_name != "None"
            else ""
        )
        starting_dir: str = app.folder_path or os.getcwd()
        bigstr += (
            "PLUTO Files (*.dbl *.vtk *.flt *.dbl.h5 *.flt.h5 *.out "
            "*.hdf5 *.tab);;All Files (*)"
        )

        # non-native dialog required so folder navigation also exposes files
        dialog = QFileDialog(
            app,
            "Select a File or Folder",
            starting_dir,
            bigstr,
        )
        dialog.setOption(QFileDialog.Option.DontUseNativeDialog, True)
        dialog.setFileMode(QFileDialog.FileMode.ExistingFile)

        def on_accept() -> None:
            """Slot called when the file dialog is accepted; triggers a load."""
            if selected := dialog.selectedFiles():
                self.finalize_load_path(selected[0])

        dialog.accepted.connect(on_accept)
        dialog.open()
        # keep a reference so PySide6 doesn't GC the dialog before it renders
        app._file_dialog = dialog

    def reload_data(self) -> None:
        """Reread data with current settings, preserving the active variable.

        Returns
        -------
        - None

        """
        app = self.app
        var_name = app.var_selector.currentText()

        # read nout from the text field; fall back to "last" if empty
        app.nout = int(app.outtext.text()) if app.outtext.text() else "last"
        app.folder_path = "./" if app.folder_path is None else app.folder_path
        self.load_data()

        # collect custom variable names, stripping the "!" override prefix
        defs = app.var_selector.property("_cv_defs") or []
        custom_names: list[str] = []
        for item in defs:
            display_name = item[0]
            clean_name = (
                display_name[1:]
                if str(display_name).startswith("!")
                else display_name
            )
            custom_names.append(clean_name)

        # restore the previously selected variable if it survived the reload
        loaded_vars: list[str] = getattr(
            app.Data,
            "load_vars",
            getattr(app.Data, "_load_vars", []),
        )
        if var_name in loaded_vars or var_name in custom_names:
            app.var_selector.setCurrentText(var_name)

    def clearload(self) -> None:
        """Reset all load-panel fields to their defaults.

        Returns
        -------
        - None

        """
        # reset folder, format, nout, and vars fields to their initial state
        app = self.app
        app.folder_path = "./"
        app.format_selector.setCurrentIndex(0)
        app.outtext.clear()
        app.varstext.clear()

    def finalize_load_path(self, file_path: str) -> None:
        """Parse the selected file path and trigger a data load.

        Parameters
        ----------
        - file_path: str
            Absolute or relative path to the selected file. The folder,
            datatype, and output index are inferred from this path.

        Returns
        -------
        - None

        """
        # infer folder, datatype, and output index from the chosen file
        app = self.app
        app.folder_path, app.datatype, app.nout = parse_selected_file(file_path)
        self.load_data()
