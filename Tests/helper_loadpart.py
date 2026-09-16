"""Expected values for LoadPart, shared by the tests that rely on it.

LoadPart stores its data in a plain BaseLoadState, so it adds no fields of its
own: the field tables live in helper_baseload.py. What belongs here is the
facade side, written by hand on purpose so the tests never compare the code
with itself.

That is the difference from helper_load.py, and it is worth knowing when
reading either: Load has its own state class for the grid, while LoadPart
reuses the base one, since particles carry their positions as variables
rather than as a grid. So there is no OWN_DEFAULTS here and nothing to merge.
"""

# Every public method of LoadPart and the manager it hands the call to.
# Checked by test_delegation and test_docstring_is_copied, while
# test_every_method_is_listed makes sure no public method is missing.
#
# Four methods against Load's sixteen: particles support selection, spectra
# and the unit conversions, and none of the grid operations, which would have
# no meaning without a grid.
DELEGATION: dict[str, str] = {
    "select": "PartToolsManager",
    "spectrum": "PartToolsManager",
    "to_astropy_units": "SetUnitsManager",
    "to_code_units": "SetUnitsManager",
}

# Every method of LoadPart that takes **kwargs, and the TypedDict of
# loadkwargs.py that declares them. __init__ is listed too: the constructor is
# where most of the keywords are actually given.
KWARGS: dict[str, str] = {
    "__init__": "LoadPartKwargs",
    "spectrum": "SpectrumKwargs",
}

# The methods that take explicit parameters only, with no **kwargs at all.
# Listed rather than left out, so that every method is accounted for by one
# table or the other; the completeness guard in test_loadkwargs.py fails until
# a new method appears in one of them.
NO_KWARGS: set[str] = {
    "select",
    "to_astropy_units",
    "to_code_units",
}

# Every manager that a LoadPart builds on its state. UnitManager is the one no
# public method delegates to: the units are computed while loading.
#
# Three against Load's eight, and they share the one state object, which is
# how a result written by one is visible to the others.
MANAGERS: list[str] = [
    "PartToolsManager",
    "SetUnitsManager",
    "UnitManager",
]
