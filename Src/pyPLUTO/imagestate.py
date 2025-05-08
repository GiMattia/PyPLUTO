# imagestate.py

from dataclasses import dataclass, field

from matplotlib.figure import Figure


@dataclass
class ImageState:
    style: str
    fig: Figure = field(default_factory=Figure)
    color: list[str] = field(default_factory=list)

    def __setattr__(self, name, value):
        super().__setattr__(name, value)
