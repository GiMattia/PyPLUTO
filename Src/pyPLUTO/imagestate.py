# imagestate.py

from dataclasses import dataclass, field

from matplotlib.figure import Figure


@dataclass
class ImageState:
    """Class that stores the state of the Image class. It contains the
    following attributes:

    - LaTeX: bool | str (non optional)
    - style: str (non optional)
    - color: list[str]
    - dictcolor: dict[int, str]
    - fig: Figure | None
    - figsize: list[float]
    - fontsize: int
    - nwin: int
    - tight: bool
    """

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
