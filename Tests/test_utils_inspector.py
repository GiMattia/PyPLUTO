import warnings

from pyPLUTO.utils.inspector import (
    _find_kwargs_keys_from_source,
    _kwargs_state,
    find_kwargs_keys,
    track_kwargs,
)


def test_find_kwargs_keys_simple():
    def f(**kwargs):
        x = kwargs["a"]
        y = kwargs.get("b", 1)
        z = kwargs.pop("c", None)
        return x, y, z

    keys = find_kwargs_keys(f)
    assert keys == {"a", "b", "c"}


def test_find_kwargs_keys_no_kwargs():
    def f(x, y):
        return x + y

    keys = find_kwargs_keys(f)
    assert keys == set()


def test_track_kwargs_basic_usage():
    @track_kwargs
    def f(a, b, **kwargs):
        return a + b + kwargs.get("c", 0)

    # Normal call with required args and extra kwarg 'c'
    assert f(1, 2, c=3) == 6


def test_track_kwargs_with_extra_keys():
    @track_kwargs(extra_keys={"x", "y"})
    def f(**kwargs):
        return sum(kwargs.get(k, 0) for k in ("a", "b"))

    # 'x' and 'y' keys are ignored due to extra_keys
    result = f(a=1, b=2, x=100, y=200)
    assert result == 3


def test_track_kwargs_check_warns_unused_kwarg():
    @track_kwargs
    def f(**kwargs):
        # only use 'a'
        return kwargs.get("a", 0)

    with warnings.catch_warnings(record=True) as w:
        warnings.simplefilter("always")
        f(a=10, b=20, check=True)

        assert any(
            "Unused kwargs" in str(warn.message) for warn in w
        ), "Expected warning not raised"
        assert any(
            "b" in str(warn.message) for warn in w
        ), "'b' missing from warning message"


def test_track_kwargs_check_no_warning_if_no_unused():
    @track_kwargs
    def f(**kwargs):
        return kwargs.get("a", 0)

    with warnings.catch_warnings(record=True) as w:
        warnings.simplefilter("always")
        f(a=10, check=True)
        # No warnings if no unused kwargs
        assert len(w) == 0


def test_track_kwargs_passes_defaults_and_args():
    @track_kwargs
    def f(a, b=2, **kwargs):
        return a + b + kwargs.get("c", 0)

    assert f(1) == 3
    assert f(1, b=3) == 4
    assert f(1, c=4) == 7


def test_state_cleared_after_warning():
    @track_kwargs
    def f(**kwargs):
        return 1

    with warnings.catch_warnings(record=True) as w:
        warnings.simplefilter("always")
        f(a=1, check=True)
        assert _kwargs_state["remaining"] == set()


def test_find_kwargs_keys_all_cases():
    def f(**kwargs):
        x = kwargs["a"]
        y = kwargs.get("b")
        z = kwargs.pop("c", None)
        return x, y, z

    keys = find_kwargs_keys(f)
    assert keys == {"a", "b", "c"}


def test_track_kwargs_extra_keys_none_and_func_none():
    # Call decorator with extra_keys=None explicitly
    decorator = track_kwargs(extra_keys=None)
    assert callable(decorator)

    @decorator
    def f(**kwargs):
        return kwargs.get("x", 1)

    assert f(x=5) == 5


def test_track_kwargs_state_clearing():
    @track_kwargs
    def f(**kwargs):
        return 0

    with warnings.catch_warnings(record=True) as w:
        warnings.simplefilter("always")
        f(unused_kwarg=42, check=True)
        # State cleared after warning
        assert _kwargs_state["remaining"] == set()


def test_subscript_with_non_string_slice_returns_none_branch():
    source_code = """
def f(**kwargs):
    x = kwargs[123]  # non-string subscript, triggers return None
    return x
"""
    keys = _find_kwargs_keys_from_source(source_code)
    assert keys == set()  # No string keys found, so empty set


def test_subscript_with_string_slice_adds_key():
    source_code = """
def f(**kwargs):
    x = kwargs["mykey"]
    return x
"""
    keys = _find_kwargs_keys_from_source(source_code)
    assert keys == {"mykey"}


def test_unused_kwargs_detection():
    @track_kwargs
    def outer(check=True, **kwargs):
        x = kwargs["x"]
        y = inner(**kwargs)

    @track_kwargs
    def inner(check=False, **kwargs):
        y = kwargs["y"]
        return y

    with warnings.catch_warnings(record=True) as w:
        warnings.simplefilter("always")
        outer(x=1, y=2, z=3)

        # Ensure exactly one warning was raised
        assert len(w) == 1
        assert "Unused kwargs: {'z'}" in str(w[0].message)


def test_wrong_unused_kwargs_detection():
    @track_kwargs
    def outer(check=True, **kwargs):
        x = kwargs.get("x", 0)
        y = inner(**kwargs)

    @track_kwargs
    def inner(check=True, **kwargs):
        y = kwargs.get("y", 0)
        return y

    with warnings.catch_warnings(record=True) as w:
        warnings.simplefilter("always")
        outer(y=2, z=3)

        # Ensure exactly one warning was raised
        assert len(w) == 1
        assert "Unused kwargs: {'z'}" in str(w[0].message)
