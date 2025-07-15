import ast
import csv
import json
import os
from pathlib import Path

# --- CONFIGURATION ---
UTILS_DIR = Path(__file__).parent.resolve()
SRC_DIR = (UTILS_DIR / "../Src/pyPLUTO").resolve()
JSON_FILE = UTILS_DIR / "exposed_kwargs.json"
CSV_FILE = UTILS_DIR / "all_kwargs.csv"

my_dict = {}

# --- Helper Functions ---


def find_python_files(root: Path):
    for dirpath, _, files in os.walk(root):
        for fname in files:
            if fname.endswith(".py"):
                yield Path(dirpath) / fname


def get_class_defs(tree):
    class_map = {}
    for node in tree.body:
        if isinstance(node, ast.ClassDef):
            class_map[node.name] = node
    return class_map


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
    """Return a list of explicit argument names (excluding self, cls, *args, **kwargs)."""
    args = []
    # .args is an ast.arguments object
    for arg in func_node.args.args:
        if arg.arg not in {"self", "cls", "kwargs"}:
            args.append(arg.arg)
    # Ignore .vararg (*args) and .kwarg (**kwargs)
    return args


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
    # True if call uses **kwargs, whether as starred arg or keyword
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
            # self.method(**kwargs)
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
            # self.<attr>.method(**kwargs)
            elif (
                isinstance(stmt.func, ast.Attribute)
                and isinstance(stmt.func.value, ast.Attribute)
                and isinstance(stmt.func.value.value, ast.Name)
                and stmt.func.value.value.id == "self"
            ):
                attr = stmt.func.value.attr
                called_name = stmt.func.attr
                if has_star_kwargs(stmt):
                    dep_class_name = attr_map.get(attr)
                    if dep_class_name and dep_class_name in class_map:
                        dep_class_node = class_map[dep_class_name]
                        keys |= recursive_scan(
                            class_map, dep_class_node, called_name, visited
                        )
    return keys


def write_unique_args_and_kwargs_csv(json_file: Path, csv_file: Path):
    """Reads a JSON file and writes all unique kwargs and explicit args, sorted alphabetically, to a CSV file (column: "argument")."""
    with open(json_file, encoding="utf-8") as f:
        data = json.load(f)

    all_names = set()
    for item in data:
        all_names.update(item.get("kwargs", []))
        all_names.update(item.get("args", []))

    names_sorted = sorted(all_names)

    with open(csv_file, "w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        for name in names_sorted:
            writer.writerow([name])

    print(f"Saved unique sorted arguments to {csv_file}")


def read_csv_file(csv_file: Path):
    my_dict = {}
    with open(csv_file, newline="", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for row in reader:
            my_dict[row["key"]] = row["value"]


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
    # Build one big global class_map
    class_map = {}
    for tree in file_to_tree.values():
        class_map.update(get_class_defs(tree))

    results = []
    print("Scanning for exposed methods and kwargs (recursively)...")
    for pyfile, tree in file_to_tree.items():
        for node in tree.body:
            if isinstance(node, ast.ClassDef):
                exposed_methods = extract_exposed_methods(node)
                if not exposed_methods:
                    continue
                for method in exposed_methods:
                    keys = recursive_scan(class_map, node, method)
                    func_node = get_function_node(node, method)
                    func_args = (
                        get_function_args(func_node)
                        if func_node is not None
                        else []
                    )
                    results.append(
                        {
                            "file": str(pyfile.relative_to(SRC_DIR.parent)),
                            "class": node.name,
                            "method": method,
                            "args": func_args,
                            "kwargs": sorted(keys),
                        }
                    )
    print(f"Found {len(results)} exposed methods.")
    with open(JSON_FILE, "w", encoding="utf-8") as f:
        json.dump(results, f, indent=2)
    print(f"Results written to {JSON_FILE}")
    write_unique_args_and_kwargs_csv(JSON_FILE, CSV_FILE)


if __name__ == "__main__":
    main()
