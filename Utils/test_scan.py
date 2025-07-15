import ast


def get_class_defs(trees):
    class_map = {}
    for tree in trees:
        for node in tree.body:
            if isinstance(node, ast.ClassDef):
                class_map[node.name] = node
    return class_map


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
    print(f"Attribute->class mapping for {class_node.name}: {mapping}")
    return mapping


def get_function_node(class_node, func_name):
    for node in class_node.body:
        if isinstance(node, ast.FunctionDef) and node.name == func_name:
            return node
    return None


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
    print(f"Direct kwargs in {func_node.name}: {kwargs_keys}")
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
    print(f"\nEntering {class_node.name}.{func_name}")
    func_node = get_function_node(class_node, func_name)
    if func_node is None:
        print(f"Could not find function {func_name} in class {class_node.name}")
        return set()
    keys = get_kwargs_keys_from_func(func_node)
    attr_map = get_attr_class_map(class_node)
    for stmt in ast.walk(func_node):
        if isinstance(stmt, ast.Call):
            print(f"CALL FOUND IN {func_node.name}: {ast.dump(stmt.func)}")
            # self.method(**kwargs)
            if (
                isinstance(stmt.func, ast.Attribute)
                and isinstance(stmt.func.value, ast.Name)
                and stmt.func.value.id == "self"
            ):
                called_name = stmt.func.attr
                print(
                    f"--> Checking for call to self.{called_name} from {func_node.name}"
                )
                if has_star_kwargs(stmt):
                    print(
                        f"Recursing to self.{called_name} from {class_node.name}.{func_name}"
                    )
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
                print(
                    f"--> Checking for call to self.{attr}.{called_name} from {func_node.name}"
                )
                if has_star_kwargs(stmt):
                    dep_class_name = attr_map.get(attr)
                    print(
                        f"Found delegation: self.{attr}.{called_name}, attr class: {dep_class_name}"
                    )
                    print(f"Available classes: {list(class_map.keys())}")
                    if dep_class_name and dep_class_name in class_map:
                        dep_class_node = class_map[dep_class_name]
                        print(f"Recursing to {dep_class_name}.{called_name}")
                        keys |= recursive_scan(
                            class_map, dep_class_node, called_name, visited
                        )
                    else:
                        print(f"Could not resolve class for attribute {attr}")
    print(f"Exiting {class_node.name}.{func_name}, found keys: {keys}")
    return keys


# ---- Minimal test driver ----

src = """
class CreateAxesManager:
    def create_axes(self, ncol=1, nrow=1, check=False, **kwargs):
        a = kwargs["delegated"]

class ImageToolsManager:
    exposed_methods = ("text",)
    def __init__(self):
        self.CreateAxesManager = CreateAxesManager()
    def text(self, **kwargs):
        self.assign_ax(ax=None, **kwargs)
    def assign_ax(self, ax=None, **kwargs):
        self.CreateAxesManager.create_axes(ncol=1, nrow=1, check=False, **kwargs)
"""

tree = ast.parse(src)
class_map = {}
for t in [tree]:
    class_map.update(get_class_defs([t]))

node = class_map["ImageToolsManager"]
for method in ["text"]:
    print(
        f"Keys for ImageToolsManager.{method}(): {recursive_scan(class_map, node, method)}"
    )
