"""Collect positional arguments and kwargs keys from all functions in pyPLUTO.

This script walks recursively through the pyPLUTO package source tree, parses
all Python files with the AST, and writes a JSON report containing:

1. per-function positional arguments
2. per-function kwargs keys accessed via kwargs[...] / kwargs.get(...) / kwargs.pop(...)
3. global deduplicated lists of all positional arguments and all kwargs keys

Place this file in: src/pyPLUTO/utils/
"""

from __future__ import annotations

import ast
import json
from pathlib import Path
from typing import Any

try:
    from .inspector import _find_kwargs_keys_from_source
except ImportError:
    from inspector import _find_kwargs_keys_from_source


def _is_python_file(path: Path) -> bool:
    """Return True if path is a Python source file."""
    return path.is_file() and path.suffix == ".py"


def _module_name_from_path(file_path: Path, package_root: Path) -> str:
    """Convert a Python file path into a module-like dotted path."""
    rel = file_path.relative_to(package_root)

    parts = list(rel.with_suffix("").parts)
    if parts[-1] == "__init__":
        parts = parts[:-1]

    return ".".join([package_root.name, *parts]) if parts else package_root.name


def _get_positional_args_from_node(
    node: ast.FunctionDef | ast.AsyncFunctionDef,
) -> list[str]:
    """Return positional argument names from a function AST node."""
    args: list[str] = []

    posonlyargs = getattr(node.args, "posonlyargs", [])
    normal_args = node.args.args

    for arg in [*posonlyargs, *normal_args]:
        if arg.arg not in {"self", "cls"}:
            args.append(arg.arg)

    return args


def _collect_functions_from_file(
    file_path: Path,
    package_root: Path,
) -> dict[str, dict[str, list[str]]]:
    """Collect args/kwargs info for all functions defined in one file."""
    try:
        source = file_path.read_text(encoding="utf-8")
    except Exception:
        return {}

    try:
        tree = ast.parse(source)
    except SyntaxError:
        return {}

    module_name = _module_name_from_path(file_path, package_root)
    results: dict[str, dict[str, list[str]]] = {}

    for node in ast.walk(tree):
        if not isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
            continue

        func_source = ast.get_source_segment(source, node)
        if func_source is None:
            continue

        func_name = f"{module_name}.{node.name}"
        args = sorted(_get_positional_args_from_node(node))
        kwargs = sorted(_find_kwargs_keys_from_source(func_source))

        results[func_name] = {
            "args": args,
            "kwargs": kwargs,
        }

    return results


def collect_package_parameters(package_root: Path) -> dict[str, Any]:
    """Recursively collect args/kwargs info from all Python files in a package."""
    functions: dict[str, dict[str, list[str]]] = {}
    all_args: set[str] = set()
    all_kwargs: set[str] = set()

    for file_path in sorted(package_root.rglob("*.py")):
        if not _is_python_file(file_path):
            continue

        file_results = _collect_functions_from_file(file_path, package_root)

        for func_name, values in file_results.items():
            functions[func_name] = values
            all_args.update(values["args"])
            all_kwargs.update(values["kwargs"])

    return {
        "package": package_root.name,
        "functions": functions,
        "all_args": sorted(all_args),
        "all_kwargs": sorted(all_kwargs),
    }


def save_package_parameters_to_json(
    output_file: str | Path = "pypluto_function_parameters.json",
) -> Path:
    """Save collected args/kwargs info to JSON.

    Assumes this file lives in src/pyPLUTO/utils/, so the package root is:
    Path(__file__).resolve().parents[1] -> src/pyPLUTO
    """
    package_root = Path(__file__).resolve().parents[1]
    data = collect_package_parameters(package_root)

    output_path = Path(output_file)
    if not output_path.is_absolute():
        output_path = Path(__file__).resolve().parent / output_path

    output_path.write_text(
        json.dumps(data, indent=2, sort_keys=True),
        encoding="utf-8",
    )

    return output_path


if __name__ == "__main__":
    output = save_package_parameters_to_json()
    print(f"Saved parameter report to: {output}")
