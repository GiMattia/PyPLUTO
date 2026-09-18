"""Test of the load.py file.

Load implements almost nothing: it builds a state, builds eight managers on
it, and hands every public call to one of them. So these tests are about the
wiring rather than about loading data -- which manager answers, whether it
shares the state, whether the arguments arrive intact, and whether what the
class says about itself is still true.

The failures they are aimed at are quiet ones. A method wired to the wrong
manager, a manager built on a state of its own, an argument dropped between
the facade and the manager, a `__str__` still advertising a method that was
renamed: none of these raise, and all of them have happened in this codebase.

The hand-written tables live in helper_load.py, so a new method or manager
fails a completeness guard here until it is listed and therefore tested.
"""

import inspect
import logging
import re
from pathlib import Path

import pytest
from astropy import units as u
from helper_load import DELEGATION, MANAGERS, UNIMPLEMENTED

import pyPLUTO as pp
from pyPLUTO.load import Load

# The hand-written tables live in helper_load.py: DELEGATION maps each public
# method to the manager it hands the call to, and MANAGERS lists the managers
# a Load builds on its state.


def _load(data_dir: Path) -> Load:
    """Load the 2D test dataset, the smallest complete one.

    Used by nearly every test here, since what is being checked is the facade
    rather than the data: the smallest real dataset keeps the tests fast
    while still exercising a genuine load rather than a stub.
    """
    return pp.Load(path=data_dir / "single_file", text=False)


# ---- Managers ----
@pytest.mark.parametrize("name", MANAGERS)
def test_managers_share_the_state(name: str, data_dir: Path) -> None:
    """Check one manager holds the same state object as the load itself.

    `is` rather than equality: two states with the same contents would pass
    an equality check and still be two objects.

    A manager with a separate state would read a different grid, or write its
    results where nobody looks, without any error.
    """
    data = _load(data_dir)
    assert getattr(data, name).state is data.state


def test_every_manager_is_listed(data_dir: Path) -> None:
    """Compare the managers a Load builds with the list in the helper.

    The test above is parametrized from that list, so a manager missing from
    it would never be checked for sharing the state. This is what keeps that
    from happening silently.
    """
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
    """Set a name on the state, read it off the load, and the reverse.

    This is the forwarding that makes `D.rho` work: the variables cannot be
    declared in advance, so both directions go through the state. It is also
    what lets a user attach a composite variable of their own and pass the
    load into their own functions.
    """
    data = _load(data_dir)
    setattr(data.state, "custom_attr", 123)  # noqa: B010
    assert data.custom_attr == 123
    data.custom_attr = 456
    assert getattr(data.state, "custom_attr") == 456  # noqa: B009


def test_unknown_attribute_raises(data_dir: Path) -> None:
    """Read a name nothing ever set, and expect AttributeError.

    The other half of the forwarding: reaching through to the state must not
    turn a missing name into None, or a misspelled variable would read as
    empty rather than as a mistake.
    """
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
    """Print the description and check each of its sections is present.

    `__str__` is documentation the class writes about itself, so it can go
    stale as quietly as a comment. This checks the shape; the two tests below
    check the contents are true.
    """
    text = str(_load(data_dir))
    assert "Load class." in text
    assert "File properties:" in text
    assert "Simulation properties" in text
    assert "Public attributes available:" in text
    assert "Public methods available:" in text
    assert "Please refrain from using" in text


@pytest.mark.parametrize(
    "method", [name for name in DELEGATION if name not in UNIMPLEMENTED]
)
def test_str_lists_every_method(method: str, data_dir: Path) -> None:
    """Look for one public method in the description, one test per method.

    Parametrized over DELEGATION, so a method added to the class fails here
    until it is also advertised. This is the exact bug found in image.py and
    loadpart.py, where `__str__` listed methods that no longer existed and
    omitted ones that did.

    The methods in UNIMPLEMENTED are left out: they exist and raise, so
    advertising them would send a user after something that is not there.
    """
    assert f"- {method}\n" in str(_load(data_dir))


@pytest.mark.parametrize("method", sorted(UNIMPLEMENTED))
def test_str_hides_what_is_not_implemented(method: str, data_dir: Path) -> None:
    """Check a method that only raises is not advertised, and still raises.

    Both halves matter: `repeat` was listed among the public methods with a
    docstring of its own while raising NotImplementedError, and once it is
    written this test fails and says to empty UNIMPLEMENTED.
    """
    data = _load(data_dir)
    assert f"- {method}\n" not in str(data)

    with pytest.raises(NotImplementedError):
        getattr(data, method)(data.rho, "l")


def test_str_attributes_exist(data_dir: Path) -> None:
    """Read the attribute names out of the description and check each exists.

    The other direction from the test above: not "is every method listed" but
    "is everything listed real". `image.py` advertised `tg` for `tight` and a
    `fontweight` that was never stored, which is what this would have caught.

    The names are pulled out of the quoted lists in the section, and `assert
    names` guards against the regex silently matching nothing.
    """
    data = _load(data_dir)
    section = str(data).split("Public attributes available:")[1]
    names = re.findall(r"'(\w+)'", section.split("Variables available:")[0])
    assert names
    for name in names:
        assert hasattr(data, name), name


@pytest.mark.parametrize(
    "keyword", ["full3D", "units", "skip_units", "user_units"]
)
def test_the_documented_keywords_are_the_real_ones(keyword: str) -> None:
    """Check a keyword that works is documented under the name the code reads.

    The class documented `full3d` with a default of True while the keyword is
    `full3D` and defaults to False, so a user copying the documentation got
    an "Unused kwargs" warning and the opposite setting; `units`,
    `skip_units` and `user_units` worked and were documented nowhere.
    """
    documented = set(
        re.findall(r"^\s*- (\w+):", inspect.getdoc(Load) or "", re.MULTILINE)
    )

    assert keyword in documented


def test_str_properties_show_their_field(data_dir: Path) -> None:
    """Read each property line of the description and check name and value.

    The file and simulation properties are printed as a label, a name in
    brackets, and a value: `- Geometry (geom) CARTESIAN`. Two things can go
    stale there. The name can stop existing -- this is what caught `(format)`
    advertised for a field called `datatype` -- and the value can be read
    from a different field than the one named, which would print, say, the
    grid size next to `(nshp)`.

    So each line is checked both ways: the name is an attribute of the load,
    and the printed value is exactly that attribute as text. The pattern
    wants a space before the bracket, so a word such as "time(s)" is never
    read as a name, and `assert pairs` guards against it matching nothing.
    """
    data = _load(data_dir)
    section = str(data).split("File properties:")[1]
    section = section.split("Public attributes available:")[0]
    pairs = re.findall(r"\s\((\w+)\)[ \t]+(.*)", section)
    assert pairs
    for name, printed in pairs:
        assert hasattr(data, name), name
        assert str(getattr(data, name)) == printed, name


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
    """Load without the keyword and check the arrays stay plain.

    The counterpart of the test above: attaching units by default would
    change the type of every variable for every user who never asked.
    """
    data = _load(data_dir)
    assert not data.unit_attached
    assert not isinstance(data.rho, u.Quantity)


# ---- Logging ----
def test_text_logs_the_single_output(
    data_dir: Path, caplog: pytest.LogCaptureFixture
) -> None:
    """Load with text on and find the folder and output in the log.

    The line a user sees on every load, so it is worth pinning: it reports
    what was actually read, and a wrong number here would misdescribe every
    session.
    """
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
    """Load nothing at all and check the log says so rather than crashing.

    `nout=None` is documented as "do not load", which leaves the output
    number never set. LoadPart used to raise AttributeError here, because it
    lacked the guard Load has; that bug was found by this test's twin.
    """
    with (
        caplog.at_level(logging.INFO, logger="pyPLUTO.load"),
        pytest.warns(UserWarning, match="No output is loaded"),
    ):
        pp.Load(path=data_dir / "single_file", nout=None, text=True)
    assert "output None" in caplog.text


# ---- Delegation to the managers ----
def test_every_method_is_listed() -> None:
    """Compare the public methods Load defines with the table in the helper.

    Adding, removing or renaming a method fails here until the table is
    updated, so no method can go untested.

    The three tests below are all parametrized from DELEGATION, so a method
    missing from it would have neither its wiring, its arguments nor its
    documentation checked, with nothing to say so.
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
    """Compare the docstring of the facade method with the manager's.

    Each facade method carries a one-line placeholder in the source, replaced
    at class creation by `method.__doc__ = Manager.method.__doc__`. Without
    that line, `help(D.read_file)` would show "Read file method." instead of
    the real documentation, and the parameters would be documented nowhere a
    user can reach.

    `assert doc` first, so a manager method that lost its own docstring fails
    as itself rather than as a mismatch between two empty strings.
    """
    data = _load(data_dir)
    doc = getattr(type(getattr(data, manager)), method).__doc__
    assert doc
    assert getattr(Load, method).__doc__ == doc
