from typing import Any

from .delegator import delegator
from .imagestate import ImageState
from .inspect_kwargs import track_kwargs


@delegator("state")
class AxesManager:

    @track_kwargs
    def __init__(self, state: ImageState, **kwargs: Any) -> None:
        self.state = state

    @track_kwargs
    def create_axes(self):
        print("Axes created! LOL")
