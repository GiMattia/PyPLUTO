"""Main window and UI wiring for the PyPLUTO GUI application."""

from __future__ import annotations

import bisect
from collections.abc import Callable
from typing import Any

from matplotlib.backends.backend_qt import (
    NavigationToolbar2QT as NavigationToolbar,
)
from matplotlib.backends.backend_qtagg import FigureCanvasQTAgg as FigureCanvas
from PySide6.QtCore import Qt, QTimer
from PySide6.QtWidgets import (
    QCheckBox,
    QComboBox,
    QDoubleSpinBox,
    QFileDialog,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QMainWindow,
    QPushButton,
    QSlider,
    QSpinBox,
    QTextEdit,
    QVBoxLayout,
    QWidget,
)

from pyPLUTO.gui.app_state import AppState
from pyPLUTO.gui.globals import (
    cmaps_avail,
    cmaps_divided,
    scales,
    vscales,
)
from pyPLUTO.gui.load_controller import LoadController
from pyPLUTO.gui.panels import PanelsMixin
from pyPLUTO.gui.plot_controller import PlotController
from pyPLUTO.gui.state_accessors import StateAccessorsMixin


class PyPLUTOApp(QMainWindow, PanelsMixin, StateAccessorsMixin):
    """Main application window for loading data and controlling plots."""

    # --- Qt widgets (set in _build_* methods) ---
    datatype_selector: QComboBox
    varstext: QLineEdit
    time_slider: QSlider
    nout_display: QSpinBox
    var_selector: QComboBox
    xaxis_selector: QComboBox
    yaxis_selector: QComboBox
    xslicetext: QLineEdit
    yslicetext: QLineEdit
    zslicetext: QLineEdit
    plot_title: QLineEdit
    xrange_min: QLineEdit
    xrange_max: QLineEdit
    yrange_min: QLineEdit
    yrange_max: QLineEdit
    vrange_min: QLineEdit
    vrange_max: QLineEdit
    xscale_selector: QComboBox
    yscale_selector: QComboBox
    vscale_selector: QComboBox
    xscale_tresh: QLineEdit
    yscale_tresh: QLineEdit
    vscale_tresh: QLineEdit
    typecmap_selector: QComboBox
    cmap_selector: QComboBox
    transpose_checkbox: QCheckBox
    ratio_checkbox: QCheckBox
    reverse_checkbox: QCheckBox
    overplot_checkbox: QCheckBox
    info_label: QTextEdit

    # --- Canvas / figure (set by PlotController.create_new_figure) ---
    canvas: FigureCanvas
    toolbar: NavigationToolbar
    canvas_layout: QVBoxLayout
    figure: Any
    Image: Any

    # --- Plot state (set by PlotController) ---
    var: Any
    xslice: Any
    yslice: Any
    zslice: Any

    # --- Playback controls (set in _build_playback_row) ---
    rewind_btn: QPushButton
    back_btn: QPushButton
    play_btn: QPushButton
    pause_btn: QPushButton
    forward_btn: QPushButton
    last_btn: QPushButton
    interval_spinbox: QDoubleSpinBox
    playback_buttons: list[QPushButton]
    _play_timer: QTimer

    # --- File dialog ---
    _file_dialog: QFileDialog | None

    def __init__(self, code: str) -> None:
        """Initialize the main application window.

        Parameters
        ----------
        code : str
            The code identifier for the application.
        """
        super().__init__()
        self.state = AppState()
        self.code: str
        codestr = f" ({self.code:= code})" if code != "PLUTO" else ""
        self.setWindowTitle(f"PyPLUTO GUI{codestr}")
        if code != "PLUTO":
            raise NotImplementedError(f"Code {code} not yet implemented")

        main_widget = QWidget()
        self.setCentralWidget(main_widget)
        main_layout = QHBoxLayout(main_widget)

        self.load_controller = LoadController(self)
        self.plot_controller = PlotController(self)

        button_layout = QVBoxLayout()
        button_layout.setSpacing(6)
        self._build_load_panel(button_layout)
        self.add_line(button_layout)
        self._build_variable_panel(button_layout)
        self.add_line(button_layout)
        self._build_slider_row(button_layout)
        self._build_playback_row(button_layout)
        self.add_line(button_layout)
        self._build_plot_panel(button_layout)
        self.add_line(button_layout)
        self._build_info_box(button_layout)
        self.add_line(button_layout)
        main_layout.addLayout(button_layout)

        self.typecmap_selector.currentIndexChanged.connect(
            self.plot_controller.update_cmap_selector,
        )

        self.canvas_layout = QVBoxLayout()
        self.plot_controller.create_new_figure()
        main_layout.addLayout(self.canvas_layout)

    def _build_load_panel(self, button_layout: QVBoxLayout) -> None:
        """Add data-loading controls: datatype, vars, and file buttons."""
        layout = QHBoxLayout()
        self.datatype_selector = self.add_combobox(layout, ["PLUTO fluid"])
        self.add_label("vars:", layout)
        self.varstext = self.add_lineedit(layout, "vars")
        button_layout.addLayout(layout)

        layout = QHBoxLayout()
        self.add_pushbutton("Select File", layout, self.select_folder)
        self.add_pushbutton("Clear", layout, self.load_controller.clearload)
        self.add_pushbutton(
            "Reload Folder",
            layout,
            self.load_controller.reload_data,
        )
        button_layout.addLayout(layout)

    def _build_variable_panel(self, button_layout: QVBoxLayout) -> None:
        """Add variable/axis/slice selectors."""
        layout = QHBoxLayout()
        self.add_label("Select the variable to plot:", layout)
        self.var_selector = self.add_combobox(layout, [])
        self.transpose_checkbox = self.add_checkbox("Transpose", layout)
        button_layout.addLayout(layout)

        layout = QHBoxLayout()
        self.add_label("Select the x-axis:", layout)
        self.xaxis_selector = self.add_combobox(layout, [], 100)
        self.add_label("y-axis:", layout)
        self.yaxis_selector = self.add_combobox(layout, [], 100)
        button_layout.addLayout(layout)

        layout = QHBoxLayout()
        self.add_label("Slices: x", layout)
        self.xslicetext = self.add_lineedit(layout, "x-slice")
        self.add_label("y", layout)
        self.yslicetext = self.add_lineedit(layout, "y-slice")
        self.add_label("z", layout)
        self.zslicetext = self.add_lineedit(layout, "z-slice")
        button_layout.addLayout(layout)

    def _build_plot_panel(self, button_layout: QVBoxLayout) -> None:
        """Add plot-options controls.

        More specifically: title, ranges, scales, cmap, and plot buttons.
        """
        layout = QHBoxLayout()
        self.add_label("Insert Title:", layout)
        self.plot_title = self.add_lineedit(layout, "title")
        self.ratio_checkbox = self.add_checkbox("Auto-ratio", layout)
        self.ratio_checkbox.setChecked(True)
        button_layout.addLayout(layout)

        layout = QHBoxLayout()
        self.add_label("xrange:", layout)
        self.xrange_min = self.add_lineedit(layout, "xmin")
        self.xrange_max = self.add_lineedit(layout, "xmax")
        self.add_label("x-scale:", layout)
        self.xscale_selector = self.add_combobox(layout, scales)
        self.xscale_tresh = self.add_lineedit(layout, "x-tresh")
        button_layout.addLayout(layout)

        layout = QHBoxLayout()
        self.add_label("yrange:", layout)
        self.yrange_min = self.add_lineedit(layout, "ymin")
        self.yrange_max = self.add_lineedit(layout, "ymax")
        self.add_label("y-scale:", layout)
        self.yscale_selector = self.add_combobox(layout, scales)
        self.yscale_tresh = self.add_lineedit(layout, "y-tresh")
        button_layout.addLayout(layout)

        layout = QHBoxLayout()
        self.add_label("vrange:", layout)
        self.vrange_min = self.add_lineedit(layout, "vmin")
        self.vrange_max = self.add_lineedit(layout, "vmax")
        self.add_label("v-scale:", layout)
        self.vscale_selector = self.add_combobox(layout, vscales)
        self.vscale_tresh = self.add_lineedit(layout, "v-tresh")
        button_layout.addLayout(layout)

        layout = QHBoxLayout()
        self.add_label("cmap:", layout)
        self.typecmap_selector = self.add_combobox(
            layout,
            list(cmaps_divided.keys()),
        )
        self.cmap_selector = self.add_combobox(layout, cmaps_avail)
        self.reverse_checkbox = self.add_checkbox("reverse", layout)
        button_layout.addLayout(layout)

        layout = QHBoxLayout()
        self.add_pushbutton("Plot", layout, self.plot_controller.plot_data)
        self.overplot_checkbox = self.add_checkbox("Overplot", layout)
        self.add_pushbutton(
            "Lock Lines", layout, self.plot_controller.lock_lines
        )
        button_layout.addLayout(layout)

        layout = QHBoxLayout()
        self.add_pushbutton(
            "Update plot",
            layout,
            self.plot_controller.update_axes,
        )
        self.add_pushbutton("Clear", layout, self.plot_controller.clear_labels)
        self.add_pushbutton(
            "Reload Canvas",
            layout,
            self.plot_controller.reload_canvas,
        )
        button_layout.addLayout(layout)

    def _build_info_box(self, button_layout: QVBoxLayout) -> None:
        """Add the read-only info/log text panel."""
        info_box = QTextEdit()
        info_box.setObjectName("info_label")
        info_box.setReadOnly(True)
        info_box.setFixedSize(370, 200)
        button_layout.addWidget(info_box)
        self.info_label = info_box

    def _build_playback_row(self, button_layout: QVBoxLayout) -> None:
        """Add media-style playback controls below the nout slider."""
        row_widget = QWidget()
        row_widget.setMaximumHeight(30)
        row = QHBoxLayout(row_widget)
        row.setContentsMargins(4, 0, 4, 0)
        row.setSpacing(3)

        def _btn(label: str, callback: Callable[[], None]) -> QPushButton:
            b = QPushButton(label)
            b.setFixedWidth(43)
            b.setEnabled(False)
            b.clicked.connect(callback)
            row.addWidget(b, stretch=1)
            return b

        self.rewind_btn = _btn("⏮", self._on_rewind)
        self.back_btn = _btn("⯬", self._on_back)
        self.play_btn = _btn("▶", self._on_play)
        self.pause_btn = _btn("⏸", self._on_pause)
        self.forward_btn = _btn("⯮", self._on_forward)
        self.last_btn = _btn("⏭", self._on_last)

        self.playback_buttons = [
            self.rewind_btn,
            self.back_btn,
            self.play_btn,
            self.pause_btn,
            self.forward_btn,
            self.last_btn,
        ]

        row.addWidget(QLabel("dt(s):"))
        self.interval_spinbox = QDoubleSpinBox()
        self.interval_spinbox.setRange(0.05, 60.0)
        self.interval_spinbox.setValue(0.1)
        self.interval_spinbox.setSingleStep(0.01)
        self.interval_spinbox.setDecimals(2)
        self.interval_spinbox.setFixedWidth(60)
        row.addWidget(self.interval_spinbox)

        button_layout.addWidget(row_widget)

        self._play_timer = QTimer(self)
        self._play_timer.setSingleShot(True)
        self._play_timer.timeout.connect(self._on_play_tick)

    def _build_slider_row(self, button_layout: QVBoxLayout) -> None:
        """Add a time-step slider to the left control panel."""
        self.time_slider = QSlider(Qt.Orientation.Horizontal)
        self.time_slider.setEnabled(False)

        self.nout_display = QSpinBox()
        self.nout_display.setButtonSymbols(QSpinBox.ButtonSymbols.NoButtons)
        self.nout_display.setFixedWidth(60)
        self.nout_display.setRange(0, 99999)
        self.nout_display.setEnabled(False)

        row_widget = QWidget()
        row_widget.setMaximumHeight(26)
        row = QHBoxLayout(row_widget)
        row.setContentsMargins(4, 0, 4, 0)
        row.addWidget(QLabel("nout:"))
        row.addWidget(self.time_slider)
        row.addWidget(self.nout_display)
        button_layout.addWidget(row_widget)

        self.time_slider.sliderMoved.connect(self._on_slider_moved)
        self.nout_display.editingFinished.connect(self._on_nout_typed)

    def _on_slider_moved(self, value: int) -> None:
        """Reload data at the selected nout and replay all live specs."""
        if not self.data_loaded:
            return
        nout = int(self.Data.outlist[value])
        self.nout = nout
        self.nout_display.setValue(nout)
        self.load_controller.reload_data()
        if not self.live_specs:
            self.info_label.append(
                "No live lines to replay — plot a line first, "
                "or overplot after locking."
            )
            return
        self.plot_controller.replay_all()

    def _on_nout_typed(self) -> None:
        """Move slider to the typed nout and replot."""
        if not self.data_loaded:
            return
        target = self.nout_display.value()
        outlist = self.Data.outlist.tolist()
        try:
            idx = outlist.index(target)
        except ValueError:
            idx = min(bisect.bisect_left(outlist, target), len(outlist) - 1)
        self.time_slider.setValue(idx)
        self._on_slider_moved(idx)

    def _on_rewind(self) -> None:
        """Stop playback and jump to the first output."""
        self._play_timer.stop()
        self.time_slider.setValue(0)
        self._on_slider_moved(0)

    def _on_back(self) -> None:
        """Step the slider back by one output."""
        idx = max(0, self.time_slider.value() - 1)
        self.time_slider.setValue(idx)
        self._on_slider_moved(idx)

    def _on_play(self) -> None:
        """Start automatic playback at the current interval setting."""
        if not self.data_loaded:
            return
        interval_ms = int(self.interval_spinbox.value() * 1000)
        self._play_timer.start(interval_ms)

    def _on_pause(self) -> None:
        """Pause automatic playback."""
        self._play_timer.stop()

    def _on_forward(self) -> None:
        """Step the slider forward by one output."""
        idx = min(self.time_slider.maximum(), self.time_slider.value() + 1)
        self.time_slider.setValue(idx)
        self._on_slider_moved(idx)

    def _on_last(self) -> None:
        """Stop playback and jump to the last output."""
        self._play_timer.stop()
        idx = self.time_slider.maximum()
        self.time_slider.setValue(idx)
        self._on_slider_moved(idx)

    def _on_play_tick(self) -> None:
        """Advance one step then reschedule; stop automatically at the end."""
        idx = self.time_slider.value() + 1
        if idx > self.time_slider.maximum():
            return
        self.time_slider.setValue(idx)
        self._on_slider_moved(idx)
        interval_ms = int(self.interval_spinbox.value() * 1000)
        self._play_timer.start(interval_ms)

    def select_folder(self) -> None:
        """Open a file dialog to select a folder containing data files."""
        self.load_controller.select_folder()
