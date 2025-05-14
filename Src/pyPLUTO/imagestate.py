# imagestate.py

from dataclasses import dataclass, field

from matplotlib.figure import Figure


@dataclass
class ImageState:
    style: str
    LaTeX: bool | str
    fig: Figure = field(default_factory=Figure)
    color: list[str] = field(default_factory=list)
    dictcolor: dict[int, str] = field(default_factory=dict)

    def __setattr__(self, name: str, value: object) -> None:
        super().__setattr__(name, value)
