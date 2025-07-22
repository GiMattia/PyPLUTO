# scan_exposed.py
import ast
import json
import os
import re
from collections import defaultdict
from pathlib import Path

# --- CONFIGURATION ---
UTILS_DIR = Path(__file__).parent.resolve()
SRC_DIR = (UTILS_DIR / "../Src/pyPLUTO").resolve()
JSON_FILE = UTILS_DIR / "exposed_kwargs.json"
LOG_FILE = UTILS_DIR / "missing_kwargs.log"
CANONICAL_FILE = UTILS_DIR / "canonical_params.csv"
ALL_KWARGS_FILE = UTILS_DIR / "all_kwargs.csv"
INTERNAL_KWARGS = {"check"}


def extract_doc_params(docstring: str) -> dict[str, str]:
    if not docstring:
        return {}
    lines = docstring.strip().splitlines()
    lines = [line.rstrip() for line in lines]
    param_docs = {}
    in_params = False
    i = 0
    while i < len(lines):
        if lines[i].strip().lower() == "parameters":
            i += 1
            while i < len(lines) and re.match(r"^\s*-{3,}", lines[i]):
                i += 1
            in_params = True
            break
        i += 1
    current_param = None
    current_desc = []
    while in_params and i < len(lines):
        line = lines[i]
        param_match = re.match(r"^\s*(\w+)\s*:\s*(.+)", line)
        if param_match:
            if current_param and current_desc:
                param_docs[current_param] = " ".join(current_desc).strip()
            current_param = param_match.group(1)
            current_desc = []
            i += 1
            continue
        if line.startswith(" ") or line.startswith("\t"):
            current_desc.append(line.strip())
        elif line.strip() == "":
            pass
        else:
            if current_param and current_desc:
                param_docs[current_param] = " ".join(current_desc).strip()
            break
        i += 1
    if current_param and current_desc:
        param_docs[current_param] = " ".join(current_desc).strip()
    return param_docs


def find_python_files(root: Path):
    for dirpath, _, files in os.walk(root):
        for fname in files:
            if fname.endswith(".py"):
                yield Path(dirpath) / fname


def get_class_defs(tree):
    return {
        node.name: node for node in tree.body if isinstance(node, ast.ClassDef)
    }


def extract_exposed_methods(class_node):
    for stmt in class_node.body:
        if isinstance(stmt, ast.Assign):
            for target in stmt.targets:
                if (
                    isinstance(target, ast.Name)
                    and target.id == "exposed_methods"
                ):
                    v = stmt.value
                    if isinstance(v, (ast.Tuple, ast.List)):
                        return [
                            elt.value
                            for elt in v.elts
                            if isinstance(elt, ast.Constant)
                            and isinstance(elt.value, str)
                        ]
    return []


def get_attr_class_map(class_node):
    mapping = {}
    for node in class_node.body:
        if isinstance(node, ast.FunctionDef) and node.name == "__init__":
            for stmt in ast.walk(node):
                if (
                    isinstance(stmt, ast.Assign)
                    and isinstance(stmt.targets[0], ast.Attribute)
                    and isinstance(stmt.targets[0].value, ast.Name)
                    and stmt.targets[0].value.id == "self"
                    and isinstance(stmt.value, ast.Call)
                ):
                    attr = stmt.targets[0].attr
                    if isinstance(stmt.value.func, ast.Name):
                        mapping[attr] = stmt.value.func.id
                    elif isinstance(stmt.value.func, ast.Attribute):
                        mapping[attr] = stmt.value.func.attr
    return mapping


def get_function_node(class_node, func_name):
    for node in class_node.body:
        if isinstance(node, ast.FunctionDef) and node.name == func_name:
            return node
    return None


def get_function_args(func_node):
    return [
        arg.arg
        for arg in func_node.args.args
        if arg.arg not in {"self", "cls", "kwargs"}
    ]


def get_kwargs_keys_from_func(func_node):
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
            if (
                isinstance(node.func, ast.Attribute)
                and isinstance(node.func.value, ast.Name)
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

    KwargsVisitor().visit(func_node)
    return kwargs_keys


def has_star_kwargs(call):
    return any(
        isinstance(arg, ast.Starred)
        and isinstance(arg.value, ast.Name)
        and arg.value.id == "kwargs"
        for arg in call.args
    ) or any(
        k.arg is None
        and isinstance(k.value, ast.Name)
        and k.value.id == "kwargs"
        for k in call.keywords
    )


def recursive_scan(class_map, class_node, func_name, visited=None):
    if visited is None:
        visited = set()
    sig = (class_node.name, func_name)
    if sig in visited:
        return set()
    visited.add(sig)
    func_node = get_function_node(class_node, func_name)
    if func_node is None:
        return set()
    keys = get_kwargs_keys_from_func(func_node)
    attr_map = get_attr_class_map(class_node)
    for stmt in ast.walk(func_node):
        if isinstance(stmt, ast.Call):
            if (
                isinstance(stmt.func, ast.Attribute)
                and isinstance(stmt.func.value, ast.Name)
                and stmt.func.value.id == "self"
            ):
                called_name = stmt.func.attr
                if has_star_kwargs(stmt):
                    keys |= recursive_scan(
                        class_map, class_node, called_name, visited
                    )
            elif (
                isinstance(stmt.func, ast.Attribute)
                and isinstance(stmt.func.value, ast.Attribute)
                and isinstance(stmt.func.value.value, ast.Name)
                and stmt.func.value.value.id == "self"
            ):
                attr = stmt.func.value.attr
                called_name = stmt.func.attr
                dep_class_name = attr_map.get(attr)
                if (
                    has_star_kwargs(stmt)
                    and dep_class_name
                    and dep_class_name in class_map
                ):
                    dep_class_node = class_map[dep_class_name]
                    keys |= recursive_scan(
                        class_map, dep_class_node, called_name, visited
                    )
    return keys


# --- MAIN LOGIC ---


def scan():
    print("Parsing source files...")
    file_to_tree = {}
    for pyfile in find_python_files(SRC_DIR):
        try:
            with open(pyfile, encoding="utf-8") as f:
                tree = ast.parse(f.read(), filename=str(pyfile))
            file_to_tree[pyfile] = tree
        except Exception as e:
            print(f"Failed to parse {pyfile}: {e}")

    class_map = {}
    for tree in file_to_tree.values():
        class_map.update(get_class_defs(tree))

    results = []
    docstring_registry = defaultdict(set)
    all_kwargs = set()

    print("Scanning for exposed methods...")
    for pyfile, tree in file_to_tree.items():
        for node in tree.body:
            if isinstance(node, ast.ClassDef):
                exposed_methods = extract_exposed_methods(node)
                if not exposed_methods:
                    continue
                for method in exposed_methods:
                    func_node = get_function_node(node, method)
                    docstring = ast.get_docstring(func_node) or ""
                    doc_params = extract_doc_params(docstring)
                    func_args = (
                        get_function_args(func_node) if func_node else []
                    )
                    kwargs = recursive_scan(class_map, node, method)

                    arg_dict = {arg: arg in doc_params for arg in func_args}
                    kwarg_dict = {kw: kw in doc_params for kw in kwargs}
                    all_kwargs.update(kwargs)

                    for param, desc in doc_params.items():
                        docstring_registry[param].add(desc)

                    results.append(
                        {
                            "file": str(pyfile.relative_to(SRC_DIR.parent)),
                            "class": node.name,
                            "method": method,
                            "args": arg_dict,
                            "kwargs": kwarg_dict,
                            "docstring": docstring,
                        }
                    )

    with open(JSON_FILE, "w", encoding="utf-8") as f:
        json.dump(results, f, indent=2)
    print(f"📄 JSON with docstrings written to {JSON_FILE}")
    """
    # Canonical param descriptions
    canonical_map = {}
    with open(CANONICAL_FILE, "w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerow(["param", "status", "canonical_description"])
        for param, descs in sorted(docstring_registry.items()):
            if len(descs) == 1:
                desc = next(iter(descs))
                canonical_map[param] = desc
                writer.writerow([param, "ok", desc])
            else:
                writer.writerow(
                    [param, "conflict", " ||| ".join(sorted(descs))]
                )
    print(f"📄 Canonical param descriptions written to {CANONICAL_FILE}")

    with open(ALL_KWARGS_FILE, "w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerow(["key", "description"])
        for kwarg in sorted(all_kwargs):
            writer.writerow([kwarg, canonical_map.get(kwarg, "")])
    print(f"📄 All kwargs written to {ALL_KWARGS_FILE}")

    print("\n🔍 Conflicts detected:")
    for param, descs in docstring_registry.items():
        if len(descs) > 1:
            print(f"⚠️ '{param}':")
            for d in descs:
                print(f"   - {d}")
    """


if __name__ == "__main__":
    scan()
