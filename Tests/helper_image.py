"""Expected values and stand-ins for ImageState, shared by its tests.

The table is written by hand on purpose: it is what the code is checked
against, so it must never be derived from the code under test. The three
views below are derived from the table itself, which is only bookkeeping.
"""

# Marks a field with no default: the code fills it in later, so reading it on
# a fresh state raises AttributeError. ImageState has none today; the marker is
# kept so this table has the same shape as the other state tables.
UNSET = object()

# What every ImageState field holds on a fresh state.
DEFAULTS: dict[str, object] = {
    "ax": [],
    "color": [],
    "dictcol": {},
    "fig": None,
    "figsize": [8.0, 5.0],
    "fontsize": 17,
    "fontweight": "normal",
    "LaTeX": True,
    "legpar": [],
    "legpos": [],
    "ncol0": 0,
    "nline": [],
    "nrow0": 0,
    "ntext": [],
    "nwin": 1,
    "setax": [],
    "setay": [],
    "set_size": False,
    "shade": [],
    "style": "default",
    "tickspar": [],
    "tight": True,
    "vlims": [],
    "volumes": [],
    "xscale": [],
    "yscale": [],
}

# The fields with a real default, and the ones filled in later
WITH_DEFAULT = {name: v for name, v in DEFAULTS.items() if v is not UNSET}
WITHOUT_DEFAULT = [name for name, v in DEFAULTS.items() if v is UNSET]

# The fields built by a default_factory: each state must get its own object
CONTAINERS = [
    name for name, v in WITH_DEFAULT.items() if isinstance(v, (dict, list, set))
]


# Every facade method of Image and the manager it hands the call to. Checked
# by test_delegation and test_docstring_is_copied, while
# test_every_method_is_listed makes sure no public method is missing.
DELEGATION: dict[str, str] = {
    "animate": "InteractiveManager",
    "colorbar": "ColorbarManager",
    "contour": "ContourManager",
    "create_axes": "CreateAxesManager",
    "display": "DisplayManager",
    "interactive": "InteractiveManager",
    "legend": "LegendManager",
    "plot": "PlotManager",
    "savefig": "ImageToolsManager",
    "scatter": "ScatterManager",
    "set_axis": "AxisManager",
    "showgrid": "GridPlotManager",
    "streamplot": "StreamplotManager",
    "text": "ImageToolsManager",
    "volume": "VolumeManager",
    "zoom": "ZoomManager",
}

# oplotbox is not a facade: it calls the AMR module function instead
NOT_DELEGATED = {"oplotbox"}

# Every manager that Image.__init__ builds on the shared state
MANAGERS: list[str] = [
    "AxisManager",
    "ColorbarManager",
    "ContourManager",
    "CreateAxesManager",
    "DisplayManager",
    "FigureManager",
    "GridPlotManager",
    "ImageToolsManager",
    "InteractiveManager",
    "LegendManager",
    "PlotManager",
    "RangeManager",
    "ScatterManager",
    "StreamplotManager",
    "VolumeManager",
    "ZoomManager",
]


# The TypedDict that annotates the **kwargs of each Image facade method, from
# imagekwargs.py. Checked by test_method_kwargs_typeddict, while
# test_every_method_is_listed makes sure no method is missing.
KWARGS: dict[str, str] = {
    "colorbar": "ColorbarKwargs",
    "contour": "ContourKwargs",
    "create_axes": "CreateAxesKwargs",
    "display": "DisplayKwargs",
    "interactive": "DisplayKwargs",
    "legend": "LegendKwargs",
    "plot": "PlotKwargs",
    "scatter": "ScatterKwargs",
    "set_axis": "SetAxisKwargs",
    "showgrid": "ShowGridKwargs",
    "streamplot": "StreamplotKwargs",
    "text": "TextKwargs",
    "volume": "VolumeKwargs",
    "zoom": "ZoomKwargs",
}

# The facade methods that take explicit parameters only, with no **kwargs
NO_KWARGS = {"animate", "savefig"}

# The tables that no facade method unpacks, and where they are unpacked
# instead: the constructor, and a manager method Image never exposes. Written
# as "module:Class.method" so the test can resolve and check each one.
OTHER_KWARGS: dict[str, str] = {
    "FigureKwargs": "pyPLUTO.image:Image.__init__",
    "SetLocKwargs": "pyPLUTO.imagefuncs.zoom:ZoomManager.place_inset_loc",
}


class DummyState:
    """The few ImageState fields that Image and ImageMixin read in the tests."""

    def __init__(self) -> None:
        self.ax = []
        self.LaTeX = False
        self.style = "old"
        self.legpar = []
        self.legpos = "right"
        self.nline = 3
        self.nwin = 9
        self.ncol0 = 1
        self.ntext = 0
        self.nrow0 = 1
        self.tight = True
        self.vlims = (0, 1)
        self.xscale = "linear"
        self.yscale = "linear"
        self.setax = []
        self.setay = []
        self.shade = []
        self.tickspar = []
