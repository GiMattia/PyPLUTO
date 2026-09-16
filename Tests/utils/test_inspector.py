"""Test of the utils/inspector.py file.

track_kwargs wraps nearly every public method in PyPLUTO, so a mistake here
misfires on all of them at once: a warning about a keyword that was in fact
used, or silence about one that was not. Both are bad in the same way, since
the whole point of the decorator is to turn a silently ignored keyword into a
message the user can act on.

The tests are grouped by the three pieces that can fail independently:

- reading the keys out of the source, which decides *which* keywords a
  function is considered to use;
- the wrapper itself, which has to leave the function callable and hide the
  internal `_check` flag from its public signature;
- deciding when to warn, which spans a whole chain of manager calls rather
  than one function.

Because the decorator is meant to be reimplemented (the `kwarden` package, in
Rust), what is pinned below is deliberately behaviour rather than
implementation: which forms name a keyword, who warns and when, and what the
shared state looks like afterwards. That makes this file the specification a
port has to satisfy.
"""

import inspect
import warnings
from collections.abc import Callable

import pytest

import pyPLUTO.utils.inspector as inspector_mod
from pyPLUTO.utils.inspector import (
    _find_kwargs_keys_from_source,
    _kwargs_remaining,
    find_kwargs_keys,
    track_kwargs,
)


# ---- Reading the keys out of the source ----
# The scan parses the text of a function and never runs it, so it can only
# find keywords that are written out as literal strings. These tests fix both
# halves of that: the forms it must recognise, and the ones it cannot, which
# are the cases a contributor has to declare with extra_keys instead.
def test_find_kwargs_keys_simple() -> None:
    """Read a function using all three dictionary forms at once.

    This is the shape almost every manager method has, so it stands for the
    common case. A failure means the scan has stopped recognising one of the
    ways a keyword is normally read, and every caller passing that keyword
    would be told it went unused.
    """

    def f(**kwargs: object) -> tuple[object, object, object]:
        x = kwargs["a"]
        y = kwargs.get("b", 1)
        z = kwargs.pop("c", None)
        return x, y, z

    keys = find_kwargs_keys(f)
    assert keys == {"a", "b", "c"}


def test_find_kwargs_keys_no_kwargs() -> None:
    """Read a function that takes no keywords and find none.

    The empty set matters as much as a full one: it is what a method with
    explicit parameters only must produce, and anything else would mean the
    scan is picking up names from somewhere other than this call's kwargs.
    """

    def f(x: int, y: int) -> int:
        return x + y

    keys = find_kwargs_keys(f)
    assert keys == set()


def test_find_kwargs_keys_all_cases() -> None:
    """Read `get` without a default, which is a different call shape.

    `kwargs.get("b")` and `kwargs.get("b", 1)` are distinct nodes in the
    parsed tree, differing by the number of arguments, so both are checked.
    Only the first argument is ever read, whether or not a fallback follows
    it; a scan that required the default would miss half the package.
    """

    def f(**kwargs: object) -> tuple[object, object, object]:
        x = kwargs["a"]
        y = kwargs.get("b")
        z = kwargs.pop("c", None)
        return x, y, z

    keys = find_kwargs_keys(f)
    assert keys == {"a", "b", "c"}


def test_subscript_with_string_slice_adds_key() -> None:
    """Read a key written as a string literal between brackets.

    The tests from here on pass source text directly rather than a function
    object, which keeps them independent of how a real method happens to be
    written and lets them state exactly one form each.
    """
    source_code = """
def f(**kwargs):
    x = kwargs["mykey"]
    return x
"""
    keys = _find_kwargs_keys_from_source(source_code)
    assert keys == {"mykey"}


def test_subscript_with_non_string_slice_returns_none_branch() -> None:
    """Ignore a subscript whose key is a number rather than a string.

    A keyword argument can only have a string name, so an integer subscript
    is some other dictionary-like use and names nothing. Recording it would
    put a key in the used set that no caller can ever pass.
    """
    source_code = """
def f(**kwargs):
    x = kwargs[123]  # non-string subscript, triggers return None
    return x
"""
    keys = _find_kwargs_keys_from_source(source_code)
    assert keys == set()  # No string keys found, so empty set


def test_a_computed_key_is_not_found() -> None:
    """Miss a key that is not written literally, and record that on purpose.

    This is a limitation rather than a bug, and an unavoidable one: the
    source is parsed and never run, so `name` has no value at the time of the
    scan. The test exists so the limitation is visible to whoever reads the
    file next, since the symptom is confusing -- the keyword works, and the
    caller is told it did not.

    A method that has to read its keywords this way declares them with
    extra_keys, which is what the tests further down cover.
    """
    source_code = """
def f(name, **kwargs):
    return kwargs.get(name)
"""
    assert _find_kwargs_keys_from_source(source_code) == set()


def test_another_object_named_kwargs_is_ignored() -> None:
    """Read only this call's kwargs, not an attribute that shares the name.

    `other.kwargs["a"]` is a dictionary belonging to something else, and the
    keyword it names has nothing to do with the call being scanned. Counting
    it would suppress a genuine warning, which is the more dangerous of the
    two failure directions.
    """
    source_code = """
def f(other, **kwargs):
    return other.kwargs["a"]
"""
    assert _find_kwargs_keys_from_source(source_code) == set()


def test_get_pop_and_setdefault_are_read() -> None:
    """Read the key named by each of the three dictionary methods scanned.

    These three name a keyword in their first argument, which is what makes
    them followable. Anything that reads the mapping as a whole does not, and
    is covered by the last test of this group.
    """
    source_code = """
def f(**kwargs):
    kwargs.setdefault("a", 1)
    kwargs.pop("b", None)
    return kwargs.get("c")
"""
    assert _find_kwargs_keys_from_source(source_code) == {"a", "b", "c"}


def test_a_membership_test_names_a_key() -> None:
    """Read the key of a "key in kwargs" test, in both its forms.

    A method writes this when only the presence of a keyword matters and its
    value is forwarded untouched, which is how contour and streamplot handle
    'colors'. Until this form was scanned, passing colors to either of them
    worked and warned that it was unused -- the exact false alarm the
    decorator exists to avoid.
    """
    source_code = """
def f(**kwargs):
    if "colors" in kwargs:
        return True
    return "cmap" not in kwargs
"""
    assert _find_kwargs_keys_from_source(source_code) == {"colors", "cmap"}


def test_a_membership_test_on_another_mapping_is_ignored() -> None:
    """Find nothing when the container tested is not kwargs.

    The counterpart of the test above: comparisons of this shape are made
    against all sorts of dictionaries throughout the package, and none of
    them says anything about the keywords of the call being scanned.
    """
    source_code = """
def f(other, **kwargs):
    return "colors" in other
"""
    assert _find_kwargs_keys_from_source(source_code) == set()


def test_a_chained_comparison_is_read_at_the_right_place() -> None:
    """Read the operand that is really tested against kwargs.

    Python allows comparisons to be chained, and `"a" < "right" in kwargs`
    means `"a" < "right" and "right" in kwargs`: the membership test applies
    to the second operand. Reading the leftmost one instead would record
    'a' here and miss 'right', so a keyword would be both invented and lost.

    No method in the package is written this way, and none should be. The
    test is here because the code that pairs operands with operators exists
    precisely for this case, and would otherwise never be exercised.
    """
    source_code = """
def f(**kwargs):
    return "a" < "right" in kwargs
"""
    assert _find_kwargs_keys_from_source(source_code) == {"right"}


def test_a_method_that_names_no_key_is_not_read() -> None:
    """Find nothing in a call that reads the whole mapping at once.

    `kwargs.items()` names no keyword, so there is nothing to record: the
    keys it yields only exist while the function runs. A method reading its
    keywords this way declares them with extra_keys, exactly as for a
    computed key.
    """
    source_code = """
def f(**kwargs):
    return {k: v for k, v in kwargs.items()}
"""
    assert _find_kwargs_keys_from_source(source_code) == set()


# ---- The wrapper keeps the function usable ----
# Whatever the decorator does about keywords, the function it wraps has to go
# on behaving exactly as written: same arguments, same defaults, same name and
# docstring. These tests are the ones that would catch a wrapper that quietly
# changed the calling convention of every method in the package.
def test_track_kwargs_basic_usage() -> None:
    """Call a wrapped function normally and get the right answer.

    The plainest possible check, and the one that would fail first if the
    wrapper stopped forwarding arguments correctly.
    """

    @track_kwargs
    def f(a: int, b: int, **kwargs: int) -> int:
        return a + b + kwargs.get("c", 0)

    # Normal call with required args and extra kwarg 'c'
    assert f(1, 2, c=3) == 6


def test_track_kwargs_passes_defaults_and_args() -> None:
    """Call a wrapped function three ways and get the declared defaults.

    The three calls cover a default taken, the same parameter given by
    keyword, and a keyword that goes to **kwargs instead. A wrapper that
    rebuilt the arguments rather than passing them straight through would
    break one of the three while leaving the others working.
    """

    @track_kwargs
    def f(a: int, b: int = 2, **kwargs: int) -> int:
        return a + b + kwargs.get("c", 0)

    assert f(1) == 3
    assert f(1, b=3) == 4
    assert f(1, c=4) == 7


def test_signature_hides_check() -> None:
    """Inspect a wrapped function and find _check gone from its signature.

    `_check` is internal: it tells a call whether it is the outermost one,
    and a user has no reason to see it in `help()` or in editor completions.
    The wrapper therefore publishes a signature with that parameter removed
    while still accepting it.

    This is load-bearing beyond cosmetics. The delegation tests of Load,
    Image and LoadPart bind arguments by name against these signatures, so
    a `_check` left in would make them pass an internal flag as if it were
    user data.
    """

    @track_kwargs
    def f(a: int, _check: bool = True, **kwargs: object) -> int:
        return a

    names = list(inspect.signature(f).parameters)
    assert names == ["a", "kwargs"]


def test_wrapper_keeps_the_identity_of_the_function() -> None:
    """Check the wrapped function still reports its own name and docstring.

    This is what `functools.wraps` is for, and it matters here because the
    facades copy a manager's docstring onto their own method: a wrapper that
    replaced `__doc__` with its own would leave every public method of Image
    and Load documented as an internal wrapper.
    """

    @track_kwargs
    def f(**kwargs: object) -> int:
        """Say something worth keeping."""
        return 1

    assert f.__name__ == "f"
    assert f.__doc__ == "Say something worth keeping."


def test_implicit_check_is_not_passed_on() -> None:
    """Call with _check a function that does not declare it, and never see it.

    The dictionary `seen` records what actually arrived inside the function.
    `_check` must not be in it: a function that does not declare the flag
    would receive it in **kwargs, and would then report it as an unused
    keyword -- the flag controlling the check being flagged by the check.
    """
    seen: dict[str, object] = {}

    @track_kwargs
    def f(**kwargs: int) -> int:
        seen.update(kwargs)
        return kwargs.get("a", 0)

    f(_check=True, a=1)
    assert seen == {"a": 1}


def test_explicit_check_is_passed_on() -> None:
    """Call with _check a function that declares it, and see it arrive.

    The mirror image of the test above. A manager that declares `_check`
    does so in order to forward it to the managers it calls, so swallowing
    it here would break the chain: every nested call would fall back to its
    own default and start checking on its own.
    """
    seen: dict[str, object] = {}

    @track_kwargs
    def f(_check: bool = True, **kwargs: int) -> int:
        seen["_check"] = _check
        seen.update(kwargs)
        return kwargs.get("a", 0)

    f(_check=True, a=1)
    assert seen == {"_check": True, "a": 1}


# ---- Deciding when to warn ----
# The decorator warns about keywords nobody read. These tests fix when that
# happens and when it must not: a false alarm trains users to ignore the
# warning, and a missed one lets a typo through silently, which is the
# situation the decorator was written to end.
def test_track_kwargs_check_warns_unused_kwarg() -> None:
    """Pass one keyword the function reads and one it does not, and warn.

    'a' is read and 'b' is not, so only 'b' may be named. The second
    assertion checks the message says which keyword was the problem: a
    warning that only said "some keyword was unused" would leave the user
    hunting through their own call.
    """

    @track_kwargs
    def f(**kwargs: int) -> int:
        # only use 'a'
        return kwargs.get("a", 0)

    with pytest.warns(UserWarning, match="Unused kwargs") as record:
        f(a=10, b=20, _check=True)

    assert "b" in str(record[0].message), "'b' missing from warning message"


def test_track_kwargs_check_no_warning_if_no_unused() -> None:
    """Pass only keywords the function reads, and get no warning at all.

    `simplefilter("error")` turns any warning into an exception, which is how
    a test asserts that nothing was raised: with the default filter a stray
    warning would simply be printed and the test would pass regardless.
    """

    @track_kwargs
    def f(**kwargs: int) -> int:
        return kwargs.get("a", 0)

    with warnings.catch_warnings():
        warnings.simplefilter("error")
        # No warnings if no unused kwargs
        assert f(a=10, _check=True) == 10


def test_no_warning_without_check() -> None:
    """Pass two unread keywords with the check off, and stay silent.

    A function that does not declare `_check` is never an outermost call, so
    it never judges anything: it may well have been handed keywords meant
    for the manager it forwards to. Only the call that saw the complete set
    is allowed to complain, which is the whole idea of the chain.
    """

    @track_kwargs
    def f(**kwargs: object) -> int:
        return 0

    with warnings.catch_warnings():
        warnings.simplefilter("error")
        assert f(unused=1, alsounused=2) == 0


def test_explicit_check_false_is_silent() -> None:
    """Turn the check off at the call and silence a function that would warn.

    Unlike the test above, this function declares `_check=True` and so would
    complain on its own; the silence has to be caused by the argument rather
    than by a default that was already off. That is exactly the call a
    manager makes to another manager, and the reason `_check=False` appears
    throughout the package.
    """

    @track_kwargs
    def f(_check: bool = True, **kwargs: int) -> int:
        return 0

    with warnings.catch_warnings():
        warnings.simplefilter("error")
        assert f(_check=False, unused=1) == 0


def test_a_parameter_name_is_not_unused() -> None:
    """Pass a keyword that names a parameter, and get no warning.

    `a` is a real parameter, so it is bound there and never reaches
    **kwargs; the source scan looks only at kwargs accesses and therefore
    cannot see it. Subtracting the parameter names is what keeps an ordinary
    keyword call from being reported as a mistake.
    """

    @track_kwargs
    def f(a: int = 0, **kwargs: object) -> int:
        return a

    with warnings.catch_warnings():
        warnings.simplefilter("error")
        assert f(a=1, _check=True) == 1


def test_warning_names_the_function_and_its_module() -> None:
    """Read the warning message and find where the keyword was refused.

    Most keywords are valid somewhere in PyPLUTO, so "unused" is only useful
    together with the place that considered it unused: `cmap` is fine for
    `display` and meaningless for `legend`. The module is checked through
    `__name__`, which is this test module, since that is where the decorated
    function was defined.
    """

    @track_kwargs
    def f(**kwargs: object) -> int:
        return 0

    with pytest.warns(UserWarning, match="nowhere") as record:
        f(nowhere=1, _check=True)

    message = str(record[0].message)
    assert "in function f" in message
    assert __name__ in message


def test_track_kwargs_with_extra_keys() -> None:
    """Pass keywords the source never mentions, declared through extra_keys.

    The function reads 'a' and 'b' through a computed key, so the scan finds
    nothing at all; 'x' and 'y' are declared instead. The returned value
    shows the computed reads did happen, and the absence of a complaint
    shows the declaration was honoured.
    """

    @track_kwargs(extra_keys={"x", "y"})
    def f(**kwargs: int) -> int:
        return sum(kwargs.get(k, 0) for k in ("a", "b"))

    # 'x' and 'y' keys are ignored due to extra_keys
    result = f(a=1, b=2, x=100, y=200)
    assert result == 3


def test_extra_keys_are_not_warned_about() -> None:
    """Pass a declared keyword to a function that reads nothing, and stay quiet.

    The sharper version of the test above: here the function body mentions no
    keyword whatsoever, so the silence can only come from the declaration.
    This is the case of a keyword forwarded straight into matplotlib.
    """

    @track_kwargs(extra_keys={"x"})
    def f(**kwargs: object) -> int:
        return 0

    with warnings.catch_warnings():
        warnings.simplefilter("error")
        assert f(x=1, _check=True) == 0


def test_track_kwargs_extra_keys_none_and_func_none() -> None:
    """Apply the decorator in its called form with nothing to configure.

    `track_kwargs` is written to work both bare and called, which are two
    different code paths: bare, it receives the function; called, it receives
    the options and must hand back a decorator to be applied afterwards. This
    takes the second path with the options empty, the awkward middle case.
    """
    # Call decorator with extra_keys=None explicitly
    decorator = track_kwargs(extra_keys=None)
    assert callable(decorator)

    @decorator
    def f(**kwargs: int) -> int:
        return kwargs.get("x", 1)

    assert f(x=5) == 5


# ---- Nested calls ----
# A real call is a chain: a facade method calls a manager, which calls other
# managers, all sharing one set of keywords. Each reads a few and forwards the
# rest, so no single call can judge them -- only the outermost one, and only
# after everything inside it has had its turn.
def test_unused_kwargs_detection() -> None:
    """Run a two-call chain and get exactly one warning, naming one keyword.

    The outer call reads 'x', the inner one reads 'y', and nobody reads 'z'.
    Judged separately, each call would complain about the other's keyword and
    the user would get two wrong warnings instead of one right one.

    `len(record) == 1` is therefore as important as the message: it is what
    says the inner call stayed quiet. The inner call is given `_check=False`
    explicitly, which is how managers call each other in the package.
    """

    @track_kwargs
    def outer(_check: bool = True, **kwargs: int) -> None:
        kwargs["x"]
        inner(_check=False, **kwargs)

    @track_kwargs
    def inner(_check: bool = False, **kwargs: int) -> int:
        y = kwargs["y"]
        return y

    with pytest.warns(UserWarning, match="Unused kwargs") as record:
        outer(x=1, y=2, z=3)

    # Ensure exactly one warning was raised
    assert len(record) == 1
    assert "Unused kwargs: {'z'}" in str(record[0].message)


def test_wrong_unused_kwargs_detection() -> None:
    """Run a chain where the inner call also checks, and still warn once.

    This is the mistake the name refers to: the inner call is given
    `_check=True`, which restarts the tracking from the keywords it was
    handed. The outer call had already accounted for 'x', so a naive
    implementation would report it a second time, or report 'z' twice.

    Exactly one warning naming only 'z' is what says the restart did not
    lose or duplicate the bookkeeping.
    """

    @track_kwargs
    def outer(_check: bool = True, **kwargs: int) -> None:
        kwargs.get("x", 0)
        inner(_check=True, **kwargs)

    @track_kwargs
    def inner(_check: bool = True, **kwargs: int) -> int:
        y = kwargs.get("y", 0)
        return y

    with pytest.warns(UserWarning, match="Unused kwargs") as record:
        outer(y=2, z=3)

    # Ensure exactly one warning was raised
    assert len(record) == 1
    assert "Unused kwargs: {'z'}" in str(record[0].message)


# ---- The tracking state ----
# The set of keywords still unaccounted for lives in one ContextVar shared by
# every decorated function in the process. That is what lets a chain of calls
# cooperate, and it is also what makes leftovers dangerous: anything left
# behind is inherited by the next call, which never saw those keywords.
def test_state_cleared_after_warning() -> None:
    """Warn once, then find the shared state empty again.

    Reading `_kwargs_remaining` directly is unusual for a test, but there is
    no other way to see this: a leftover set changes nothing about the call
    that produced it and only misfires later, somewhere else.
    """

    @track_kwargs
    def f(**kwargs: object) -> int:
        return 1

    with pytest.warns(UserWarning, match="Unused kwargs"):
        f(a=1, _check=True)
    assert _kwargs_remaining.get() is None


def test_track_kwargs_state_clearing() -> None:
    """Warn once, then make a second clean call and get no second warning.

    Where the test above inspects the state, this one demonstrates the
    consequence: the second call passes no keywords at all, so if the first
    call's leftovers survived, it would be blamed for 'unused_kwarg', which
    it never saw. That is the failure a user would actually meet -- a warning
    about a keyword absent from the call in front of them.
    """

    @track_kwargs
    def f(**kwargs: object) -> int:
        return 0

    with pytest.warns(UserWarning, match="Unused kwargs"):
        f(unused_kwarg=42, _check=True)
    # ContextVar is reset to None after the outer call completes
    assert _kwargs_remaining.get() is None

    # A second call must be judged on its own keywords only.
    with warnings.catch_warnings():
        warnings.simplefilter("error")
        assert f(_check=True) == 0


def test_state_is_cleared_even_without_a_warning() -> None:
    """Make a call with nothing to report, and still find the state empty.

    Clearing is easy to put inside the branch that warns, where it would be
    reached only when something went wrong. A clean call has to clear up
    after itself too, or the very next call inherits its keywords.
    """

    @track_kwargs
    def f(**kwargs: int) -> int:
        return kwargs.get("a", 0)

    f(a=1, _check=True)
    assert _kwargs_remaining.get() is None


# ---- The source cache ----
# Reading a function's source and parsing it is far too slow to do on every
# call, so it happens once per distinct source text and the result is cached.
def test_identical_sources_share_one_result() -> None:
    """Scan the same text twice and get back the very same set object.

    The cache is keyed on the source text, so two functions written
    identically share one result. `is` rather than `==` is what proves the
    second call was served from the cache rather than parsed again.

    Sharing is safe because the same text always yields the same keys; it
    would not be if the scan depended on anything outside the text.
    """
    source = 'def f(**kwargs):\n    return kwargs.get("a")\n'
    first = _find_kwargs_keys_from_source(source)
    second = _find_kwargs_keys_from_source(source)
    assert first == {"a"}
    assert second is first


def test_indented_source_is_read() -> None:
    """Scan a method, whose source arrives indented inside its class.

    `inspect.getsource` returns a method still carrying the indentation it
    has in the class body, and that text is not a valid module on its own:
    parsing it directly raises IndentationError. Dedenting first is what
    makes the decorator usable on methods, which is to say on essentially
    every decorated function in PyPLUTO.
    """

    class Holder:
        """Hold a decorated method, to be read at class indentation."""

        def method(self, **kwargs: object) -> object:
            """Read one keyword."""
            return kwargs.get("indented")

    assert find_kwargs_keys(Holder.method) == {"indented"}


def test_every_public_name_is_tested() -> None:
    """Compare what the module offers with what this file covers.

    A completeness guard rather than a behaviour test: it fails when a new
    public helper appears in inspector.py and nothing here exercises it, so
    the module that wraps every method in PyPLUTO cannot quietly grow an
    untested corner.

    The two assertions are kept apart so the message says which way the
    tables drifted: something new that is untested, or something tested that
    no longer exists.
    """

    # Only what the module defines itself: the typing names it imports are
    # callable too, and belong to their own modules.
    public: set[str] = {
        name
        for name, value in vars(inspector_mod).items()
        if not name.startswith("_")
        and isinstance(value, Callable)
        and getattr(value, "__module__", None) == inspector_mod.__name__
    }
    tested = {"find_kwargs_keys", "track_kwargs"}
    missing, stale = public - tested, tested - public
    assert not missing, f"not tested in this file: {sorted(missing)}"
    assert not stale, f"tested but no longer public: {sorted(stale)}"
