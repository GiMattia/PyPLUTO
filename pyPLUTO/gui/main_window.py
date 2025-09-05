from PyQt6.QtWidgets import (
    QHBoxLayout,
    QMainWindow,
    QTextEdit,
    QVBoxLayout,
    QWidget,
)

from .globals import cmaps, cmaps_avail, format_avail, scales, vscales


class PyPLUTOApp(QMainWindow):
    def __init__(self, code: str):
        super().__init__()
        codestr = f" ({self.code:= code})" if code != "PLUTO" else ""
        self.setWindowTitle(f"PyPLUTO GUI{codestr}")
        if code != "PLUTO":
            raise NotImplementedError(f"Code {code} not yet implemented")

        self.folder_path = None
        self.datatype = None
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
        self.add_pushbutton("Select File", layout, self.select_folder)
        self.add_pushbutton("Clear", layout, self.clearload)
        self.add_pushbutton("Reload Folder", layout, self.reload_data)
        button_layout.addLayout(layout)

        self.add_line(button_layout)

        layout = QHBoxLayout()
        self.add_label("Select the variable to plot:", layout)
        self.add_combobox("var_selector", layout, [])
        self.add_checkbox("Transpose", layout, "transpose_checkbox")
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
        self.add_checkbox("Auto-ratio", layout, "ratio_checkbox")
        self.ratio_checkbox.setChecked(True)  # type: ignore
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
        self.add_combobox("vscale_selector", layout, vscales)
        self.add_lineedit("vscale_tresh", layout, "v-tresh")
        button_layout.addLayout(layout)

        layout = QHBoxLayout()
        self.add_label("cmap:", layout)
        self.add_combobox("typecmap_selector", layout, cmaps.keys())
        self.add_combobox("cmap_selector", layout, cmaps_avail)
        self.add_checkbox("reverse", layout, "reverse_checkbox")
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

        info_box = QTextEdit()
        info_box.setObjectName("info_label")
        info_box.setReadOnly(True)
        info_box.setFixedSize(370, 200)  # keep your original fixed size
        button_layout.addWidget(info_box)
        self.info_label = info_box

        self.add_line(button_layout)

        main_layout.addLayout(button_layout)

        self.typecmap_selector.currentIndexChanged.connect(
            self.update_cmap_selector
        )  # type: ignore

        self.canvas_layout = QVBoxLayout()
        self.create_new_figure()
        main_layout.addLayout(self.canvas_layout)

    from .config import (
        _finalize_load_path,
        clearload,
        load_data,
        reload_data,
        select_folder,
    )
    from .panels import (
        add_checkbox,
        add_combobox,
        add_label,
        add_line,
        add_lineedit,
        add_pushbutton,
    )
    from .utils import (
        check_axisparam,
        clear_labels,
        create_new_figure,
        plot_data,
        reload_canvas,
        set_range,
        update_axes,
        update_cmap_selector,
    )
