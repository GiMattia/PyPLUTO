"""Inspect kwargs keys from source code."""

from __future__ import annotations

import ast
import functools
import inspect
import textwrap
import warnings
from collections.abc import Callable
from typing import Any, ParamSpec, TypeVar, overload


@functools.cache
def _find_kwargs_keys_from_source(source: str) -> set[str]:
    """Find kwargs keys from source code.

    Works through the Abstract Syntax Tree (AST) to identify keys used in
    `kwargs` dictionary accesses, such as `kwargs['key']`, `kwargs.get('key')`,
    or `kwargs.pop('key')`. The results are returned as a set of strings
    representing the keys found in the source code and cached for performance.
    """
    # Parse the source code into an AST
    tree = ast.parse(source)
    kwargs_keys = set()

    class KwargsVisitor(ast.NodeVisitor):
        """Visitor class to traverse the AST and find keys used in kwargs."""

        def _get_str_from_slice(self, slice_node: ast.AST) -> str | None:
            """Get string from slice node."""
            if isinstance(slice_node, ast.Constant) and isinstance(
                slice_node.value, str
            ):
                return slice_node.value
            return None

        def visit_Subscript(self, node: ast.Subscript) -> None:
            """Visit Subscript nodes to find kwargs keys."""
            if isinstance(node.value, ast.Name) and node.value.id == "kwargs":
                key = self._get_str_from_slice(node.slice)
                if key is not None:
                    kwargs_keys.add(key)
            self.generic_visit(node)

        def visit_Call(self, node: ast.Call) -> None:
            """Visit Call nodes to find kwargs keys."""
            if (
                isinstance(node.func, ast.Attribute)
                and (
                    isinstance(node.func.value, ast.Name)
                    and node.func.value.id == "kwargs"
                    and node.func.attr in {"get", "pop"}
                )
                and (
                    node.args
                    and isinstance(node.args[0], ast.Constant)
                    and isinstance(node.args[0].value, str)
                )
            ):
                kwargs_keys.add(node.args[0].value)
            self.generic_visit(node)

    KwargsVisitor().visit(tree)
    return kwargs_keys


def find_kwargs_keys(func: Callable[..., Any]) -> set[str]:
    """Find kwargs keys from source code."""
    source = inspect.getsource(func)
    source = textwrap.dedent(source)
    return _find_kwargs_keys_from_source(source)


# Shared state for tracking across nested calls
P = ParamSpec("P")
R = TypeVar("R")
_kwargs_state: dict[str, set[str]] = {"remaining": set()}


@overload
def track_kwargs(func: Callable[P, R]) -> Callable[P, R]: ...


@overload
def track_kwargs(
    *, extra_keys: set[str] | None = None
) -> Callable[[Callable[P, R]], Callable[P, R]]: ...


def track_kwargs(
    func: Callable[P, R] | None = None,
    *,
    extra_keys: set[str] | None = None,
) -> Callable[P, R] | Callable[[Callable[P, R]], Callable[P, R]]:
    """Track kwargs keys from source code."""

    def decorator(inner_func: Callable[P, R]) -> Callable[P, R]:
        """Track kwargs keys from source code."""
        used_keys = find_kwargs_keys(inner_func)
        if extra_keys:
            used_keys |= extra_keys

        @functools.wraps(inner_func)
        def wrapper(*args: P.args, **kwargs: P.kwargs) -> R:
            """Track kwargs keys from source code."""
            sig = inspect.signature(inner_func)
            bound = sig.bind(*args, **kwargs)
            bound.apply_defaults()
            check = bound.arguments.get("check", False)

            # Be robust to "check" passed via kwargs even if not bound.
            if not bool(check) and "check" in kwargs:
                check = kwargs.pop("check", False)

            if bool(check):
                _kwargs_state["remaining"] = set(kwargs)

            _kwargs_state["remaining"] -= used_keys
            _kwargs_state["remaining"] -= set(sig.parameters.keys())

            result = inner_func(*args, **kwargs)

            func_name = getattr(inner_func, "__name__", repr(inner_func))
            mod_name = getattr(inner_func, "__module__", "<unknown>")

            remaining = _kwargs_state.get("remaining", set())
            if bool(check) and remaining:
                warnings.warn(
                    f"Unused kwargs: {remaining} "
                    f"in function {func_name} "
                    f"of {mod_name}",
                    UserWarning,
                    stacklevel=2,
                )
                remaining.clear()

            return result

        return wrapper

    if func is not None and callable(func):
        return decorator(func)

    return decorator
