from PyQt6.QtWidgets import QCheckBox, QComboBox, QFrame, QLabel, QLineEdit, QPushButton


def add_line(self, control_layout):

    line = QFrame()
    line.setFrameShape(QFrame.Shape.HLine)
    line.setFrameShadow(QFrame.Shadow.Sunken)
    control_layout.addWidget(line)


def add_combobox(self, label, control_layout, data, width=None, height=None):

    combo_box = QComboBox()
    setattr(self, label, combo_box)
    combo_box.addItems(data)
    if isinstance(width, int):
        combo_box.setFixedWidth(width)
    control_layout.addWidget(combo_box)


def add_label(self, label, control_layout, data=None, width=None, height=None):

    labelgui = QLabel(label)
    if isinstance(width, int):
        labelgui.setFixedWidth(width)
    if isinstance(height, int):
        labelgui.setFixedHeight(height)
    if data is not None:
        setattr(self, data, labelgui)
    control_layout.addWidget(labelgui)


def add_lineedit(self, label, control_layout, data=None, width=None, height=None):

    lineedit = QLineEdit()
    setattr(self, label, lineedit)
    lineedit.setPlaceholderText(data)
    if isinstance(width, int):
        lineedit.setFixedWidth(width)
    control_layout.addWidget(lineedit)


def add_checkbox(self, label, control_layout, data=None, width=None, height=None):

    checkbox = QCheckBox(label)
    if data is not None:
        setattr(self, data, checkbox)
    control_layout.addWidget(checkbox)


def add_pushbutton(self, label, control_layout, data=None, width=None):

    pushbutton = QPushButton(label)
    setattr(self, label, pushbutton)
    if isinstance(width, int):
        pushbutton.setFixedWidth(width)
    pushbutton.clicked.connect(data)
    control_layout.addWidget(pushbutton)
