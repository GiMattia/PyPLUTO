# inspect_kwargs.py
import ast
import functools
import inspect
import textwrap
import warnings
from collections.abc import Callable
from typing import Any


@functools.cache
def _find_kwargs_keys_from_source(source: str) -> set[str]:
    tree = ast.parse(source)
    kwargs_keys = set()

    class KwargsVisitor(ast.NodeVisitor):
        def visit_Subscript(self, node):
            if isinstance(node.value, ast.Name) and node.value.id == "kwargs":
                if isinstance(node.slice, ast.Constant) and isinstance(
                    node.slice.value, str
                ):
                    kwargs_keys.add(node.slice.value)
            self.generic_visit(node)

        def visit_Call(self, node):
            if isinstance(node.func, ast.Attribute):
                if (
                    isinstance(node.func.value, ast.Name)
                    and node.func.value.id == "kwargs"
                    and node.func.attr in {"get", "pop"}
                ):
                    if (
                        node.args
                        and isinstance(node.args[0], ast.Constant)
                        and isinstance(node.args[0].value, str)
                    ):
                        kwargs_keys.add(node.args[0].value)
            self.generic_visit(node)

    KwargsVisitor().visit(tree)
    return kwargs_keys


def find_kwargs_keys(func):
    source = inspect.getsource(func)
    source = textwrap.dedent(source)
    return _find_kwargs_keys_from_source(source)


# Shared state for tracking across nested calls
_kwargs_state: dict = {"remaining": set()}


def track_kwargs(func: Callable[..., Any]) -> Callable[..., Any]:
    used_keys = find_kwargs_keys(func)

    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        sig = inspect.signature(func)
        bound = sig.bind(*args, **kwargs)
        bound.apply_defaults()
        check = bound.arguments.get("check", False)

        if check:
            _kwargs_state["remaining"] = set(kwargs)

        _kwargs_state["remaining"] -= used_keys
        _kwargs_state["remaining"] -= set(sig.parameters.keys())

        result = func(*args, **kwargs)

        if check:
            if _kwargs_state["remaining"]:
                warn = (
                    f"Unused kwargs: {_kwargs_state['remaining']} "
                    f"in function {func.__name__} "
                    f"of class {func.__module__}\n"
                )
                warnings.warn(warn, UserWarning)
            _kwargs_state.clear()

        return result

    return wrapper
