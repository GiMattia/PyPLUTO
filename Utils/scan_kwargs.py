import ast
import json
import os
from pathlib import Path

# --- CONFIGURATION ---
UTILS_DIR = Path(__file__).parent.resolve()
SRC_DIR = (UTILS_DIR / "../Src/pyPLUTO").resolve()
JSON_FILE = UTILS_DIR / "exposed_kwargs.json"
LOG_FILE = UTILS_DIR / "missing_kwargs.log"
INTERNAL_KWARGS = {"check"}  # kwargs ignored for docs

# --- Helper Functions ---


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


def arg_in_docstring(docstring: str, name: str) -> bool:
    return name in docstring if docstring else False


# --- MAIN LOGIC ---


def main():
    print("Parsing all source files...")
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
    warnings = []
    summary = []
    total_missing = 0

    print("Scanning for exposed methods and kwargs (recursively)...")
    for pyfile, tree in file_to_tree.items():
        for node in tree.body:
            if isinstance(node, ast.ClassDef):
                exposed_methods = extract_exposed_methods(node)
                if not exposed_methods:
                    continue
                for method in exposed_methods:
                    func_node = get_function_node(node, method)
                    docstring = (
                        ast.get_docstring(func_node) if func_node else ""
                    )
                    func_args = (
                        get_function_args(func_node) if func_node else []
                    )
                    kwargs = recursive_scan(class_map, node, method)

                    arg_dict = {
                        arg: arg_in_docstring(docstring, arg)
                        for arg in func_args
                    }
                    kwarg_dict = {}
                    missing_in_func = []

                    for kw in kwargs:
                        present = arg_in_docstring(docstring, kw)
                        kwarg_dict[kw] = present
                        if not present and kw not in INTERNAL_KWARGS:
                            msg = (
                                f"🚨 WARNING: kwarg '{kw}' is NOT documented in docstring.\n"
                                f"    → File: {pyfile.relative_to(SRC_DIR.parent)}\n"
                                f"    → Class: {node.name}\n"
                                f"    → Method: {method}\n"
                            )
                            # print("\n" + msg)
                            warnings.append(msg)
                            missing_in_func.append(kw)

                    if missing_in_func:
                        total_missing += len(missing_in_func)
                        summary.append(
                            f"{node.name}.{method} → {len(missing_in_func)} undocumented kwargs:\n"
                            + "".join(
                                f"    - '{kw}'\n" for kw in missing_in_func
                            )
                        )

                    results.append(
                        {
                            "file": str(pyfile.relative_to(SRC_DIR.parent)),
                            "class": node.name,
                            "method": method,
                            "args": arg_dict,
                            "kwargs": kwarg_dict,
                        }
                    )

    print(f"\n✅ Finished scanning. Found {len(results)} exposed methods.")
    with open(JSON_FILE, "w", encoding="utf-8") as f:
        json.dump(results, f, indent=2)
    print(f"\n🚨 Total undocumented kwargs: {total_missing}")
    print(f"\n📄 Results written to {JSON_FILE}")

    with open(LOG_FILE, "w", encoding="utf-8") as logf:
        if warnings:
            logf.write("Missing kwarg documentation warnings:\n\n")
            for msg in warnings:
                logf.write(msg + "\n")
            logf.write("\nSUMMARY OF MISSING KWARGS:\n\n")
            for line in summary:
                logf.write(line + "\n")
            logf.write(f"\nTotal undocumented kwargs: {total_missing}\n")
            print(f"\n📝 Warnings and summary written to: {LOG_FILE}")
        else:
            logf.write("🎉 All kwargs are documented properly!\n")
            print("\n🎉 No undocumented kwargs found!")


if __name__ == "__main__":
    main()
