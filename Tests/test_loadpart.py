"""Test of the loadpart.py file."""

import inspect
import logging
from pathlib import Path

import numpy as np
import pytest
from astropy import units as u
from helper_loadpart import DELEGATION, MANAGERS

import pyPLUTO as pp
from pyPLUTO.loadpart import LoadPart

# The hand-written tables live in helper_loadpart.py: DELEGATION maps each
# public method to the manager it hands the call to, and MANAGERS lists the
# managers a LoadPart builds on its state.


def _loadpart(data_dir: Path) -> LoadPart:
    """Load the cosmic-ray particle dataset, the only one with particles."""
    return pp.LoadPart(path=data_dir / "particles_cr", text=False)


# ---- Managers ----
@pytest.mark.parametrize("name", MANAGERS)
def test_managers_share_the_state(name: str, data_dir: Path) -> None:
    """Build every manager on the load's own state.

    A manager with a separate state would read different particles, or write
    its results where nobody looks, without any error.
    """
    data = _loadpart(data_dir)
    assert getattr(data, name).state is data.state


def test_every_manager_is_listed(data_dir: Path) -> None:
    """Keep MANAGERS in sync with the managers a LoadPart builds."""
    data = _loadpart(data_dir)
    built = {name for name in vars(data.state) if name.endswith("Manager")}
    missing, stale = built - set(MANAGERS), set(MANAGERS) - built
    assert not missing, (
        f"not listed in MANAGERS, so untested: {sorted(missing)}"
    )
    assert not stale, (
        f"listed in MANAGERS but not built by LoadPart: {sorted(stale)}"
    )


# ---- Attribute access ----
def test_attribute_reads_and_writes_the_state(data_dir: Path) -> None:
    """Read and write the load attributes through the state."""
    data = _loadpart(data_dir)
    setattr(data.state, "custom_attr", 123)  # noqa: B010
    assert data.custom_attr == 123
    data.custom_attr = 456
    assert getattr(data.state, "custom_attr") == 456  # noqa: B009


def test_unknown_attribute_raises(data_dir: Path) -> None:
    """Raise AttributeError for an attribute the state does not have."""
    data = _loadpart(data_dir)
    with pytest.raises(AttributeError):
        data.wrong  # noqa: B018


def test_state_is_set_on_the_instance(data_dir: Path) -> None:
    """Keep state on the instance, not forwarded into itself.

    __setattr__ sends every assignment to the state, so state itself must be
    the one exception or the object would never get one.
    """
    data = _loadpart(data_dir)
    assert "state" in vars(data)
    assert data.state is not data.state.__dict__.get("state")


# ---- Printing ----
def test_repr_shows_the_state(data_dir: Path) -> None:
    """Show the output number and the folder of the load."""
    text = repr(_loadpart(data_dir))
    assert text.startswith("LoadPart(")
    assert "nout=" in text
    assert "particles_cr" in text


def test_str_describes_the_load(data_dir: Path) -> None:
    """Describe the file, the simulation and the public methods."""
    text = str(_loadpart(data_dir))
    assert "LoadPart class." in text
    assert "File properties:" in text
    assert "Simulation properties" in text
    assert "Variables loaded:" in text
    assert "Public methods available:" in text
    assert "Please refrain from using" in text


@pytest.mark.parametrize("method", DELEGATION)
def test_str_lists_every_method(method: str, data_dir: Path) -> None:
    """List every public method in the description, so it cannot go stale."""
    assert f"- {method}\n" in str(_loadpart(data_dir))


def test_str_lists_the_loaded_variables(data_dir: Path) -> None:
    """Advertise the variables that were really loaded."""
    data = _loadpart(data_dir)
    assert data.state.d_vars
    for name in data.state.d_vars:
        assert f"'{name}'" in str(data)


# ---- Units ----
def test_units_keyword_attaches_astropy_units(data_dir: Path) -> None:
    """Convert the variables at construction when units is given.

    Passing units to the constructor must do the same as calling
    to_astropy_units afterwards, so the arrays come back as Quantity.
    """
    data = pp.LoadPart(path=data_dir / "particles_cr", units=True, text=False)
    assert data.unit_attached
    name = next(iter(data.unit_attached))
    assert isinstance(getattr(data, name), u.Quantity)


def test_no_units_keyword_leaves_plain_arrays(data_dir: Path) -> None:
    """Leave the variables untouched when units is not given."""
    data = _loadpart(data_dir)
    assert not data.unit_attached


# ---- Deprecated keywords ----
def test_nfile_lp_is_deprecated(data_dir: Path) -> None:
    """Warn on nfile_lp, but still use it as chnk.

    The keyword was renamed, so an old script must keep working while it is
    told to move on.
    """
    with pytest.warns(DeprecationWarning, match="nfile_lp"):
        data = pp.LoadPart(
            path=data_dir / "particles_cr", text=False, nfile_lp=0
        )
    assert data.state.chnk == 0


def test_chnk_wins_over_nfile_lp(data_dir: Path) -> None:
    """Keep chnk when both are given, since it is the current name."""
    with pytest.warns(DeprecationWarning, match="nfile_lp"):
        data = pp.LoadPart(
            path=data_dir / "particles_cr", text=False, chnk=0, nfile_lp=1
        )
    assert data.state.chnk == 0


# ---- Logging ----
def test_text_logs_the_single_output(
    data_dir: Path, caplog: pytest.LogCaptureFixture
) -> None:
    """Report the folder and the output number when text is on."""
    with caplog.at_level(logging.INFO, logger="pyPLUTO.loadpart"):
        pp.LoadPart(path=data_dir / "particles_cr", text=True)
    assert "particles_cr" in caplog.text
    assert "output 0" in caplog.text


def test_text_logs_every_output_as_plain_ints(
    data_dir: Path, tmp_path: Path, caplog: pytest.LogCaptureFixture
) -> None:
    """Report a multiple load as a list of plain ints.

    nout is an array of numpy integers here, whose repr would litter the line
    with np.int64(...), so the message is built from a converted copy. The
    only particle dataset holds a single output, so a second one is copied
    next to it to get a multiple load at all.

    LONG TEST: CHECK
    """
    source = data_dir / "particles_cr" / "particles.0000.dbl"
    (tmp_path / source.name).write_bytes(source.read_bytes())
    (tmp_path / "particles.0001.dbl").write_bytes(source.read_bytes())

    with caplog.at_level(logging.INFO, logger="pyPLUTO.loadpart"):
        data = pp.LoadPart(path=tmp_path, nout="all", text=True)

    assert isinstance(data.state.nout, np.ndarray)
    assert "output [0, 1]" in caplog.text


def test_text_logs_no_output_when_nothing_is_loaded(
    data_dir: Path, caplog: pytest.LogCaptureFixture
) -> None:
    """Report no output when nout is None, so nothing was ever loaded."""
    with (
        caplog.at_level(logging.INFO, logger="pyPLUTO.loadpart"),
        pytest.warns(UserWarning, match="No output is loaded"),
    ):
        pp.LoadPart(path=data_dir / "particles_cr", nout=None, text=True)
    assert "output None" in caplog.text


# ---- Delegation to the managers ----
def test_every_method_is_listed() -> None:
    """Keep DELEGATION in sync with the public methods LoadPart defines.

    Adding, removing or renaming a method fails here until the table is
    updated, so no method can go untested.
    """
    public = {
        name
        for name, attribute in vars(LoadPart).items()
        if callable(attribute) and not name.startswith("_")
    }
    missing, stale = public - set(DELEGATION), set(DELEGATION) - public
    assert not missing, (
        f"not listed in DELEGATION, so untested: {sorted(missing)}"
    )
    assert not stale, (
        f"listed in DELEGATION but no longer a LoadPart method: {sorted(stale)}"
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
    data = _loadpart(data_dir)
    target = getattr(data, manager)
    calls: list[tuple[tuple[object, ...], dict[str, object]]] = []
    result = object()

    def record(*args: object, **kwargs: object) -> object:
        calls.append((args, kwargs))
        return result

    monkeypatch.setattr(target, method, record)

    params = inspect.signature(getattr(LoadPart, method)).parameters.values()
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
    data = _loadpart(data_dir)
    doc = getattr(type(getattr(data, manager)), method).__doc__
    assert doc
    assert getattr(LoadPart, method).__doc__ == doc


# ---- Loaded data ----
def test_particles_are_loaded(data_dir: Path) -> None:
    """Load the particle arrays, all with one entry per particle."""
    data = _loadpart(data_dir)
    nshp = data.state.nshp
    assert nshp
    for name in data.state.d_vars:
        assert np.shape(getattr(data, name))[0] == nshp
