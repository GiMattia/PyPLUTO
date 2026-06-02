"""Produce two reference files for every function in pyPLUTO.

pypluto_funcs.json
    Every function/method with its direct args and kwargs + descriptions.
    Not recursive — only what each function itself defines or accesses.

pypluto_kwargs_conflicts.json
    Every kwargs key that appears with two or more different descriptions
    across the codebase.

Usage
-----
    python src/pyPLUTO/utils/inspect_funcs.py
"""

from __future__ import annotations

import importlib
import inspect
import json
import pkgutil
import sys
from collections import defaultdict
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[3] / "src"))

import pyPLUTO as _pkg
from pyPLUTO.utils.make_docstrings import (
    PACKAGE_ROOT,
    _extract_used_keys,
    audit_package,
)

OUT_FUNCS = PACKAGE_ROOT / "utils" / "pypluto_funcs.json"
OUT_CONFLICTS = PACKAGE_ROOT / "utils" / "pypluto_kwargs_conflicts.json"
OUT_TRANSITIVE = PACKAGE_ROOT / "utils" / "pypluto_transitive_kwargs.json"

_SKIP = {"self", "cls"}
_VAR = (inspect.Parameter.VAR_POSITIONAL, inspect.Parameter.VAR_KEYWORD)


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------


def _parse_doc(docstring: str | None) -> dict[str, str]:
    """Return {param: description} from a NumPy-style Parameters section.

    Only top-level bullets (at the shallowest indentation of the section)
    are treated as parameters; deeper bullets are nested sub-points of the
    current parameter's description. The literal ``kwargs`` / ``**kwargs``
    parameter is skipped (it is not a real keyword).
    """
    if not docstring:
        return {}
    params: dict[str, str] = {}
    in_params, key, parts = False, None, []
    param_indent: int | None = None

    def flush() -> None:
        """Flush the current parameter key/parts accumulator into *params*."""
        if key:
            params[key] = " ".join(parts).strip()

    lines = docstring.splitlines()
    for i, line in enumerate(lines):
        s = line.strip()
        indent = len(line) - len(line.lstrip())
        next_dashes = i + 1 < len(lines) and lines[i + 1].strip().startswith(
            "---"
        )
        if s in {"Parameters", "Parameters:"} and next_dashes:
            flush()
            key, parts, in_params = None, [], True
            param_indent = None
        elif (
            in_params
            and s
            and not s.startswith("-")
            and not line.startswith(" ")
            and next_dashes
        ):
            flush()
            in_params, key, parts = False, None, []
        if not in_params:
            continue
        # A new parameter only if the bullet sits at the section's top
        # indentation level (deeper bullets are description sub-points).
        is_param_bullet = (
            s.startswith("- ")
            and ":" in s[2:]
            and (param_indent is None or indent <= param_indent)
        )
        if is_param_bullet:
            if param_indent is None:
                param_indent = indent
            flush()
            body = s[2:]
            colon = body.index(":")
            raw = body[:colon].strip()
            key = raw[: raw.index("(")].strip() if "(" in raw else raw
            parts = (
                [body[colon + 1 :].strip()] if body[colon + 1 :].strip() else []
            )
        elif key and s and not all(c == "-" for c in s):
            parts.append(s)
    flush()

    # Drop the literal kwargs parameter — it is not a real keyword
    for artifact in ("kwargs", "**kwargs"):
        params.pop(artifact, None)
    return params


def _runtime_registry() -> dict[str, object]:
    """Map qualname → callable for every pyPLUTO-native function/method."""
    reg: dict[str, object] = {}
    for _, modname, _ in pkgutil.walk_packages(
        _pkg.__path__, _pkg.__name__ + ".", onerror=lambda _: None
    ):
        try:
            mod = importlib.import_module(modname)
        except Exception:
            continue
        for cls_name, cls in inspect.getmembers(mod, inspect.isclass):
            if not cls.__module__.startswith("pyPLUTO"):
                continue
            for mname, obj in inspect.getmembers(cls, callable):
                if not isinstance(
                    inspect.getattr_static(cls, mname, None), property
                ):
                    reg[f"{cls_name}.{mname}"] = obj
        for fn_name, fn in inspect.getmembers(mod, inspect.isfunction):
            if fn.__module__.startswith("pyPLUTO"):
                reg[fn_name] = fn
    return reg


def _ann(p: inspect.Parameter) -> str:
    """Return the annotation of *p* as a plain string, or ``""`` if absent.

    Parameters
    ----------
    - p: inspect.Parameter
        The parameter whose annotation should be extracted.

    Returns
    -------
    - str
    """
    a = p.annotation
    if a is p.empty:
        return ""
    return a if isinstance(a, str) else getattr(a, "__name__", str(a))


def _args_entry(obj: object, doc: dict[str, str]) -> dict[str, str]:
    """Return {param: 'type, default X — description'} from signature."""
    try:
        sig = inspect.signature(obj)  # ty:ignore[invalid-argument-type]
    except (TypeError, ValueError):
        return {}
    result: dict[str, str] = {}
    for name, p in sig.parameters.items():
        if name in _SKIP or p.kind in _VAR:
            continue
        ann = _ann(p)
        default = "" if p.default is p.empty else f"default {p.default!r}"
        header = ", ".join(filter(None, [ann, default]))
        desc = doc.get(name, "")
        result[name] = (
            f"{header} — {desc}" if header and desc else header or desc
        )
    return result


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------


def _build_transitive(items: list) -> dict[str, list[str]]:
    """Return {file::qualname: [sorted transitive kwargs]} for every item."""
    from pyPLUTO.utils.make_docstrings import (  # noqa: PLC0415
        _build_used_keys_registry,
        resolve_full_kwargs,
    )

    full_kwargs = resolve_full_kwargs(items, _build_used_keys_registry())
    by_qualname = {
        qn: sorted(k for k in keys if k != "check")
        for qn, keys in full_kwargs.items()
    }
    return {
        f"{item.file}::{item.qualname}": by_qualname.get(item.qualname, [])
        for item in sorted(items, key=lambda i: (i.file, i.qualname))
        if item.kind != "class"
    }


def main() -> None:
    """Generate and write function/kwargs reference JSON files for pyPLUTO."""
    conflicts_only = "--conflicts-only" in sys.argv
    all_items = audit_package()
    runtime = _runtime_registry()
    funcs: dict[str, dict[str, dict[str, str]]] = {}

    for item in all_items:
        if item.kind not in ("function", "method"):
            continue
        doc = _parse_doc(item.docstring)
        obj = runtime.get(item.qualname)
        args = _args_entry(obj, doc) if obj else {}

        # Start with direct kwargs (AST-detected)
        kwargs: dict[str, str] = {
            k: doc.get(k, "") for k in item.direct_kwargs_keys
        }

        # For @track_kwargs functions, also include documented parameters that
        # are NOT in the signature — these are forwarded kwargs documented in
        # the docstring but never accessed directly (e.g. 'var' in
        # Load.__init__ which is forwarded to InitLoadManager).
        # We detect @track_kwargs by the presence of a 'used_keys' closure.
        has_track_kwargs = _extract_used_keys(obj) is not None if obj else False
        if has_track_kwargs:
            sig_params = set(args) | {"self", "cls", "check"}
            for key, desc in doc.items():
                if key not in sig_params and key not in kwargs:
                    kwargs[key] = desc

        if not args and not kwargs:
            continue
        funcs[f"{item.file}::{item.qualname}"] = {
            "args": args,
            "kwargs": kwargs,
        }

    by_key: defaultdict[str, defaultdict[str, list[str]]] = defaultdict(
        lambda: defaultdict(list)
    )
    for label, entry in funcs.items():
        for key, desc in entry["kwargs"].items():
            if desc:
                by_key[key][desc].append(label)

    conflicts = {
        k: [{"description": d, "functions": fs} for d, fs in v.items()]
        for k, v in sorted(by_key.items())
        if len(v) > 1
    }

    OUT_CONFLICTS.write_text(
        json.dumps(conflicts, indent=2, ensure_ascii=False)
    )
    print(f"Written {len(conflicts)} conflicting kwargs → {OUT_CONFLICTS}")

    if not conflicts_only:
        OUT_FUNCS.write_text(json.dumps(funcs, indent=2, ensure_ascii=False))
        print(f"Written {len(funcs)} functions → {OUT_FUNCS}")
        transitive = _build_transitive(all_items)
        OUT_TRANSITIVE.write_text(
            json.dumps(transitive, indent=2, ensure_ascii=False)
        )
        print(f"Written {len(transitive)} entries → {OUT_TRANSITIVE}")


if __name__ == "__main__":
    main()
