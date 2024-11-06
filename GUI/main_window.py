import pyPLUTO as pp
from PyQt6.QtWidgets import (
    QMainWindow, QWidget, QVBoxLayout, QLabel, QPushButton,
    QComboBox, QSplitter, QFrame, QHBoxLayout, QLineEdit, QCheckBox
)
from PyQt6.QtCore import Qt
from matplotlib.backends.backend_qtagg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.backends.backend_qtagg import NavigationToolbar2QT as NavigationToolbar
from matplotlib.figure import Figure
from matplotlib import colormaps
import matplotlib.scale as mscale

scales = list(mscale.get_scale_names())
scales = [scales[3]] + [scales[0]] + scales[4:]

cmaps = [('Perceptually Uniform Sequential', [
            'viridis', 'plasma', 'inferno', 'magma', 'cividis']),
         ('Sequential', [
            'Greys', 'Purples', 'Blues', 'Greens', 'Oranges', 'Reds',
            'YlOrBr', 'YlOrRd', 'OrRd', 'PuRd', 'RdPu', 'BuPu',
            'GnBu', 'PuBu', 'YlGnBu', 'PuBuGn', 'BuGn', 'YlGn']),
         ('Sequential (2)', [
            'binary', 'gist_yarg', 'gist_gray', 'gray', 'bone', 'pink',
            'spring', 'summer', 'autumn', 'winter', 'cool', 'Wistia',
            'hot', 'afmhot', 'gist_heat', 'copper']),
         ('Diverging', [
            'PiYG', 'PRGn', 'BrBG', 'PuOr', 'RdGy', 'RdBu',
            'RdYlBu', 'RdYlGn', 'Spectral', 'coolwarm', 'bwr', 'seismic']),
         ('Cyclic', ['twilight', 'twilight_shifted', 'hsv']),
         ('Qualitative', [
            'Pastel1', 'Pastel2', 'Paired', 'Accent',
            'Dark2', 'Set1', 'Set2', 'Set3',
            'tab10', 'tab20', 'tab20b', 'tab20c']),
         ('Miscellaneous', [
            'flag', 'prism', 'ocean', 'gist_earth', 'terrain', 'gist_stern',
            'gnuplot', 'gnuplot2', 'CMRmap', 'cubehelix', 'brg',
            'gist_rainbow', 'rainbow', 'jet', 'turbo', 'nipy_spectral',
            'gist_ncar'])]

class PlotWindow(QWidget):
    def __init__(self, fig, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.canvas = FigureCanvas(fig)
        self.toolbar = NavigationToolbar(self.canvas, self)  # Add the toolbar

        layout = QVBoxLayout()
        layout.addWidget(self.toolbar)  # Add the toolbar at the top
        layout.addWidget(self.canvas)
        self.setLayout(layout)
class PyPLUTOApp(QMainWindow):

    def __init__(self, code):
        super().__init__()
        self.code = code
        codestr = f" ({self.code})" if code != "PLUTO" else ""
        self.setWindowTitle(f"PyPLUTO GUI{codestr}")
        self.folder_path = None
        self.data_loaded = False
        self.datatype    = None

        # Create main layout with a splitter
        main_splitter = QSplitter(Qt.Orientation.Horizontal)

        # Left Panel for controls
        control_widget = QWidget()
        control_layout = QVBoxLayout(control_widget)

        # Add Loading Controls (Format selection)
        layout = QHBoxLayout()
        self.add_combobox("datatype_selector", layout, ["fluid", "particles"])
        self.add_label("Preferred format:", layout)
        self.add_combobox("format_selector", layout, ["None",   "dbl",    "flt",  "vtk", 
                                                 "dbl.h5", "flt.h5", "hdf5", "tab"])
        control_layout.addLayout(layout)

        layout = QHBoxLayout()
        self.add_label("nout:", layout)
        self.add_lineedit("outtext", layout, "nout")
        self.add_label("vars:", layout)
        self.add_lineedit("varstext", layout, "vars")
        control_layout.addLayout(layout)

        layout = QHBoxLayout()
        self.add_checkbox("Avoid 3D", layout, "threed_checkbox")
        self.add_label("amr_label", layout)
        self.add_lineedit("amr_selector", layout, "AMR level")
        self.add_label("nlp_label", layout)
        self.add_lineedit("nlp_selector", layout, "LP chunk")
        control_layout.addLayout(layout)

        layout = QHBoxLayout()
        self.add_pushbutton("Select Folder", layout, self.select_folder)
        self.add_pushbutton("Clear", layout, self.clearload, 100)
        self.add_pushbutton("Reload Data", layout, self.reload_data)
        control_layout.addLayout(layout)

        self.add_line(control_layout)

        # Add Plotting Controls (Variable selection)
        var_layout = QHBoxLayout()
        self.var_label = QLabel("Select the variable to plot:")
        var_layout.addWidget(self.var_label)

        self.var_selector = QComboBox()
        var_layout.addWidget(self.var_selector)

        # Scatter checkbox
        self.transpose_checkbox = QCheckBox("Transpose")
        var_layout.addWidget(self.transpose_checkbox)

        # Add the variable selection layout to the control layout
        control_layout.addLayout(var_layout)

        xyaxis_layout = QHBoxLayout()
        self.xaxis_label = QLabel("Select the x-axis:")
        xyaxis_layout.addWidget(self.xaxis_label)

        self.xaxis_selector = QComboBox()
        xyaxis_layout.addWidget(self.xaxis_selector)

    
        self.yaxis_label = QLabel("y-axis (display):")
        xyaxis_layout.addWidget(self.yaxis_label)

        self.yaxis_selector = QComboBox()
        xyaxis_layout.addWidget(self.yaxis_selector)

        # Add the variable selection layout to the control layout
        control_layout.addLayout(xyaxis_layout)

        layout = QHBoxLayout()
        self.add_label("x-slice:", layout)
        self.add_lineedit("xslicetext", layout, "x-slice")
        self.add_label("y-slice:", layout)
        self.add_lineedit("yslicetext", layout, "y-slice")
        self.add_label("z-slice:", layout)
        self.add_lineedit("zslicetext", layout, "z-slice")
        control_layout.addLayout(layout)

        self.add_line(control_layout)

        layout = QHBoxLayout()
        self.title_label = QLabel("Title:")
        layout.addWidget(self.title_label)

        self.title_label = QLineEdit()
        self.title_label.setPlaceholderText("title")
        layout.addWidget(self.title_label)
        control_layout.addLayout(layout)

        # Add xrange input fields and label
        range_layout = QHBoxLayout()
        self.xrange_label = QLabel("xrange:")
        range_layout.addWidget(self.xrange_label)

        self.xrange_min = QLineEdit()
        self.xrange_min.setPlaceholderText("xmin")
        range_layout.addWidget(self.xrange_min)

        self.xrange_max = QLineEdit()
        self.xrange_max.setPlaceholderText("xmax")
        range_layout.addWidget(self.xrange_max)

        # Add labels input fields and label
        self.xlabel_label = QLabel("xtitle:   ")
        range_layout.addWidget(self.xlabel_label)

        self.xlabel_label = QLineEdit()
        self.xlabel_label.setPlaceholderText("xtitle")
        self.xlabel_label.setMinimumWidth(137)
        range_layout.addWidget(self.xlabel_label)

        control_layout.addLayout(range_layout)

        # Add yrange input fields and label
        label_layout = QHBoxLayout()
        self.yrange_label = QLabel("yrange:")
        label_layout.addWidget(self.yrange_label)

        self.yrange_min = QLineEdit()
        self.yrange_min.setPlaceholderText("ymin")
        label_layout.addWidget(self.yrange_min)

        self.yrange_max = QLineEdit()
        self.yrange_max.setPlaceholderText("ymax")
        label_layout.addWidget(self.yrange_max)

        self.ylabel_label = QLabel("ytitle:   ")
        label_layout.addWidget(self.ylabel_label)

        self.ylabel_label = QLineEdit()
        self.ylabel_label.setPlaceholderText("ytitle")
        self.ylabel_label.setMinimumWidth(137)
        label_layout.addWidget(self.ylabel_label)

        control_layout.addLayout(label_layout)

        # Add vrange input fields and label
        vrange_layout = QHBoxLayout()

        vrange_label = QLabel("vrange:")
        vrange_layout.addWidget(vrange_label)

        self.vrange_min = QLineEdit()
        self.vrange_min.setPlaceholderText("vmin")
        vrange_layout.addWidget(self.vrange_min)

        self.vrange_max = QLineEdit()
        self.vrange_max.setPlaceholderText("vmax")
        vrange_layout.addWidget(self.vrange_max)

        self.clabel_label = QLabel("ctitle:   ")
        vrange_layout.addWidget(self.clabel_label)

        self.clabel_label = QLineEdit()
        self.clabel_label.setPlaceholderText("vtitle")
        self.clabel_label.setMinimumWidth(137)
        vrange_layout.addWidget(self.clabel_label)

        control_layout.addLayout(vrange_layout)

        layout = QHBoxLayout()

        self.add_label("lstyle:", layout)
        self.add_lineedit("lstyle_selector", layout, "lstyle")
        self.add_label("lwidth:", layout)
        self.add_lineedit("lwidth_selector", layout, "lwidth")
        self.add_label("lcolor:", layout)
        self.add_lineedit("lcolor_selector", layout, "lcolor")

        control_layout.addLayout(layout)

        layout = QHBoxLayout()
        self.add_label("marker:", layout)
        self.add_lineedit("marker_selector", layout, "marker")
        self.add_label("msize:", layout)
        self.add_lineedit("msize_selector", layout, "msize")
        self.add_label("mfill:", layout)
        self.add_lineedit("mfill_selector", layout, "mfill")

        control_layout.addLayout(layout)


        cmap_layout = QHBoxLayout()
        self.cmap_label = QLabel("Cmap:")
        cmap_layout.addWidget(self.cmap_label)

        self.typecmap_selector = QComboBox()
        cmaps = ['All','Uniform','Diverging','Qualitative','Miscellaneous']
        self.typecmap_selector.addItems(cmaps)
        cmap_layout.addWidget(self.typecmap_selector)

        self.cmap_selector = QComboBox()
        self.cmaps_avail = [list(colormaps)[2]] + list(colormaps)[0:2] + list(colormaps)[3:]
        self.cmap_selector.addItems(self.cmaps_avail)
        cmap_layout.addWidget(self.cmap_selector)

        self.cmapreverse_checkbox = QCheckBox("Reversed")
        cmap_layout.addWidget(self.cmapreverse_checkbox)

        control_layout.addLayout(cmap_layout)

        xyscale_layout = QHBoxLayout()

        self.xscale_label = QLabel("x-scale:")
        xyscale_layout.addWidget(self.xscale_label)

        self.xscale_selector = QComboBox()
        self.xscale_selector.addItems(scales)
        xyscale_layout.addWidget(self.xscale_selector)

        self.xscale_tresh = QLineEdit()
        self.xscale_tresh.setPlaceholderText("x-tresh")
        xyscale_layout.addWidget(self.xscale_tresh)

        self.yscale_label = QLabel("y-scale:")
        xyscale_layout.addWidget(self.yscale_label)

        self.yscale_selector = QComboBox()
        self.yscale_selector.addItems(scales)
        xyscale_layout.addWidget(self.yscale_selector)

        self.yscale_tresh = QLineEdit()
        self.yscale_tresh.setPlaceholderText("y-tresh")
        xyscale_layout.addWidget(self.yscale_tresh)

        control_layout.addLayout(xyscale_layout)

        vscale_layout = QHBoxLayout()

        self.varscale_label = QLabel("v-scale:")
        vscale_layout.addWidget(self.varscale_label)

        self.varscale_selector = QComboBox()
        self.varscale_selector.addItems(scales)
        vscale_layout.addWidget(self.varscale_selector)

        self.varscale_tresh = QLineEdit()
        self.varscale_tresh.setPlaceholderText("v-tresh")
        vscale_layout.addWidget(self.varscale_tresh)

        # Scatter checkbox
        self.shade_label = QLabel("Shading")
        vscale_layout.addWidget(self.shade_label)

        self.shade_selector = QComboBox()
        self.shade_selector.addItems(['auto','flat','nearest','gouraud'])
        vscale_layout.addWidget(self.shade_selector)


        control_layout.addLayout(vscale_layout)

        self.add_line(control_layout)
        self.add_line(control_layout)

        # Horizontal layout for Plot button and Overplot checkbox, centered in the middle of the two columns
        button_layout_1 = QHBoxLayout()

        # Plot button
        self.plot_button = QPushButton("Plot")
        self.plot_button.setMinimumWidth(185)
        self.plot_button.clicked.connect(self.plot_selected_variable)
        button_layout_1.addWidget(self.plot_button)

        # Overplot checkbox
        self.overplot_checkbox = QCheckBox("Overplot")
        button_layout_1.addWidget(self.overplot_checkbox)

        # Scatter checkbox
        self.scatter_checkbox = QCheckBox("Scatter")
        button_layout_1.addWidget(self.scatter_checkbox)

        # Add the button layout to the main control layout
        control_layout.addLayout(button_layout_1)

        # Horizontal layout for Clear and Save buttons
        button_layout_2 = QHBoxLayout()
        self.updateaxis_button = QPushButton("Update axes")
        self.updateaxis_button.setMinimumWidth(100)
        self.updateaxis_button.clicked.connect(self.update_axes)
        button_layout_2.addWidget(self.updateaxis_button)

        self.clearlabels_button = QPushButton("Clear")
        self.clearlabels_button.setMinimumWidth(100)
        self.clearlabels_button.clicked.connect(self.clear_labels)
        button_layout_2.addWidget(self.clearlabels_button)

        self.save_button = QPushButton("Save")
        self.save_button.setMinimumWidth(100)
        self.save_button.clicked.connect(self.save_figure)
        button_layout_2.addWidget(self.save_button)

        control_layout.addLayout(button_layout_2)

        # Add line separator between buttons and information
        self.add_line(control_layout)

        # Add Information display
       # self.info_label = QLabel("Information:")
       # control_layout.addWidget(self.info_label)
      #  self.info_label.setWordWrap(True)
      #  self.info_label.setFixedWidth(370)

        # Add Left Panel to splitter
        main_splitter.addWidget(control_widget)

        # Right Panel for Plot Display
        self.plot_window = PlotWindow(Figure())
        main_splitter.addWidget(self.plot_window)

        # Set splitter orientation to horizontal
        main_splitter.setOrientation(Qt.Orientation.Horizontal)

        # Adjust the stretch factors for a 1:2 ratio (left panel half of the right panel)
        main_splitter.setStretchFactor(0, 1)
        main_splitter.setStretchFactor(1, 2)

        # Set minimum sizes for panels
        control_widget.setMinimumWidth(400)
        self.plot_window.setMinimumWidth(765)

        # Set main splitter as the central widget
        self.setCentralWidget(main_splitter)

        # Initialize plotting object
        self.I = pp.Image(figsize=[7.5, 6.3])

    from config import select_folder, clearload, reload_data, load_data
    from utils  import plot_selected_variable, update_axes, clear_labels, check_axisparam, save_figure


    # Create a line separator and add it to the control layout
    def add_line(self, control_layout):

        line = QFrame()
        line.setFrameShape(QFrame.Shape.HLine)
        line.setFrameShadow(QFrame.Shadow.Sunken)
        control_layout.addWidget(line)

    # Create a QComboBox and set it as an attribute of the instance
    def add_combobox(self, label, control_layout, data, width = None):

        combo_box = QComboBox()
        setattr(self, label, combo_box)
        combo_box.addItems(data)
        if isinstance(width, int):
            combo_box.setMinimumWidth(width)
        control_layout.addWidget(combo_box)

    def add_label(self, label, control_layout, data = None, width = None):

        labelgui = QLabel(label)
        if isinstance(width, int):
            labelgui.setMinimumWidth(width)
        control_layout.addWidget(labelgui)

    def add_lineedit(self, label, control_layout, data = None, width = None):

        lineedit = QLineEdit()
        setattr(self, label, lineedit)
        lineedit.setPlaceholderText(data)
        if isinstance(width, int):
            lineedit.setMinimumWidth(width)
        control_layout.addWidget(lineedit)

    def add_checkbox(self, label, control_layout, data = None, width = None):

        checkbox = QCheckBox(label)
        setattr(self, data, checkbox)
        control_layout.addWidget(checkbox)

    def add_pushbutton(self, label, control_layout, data = None, width = None):

        pushbutton = QPushButton(label)
        setattr(self, label, pushbutton)
        if isinstance(width, int):
            pushbutton.setMinimumWidth(width)
        pushbutton.clicked.connect(data)
        control_layout.addWidget(pushbutton)
