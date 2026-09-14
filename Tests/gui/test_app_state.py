"""Test of the app_state.py file."""

from dataclasses import fields

import numpy as np
import pytest

from pyPLUTO.gui.app_state import AppState

# The expected default of every AppState field. This table is the single
# source of truth: each entry is checked by test_default, and
# test_every_field_has_a_default makes sure no declared field is missing.
DEFAULTS: dict[str, object] = {
    # Load/session state: nothing loaded yet. The plot controller refuses to
    # plot while data_loaded is False.
    "folder_path": None,
    "datatype": None,
    "nout": 0,
    "data_loaded": False,
    # Plot/session state: nothing plotted yet. firstplot=True makes the first
    # plot set the axis limits instead of growing them, which is also why the
    # zero axis ranges below are harmless: they are replaced, not stretched to
    # include zero.
    "firstplot": True,
    "vardim": 0,
    "numlines": 0,
    "xmin": 0.0,
    "xmax": 0.0,
    "ymin": 0.0,
    "ymax": 0.0,
    "datadict": {},
    # Line-lock / slider replay state: no locked and no live lines.
    "frozen_lines": [],
    "live_specs": [],
    # Runtime objects: the dataset, the figure and the plotted variable only
    # exist once a load or a plot creates them.
    "Data": None,
    "Image": None,
    "var": None,
}


@pytest.mark.parametrize(("name", "expected"), DEFAULTS.items())
def test_default(name: str, expected: object) -> None:
    """Start every field from its expected default, with the expected type.

    The type is checked too because 0 == 0.0 == False in Python: comparing
    values alone would not notice, e.g., nout defaulting to False.
    """
    value = getattr(AppState(), name)
    assert value == expected
    assert type(value) is type(expected)


def test_every_field_has_a_default() -> None:
    """Keep DEFAULTS in sync with the fields AppState declares.

    Adding, removing or renaming a field fails here until the table above is
    updated, so no field can go untested.
    """
    declared = {field.name for field in fields(AppState)}
    assert set(DEFAULTS) == declared


def test_containers_are_not_shared() -> None:
    """Give every state its own dict and lists (default_factory).

    Filling one window's plot settings, locked lines or live lines never leaks
    into another window.
    """
    first, second = AppState(), AppState()
    first.datadict["rho"] = 1
    first.frozen_lines.append({"a": 1})
    first.live_specs.append({"b": 2})
    assert second.datadict == {}
    assert second.frozen_lines == []
    assert second.live_specs == []


def test_values_can_be_set_at_creation() -> None:
    """Accept the load settings directly in the constructor."""
    state = AppState(folder_path="/tmp", datatype="dbl", nout=3)
    assert state.folder_path == "/tmp"
    assert state.datatype == "dbl"
    assert state.nout == 3


def test_values_can_be_changed() -> None:
    """Let the controllers update the state in place, e.g. after a load."""
    state = AppState()
    state.var = np.ones(3)
    state.data_loaded = True
    assert state.data_loaded is True
    assert state.var.shape == (3,)


def test_undeclared_attribute_is_rejected() -> None:
    """Reject undeclared attributes, thanks to slots=True.

    A typo such as "fistplot" fails loudly instead of silently creating a new
    field.
    """
    state = AppState()
    with pytest.raises(AttributeError):
        setattr(state, "fistplot", False)  # noqa: B010
