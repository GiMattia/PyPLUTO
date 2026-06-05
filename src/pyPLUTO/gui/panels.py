"""Widget-construction mixin for the main GUI window."""

from __future__ import annotations

from collections.abc import Callable

from PySide6.QtWidgets import (
    QCheckBox,
    QComboBox,
    QFrame,
    QLabel,
    QLayout,
    QLineEdit,
    QPushButton,
)


class PanelsMixin:
    """Small helpers to build repetitive Qt widgets."""

    def add_line(self, control_layout: QLayout) -> None:
        """Add a horizontal sunken separator line to a layout.

        Parameters
        ----------
        - control_layout: QLayout
            The Qt layout that will receive the separator widget.

        Returns
        -------
        - None

        """
        line = QFrame()
        line.setFrameShape(QFrame.Shape.HLine)
        line.setFrameShadow(QFrame.Shadow.Sunken)
        control_layout.addWidget(line)

    def add_combobox(
        self,
        control_layout: QLayout,
        data: list[str],
        width: int | None = None,
        height: int | None = None,
    ) -> QComboBox:
        """Create a combo box pre-populated with items and add it to a layout.

        Parameters
        ----------
        - control_layout: QLayout
            The Qt layout that will receive the combo box.
        - data: list[str]
            Sequence of item strings to populate the combo box.
        - width: int or None, default None
            Fixed pixel width; ignored when not an integer.
        - height: int or None, default None
            Reserved for future use; currently ignored.

        Returns
        -------
        - QComboBox

        """
        _ = height
        combo_box = QComboBox()
        combo_box.addItems(data)
        if isinstance(width, int):
            combo_box.setFixedWidth(width)
        control_layout.addWidget(combo_box)
        return combo_box

    def add_label(
        self,
        label: str,
        control_layout: QLayout,
        width: int | None = None,
        height: int | None = None,
    ) -> QLabel:
        """Create a text label and add it to a layout.

        Parameters
        ----------
        - label: str
            Display text for the label.
        - control_layout: QLayout
            The Qt layout that will receive the label.
        - width: int or None, default None
            Fixed pixel width; ignored when not an integer.
        - height: int or None, default None
            Fixed pixel height; ignored when not an integer.

        Returns
        -------
        - QLabel

        """
        labelgui = QLabel(label)
        if isinstance(width, int):
            labelgui.setFixedWidth(width)
        if isinstance(height, int):
            labelgui.setFixedHeight(height)
        control_layout.addWidget(labelgui)
        return labelgui

    def add_lineedit(
        self,
        control_layout: QLayout,
        data: str | None = None,
        width: int | None = None,
        height: int | None = None,
    ) -> QLineEdit:
        """Create a single-line text input and add it to a layout.

        Parameters
        ----------
        - control_layout: QLayout
            The Qt layout that will receive the line edit.
        - data: str or None, default None
            Placeholder text shown when the field is empty.
        - width: int or None, default None
            Fixed pixel width; ignored when not an integer.
        - height: int or None, default None
            Reserved for future use; currently ignored.

        Returns
        -------
        - QLineEdit

        """
        _ = height
        lineedit = QLineEdit()
        lineedit.setPlaceholderText(data if isinstance(data, str) else "")
        if isinstance(width, int):
            lineedit.setFixedWidth(width)
        control_layout.addWidget(lineedit)
        return lineedit

    def add_checkbox(
        self,
        label: str,
        control_layout: QLayout,
        width: int | None = None,
        height: int | None = None,
    ) -> QCheckBox:
        """Create a check box and add it to a layout.

        Parameters
        ----------
        - label: str
            Text displayed next to the check box.
        - control_layout: QLayout
            The Qt layout that will receive the check box.
        - width: int or None, default None
            Reserved for future use; currently ignored.
        - height: int or None, default None
            Reserved for future use; currently ignored.

        Returns
        -------
        - QCheckBox

        """
        _ = (width, height)
        checkbox = QCheckBox(label)
        control_layout.addWidget(checkbox)
        return checkbox

    def add_pushbutton(
        self,
        label: str,
        control_layout: QLayout,
        callback: Callable[[], None] | None = None,
        width: int | None = None,
    ) -> QPushButton:
        """Create a push button and add it to a layout.

        Optionally, wire a click handler.

        Parameters
        ----------
        - label: str
            Text displayed on the button face.
        - control_layout: QLayout
            The Qt layout that will receive the button.
        - callback: Callable[[], None] or None, default None
            Slot connected to the ``clicked`` signal; skipped when ``None``.
        - width: int or None, default None
            Fixed pixel width; ignored when not an integer.

        Returns
        -------
        - QPushButton

        """
        pushbutton = QPushButton(label)
        if isinstance(width, int):
            pushbutton.setFixedWidth(width)
        if callback is not None:
            pushbutton.clicked.connect(callback)  # type: ignore[arg-type]
        control_layout.addWidget(pushbutton)
        return pushbutton
