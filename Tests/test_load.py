"""Test of the load.py file."""

import inspect
import logging
import re
from pathlib import Path

import pytest
from astropy import units as u
from helper_load import DELEGATION, MANAGERS

import pyPLUTO as pp
from pyPLUTO.load import Load

# The hand-written tables live in helper_load.py: DELEGATION maps each public
# method to the manager it hands the call to, and MANAGERS lists the managers
# a Load builds on its state.


def _load(data_dir: Path) -> Load:
    """Load the 2D test dataset, the smallest complete one."""
    return pp.Load(path=data_dir / "single_file", text=False)


# ---- Managers ----
@pytest.mark.parametrize("name", MANAGERS)
def test_managers_share_the_state(name: str, data_dir: Path) -> None:
    """Build every manager on the load's own state.

    A manager with a separate state would read a different grid, or write its
    results where nobody looks, without any error.
    """
    data = _load(data_dir)
    assert getattr(data, name).state is data.state


def test_every_manager_is_listed(data_dir: Path) -> None:
    """Keep MANAGERS in sync with the managers a Load builds."""
    data = _load(data_dir)
    built = {name for name in vars(data.state) if name.endswith("Manager")}
    missing, stale = built - set(MANAGERS), set(MANAGERS) - built
    assert not missing, (
        f"not listed in MANAGERS, so untested: {sorted(missing)}"
    )
    assert not stale, (
        f"listed in MANAGERS but not built by Load: {sorted(stale)}"
    )


# ---- Attribute access ----
def test_attribute_reads_and_writes_the_state(data_dir: Path) -> None:
    """Read and write the load attributes through the state."""
    data = _load(data_dir)
    setattr(data.state, "custom_attr", 123)  # noqa: B010
    assert data.custom_attr == 123
    data.custom_attr = 456
    assert getattr(data.state, "custom_attr") == 456  # noqa: B009


def test_unknown_attribute_raises(data_dir: Path) -> None:
    """Raise AttributeError for an attribute the state does not have."""
    data = _load(data_dir)
    with pytest.raises(AttributeError):
        data.wrong  # noqa: B018


# ---- Printing ----
def test_repr_shows_the_state(data_dir: Path) -> None:
    """Show the output number, the folder and the geometry of the load.

    nout is a numpy integer, so repr wraps it as np.int64(0) instead of 0.
    The pattern accepts the wrapper but still pins the number to 0, the only
    output single_file holds.
    """
    data = _load(data_dir)
    text = repr(data)
    assert text.startswith("Load(")
    assert re.search(r"nout=(?:np\.\w+\()?0\)?,", text), text
    assert "geom='CARTESIAN'" in text
    assert "single_file" in text


def test_str_describes_the_load(data_dir: Path) -> None:
    """Describe the file, the simulation and the public methods."""
    text = str(_load(data_dir))
    assert "Load class." in text
    assert "File properties:" in text
    assert "Simulation properties" in text
    assert "Public attributes available:" in text
    assert "Public methods available:" in text
    assert "Please refrain from using" in text


@pytest.mark.parametrize("method", DELEGATION)
def test_str_lists_every_method(method: str, data_dir: Path) -> None:
    """List every public method in the description, so it cannot go stale."""
    assert f"- {method}\n" in str(_load(data_dir))


def test_str_attributes_exist(data_dir: Path) -> None:
    """Advertise only attributes that the load really has."""
    data = _load(data_dir)
    section = str(data).split("Public attributes available:")[1]
    names = re.findall(r"'(\w+)'", section.split("Variables available:")[0])
    assert names
    for name in names:
        assert hasattr(data, name), name


# ---- Units ----
def test_units_keyword_attaches_astropy_units(data_dir: Path) -> None:
    """Convert the variables at construction when units is given.

    Passing units to the constructor must do the same as calling
    to_astropy_units afterwards, so the arrays come back as Quantity.
    """
    data = pp.Load(path=data_dir / "single_file", units=True, text=False)
    assert "rho" in data.unit_attached
    assert isinstance(data.rho, u.Quantity)


def test_no_units_keyword_leaves_plain_arrays(data_dir: Path) -> None:
    """Leave the variables untouched when units is not given."""
    data = _load(data_dir)
    assert not data.unit_attached
    assert not isinstance(data.rho, u.Quantity)


# ---- Logging ----
def test_text_logs_the_single_output(
    data_dir: Path, caplog: pytest.LogCaptureFixture
) -> None:
    """Report the folder and the output number when text is on."""
    with caplog.at_level(logging.INFO, logger="pyPLUTO.load"):
        pp.Load(path=data_dir / "single_file", text=True)
    assert "single_file" in caplog.text
    assert "output 0" in caplog.text


def test_text_logs_every_output_as_plain_ints(
    data_dir: Path, caplog: pytest.LogCaptureFixture
) -> None:
    """Report a multiple load as a list of plain ints.

    nout holds numpy integers here, whose repr would litter the line with
    np.int64(...), so the message is built from a converted copy.
    """
    with caplog.at_level(logging.INFO, logger="pyPLUTO.load"):
        pp.Load(path=data_dir / "multiple_outputs", nout="all", text=True)
    assert "output [0, 1, 2, 3, 4]" in caplog.text


def test_text_logs_no_output_when_nothing_is_loaded(
    data_dir: Path, caplog: pytest.LogCaptureFixture
) -> None:
    """Report no output when nout is None, so nothing was ever loaded."""
    with (
        caplog.at_level(logging.INFO, logger="pyPLUTO.load"),
        pytest.warns(UserWarning, match="No output is loaded"),
    ):
        pp.Load(path=data_dir / "single_file", nout=None, text=True)
    assert "output None" in caplog.text


# ---- Delegation to the managers ----
def test_every_method_is_listed() -> None:
    """Keep DELEGATION in sync with the public methods Load defines.

    Adding, removing or renaming a method fails here until the table is
    updated, so no method can go untested.
    """
    public = {
        name
        for name, attribute in vars(Load).items()
        if callable(attribute) and not name.startswith("_")
    }
    missing, stale = public - set(DELEGATION), set(DELEGATION) - public
    assert not missing, (
        f"not listed in DELEGATION, so untested: {sorted(missing)}"
    )
    assert not stale, (
        f"listed in DELEGATION but no longer a Load method: {sorted(stale)}"
    )


@pytest.mark.parametrize(("method", "manager"), DELEGATION.items())
def test_delegation(
    method: str, manager: str, data_dir: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    """Hand every argument to the right manager and return its result.

    Each argument is a fresh object(), and must arrive at the manager's
    parameter with the same name, whether the facade passes it by position or
    by keyword. An extra keyword checks that **kwargs are forwarded too. The
    manager signature is unwrapped because track_kwargs hides _check from it.

    LONG TEST: CHECK
    """
    data = _load(data_dir)
    target = getattr(data, manager)
    calls: list[tuple[tuple[object, ...], dict[str, object]]] = []
    result = object()

    def record(*args: object, **kwargs: object) -> object:
        calls.append((args, kwargs))
        return result

    monkeypatch.setattr(target, method, record)

    params = inspect.signature(getattr(Load, method)).parameters.values()
    sent = {
        p.name: object()
        for p in params
        if p.name != "self" and p.kind is not p.VAR_KEYWORD
    }
    extra = (
        {"extra": object()}
        if any(p.kind is p.VAR_KEYWORD for p in params)
        else {}
    )

    assert getattr(data, method)(**sent, **extra) is result

    ((args, kwargs),) = calls
    signature = inspect.signature(inspect.unwrap(getattr(type(target), method)))
    received = signature.bind(None, *args, **kwargs).arguments
    var_kw = next(
        (
            p.name
            for p in signature.parameters.values()
            if p.kind is p.VAR_KEYWORD
        ),
        None,
    )
    forwarded = received.pop(var_kw, {}) if var_kw else {}
    for name, value in sent.items():
        assert received[name] is value, name
    for name, value in extra.items():
        assert forwarded[name] is value, name


@pytest.mark.parametrize(("method", "manager"), DELEGATION.items())
def test_docstring_is_copied(method: str, manager: str, data_dir: Path) -> None:
    """Show the manager's documentation on the facade method."""
    data = _load(data_dir)
    doc = getattr(type(getattr(data, manager)), method).__doc__
    assert doc
    assert getattr(Load, method).__doc__ == doc
