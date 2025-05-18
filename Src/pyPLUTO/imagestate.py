# imagestate.py

from dataclasses import dataclass, field

from matplotlib.figure import Figure


@dataclass
class ImageState:
    LaTeX: bool | str
    style: str
    color: list[str] = field(default_factory=list)
    dictcolor: dict[int, str] = field(default_factory=dict)
    fig: Figure | None = None
    figsize: list[float] = field(default_factory=lambda: [8.0, 5.0])
    fontsize: int = 17
    nwin: int = 1
    tight: bool = True
    _set_size: bool = False

    def __setattr__(self, name: str, value: object) -> None:
        super().__setattr__(name, value)
