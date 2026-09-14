"""Expected values for BaseLoadState, shared by the tests that rely on it.

The table is written by hand on purpose: it is what the code is checked
against, so it must never be derived from the code under test. The three
views below are derived from the table itself, which is only bookkeeping.
"""

# Marks a field with no default: the loading classes fill it in, so reading it
# on a fresh state raises AttributeError.
UNSET = object()

# What every BaseLoadState field holds on a fresh state.
DEFAULTS: dict[str, object] = {
    "alone": UNSET,
    "charsize": UNSET,
    "class_name": UNSET,
    "chnk": None,
    "code": "gPLUTO",
    "d_info": {},
    "d_vars": {},
    "datatype": "Unknown",
    "dim": UNSET,
    "endian": None,
    "filepath": UNSET,
    "infogrid": True,
    "lennout": UNSET,
    "lennoutlist": UNSET,
    "matching_files": None,
    "mmaps": [],
    "multiple": False,
    "nout": UNSET,
    "noutlist": UNSET,
    "nshp": UNSET,
    "ntime": UNSET,
    "ntimelist": UNSET,
    "outlist": UNSET,
    "pathdir": "./",
    "text": None,
    "timelist": UNSET,
    "unit_attached": set(),
    "unit_base": {},
    "unit_userdef": {},
    "units": {},
    "varoffset": {},
    "varshape": {},
}

# The fields with a real default, and the ones only a load fills in
WITH_DEFAULT = {name: v for name, v in DEFAULTS.items() if v is not UNSET}
WITHOUT_DEFAULT = [name for name, v in DEFAULTS.items() if v is UNSET]

# The fields built by a default_factory: each state must get its own object
CONTAINERS = [
    name for name, v in WITH_DEFAULT.items() if isinstance(v, (dict, list, set))
]
