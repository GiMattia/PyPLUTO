# inspect_kwargs.py
import ast
import functools
import inspect
import textwrap
import warnings
from collections.abc import Callable
from typing import Any, TypeVar, overload


@functools.cache
def _find_kwargs_keys_from_source(source: str) -> set[str]:
    """Internal function to find kwargs keys from source code. Works through the
    Abstract Syntax Tree (AST) to identify keys used in `kwargs` dictionary
    accesses, such as `kwargs['key']`, `kwargs.get('key')`, or
    `kwargs.pop('key')`. The results are returned as a set of strings
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


def find_kwargs_keys(func: Callable[..., Any]) -> set[str]:
    """Find kwargs keys from source code."""
    source = inspect.getsource(func)
    source = textwrap.dedent(source)
    return _find_kwargs_keys_from_source(source)


def find_kwargs_keys_recursive(func_source: str, class_source: str) -> set[str]:
    """Given the source of a method and its class,
    return the set of all kwargs keys used in that method and helper methods
    (recursively) where **kwargs is passed.
    """
    kwargs_keys = set()
    seen = set()

    class_node = None
    class_tree = ast.parse(class_source)
    for node in class_tree.body:
        if isinstance(node, ast.ClassDef):
            class_node = node
            break
    if not class_node:
        return _find_kwargs_keys_from_source(func_source)

    def _recurse(func_node):
        func_code = ast.get_source_segment(class_source, func_node)
        direct_keys = _find_kwargs_keys_from_source(func_code)
        all_keys = set(direct_keys)
        seen.add(func_node.name)
        # Search for calls to self.method(..., **kwargs)
        for stmt in ast.walk(func_node):
            if isinstance(stmt, ast.Call):
                # Only look for self.<something>
                if (
                    isinstance(stmt.func, ast.Attribute)
                    and isinstance(stmt.func.value, ast.Name)
                    and stmt.func.value.id == "self"
                ):
                    method_name = stmt.func.attr
                    # Look for **kwargs in args
                    if any(
                        isinstance(arg, ast.Starred)
                        and isinstance(arg.value, ast.Name)
                        and arg.value.id == "kwargs"
                        for arg in stmt.args
                    ):
                        # Recurse if method exists and not seen yet
                        for meth in class_node.body:
                            if (
                                isinstance(meth, ast.FunctionDef)
                                and meth.name == method_name
                                and method_name not in seen
                            ):
                                all_keys |= _recurse(meth)
        return all_keys

    # Get function node from class AST
    for node in class_node.body:
        if isinstance(node, ast.FunctionDef):
            func_code = ast.get_source_segment(class_source, node)
            if func_code and func_code.strip() == func_source.strip():
                return _recurse(node)
    # Fallback if not found as AST node
    return _find_kwargs_keys_from_source(func_source)


# Shared state for tracking across nested calls
F = TypeVar("F", bound=Callable[..., Any])
_kwargs_state: dict[str, Any] = {"remaining": set()}


@overload
def track_kwargs(func: F) -> F:
    """Decorator to track kwargs keys from source code."""


@overload
def track_kwargs(*, extra_keys: set[str] | None = None) -> Callable[[F], F]:
    """Return a decorator to track kwargs keys from source code."""


def track_kwargs(
    func: Callable[..., Any] | None = None,
    *,
    extra_keys: set[str] | None = None,
) -> Callable[..., Any]:
    """Decorator to track kwargs keys from source code."""

    def decorator(inner_func: Callable[..., Any]) -> Callable[..., Any]:
        """Decorator to track kwargs keys from source code."""
        used_keys = find_kwargs_keys(inner_func)
        if extra_keys:
            used_keys |= extra_keys

        @functools.wraps(inner_func)
        def wrapper(*args: Any, **kwargs: Any) -> Any:
            """Wrapper to track kwargs keys from source code."""
            sig = inspect.signature(inner_func)
            bound = sig.bind(*args, **kwargs)
            bound.apply_defaults()
            check = bound.arguments.get("check", False)

            if not check and "check" in kwargs:
                check = kwargs.pop("check", False)
            if check:
                _kwargs_state["remaining"] = set(kwargs)

            _kwargs_state["remaining"] -= used_keys
            _kwargs_state["remaining"] -= set(sig.parameters.keys())

            result = inner_func(*args, **kwargs)

            if check and _kwargs_state.get("remaining"):
                warnings.warn(
                    f"Unused kwargs: {_kwargs_state['remaining']} "
                    f"in function {inner_func.__name__} "
                    f"of {inner_func.__module__}",
                    UserWarning,
                )
                _kwargs_state["remaining"].clear()

            return result

        return wrapper

    if func is not None and callable(func):
        return decorator(func)

    return decorator
