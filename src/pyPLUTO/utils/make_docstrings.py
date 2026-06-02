"""Audit public-API docstrings in the pyPLUTO source tree.

Walks every .py file under src/pyPLUTO/ with the AST, collects all public
classes, functions and methods (including ``__init__``), and reports the
status of each docstring.

Also detects **kwargs forwarding and resolves the complete set of kwarg keys
reachable via the transitive call chain.  A method's full kwargs contract
includes everything it accesses directly PLUS everything accepted by callees
it forwards ``**kwargs`` to (recursively).

Three access patterns are detected:
  - ``kwargs["key"]``          subscript with string literal
  - ``kwargs.get("key", ...)`` / ``kwargs.pop("key", ...)``
  - ``"key" in kwargs``        membership test

Statuses
--------
MISSING   : no docstring at all
EMPTY     : docstring exists but is blank
ONE-LINER : single-line docstring (may need expanding)
OK        : multi-line docstring present

Usage
-----
Run from the repo root::

    python src/pyPLUTO/utils/make_docstrings.py
    python src/pyPLUTO/utils/make_docstrings.py --missing
    python src/pyPLUTO/utils/make_docstrings.py --kwargs
    python src/pyPLUTO/utils/make_docstrings.py --json
    python src/pyPLUTO/utils/make_docstrings.py --json --missing > report.json
"""

from __future__ import annotations

import ast
import json
import sys
from dataclasses import asdict, dataclass, field
from pathlib import Path

# ---------------------------------------------------------------------------
# Configuration
# ---------------------------------------------------------------------------

PACKAGE_ROOT = Path(__file__).resolve().parents[1]  # src/pyPLUTO/

_INCLUDE_DUNDER = {"__init__"}
_SKIP_DIRS = {"__pycache__", ".git", "build", "dist"}


# ---------------------------------------------------------------------------
# Data model
# ---------------------------------------------------------------------------


@dataclass
class DocItem:
    """One audited entry."""

    file: str
    module: str
    qualname: str
    kind: str  # "class" | "function" | "method"
    lineno: int
    status: str  # "MISSING" | "EMPTY" | "ONE-LINER" | "OK"
    docstring: str | None
    direct_kwargs_keys: list[str] = field(default_factory=list)
    forwards_kwargs_to: list[str] = field(default_factory=list)

    @property
    def full_name(self) -> str:
        """Fully qualified dotted name."""
        return f"{self.module}.{self.qualname}"


def _classify(raw: str | None) -> str:
    """Return a docstring status label for the given raw docstring text.

    Parameters
    ----------
    - raw: str | None
        The raw docstring extracted from the AST node, or None if absent.

    Returns
    -------
    - str: one of ``"MISSING"``, ``"EMPTY"``, ``"ONE-LINER"``, or ``"OK"``.
    """
    if raw is None:
        return "MISSING"
    stripped = raw.strip()
    if not stripped:
        return "EMPTY"
    if "\n" not in stripped:
        return "ONE-LINER"
    return "OK"


# ---------------------------------------------------------------------------
# kwargs key detector  (pure AST, no imports required)
# ---------------------------------------------------------------------------


def _find_direct_kwargs_keys(
    node: ast.FunctionDef | ast.AsyncFunctionDef,
) -> list[str]:
    """Return kwargs string keys accessed directly in *node*'s body.

    Detects three patterns:
      - ``kwargs["key"]``
      - ``kwargs.get("key", ...)`` / ``kwargs.pop("key", ...)``
      - ``"key" in kwargs``
    """
    keys: set[str] = set()

    class _Finder(ast.NodeVisitor):
        def visit_Subscript(self, n: ast.Subscript) -> None:
            if isinstance(n.value, ast.Name) and n.value.id == "kwargs":
                if isinstance(n.slice, ast.Constant) and isinstance(
                    n.slice.value, str
                ):
                    keys.add(n.slice.value)
            self.generic_visit(n)

        def visit_Call(self, n: ast.Call) -> None:
            if (
                isinstance(n.func, ast.Attribute)
                and isinstance(n.func.value, ast.Name)
                and n.func.value.id == "kwargs"
                and n.func.attr in {"get", "pop"}
                and n.args
                and isinstance(n.args[0], ast.Constant)
                and isinstance(n.args[0].value, str)
            ):
                keys.add(n.args[0].value)
            self.generic_visit(n)

        def visit_Compare(self, n: ast.Compare) -> None:
            # "key" in kwargs
            for op, comp in zip(n.ops, n.comparators):
                if (
                    isinstance(op, ast.In)
                    and isinstance(comp, ast.Name)
                    and comp.id == "kwargs"
                    and isinstance(n.left, ast.Constant)
                    and isinstance(n.left.value, str)
                ):
                    keys.add(n.left.value)
            self.generic_visit(n)

    _Finder().visit(node)
    return sorted(keys)


# ---------------------------------------------------------------------------
# **kwargs forwarding detector
# ---------------------------------------------------------------------------


def _find_kwargs_forwards(
    node: ast.FunctionDef | ast.AsyncFunctionDef,
) -> list[str]:
    """Return human-readable names of calls that receive ``**kwargs``."""
    forwards: list[str] = []

    class _ForwardFinder(ast.NodeVisitor):
        def visit_Call(self, call: ast.Call) -> None:
            has_star = any(
                isinstance(kw, ast.keyword)
                and kw.arg is None
                and isinstance(kw.value, ast.Name)
                and kw.value.id == "kwargs"
                for kw in call.keywords
            )
            if has_star:
                forwards.append(_call_name(call.func))
            self.generic_visit(call)

    _ForwardFinder().visit(node)
    return forwards


def _call_name(func_node: ast.expr) -> str:
    """Return a human-readable dotted name for an AST call-target node.

    Handles simple ``Name`` nodes (e.g. ``foo``) and ``Attribute`` chains
    (e.g. ``self.bar.baz``).  Anything more complex (subscripts, calls, …)
    returns the placeholder ``"<expr>"``.

    Parameters
    ----------
    - func_node: ast.expr
        The ``func`` field of an ``ast.Call`` node.

    Returns
    -------
    - str: dotted name string, or ``"<expr>"`` if not resolvable.
    """
    if isinstance(func_node, ast.Name):
        return func_node.id
    if isinstance(func_node, ast.Attribute):
        parts: list[str] = []
        node: ast.expr = func_node
        while isinstance(node, ast.Attribute):
            parts.append(node.attr)
            node = node.value
        if isinstance(node, ast.Name):
            parts.append(node.id)
        return ".".join(reversed(parts))
    return "<expr>"


# ---------------------------------------------------------------------------
# AST visitor
# ---------------------------------------------------------------------------


class _DocstringVisitor(ast.NodeVisitor):
    """Collect DocItem entries from a single parsed module."""

    def __init__(self, module: str, rel_file: str) -> None:
        """Initialize the visitor with the module name and relative file path.

        Parameters
        ----------
        - module: str
            Dotted module name derived from the file path (e.g. ``pyPLUTO.load``).
        - rel_file: str
            File path relative to the package root, used in reported items.

        Returns
        -------
        - None

        """
        self.module = module
        self.rel_file = rel_file
        self.items: list[DocItem] = []
        self._class_stack: list[str] = []

    def visit_ClassDef(self, node: ast.ClassDef) -> None:
        """Visit a class definition, record its docstring, and recurse into it.

        Private classes (names starting with ``_``) are skipped entirely.
        The class name is pushed onto the stack before visiting its body so
        that nested methods receive the correct qualified name prefix, then
        popped afterwards.

        Parameters
        ----------
        - node: ast.ClassDef
            The class definition AST node to process.
        """
        if node.name.startswith("_"):
            return

        qualname = ".".join([*self._class_stack, node.name])
        raw = ast.get_docstring(node)
        self.items.append(
            DocItem(
                file=self.rel_file,
                module=self.module,
                qualname=qualname,
                kind="class",
                lineno=node.lineno,
                status=_classify(raw),
                docstring=raw,
            )
        )
        self._class_stack.append(node.name)
        self.generic_visit(node)
        self._class_stack.pop()

    def visit_FunctionDef(self, node: ast.FunctionDef) -> None:
        """Dispatch a synchronous function or method node to ``_visit_func``.

        Parameters
        ----------
        - node: ast.FunctionDef
            The synchronous function definition AST node to process.

        Returns
        -------
        - None

        """
        self._visit_func(node)

    def visit_AsyncFunctionDef(self, node: ast.AsyncFunctionDef) -> None:
        """Dispatch an async function or method node to ``_visit_func``.

        Parameters
        ----------
        - node: ast.AsyncFunctionDef
            The async function definition AST node to process.

        Returns
        -------
        - None

        """
        self._visit_func(node)

    def _visit_func(self, node: ast.FunctionDef | ast.AsyncFunctionDef) -> None:
        """Record a DocItem for a function or method node if it is public.

        Private names (prefixed with ``_``) are skipped unless they appear in
        ``_INCLUDE_DUNDER``.  Kwargs keys and forwarding targets are extracted
        from the AST body and stored alongside the docstring status.

        Parameters
        ----------
        - node: ast.FunctionDef | ast.AsyncFunctionDef
            The function or async-function definition AST node to inspect.

        Returns
        -------
        - None

        """
        name = node.name
        if not (not name.startswith("_") or name in _INCLUDE_DUNDER):
            return

        qualname = ".".join([*self._class_stack, name])
        kind = "method" if self._class_stack else "function"
        raw = ast.get_docstring(node)

        has_kwarg = node.args.kwarg is not None
        direct_keys = _find_direct_kwargs_keys(node) if has_kwarg else []
        forwards = _find_kwargs_forwards(node) if has_kwarg else []

        self.items.append(
            DocItem(
                file=self.rel_file,
                module=self.module,
                qualname=qualname,
                kind=kind,
                lineno=node.lineno,
                status=_classify(raw),
                docstring=raw,
                direct_kwargs_keys=direct_keys,
                forwards_kwargs_to=forwards,
            )
        )


# ---------------------------------------------------------------------------
# Transitive kwargs chain resolution via track_kwargs closures
# ---------------------------------------------------------------------------


def _method_key(name: str) -> str:
    """Return the bare method name from a dotted forwarding target."""
    return name.rsplit(".", 1)[-1]


def _build_used_keys_registry() -> dict[str, set[str]]:
    """Walk pyPLUTO and extract used_keys from every track_kwargs wrapper.

    Returns a mapping bare_method_name → used_keys (already includes
    extra_keys because track_kwargs bakes them in at decoration time).
    Falls back to an empty dict if pyPLUTO is not importable.
    """
    registry: dict[str, set[str]] = {}
    try:
        import importlib
        import inspect
        import pkgutil

        import pyPLUTO as _pkg  # noqa: PLC0415

        for _importer, modname, _ispkg in pkgutil.walk_packages(
            path=_pkg.__path__,
            prefix=_pkg.__name__ + ".",
            onerror=lambda _: None,
        ):
            try:
                mod = importlib.import_module(modname)
            except Exception:
                continue

            for _cls_name, cls in inspect.getmembers(mod, inspect.isclass):
                for method_name, obj in inspect.getmembers(cls):
                    keys = _extract_used_keys(obj)
                    if keys is not None:
                        registry.setdefault(method_name, set()).update(keys)

    except Exception:
        pass

    return registry


def _extract_used_keys(obj: object) -> set[str] | None:
    """Return used_keys from a track_kwargs wrapper closure, or None."""
    func = obj.fget if isinstance(obj, property) else obj
    if not callable(func):
        return None
    closure = getattr(func, "__closure__", None)
    if not closure:
        return None
    code = getattr(func, "__code__", None)
    if code is None:
        return None
    for var_name, cell in zip(code.co_freevars, closure):
        if var_name == "used_keys":
            try:
                val = cell.cell_contents
                if isinstance(val, set):
                    return val
            except ValueError:
                pass
    return None


def resolve_full_kwargs(
    items: list[DocItem],
    registry: dict[str, set[str]] | None = None,
) -> dict[str, list[str]]:
    """For each item with **kwargs, return the complete sorted list of kwarg
    keys reachable via the full transitive forwarding chain.

    Uses the track_kwargs closure registry (which includes extra_keys) for
    key detection, then follows the **kwargs forwarding graph from the AST.
    Falls back to the pure-AST direct_kwargs_keys if the registry misses a
    method.
    """
    if registry is None:
        registry = _build_used_keys_registry()

    # bare method name → set of keys (from closure or AST fallback)
    def _keys_for(bare_name: str, ast_keys: set[str]) -> set[str]:
        return registry.get(bare_name, None) or ast_keys

    # bare method name → AST-detected direct kwargs keys
    ast_direct: dict[str, set[str]] = {}
    for item in items:
        ast_direct.setdefault(_method_key(item.qualname), set()).update(
            item.direct_kwargs_keys
        )

    # qualname → set of direct forward target bare names
    fwd: dict[str, set[str]] = {
        item.qualname: {_method_key(f) for f in item.forwards_kwargs_to}
        for item in items
        if item.forwards_kwargs_to
    }

    result: dict[str, list[str]] = {}
    for item in items:
        bare = _method_key(item.qualname)
        own_keys = _keys_for(bare, set(item.direct_kwargs_keys))
        if not own_keys and not item.forwards_kwargs_to:
            continue

        all_keys: set[str] = set(own_keys)
        visited: set[str] = set()
        queue: list[str] = list(fwd.get(item.qualname, set()))

        while queue:
            callee = queue.pop()
            if callee in visited:
                continue
            visited.add(callee)
            all_keys |= _keys_for(callee, ast_direct.get(callee, set()))
            # follow callee's own forwards
            for other_item in items:
                if _method_key(other_item.qualname) == callee:
                    for nxt in fwd.get(other_item.qualname, set()):
                        if nxt not in visited:
                            queue.append(nxt)

        if all_keys:
            result[item.qualname] = sorted(all_keys)

    return result


# ---------------------------------------------------------------------------
# File and package walkers
# ---------------------------------------------------------------------------


def _module_name(file_path: Path, root: Path) -> str:
    """Convert a file path inside *root* to a dotted module name."""
    rel = file_path.relative_to(root.parent)
    parts = list(rel.with_suffix("").parts)
    if parts[-1] == "__init__":
        parts = parts[:-1]
    return ".".join(parts)


def audit_file(file_path: Path, root: Path) -> list[DocItem]:
    """Return DocItem list for one Python file."""
    try:
        source = file_path.read_text(encoding="utf-8")
        tree = ast.parse(source, filename=str(file_path))
    except (OSError, SyntaxError):
        return []

    module = _module_name(file_path, root)
    rel_file = str(file_path.relative_to(root.parent))
    visitor = _DocstringVisitor(module, rel_file)
    visitor.visit(tree)
    return visitor.items


def audit_package(root: Path = PACKAGE_ROOT) -> list[DocItem]:
    """Recursively audit all .py files under *root*."""
    items: list[DocItem] = []
    for path in sorted(root.rglob("*.py")):
        if any(skip in path.parts for skip in _SKIP_DIRS):
            continue
        items.extend(audit_file(path, root))
    return items


# ---------------------------------------------------------------------------
# Reporting
# ---------------------------------------------------------------------------

_STATUS_ORDER = {"MISSING": 0, "EMPTY": 1, "ONE-LINER": 2, "OK": 3}
_STATUS_COLOUR = {
    "MISSING": "\033[91m",
    "EMPTY": "\033[91m",
    "ONE-LINER": "\033[93m",
    "OK": "\033[92m",
}
_RESET = "\033[0m"


def _colour(status: str, text: str, use_colour: bool) -> str:
    """Wrap *text* in the ANSI colour code corresponding to *status*.

    Parameters
    ----------
    - status: str
        One of the recognised status labels (``"MISSING"``, ``"EMPTY"``,
        ``"ONE-LINER"``, ``"OK"``).
    - text: str
        The string to colourise.
    - use_colour: bool
        When ``False`` the original *text* is returned unchanged.

    Returns
    -------
    - str: ANSI-coloured string, or the original *text* if colour is disabled.
    """
    if not use_colour:
        return text
    return f"{_STATUS_COLOUR.get(status, '')}{text}{_RESET}"


def print_report(
    items: list[DocItem],
    *,
    missing_only: bool = False,
    kwargs_only: bool = False,
    use_colour: bool = True,
) -> None:
    """Print a human-readable report to stdout."""
    full_kwargs = resolve_full_kwargs(items)

    if missing_only:
        items = [i for i in items if i.status in {"MISSING", "EMPTY"}]
    if kwargs_only:
        items = [i for i in items if i.qualname in full_kwargs]

    by_file: dict[str, list[DocItem]] = {}
    for item in items:
        by_file.setdefault(item.file, []).append(item)

    for file, file_items in by_file.items():
        print(f"\n{file}")
        print("  " + "-" * (len(file) + 2))
        for item in file_items:
            tag = _colour(item.status, f"[{item.status:<10}]", use_colour)
            doc_preview = ""
            if item.docstring:
                first = item.docstring.strip().splitlines()[0]
                doc_preview = f"  # {first[:50]}"
            kwarg_line = ""
            if item.qualname in full_kwargs:
                keys = full_kwargs[item.qualname]
                kwarg_line = f"\n      kwargs: {keys}"
                if use_colour:
                    kwarg_line = f"\n      \033[36mkwargs: {keys}\033[0m"
            print(
                f"  {tag}  l.{item.lineno:<5} "
                f"{item.kind:<9} {item.qualname}{doc_preview}"
                f"{kwarg_line}"
            )

    total = len(items)
    counts = {s: sum(1 for i in items if i.status == s) for s in _STATUS_ORDER}
    kw_count = sum(1 for i in items if i.qualname in full_kwargs)
    print("\n" + "=" * 60)
    print(f"Total public items      : {total}")
    for status, count in sorted(
        counts.items(), key=lambda x: _STATUS_ORDER[x[0]]
    ):
        if count:
            print(f"  {_colour(status, status, use_colour):<20} {count}")
    if kw_count:
        print(
            f"  with **kwargs          {kw_count}  (use --kwargs to list with keys)"
        )
    print("=" * 60)


def print_json(
    items: list[DocItem],
    *,
    missing_only: bool = False,
    kwargs_only: bool = False,
) -> None:
    """Print a JSON report to stdout."""
    full_kwargs = resolve_full_kwargs(items)
    if missing_only:
        items = [i for i in items if i.status in {"MISSING", "EMPTY"}]
    if kwargs_only:
        items = [i for i in items if i.qualname in full_kwargs]
    data = []
    for item in items:
        d = asdict(item)
        d["full_name"] = item.full_name
        d["full_kwargs"] = full_kwargs.get(item.qualname, [])
        data.append(d)
    print(json.dumps(data, indent=2))


# ---------------------------------------------------------------------------
# Entry point
# ---------------------------------------------------------------------------


def main() -> None:
    """Parse CLI arguments and run the docstring audit, then print results.

    Recognised flags (passed as ``sys.argv`` arguments):

    - ``--json``       — emit a JSON report instead of human-readable text.
    - ``--missing``    — show only items with ``MISSING`` or ``EMPTY`` status.
    - ``--kwargs``     — show only items that accept ``**kwargs``.
    - ``--no-colour``  — disable ANSI colour codes in the text report.
    """
    args = sys.argv[1:]
    as_json = "--json" in args
    missing_only = "--missing" in args
    kwargs_only = "--kwargs" in args
    use_colour = sys.stdout.isatty() and "--no-colour" not in args

    items = audit_package()

    if as_json:
        print_json(items, missing_only=missing_only, kwargs_only=kwargs_only)
    else:
        print_report(
            items,
            missing_only=missing_only,
            kwargs_only=kwargs_only,
            use_colour=use_colour,
        )


if __name__ == "__main__":
    main()
