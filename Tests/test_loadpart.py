"""Test of the loadpart.py file.

The particle twin of test_load.py, and kept deliberately parallel to it: the
same tests in the same order, so neither facade is held to a lower standard
and a reader who knows one file knows the other.

LoadPart implements almost nothing either -- it builds a state, builds three
managers on it, and hands every public call to one of them -- so these tests
are about the wiring rather than about loading particles. The failures they
are aimed at are quiet: a method wired to the wrong manager, a manager built
on a state of its own, an argument dropped between facade and manager.

Two bugs found by this file are worth remembering, because both were things
Load had and LoadPart had not: `__str__` advertised only half its methods,
and `LoadPart(nout=None)` crashed although the docstring documents it.
"""

import inspect
import logging
import re
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
    """Load the cosmic-ray particle dataset, the only one with particles.

    Used by nearly every test here. It holds a single output, which is why
    the multiple-output test below has to build its own folder.
    """
    return pp.LoadPart(path=data_dir / "particles_cr", text=False)


# ---- Managers ----
@pytest.mark.parametrize("name", MANAGERS)
def test_managers_share_the_state(name: str, data_dir: Path) -> None:
    """Check one manager holds the same state object as the load itself.

    `is` rather than equality: two states with the same contents would pass
    an equality check and still be two objects.

    A manager with a separate state would read different particles, or write
    its results where nobody looks, without any error.
    """
    data = _loadpart(data_dir)
    assert getattr(data, name).state is data.state


def test_every_manager_is_listed(data_dir: Path) -> None:
    """Compare the managers a LoadPart builds with the list in the helper.

    The test above is parametrized from that list, so a manager missing from
    it would never be checked for sharing the state.
    """
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
    """Set a name on the state, read it off the load, and the reverse.

    This is the forwarding that makes a particle variable reachable: the
    names come from the files and cannot be declared in advance, so both
    directions go through the state.
    """
    data = _loadpart(data_dir)
    setattr(data.state, "custom_attr", 123)  # noqa: B010
    assert data.custom_attr == 123
    data.custom_attr = 456
    assert getattr(data.state, "custom_attr") == 456  # noqa: B009


def test_unknown_attribute_raises(data_dir: Path) -> None:
    """Read a name nothing ever set, and expect AttributeError.

    Reaching through to the state must not turn a missing name into None, or
    a misspelled variable would read as empty rather than as a mistake.
    """
    data = _loadpart(data_dir)
    with pytest.raises(AttributeError):
        data.wrong  # noqa: B018


def test_state_is_set_on_the_instance(data_dir: Path) -> None:
    """Check the state lives on the LoadPart rather than inside itself.

    __setattr__ sends every assignment to the state, so state itself must be
    the one exception or the object would never get one -- the first line of
    __init__ would try to store a state inside a state that does not exist.
    """
    data = _loadpart(data_dir)
    assert "state" in vars(data)
    assert data.state is not data.state.__dict__.get("state")


# ---- Printing ----
def test_repr_shows_the_state(data_dir: Path) -> None:
    """Print the repr and check it names the output and the folder.

    Shorter than the Load version, which also reports the geometry: there is
    no mesh here to report.
    """
    text = repr(_loadpart(data_dir))
    assert text.startswith("LoadPart(")
    assert "nout=" in text
    assert "particles_cr" in text


def test_str_describes_the_load(data_dir: Path) -> None:
    """Print the description and check each of its sections is present.

    `__str__` is documentation the class writes about itself, so it can go
    stale as quietly as a comment. This checks the shape; the tests below
    check the contents are true.
    """
    text = str(_loadpart(data_dir))
    assert "LoadPart class." in text
    assert "File properties:" in text
    assert "Simulation properties" in text
    assert "Variables loaded:" in text
    assert "Public methods available:" in text
    assert "Please refrain from using" in text


@pytest.mark.parametrize("method", DELEGATION)
def test_str_lists_every_method(method: str, data_dir: Path) -> None:
    """Look for one public method in the description, one test per method.

    Parametrized over DELEGATION, so a method added to the class fails here
    until it is also advertised. This is the test that caught `__str__`
    listing only select and spectrum while to_astropy_units and to_code_units
    were equally public.
    """
    assert f"- {method}\n" in str(_loadpart(data_dir))


def test_str_properties_show_their_field(data_dir: Path) -> None:
    """Read each property line of the description and check name and value.

    The twin of the Load test. The file and simulation properties are printed
    as a label, a name in brackets, and a value: `- File format (datatype)
    dbl`. The name must be an attribute of the load, and the printed value
    must be exactly that attribute as text, or the line is describing a
    field that no longer exists, or showing a different one.

    The pattern wants a space before the bracket: this description has
    "time(s) (ntime)", and without the space `s` would be read as a name.
    `assert pairs` guards against the pattern matching nothing.
    """
    data = _loadpart(data_dir)
    section = str(data).split("File properties:")[1]
    section = section.split("Variables loaded:")[0]
    pairs = re.findall(r"\s\((\w+)\)[ \t]+(.*)", section)
    assert pairs
    for name, printed in pairs:
        assert hasattr(data, name), name
        assert str(getattr(data, name)) == printed, name


def test_str_lists_the_loaded_variables(data_dir: Path) -> None:
    """Check every variable the load holds is named in the description.

    The particle equivalent of checking the advertised attributes exist: the
    variables are discovered from the files, so the description has to follow
    whatever was read rather than a fixed list.
    """
    data = _loadpart(data_dir)
    assert data.state.d_vars
    for name in data.state.d_vars:
        assert f"'{name}'" in str(data)


# ---- Units ----
def test_units_keyword_attaches_astropy_units(data_dir: Path) -> None:
    """Load with units on and check a variable comes back as a Quantity.

    Passing units to the constructor must do the same as calling
    to_astropy_units afterwards, so the arrays come back as Quantity.

    The variable is taken from unit_attached rather than named outright,
    since which particle variables carry units depends on the dataset.
    """
    data = pp.LoadPart(path=data_dir / "particles_cr", units=True, text=False)
    assert data.unit_attached
    name = next(iter(data.unit_attached))
    assert isinstance(getattr(data, name), u.Quantity)


def test_no_units_keyword_leaves_plain_arrays(data_dir: Path) -> None:
    """Load without the keyword and check nothing was converted.

    The counterpart of the test above: attaching units by default would
    change the type of every variable for every user who never asked.
    """
    data = _loadpart(data_dir)
    assert not data.unit_attached


# ---- Deprecated keywords ----
def test_nfile_lp_is_deprecated(data_dir: Path) -> None:
    """Pass the old keyword and check it warns and still takes effect.

    The keyword was renamed, so an old script must keep working while it is
    told to move on. Both halves matter: a warning that broke the call would
    be worse than the rename, and a silent rename would never be adopted.
    """
    with pytest.warns(DeprecationWarning, match="nfile_lp"):
        data = pp.LoadPart(
            path=data_dir / "particles_cr", text=False, nfile_lp=0
        )
    assert data.state.chnk == 0


def test_chnk_wins_over_nfile_lp(data_dir: Path) -> None:
    """Pass both names and check the current one wins.

    `setdefault` is what decides this, and it is easy to write the other way
    round: an old script that was half-updated would then be silently
    overridden by the keyword it was migrating away from.
    """
    with pytest.warns(DeprecationWarning, match="nfile_lp"):
        data = pp.LoadPart(
            path=data_dir / "particles_cr", text=False, chnk=0, nfile_lp=1
        )
    assert data.state.chnk == 0


# ---- Logging ----
def test_text_logs_the_single_output(
    data_dir: Path, caplog: pytest.LogCaptureFixture
) -> None:
    """Load with text on and find the folder and output in the log.

    The line a user sees on every load, so it is worth pinning: a wrong
    number here would misdescribe every session.
    """
    with caplog.at_level(logging.INFO, logger="pyPLUTO.loadpart"):
        pp.LoadPart(path=data_dir / "particles_cr", text=True)
    assert "particles_cr" in caplog.text
    assert "output 0" in caplog.text


def test_text_logs_every_output_as_plain_ints(
    data_dir: Path, tmp_path: Path, caplog: pytest.LogCaptureFixture
) -> None:
    """Load two outputs and check the log shows plain ints, not numpy ones.

    nout is an array of numpy integers here, whose repr would litter the line
    with np.int64(...), so the message is built from a converted copy.

    The only particle dataset holds a single output, so a second one is
    copied next to it: without that, the branch that formats several outputs
    is unreachable and was never exercised by anything.
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
    """Load nothing at all and check the log says so rather than crashing.

    `nout=None` is documented as "do not load", which leaves the output
    number never set. This used to raise AttributeError, because LoadPart
    lacked the guard Load had; that is the bug this test was written for.
    """
    with (
        caplog.at_level(logging.INFO, logger="pyPLUTO.loadpart"),
        pytest.warns(UserWarning, match="No output is loaded"),
    ):
        pp.LoadPart(path=data_dir / "particles_cr", nout=None, text=True)
    assert "output None" in caplog.text


# ---- Delegation to the managers ----
def test_every_method_is_listed() -> None:
    """Compare the public methods LoadPart defines with the helper table.

    Adding, removing or renaming a method fails here until the table is
    updated, so no method can go untested.

    The three tests below are all parametrized from DELEGATION, so a method
    missing from it would have neither its wiring, its arguments nor its
    documentation checked, with nothing to say so.
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
    """Call one facade method and check the manager received it intact.

    The strongest test in the file, and the one that would catch a facade
    method quietly dropping or reordering an argument -- which produces wrong
    results rather than an error, since most of these parameters are optional.

    It works by replacing the manager's method with a recorder, calling the
    facade, then binding what was recorded against the manager's real
    signature. Binding is what makes the check independent of *how* the
    facade passes things: by position or by keyword, the argument has to land
    on the parameter of the same name.

    Each argument is a fresh object(), so an argument that ended up on the
    wrong parameter cannot coincidentally look right. An extra keyword checks
    that **kwargs are forwarded too, and the return value is the same object
    the manager produced, so the facade is not post-processing anything.

    The manager signature is unwrapped because track_kwargs replaces it with
    one that hides _check, and binding needs the real one.
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
    """Compare the docstring of the facade method with the manager's.

    Each facade method carries a one-line placeholder in the source, replaced
    at class creation by `method.__doc__ = Manager.method.__doc__`. Without
    that line, `help(D.spectrum)` would show "Spectrum method." instead of
    the real documentation.
    """
    data = _loadpart(data_dir)
    doc = getattr(type(getattr(data, manager)), method).__doc__
    assert doc
    assert getattr(LoadPart, method).__doc__ == doc


# ---- Loaded data ----
def test_particles_are_loaded(data_dir: Path) -> None:
    """Check every loaded variable has one entry per particle.

    The one test here that looks at the data rather than the wiring. It is
    cheap and catches a whole class of reading bug: a variable read with the
    wrong offset or stride comes out the wrong length, and every plot made
    from it would silently be of something else.
    """
    data = _loadpart(data_dir)
    nshp = data.state.nshp
    assert nshp
    for name in data.state.d_vars:
        assert np.shape(getattr(data, name))[0] == nshp
