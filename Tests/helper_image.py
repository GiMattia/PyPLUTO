"""Expected values for ImageState, ImageMixin and Image, shared by their tests.

The table is written by hand on purpose: it is what the code is checked
against, so it must never be derived from the code under test. The three
views below are derived from the table itself, which is only bookkeeping.

This module carries more than the load helpers do, because Image is the
largest facade in the package: the field table, the sixteen managers and the
method each is reached through, and the kwargs table each method is
annotated with.

Everything except the three derived views is hand-written, so the tests have
something independent to compare the code against.
"""

# Marks a field with no default: the code fills it in later, so reading it on
# a fresh state raises AttributeError. ImageState has none today; the marker is
# kept so this table has the same shape as the other state tables.
#
# Every state helper is written the same way even where a part is empty, so
# the state and mixin test files can be read side by side and none of them is
# held to a lower standard than the others.
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

# The fields with a real default, and the ones filled in later. WITHOUT_DEFAULT
# is empty for ImageState, which test_imagestate.py asserts rather than skips:
# an empty parametrize set becomes a silent skip, so it is stated outright.
WITH_DEFAULT = {name: v for name, v in DEFAULTS.items() if v is not UNSET}
WITHOUT_DEFAULT = [name for name, v in DEFAULTS.items() if v is UNSET]

# The fields built by a default_factory: each state must get its own object,
# or two images would share one list and draw into each other's axes.
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

# oplotbox is not a facade: it calls the AMR module function instead, so it is
# listed here to be excluded rather than left out, which would make the
# completeness guard unable to tell it from a method someone forgot.
NOT_DELEGATED = {"oplotbox"}

# Every manager that Image.__init__ builds on the shared state.
#
# Longer than DELEGATION by two: FigureManager and RangeManager are built and
# used internally but reached through no public method of their own.
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

# The facade methods that take explicit parameters only, with no **kwargs.
# Listed rather than left out, so every facade method is accounted for by one
# table or the other.
NO_KWARGS = {"animate", "savefig"}

# The tables that no facade method unpacks, and where they are unpacked
# instead: the constructor, and a manager method Image never exposes. Written
# as "module:Class.method" so the test can resolve and check each one.
OTHER_KWARGS: dict[str, str] = {
    "FigureKwargs": "pyPLUTO.image:Image.__init__",
    "SetLocKwargs": "pyPLUTO.imagefuncs.zoom:ZoomManager.place_inset_loc",
}
