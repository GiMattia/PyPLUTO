"""Expected values for LoadState, shared by the tests that rely on it.

LoadState extends BaseLoadState, so its table is the base table from
helper_baseload.py plus the fields LoadState adds. Both parts are written by
hand on purpose: they are what the code is checked against, so they must never
be derived from the code under test. The three views below are derived from
the table itself, which is only bookkeeping.
"""

from helper_baseload import DEFAULTS as BASELOAD_DEFAULTS
from helper_baseload import UNSET

# What every field LoadState adds holds on a fresh state. Only full3D and
# level have a default: the grid fields are filled in while loading.
OWN_DEFAULTS: dict[str, object] = {
    "defh": UNSET,
    "dx1": UNSET,
    "dx2": UNSET,
    "dx3": UNSET,
    "full3D": False,
    "geom": UNSET,
    "gridsize": UNSET,
    "gridsize_st1": UNSET,
    "gridsize_st2": UNSET,
    "gridsize_st3": UNSET,
    "level": 0,
    "nshp_st1": UNSET,
    "nshp_st2": UNSET,
    "nshp_st3": UNSET,
    "nx1": UNSET,
    "nx2": UNSET,
    "nx3": UNSET,
    "plini": UNSET,
    "x1": UNSET,
    "x1c": UNSET,
    "x1p": UNSET,
    "x1r": UNSET,
    "x1rc": UNSET,
    "x1rp": UNSET,
    "x1rt": UNSET,
    "x1t": UNSET,
    "x2": UNSET,
    "x2c": UNSET,
    "x2p": UNSET,
    "x2r": UNSET,
    "x2rc": UNSET,
    "x2rp": UNSET,
    "x3": UNSET,
    "x3c": UNSET,
    "x3r": UNSET,
    "x3rc": UNSET,
    "x3rt": UNSET,
    "x3t": UNSET,
}

# What every LoadState field holds on a fresh state: the inherited fields plus
# the ones above.
DEFAULTS: dict[str, object] = {**BASELOAD_DEFAULTS, **OWN_DEFAULTS}

# The fields with a real default, and the ones only a load fills in
WITH_DEFAULT = {name: v for name, v in DEFAULTS.items() if v is not UNSET}
WITHOUT_DEFAULT = [name for name, v in DEFAULTS.items() if v is UNSET]

# The fields built by a default_factory: each state must get its own object
CONTAINERS = [
    name for name, v in WITH_DEFAULT.items() if isinstance(v, (dict, list, set))
]

# Every public method of Load and the manager it hands the call to. Checked by
# test_delegation and test_docstring_is_copied, while
# test_every_method_is_listed makes sure no public method is missing.
DELEGATION: dict[str, str] = {
    "cartesian_vector": "TransformManager",
    "curl": "NablaManager",
    "divergence": "NablaManager",
    "find_contour": "FindLinesManager",
    "find_fieldlines": "FindLinesManager",
    "fourier": "FourierManager",
    "gradient": "NablaManager",
    "mirror": "TransformManager",
    "read_file": "ReadFileManager",
    "repeat": "TransformManager",
    "reshape_cartesian": "TransformManager",
    "reshape_uniform": "TransformManager",
    "slices": "TransformManager",
    "to_astropy_units": "SetUnitsManager",
    "to_code_units": "SetUnitsManager",
    "write_file": "WriteFileManager",
}

# Every method of Load that takes **kwargs, and the TypedDict of loadkwargs.py
# that declares them. __init__ is listed too: the constructor is where most of
# the keywords are actually given.
KWARGS: dict[str, str] = {
    "__init__": "LoadKwargs",
    "cartesian_vector": "CartesianVectorKwargs",
    "find_contour": "FindContourKwargs",
    "find_fieldlines": "FindFieldlinesKwargs",
    "fourier": "FourierKwargs",
    "read_file": "ReadFileKwargs",
    "reshape_cartesian": "ReshapeKwargs",
    "reshape_uniform": "ReshapeKwargs",
    "slices": "SlicesKwargs",
    "write_file": "WriteFileKwargs",
}

# The methods that take explicit parameters only, with no **kwargs at all.
NO_KWARGS: set[str] = {
    "curl",
    "divergence",
    "gradient",
    "mirror",
    "repeat",
    "to_astropy_units",
    "to_code_units",
}

# Every manager that a Load builds on its state. UnitManager is the one no
# public method delegates to: the units are computed while loading.
MANAGERS: list[str] = [
    "FindLinesManager",
    "FourierManager",
    "NablaManager",
    "ReadFileManager",
    "SetUnitsManager",
    "TransformManager",
    "UnitManager",
    "WriteFileManager",
]
