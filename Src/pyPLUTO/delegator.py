# delegator.py

from collections.abc import Callable, Iterable
from typing import Any


def delegator(
    *attr_names: str,
    exclude: Iterable[str] = (),
    readonly: bool = False,
) -> Callable:
    """Delegate attribute access to multiple internal attributes (e.g., 'state', 'manager').

    Parameters
    ----------
        *attr_names (str): attribute names to delegate to (in order of priority)
        exclude (Iterable[str]): attribute names NOT to delegate
        readonly (bool): if True, __setattr__ won't delegate

    """
    exclude_set = set(exclude)

    def decorator(cls):
        orig_getattr = getattr(cls, "__getattr__", None)

        def __getattr__(self, name: str) -> Any:
            if name in exclude_set:
                raise AttributeError(
                    f"'{type(self).__name__}' has no attribute '{name}' (excluded from delegation)"
                )
            for attr_name in attr_names:
                target = getattr(self, attr_name, None)
                if target and hasattr(target, name):
                    return getattr(target, name)
            if orig_getattr:
                return orig_getattr(self, name)
            raise AttributeError(
                f"'{type(self).__name__}' object has no attribute '{name}'"
            )

        def __setattr__(self, name: str, value: Any) -> None:
            if (
                name in attr_names
                or name in self.__dict__
                or name in exclude_set
                or readonly
            ):
                object.__setattr__(self, name, value)
            else:
                for attr_name in attr_names:
                    target = getattr(self, attr_name, None)
                    if target and hasattr(target, name):
                        setattr(target, name, value)
                        return
                object.__setattr__(self, name, value)

        def assign(self, **kwargs: Any) -> None:
            for key, value in kwargs.items():
                setattr(self, key, value)  # Set in the current object
                setattr(self.state, key, value)
            return self

        cls.__getattr__ = __getattr__
        cls.__setattr__ = __setattr__
        cls.assign = assign
        return cls

    return decorator
