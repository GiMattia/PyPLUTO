import importlib
import inspect
import pkgutil
from collections.abc import Callable
from types import ModuleType

from pyPLUTO.inspect_kwargs import find_kwargs_keys


class TrackKwargsCollector:
    def __init__(self, root_package: str):
        self.root_package = root_package
        self.results: dict[str, set[str]] = {}

    def _is_tracked(self, obj: Callable) -> bool:
        return (
            any(
                getattr(deco, "__name__", "") == "track_kwargs"
                for deco in getattr(obj, "__wrapped_decorators__", [obj])
            )
            or getattr(obj, "__name__", "") == "track_kwargs"
        )

    def _process_function(self, obj: Callable, qualname: str):
        try:
            if self._is_tracked(obj):
                keys = find_kwargs_keys(obj)
                if keys:
                    self.results[qualname] = keys
        except Exception:
            pass

    def _process_module(self, module: ModuleType, modname: str):
        for name, obj in inspect.getmembers(module, inspect.isfunction):
            self._process_function(obj, f"{modname}.{name}")

        for clsname, cls in inspect.getmembers(module, inspect.isclass):
            for methname, method in inspect.getmembers(cls, inspect.isfunction):
                self._process_function(
                    method, f"{modname}.{clsname}.{methname}"
                )

    def collect(self) -> dict[str, set[str]]:
        package = importlib.import_module(self.root_package)
        for _, modname, ispkg in pkgutil.walk_packages(
            package.__path__, package.__name__ + "."
        ):
            try:
                module = importlib.import_module(modname)
                self._process_module(module, modname)
            except Exception as e:
                print(f"Skipped {modname}: {e}")
        return self.results


if __name__ == "__main__":
    collector = TrackKwargsCollector("./")
    results = collector.collect()

    for name, keys in results.items():
        print(f"{name}: {sorted(keys)}")
