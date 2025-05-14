from collections.abc import Callable
from typing import Any, Protocol, TypeVar

T = TypeVar("T")


class HasState(Protocol):
    """Protocol for objects that have a 'state' attribute."""

    state: Any  # We use Any because it can be any object (e.g., ImageState)


def delegator(
    *attr_names: str,
) -> Callable[[type[T]], type[T]]:
    """Delegate attribute access to internal attributes like 'state'.

    Parameters
    ----------
    *attr_names : str
        Attributes to delegate to.

    """

    def decorator(cls: type[T]) -> type[T]:
        """Decorator to add delegation functionality to a class."""
        orig_getattr = getattr(cls, "__getattr__", None)

        def __getattr__(self: HasState, name: str) -> Any:
            """Delegate attribute access to internal attributes like
            'state'."""
            for attr_name in attr_names:
                target = getattr(self, attr_name, None)
                if target and hasattr(target, name):
                    return getattr(target, name)
            if orig_getattr:
                return orig_getattr(self, name)
            raise AttributeError(
                f"'{type(self).__name__}' object has no attribute '{name}'"
            )

        def __setattr__(self: HasState, name: str, value: Any) -> None:
            """Delegate attribute access to internal attributes like
            'state'."""
            if name in attr_names or name in self.__dict__:
                object.__setattr__(self, name, value)
            else:
                for attr_name in attr_names:
                    target = getattr(self, attr_name, None)
                    if target and hasattr(target, name):
                        setattr(target, name, value)
                        return
                object.__setattr__(self, name, value)

        def assign(self: HasState, **kwargs: Any) -> HasState:
            """Assign attributes to internal attributes like 'state'."""
            for key, value in kwargs.items():
                setattr(self, key, value)
                setattr(self.state, key, value)
            return self

        cls.__getattr__ = __getattr__  # type: ignore
        cls.__setattr__ = __setattr__  # type: ignore
        cls.assign = assign  # type: ignore
        return cls

    return decorator
