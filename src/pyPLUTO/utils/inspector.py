"""Inspect kwargs keys from source code.

Most PyPLUTO methods accept **kwargs, forward part of them to another manager
and read the rest themselves. That is convenient to write and easy to get
wrong to call: a misspelled keyword is simply ignored, so `cmpa="plasma"`
produces a plot with the default colormap and no complaint anywhere.

The decorator in this module, `track_kwargs`, closes that gap. It reads the
*source* of each decorated function to learn which keywords the function
looks at, keeps track of what is left over across the chain of manager calls,
and warns once, at the end of the outermost call, about anything nobody used.

Reading the source rather than the running call is what makes this possible
at all: the keys a function reads are spelled out in it, while at runtime an
unused keyword is indistinguishable from one that was consumed. The cost is
that only literal keys can be found, so a function reading `kwargs[name]`
must declare its keywords through `extra_keys` instead.
"""

from __future__ import annotations

import ast
import contextvars
import functools
import inspect
import textwrap
import warnings
from collections.abc import Callable
from typing import Any, ParamSpec, TypeVar, cast, overload


@functools.cache
def _find_kwargs_keys_from_source(source: str) -> set[str]:
    """Find kwargs keys from source code.

    Works through the Abstract Syntax Tree (AST) to identify keys used in
    `kwargs` dictionary accesses, such as `kwargs['key']`, `kwargs.get('key')`,
    or `kwargs.pop('key')`. The results are returned as a set of strings
    representing the keys found in the source code and cached for performance.

    The text is parsed, never executed, which is both why this is safe to run
    on import and why only literal keys can be found: `kwargs.get(name)` has
    no key to read until the function actually runs.

    Parameters
    ----------
    - source (not optional): str
        The source of one function, already dedented. It is the cache key, so
        two functions with identical text are read once; that is a saving
        rather than a hazard, since the same text always yields the same keys.

    Returns
    -------
    - set[str]
        Every keyword the function reads by a literal name. Empty for a
        function that takes no kwargs, or reads them in a way the scan cannot
        follow.

    Examples
    --------
    - Example #1: a function reading two keywords, one of each form

        >>> source = inspect.getsource(plot)
        >>> _find_kwargs_keys_from_source(source)
        {'cmap', 'title'}

    """
    # Parse the source code into an AST
    tree = ast.parse(source)
    kwargs_keys = set()

    class KwargsVisitor(ast.NodeVisitor):
        """Visitor class to traverse the AST and find keys used in kwargs.

        ast.NodeVisitor walks a tree and, for each node, calls the method
        named after the node type if one exists. Defining visit_Subscript and
        visit_Call is therefore enough to be handed every `kwargs[...]` and
        every `kwargs.get(...)` in the function, wherever they are nested.
        """

        def _get_str_from_slice(self, slice_node: ast.AST) -> str | None:
            """Get string from slice node.

            Parameters
            ----------
            - slice_node (not optional): ast.AST
                Whatever stands between the brackets of a subscript.

            Returns
            -------
            - str | None
                The key when it is a string literal, and None otherwise: a
                number cannot be a keyword, and a variable has no value yet.

            Examples
            --------
            - Example #1: the slice of kwargs["cmap"]

                >>> self._get_str_from_slice(node.slice)
                'cmap'

            """
            if isinstance(slice_node, ast.Constant) and isinstance(
                slice_node.value,
                str,
            ):
                return slice_node.value
            return None

        def visit_Subscript(self, node: ast.Subscript) -> None:
            """Visit Subscript nodes to find kwargs keys.

            Handles the `kwargs["key"]` form. The name being subscripted must
            be `kwargs` itself: `other.kwargs["key"]` is an attribute of
            another object and has nothing to do with this call.

            Parameters
            ----------
            - node (not optional): ast.Subscript
                The subscript node being visited.

            Returns
            -------
            - None

            Examples
            --------
            - Example #1: visiting kwargs["cmap"] records 'cmap'

                >>> KwargsVisitor().visit(tree)

            """
            if isinstance(node.value, ast.Name) and node.value.id == "kwargs":
                key = self._get_str_from_slice(node.slice)
                if key is not None:
                    kwargs_keys.add(key)

            # Keep walking: the subscript may contain further nodes, and
            # skipping generic_visit would stop the traversal here.
            self.generic_visit(node)

        def visit_Compare(self, node: ast.Compare) -> None:
            """Visit Compare nodes to find kwargs keys tested for membership.

            Handles the `"key" in kwargs` form, which a method uses when the
            presence of a keyword is the question and its value is passed on
            untouched. Without this the keyword would be reported as unused
            by the very method that acted on it.

            A comparison can be chained, as in `a < b in kwargs`, so the
            operands are paired with the operators rather than assuming the
            test is the first one.

            Parameters
            ----------
            - node (not optional): ast.Compare
                The comparison node being visited.

            Returns
            -------
            - None

            Examples
            --------
            - Example #1: visiting 'if "colors" in kwargs' records 'colors'

                >>> KwargsVisitor().visit(tree)

            """
            # In a chain, operator i compares operand i with operand i + 1.
            operands = [node.left, *node.comparators]
            for index, op in enumerate(node.ops):
                if not isinstance(op, (ast.In, ast.NotIn)):
                    continue
                key, container = operands[index], operands[index + 1]
                if (
                    isinstance(container, ast.Name)
                    and container.id == "kwargs"
                    and isinstance(key, ast.Constant)
                    and isinstance(key.value, str)
                ):
                    kwargs_keys.add(key.value)
            self.generic_visit(node)

        def visit_Call(self, node: ast.Call) -> None:
            """Visit Call nodes to find kwargs keys.

            Handles the `kwargs.get("key")`, `kwargs.pop("key")` and
            `kwargs.setdefault("key", ...)` forms, which are the dictionary
            methods that name a keyword in their first argument. Anything
            else that reads the whole mapping at once, such as `kwargs.items()`
            or `kwargs.keys()`, names nothing and cannot be scanned; a
            function reading its keywords that way declares them through
            `extra_keys` instead.

            Parameters
            ----------
            - node (not optional): ast.Call
                The call node being visited.

            Returns
            -------
            - None

            Examples
            --------
            - Example #1: visiting kwargs.get("cmap", None) records 'cmap'

                >>> KwargsVisitor().visit(tree)

            """
            # Three things have to hold: the call is on an attribute, the
            # object is the name kwargs, and the first argument is a literal
            # string. The default that may follow it is irrelevant here.
            if (
                isinstance(node.func, ast.Attribute)
                and (
                    isinstance(node.func.value, ast.Name)
                    and node.func.value.id == "kwargs"
                    and node.func.attr in {"get", "pop", "setdefault"}
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
    """Find kwargs keys from source code.

    Wraps the cached scan above with the two steps that need the function
    object rather than its text: fetching the source, and removing the
    indentation it carries.

    Parameters
    ----------
    - func (not optional): Callable
        The function to read. It must have source available, which every
        function defined in the package does.

    Returns
    -------
    - set[str]
        The keywords the function reads by a literal name.

    Examples
    --------
    - Example #1: the keywords read by a manager method

        >>> find_kwargs_keys(PlotManager.plot)

    """
    source = inspect.getsource(func)

    # A method arrives indented inside its class, which is a syntax error on
    # its own; dedenting is what lets it be parsed in isolation.
    source = textwrap.dedent(source)
    return _find_kwargs_keys_from_source(source)


P = ParamSpec("P")
R = TypeVar("R")

# The keywords not yet accounted for by anyone in the current call chain.
# A ContextVar rather than a plain global so that two calls running in
# different threads, or in different async tasks, cannot consume each other's
# keywords; None means no call is currently tracking.
_kwargs_remaining: contextvars.ContextVar[set[str] | None] = (
    contextvars.ContextVar("_kwargs_remaining", default=None)
)


# The two overloads describe the two ways the decorator is written:
# bare, as @track_kwargs, and called, as @track_kwargs(extra_keys={...}).
@overload
def track_kwargs(func: Callable[P, R]) -> Callable[P, R]: ...


@overload
def track_kwargs(
    *,
    extra_keys: set[str] | None = None,
) -> Callable[[Callable[P, R]], Callable[P, R]]: ...


def track_kwargs(
    func: Callable[P, R] | None = None,
    *,
    extra_keys: set[str] | None = None,
) -> Callable[P, R] | Callable[[Callable[P, R]], Callable[P, R]]:
    """Track kwargs keys from source code.

    Wraps a function so that the keywords nobody reads are reported. The
    bookkeeping spans the whole chain of calls rather than one function,
    because a method typically reads two of its keywords and forwards the
    rest to a manager that reads the others: judged on its own, every call in
    that chain would complain about keywords meant for the next one.

    The chain therefore works as follows. A call with `_check` true starts the
    tracking by recording every keyword it was given. Each call, outermost and
    nested alike, removes what it reads from that record. The call that
    started it warns about whatever is left and clears the record. Managers
    calling other managers pass `_check=False` for exactly this reason.

    Parameters
    ----------
    - func: Callable | None, default None
        The function to wrap, when the decorator is used bare. It is None when
        the decorator is called with options, and a decorator is returned
        instead.
    - extra_keys: set[str] | None, default None
        Keywords to treat as read although the source scan cannot see them:
        those read through a computed key, and those forwarded unchanged to
        another library.

    Returns
    -------
    - Callable
        The wrapped function, or the decorator that will wrap it.

    Examples
    --------
    - Example #1: the usual form

        >>> @track_kwargs
        ... def plot(self, _check=True, **kwargs): ...

    - Example #2: declaring keywords the scan cannot find

        >>> @track_kwargs(extra_keys={"left", "right"})
        ... def create_axes(self, _check=True, **kwargs): ...

    """

    def decorator(inner_func: Callable[P, R]) -> Callable[P, R]:
        """Wrap one function, reading its keywords once at decoration time.

        Everything that can be computed from the function itself is computed
        here rather than on every call: the source scan, the signature, and
        the names used in the warning.

        Parameters
        ----------
        - inner_func (not optional): Callable
            The function being decorated.

        Returns
        -------
        - Callable
            The wrapper that replaces it.

        Examples
        --------
        - Example #1: applied by track_kwargs itself

            >>> decorator(plot)

        """
        used_keys = find_kwargs_keys(inner_func)
        if extra_keys:
            used_keys |= extra_keys

        sig = inspect.signature(inner_func)

        # A keyword that names a parameter never reaches **kwargs, so the
        # scan cannot see it; subtracting the parameter names keeps such a
        # call from being reported as unused.
        param_keys = frozenset(sig.parameters.keys())
        func_name = getattr(inner_func, "__name__", repr(inner_func))
        mod_name = getattr(inner_func, "__module__", "<unknown>")

        # The signature shown to users, help() and the type checkers, with
        # the internal flag removed.
        public_params = [
            p for name, p in sig.parameters.items() if name != "_check"
        ]

        # A function that declares _check decides its own default; one that
        # does not is never an outermost call and so never checks.
        _check_default: bool = (
            sig.parameters["_check"].default
            if "_check" in sig.parameters
            else False
        )
        _check_is_explicit = "_check" in sig.parameters

        @functools.wraps(inner_func)
        def wrapper(*args: P.args, **kwargs: P.kwargs) -> R:
            """Run the wrapped function, accounting for its keywords.

            Parameters
            ----------
            - args (not optional): P.args
                Positional arguments, passed straight through.
            - kwargs (not optional): P.kwargs
                Keyword arguments, passed through minus `_check` when the
                function does not declare it.

            Returns
            -------
            - R
                Whatever the wrapped function returns.

            Examples
            --------
            - Example #1: an outermost call that checks its keywords

                >>> Image().plot(x, y, cmap="plasma")

            """
            check = kwargs.get("_check", _check_default)

            # A function that does not declare _check must not receive it:
            # it would land in **kwargs and be reported as unused by the very
            # call it was meant to control.
            if not _check_is_explicit:
                cast("Any", kwargs).pop("_check", None)

            # An outermost call starts the tracking from its own keywords.
            # A nested one leaves the record alone, so the keywords the outer
            # call already accounted for are not judged twice.
            if bool(check):
                _kwargs_remaining.set(set(kwargs))

            # Account for what this function reads, whether it started the
            # tracking or was called from somewhere that did.
            current = _kwargs_remaining.get()
            if current is not None:
                current -= used_keys
                current -= param_keys

            result = inner_func(*args, **kwargs)

            # Only the call that started the tracking reports, and only once
            # everything nested inside it has had its turn.
            if bool(check):
                current = _kwargs_remaining.get()
                if current:
                    warnings.warn(
                        f"Unused kwargs: {current} "
                        f"in function {func_name} "
                        f"of {mod_name}",
                        UserWarning,
                        stacklevel=2,
                    )

                # Clear the record, or the next call would inherit it.
                _kwargs_remaining.set(None)

            return result

        # Replace the signature so that _check, which is internal, does not
        # show up in help() or in the editor completions of a public method.
        cast("Any", wrapper).__signature__ = sig.replace(
            parameters=public_params
        )
        return wrapper

    # Bare use, @track_kwargs, hands the function straight in; the called
    # form, @track_kwargs(extra_keys=...), hands in nothing and gets the
    # decorator back to be applied afterwards.
    if func is not None and callable(func):
        return decorator(func)

    return decorator
