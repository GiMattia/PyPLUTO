"""Expected values for BaseLoadState, shared by the tests that rely on it.

The table is written by hand on purpose: it is what the code is checked
against, so it must never be derived from the code under test. The three
views below are derived from the table itself, which is only bookkeeping.

That distinction is the whole idea of these helper modules, and it is worth
being clear about. A test that read the defaults off BaseLoadState and then
checked a state against them would pass whatever the defaults happened to be,
including a wrong one; it would only be comparing the code with itself. The
table below is a second, independent statement of what the defaults should
be, so the two can disagree -- which is exactly when a test should fail.

The cost is real: adding a field to BaseLoadState means adding a line here
too, and the completeness guards in test_baseloadstate.py fail until it is
done. That is deliberate. It is what stops a new field from slipping in with
nothing checking it.

BaseLoadState holds what Load and LoadPart have in common; LoadState adds the
grid on top of it, and helper_load.py extends this table rather than
repeating it.
"""

# Marks a field with no default: the loading classes fill it in, so reading it
# on a fresh state raises AttributeError.
#
# A plain object() is used rather than None or a string because it can never
# be mistaken for a real default: it compares equal to nothing but itself, so
# `v is UNSET` cannot accidentally match a field whose real value is None.
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

# The fields with a real default, and the ones only a load fills in.
# Splitting the table this way lets the two be tested differently: a field
# with a default is checked for its value, while one without is checked for
# raising AttributeError until a load fills it in.
WITH_DEFAULT = {name: v for name, v in DEFAULTS.items() if v is not UNSET}
WITHOUT_DEFAULT = [name for name, v in DEFAULTS.items() if v is UNSET]

# The fields built by a default_factory: each state must get its own object.
#
# A mutable default on a dataclass has to be built per instance, and getting
# that wrong is the classic Python trap: every state would share one dict, so
# loading a second dataset would overwrite the variables of the first. These
# are the fields where that could happen, and test_baseloadstate.py checks
# that two fresh states do not share them.
CONTAINERS = [
    name for name, v in WITH_DEFAULT.items() if isinstance(v, (dict, list, set))
]
