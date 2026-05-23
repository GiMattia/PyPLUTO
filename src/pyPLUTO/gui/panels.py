"""Widget-construction mixin for the main GUI window."""

from PySide6.QtWidgets import (
    QCheckBox,
    QComboBox,
    QFrame,
    QLabel,
    QLineEdit,
    QPushButton,
)


class PanelsMixin:
    """Small helpers to build repetitive Qt widgets."""

    def add_line(self, control_layout):
        line = QFrame()
        line.setFrameShape(QFrame.Shape.HLine)
        line.setFrameShadow(QFrame.Shadow.Sunken)
        control_layout.addWidget(line)

    def add_combobox(self, control_layout, data, width=None, height=None):
        _ = height
        combo_box = QComboBox()
        combo_box.addItems(data)
        if isinstance(width, int):
            combo_box.setFixedWidth(width)
        control_layout.addWidget(combo_box)
        return combo_box

    def add_label(self, label, control_layout, width=None, height=None):
        labelgui = QLabel(label)
        if isinstance(width, int):
            labelgui.setFixedWidth(width)
        if isinstance(height, int):
            labelgui.setFixedHeight(height)
        control_layout.addWidget(labelgui)
        return labelgui

    def add_lineedit(self, control_layout, data=None, width=None, height=None):
        _ = height
        lineedit = QLineEdit()
        lineedit.setPlaceholderText(data if isinstance(data, str) else "")
        if isinstance(width, int):
            lineedit.setFixedWidth(width)
        control_layout.addWidget(lineedit)
        return lineedit

    def add_checkbox(self, label, control_layout, width=None, height=None):
        _ = (width, height)
        checkbox = QCheckBox(label)
        control_layout.addWidget(checkbox)
        return checkbox

    def add_pushbutton(self, label, control_layout, callback=None, width=None):
        pushbutton = QPushButton(label)
        if isinstance(width, int):
            pushbutton.setFixedWidth(width)
        if callback is not None:
            pushbutton.clicked.connect(callback)  # type: ignore[arg-type]
        control_layout.addWidget(pushbutton)
        return pushbutton
