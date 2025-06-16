# mediator.py
from collections.abc import Sequence
from typing import Any, Generic, Protocol, TypeVar

StateType_co = TypeVar("StateType_co", covariant=True)


class ManagerProtocol(Protocol, Generic[StateType_co]):
    def __init__(self, state: StateType_co) -> None: ...  # pragma: no cover


class Mediator(Generic[StateType_co]):
    def __init__(
        self,
        state: StateType_co,
        manager_classes: Sequence[type[ManagerProtocol[StateType_co]]],
    ) -> None:
        object.__setattr__(self, "state", state)
        object.__setattr__(self, "_manager_classes", manager_classes)
        object.__setattr__(self, "_instances", {})

    def __getattr__(self, name: str) -> Any:
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
