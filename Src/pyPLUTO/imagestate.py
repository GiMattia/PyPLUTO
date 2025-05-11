# imagestate.py

from dataclasses import dataclass, field

from matplotlib.figure import Figure


@dataclass
class ImageState:
    style: str
    LaTeX: bool | str
    fig: Figure = field(default_factory=Figure)
    color: list[str] = field(default_factory=list)
    numcolors: int = 10
    _with_black: bool = False
    _with_white: bool = False
    _old_color: bool = False

    def __setattr__(self, name: str, value: object) -> None:
        super().__setattr__(name, value)
