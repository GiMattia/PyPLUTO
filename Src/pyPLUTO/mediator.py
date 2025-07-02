# mediator.py
from collections.abc import Sequence
from typing import Any, Generic, Protocol, TypeVar

StateType_co = TypeVar("StateType_co", covariant=True)


class ManagerProtocol(Protocol, Generic[StateType_co]):
    """Protocol for manager classes used in the Mediator pattern."""

    def __init__(self, state: StateType_co) -> None: ...  # pragma: no cover


class Mediator(Generic[StateType_co]):
    """Mediator class that manages the interaction between different manager
    classes. This class acts as a central point of communication for various
    manager classes, allowing them to interact with the shared state without
    needing to know about each other directly. It dynamically creates instances
    of the manager classes as needed and delegates method calls to the
    appropriate manager based on the requested method.
    """

    def __init__(
        self,
        state: StateType_co,
        manager_classes: Sequence[type[ManagerProtocol[StateType_co]]],
    ) -> None:
        """Initializes the Mediator with a shared state and a list of manager
        classes."""
        object.__setattr__(self, "state", state)
        object.__setattr__(self, "_manager_classes", manager_classes)
        object.__setattr__(self, "_instances", {})

    def __getattr__(self, name: str) -> Any:
        """Delegates attribute access to the appropriate manager class based on
        the requested method name. If the method is not found in any manager,
        raises an AttributeError.
        """
        for manager_cls in self._manager_classes:
            if manager_cls not in self._instances:
                self._instances[manager_cls] = manager_cls(self.state)
            manager = self._instances[manager_cls]
            if (
                hasattr(manager, "exposed_methods")
                and name in manager.exposed_methods
            ):
                return getattr(manager, name)

        raise AttributeError(
            f"{type(self).__name__!r} object has no attribute {name!r}"
        )
