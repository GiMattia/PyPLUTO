# imagestate.py
from dataclasses import dataclass, field
from typing import Any

from matplotlib.figure import Figure


@dataclass
class ImageState:
    style: str
    fig: Figure = field(default_factory=Figure)
    color: list[str] = field(default_factory=list)


class ImageStateComponent:
    def __init__(self, state: ImageState) -> None:
        self.state: ImageState = state

    def __getattr__(self, name: str) -> Any:
        try:
            return getattr(self.state, name)
        except AttributeError:
            raise AttributeError(
                f"'{type(self).__name__}' object has no attribute '{name}'"
            )

    def __setattr__(self, name: str, value: Any) -> None:
        if name == "state" or name in self.__dict__:
            object.__setattr__(self, name, value)
        else:
            setattr(self.state, name, value)
