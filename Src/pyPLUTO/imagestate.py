# imagestate.py

from dataclasses import dataclass, field

from matplotlib.figure import Figure


@dataclass
class ImageState:
    style: str
    LaTeX: bool | str
    fig: Figure | None = None
    color: list[str] = field(default_factory=list)
    dictcolor: dict[int, str] = field(default_factory=dict)
    nwin: int = 1
    fontsize: int = 17
    tight: bool = True
    figsize: list[float] = field(default_factory=lambda: [8.0, 5.0])
    _set_size: bool = False

    def __setattr__(self, name: str, value: object) -> None:
        super().__setattr__(name, value)
