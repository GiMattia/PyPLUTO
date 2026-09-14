"""Test of the template.py file.

template.py is the reference a new contributor copies when adding a manager,
so it is tested on two fronts: the example it shows must really work, and the
claims it makes about the architecture and about the rest of the repository
must stay true. A stale template is worse than no template, since it teaches
a pattern that no longer matches the code.
"""

import dataclasses
import doctest
import inspect
import re
import typing
import warnings
from pathlib import Path

import pytest

import pyPLUTO as pp
from pyPLUTO import template
from pyPLUTO.template import (
    Example,
    ExampleKwargs,
    ExampleManager,
    ExampleMixin,
    ExampleState,
)

SOURCE = Path(template.__file__).read_text(encoding="utf-8")

# The repository root, reached from this file so the checks below do not
# depend on the working directory, and the folders a path in the template may
# be written relative to: the root ("CONTRIBUTING.md"), src ("pyPLUTO/..."),
# the package ("imagefuncs/plot.py") and the docs ("toolsmethods.rst").
ROOT = Path(__file__).resolve().parents[1]
BASES = [ROOT, ROOT / "src", ROOT / "src" / "pyPLUTO", ROOT / "Docs" / "source"]

# Files the template names as hypothetical rather than real: the angle-bracket
# placeholders, plus the manager file the worked example pretends to add.
PLACEHOLDER = "pyPLUTO/imagefuncs/example.py"

# Every file the template points a reader at, taken from the backticked paths
# in its text. They are checked one by one below, so a renamed or deleted file
# cannot leave the template sending contributors to a dead end.
REFERENCED = sorted(
    path
    for path in set(re.findall(r"`([\w./<>-]+\.(?:py|rst|md))`", SOURCE))
    if "<" not in path and path != PLACEHOLDER
)


# ---- The example works ----
def test_rescale_multiplies_every_value() -> None:
    """Multiply every stored value by the factor, and return them."""
    state = ExampleState(values=[1.0, 2.0, 3.0])
    assert ExampleManager(state).rescale(factor=2.0) == [2.0, 4.0, 6.0]


def test_rescale_writes_through_to_the_state() -> None:
    """Store the result on the state, not only in the returned list.

    The whole point of the pattern is that a manager mutates the shared
    state, so a version that only returned a new list would look right here
    and be wrong everywhere else.
    """
    state = ExampleState(values=[1.0, 2.0])
    ExampleManager(state).rescale(factor=3.0)
    assert state.values == [3.0, 6.0]


def test_rescale_defaults_to_no_change() -> None:
    """Leave the values alone when no factor is given."""
    state = ExampleState(values=[1.0, 2.0])
    assert ExampleManager(state).rescale() == [1.0, 2.0]


def test_label_kwarg_overwrites_the_state() -> None:
    """Overwrite the label when the keyword is given."""
    state = ExampleState(label="before")
    ExampleManager(state).rescale(label="after")
    assert state.label == "after"


def test_label_kwarg_is_optional() -> None:
    """Keep the label when the keyword is left out."""
    state = ExampleState(label="before")
    ExampleManager(state).rescale()
    assert state.label == "before"


def test_manager_shares_the_state_by_reference() -> None:
    """Share one state object between the manager and its owner.

    This is the claim the module docstring makes first: a manager that copied
    the state would silently stop talking to the others.
    """
    state = ExampleState(values=[1.0])
    manager = ExampleManager(state)
    assert manager.state is state
    manager.rescale(factor=5.0)
    assert state.values == [5.0]


def test_each_state_gets_its_own_values() -> None:
    """Build a fresh list per state, as the default_factory promises."""
    first, second = ExampleState(), ExampleState()
    assert first.values is not second.values
    first.values.append(1.0)
    assert second.values == []


# ---- track_kwargs ----
def test_unknown_kwarg_warns() -> None:
    """Warn about a keyword the method never reads.

    track_kwargs is the piece a new contributor is most likely to leave out,
    so the template has to show it working.
    """
    state = ExampleState(values=[1.0])
    with pytest.warns(UserWarning, match="unknown"):
        # The bad keyword is the point of the test, so the type error it
        # raises is expected and silenced.
        ExampleManager(state).rescale(factor=2.0, unknown=1)  # type: ignore[call-arg] # pyright: ignore[reportCallIssue]


def test_unknown_kwarg_is_silent_when_check_is_off() -> None:
    """Stay silent with _check=False, the way a manager calls another one."""
    state = ExampleState(values=[1.0])
    with warnings.catch_warnings():
        warnings.simplefilter("error")
        # As above: the unknown keyword is deliberate.
        ExampleManager(state).rescale(factor=2.0, _check=False, unknown=1)  # type: ignore[call-arg] # pyright: ignore[reportCallIssue]


# ---- The architecture the template teaches ----
def test_state_is_a_dataclass() -> None:
    """Keep the state a plain dataclass, with no behaviour of its own."""
    assert dataclasses.is_dataclass(ExampleState)
    assert not [
        name
        for name, value in vars(ExampleState).items()
        if callable(value) and not name.startswith("__")
    ]


def test_kwargs_is_a_total_false_typeddict() -> None:
    """Make every kwarg optional, with total=False."""
    assert typing.is_typeddict(ExampleKwargs)
    assert ExampleKwargs.__required_keys__ == frozenset()


def test_kwargs_does_not_repeat_an_explicit_parameter() -> None:
    """Keep the TypedDict free of the method's own named parameters.

    The template states this rule in section 2, so the example itself must
    obey it: a key that is also a parameter could never be reached through
    kwargs.
    """
    signature = inspect.signature(inspect.unwrap(ExampleManager.rescale))
    named = {
        name
        for name, p in signature.parameters.items()
        if p.kind is not p.VAR_KEYWORD
    }
    clash = named & set(ExampleKwargs.__annotations__)
    assert not clash, f"declared both as parameter and kwarg: {sorted(clash)}"


def test_mixin_property_reads_and_writes_the_state() -> None:
    """Reach the state field through the mixin property, both ways."""
    state = ExampleState(label="first")
    manager = ExampleManager(state)
    assert manager.label == "first"
    manager.label = "second"
    assert state.label == "second"


def test_manager_inherits_the_mixin() -> None:
    """Give the manager the shared properties, as every real one does."""
    assert issubclass(ExampleManager, ExampleMixin)


# ---- The template stays honest ----
def test_docstring_examples_run() -> None:
    """Run the Examples block of the module as a doctest.

    The example output is written by hand in the docstring, so this is what
    keeps it from drifting away from what the code returns.
    """
    results = doctest.testmod(template, verbose=False)
    assert results.attempted
    assert not results.failed


def test_template_references_other_files() -> None:
    """Find the referenced paths, so the test below is not vacuous.

    An empty list would turn it into a skip rather than a failure, and the
    template could then point anywhere without anyone noticing.
    """
    assert REFERENCED


@pytest.mark.parametrize("path", REFERENCED)
def test_referenced_file_exists(path: str) -> None:
    """Point only at files that really exist.

    The template sends a contributor to a dozen other files by name; a
    renamed one would leave them looking for something that is not there.
    """
    assert any((base / path).exists() for base in BASES), path


# ---- The facade of section 5 ----
def test_facade_builds_its_manager_on_its_own_state() -> None:
    """Hand the facade's state to the manager it builds.

    This is the wiring every real top-level class repeats, so the template
    has to get it right.
    """
    example = Example()
    assert example.ExManager.state is example.state


def test_facade_delegates_to_the_manager() -> None:
    """Forward the call to the manager and return what it returns."""
    example = Example()
    example.state.values = [1.0, 2.0]
    assert example.rescale(factor=2.0) == [2.0, 4.0]
    assert example.state.values == [2.0, 4.0]


def test_facade_forwards_its_kwargs() -> None:
    """Pass the keywords through to the manager, not only the parameters."""
    example = Example()
    example.rescale(label="through the facade")
    assert example.state.label == "through the facade"


def test_facade_unpacks_the_same_kwargs_as_the_manager() -> None:
    """Annotate the facade with the manager's own TypedDict.

    A facade typed with Any would accept any keyword and let pyright check
    nothing, which is the opposite of what sections 2 and 5 teach.
    """
    hints = typing.get_type_hints(Example.rescale, include_extras=True)
    unpacked = typing.get_args(hints["kwargs"])
    assert unpacked, "the facade does not unpack a TypedDict"
    assert unpacked[0] is ExampleKwargs


def test_facade_docstring_is_copied() -> None:
    """Show the manager's documentation on the facade method.

    The facade method's own docstring is a one-line placeholder, so without
    the copy a user calling through the top-level class would see nothing.
    """
    assert Example.rescale.__doc__ == ExampleManager.rescale.__doc__
    assert Example.rescale.__doc__ != "Rescale method."


def test_facade_reaches_the_state_through_the_mixin() -> None:
    """Give the facade the same properties as the manager."""
    example = Example()
    example.label = "set on the facade"
    assert example.state.label == "set on the facade"


def test_module_is_not_public() -> None:
    """Keep the template out of the public API, as its docstring says."""
    assert "template" not in pp.__all__
    init = (ROOT / "src" / "pyPLUTO" / "__init__.py").read_text(
        encoding="utf-8"
    )
    assert "template" not in init
