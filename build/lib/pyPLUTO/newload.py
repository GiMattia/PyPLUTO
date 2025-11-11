"""The Load class loads the data (fluid) from the output files."""

# mypy: ignore-errors

from typing import Any

from .loadmixin import LoadMixin
from .loadstate import LoadState
from .utils.inspector import track_kwargs


class Load(LoadMixin):
    """The Load class loads the data (fluid) from the output files.

    The initialization corresponds to the loading, if wanted, of one or more
    datafiles for the fluid. The data are loaded in a memory mapped numpy
    multidimensional array. Such approach does not load the full data
    until needed. Basic operations (i.e. no numpy) are possible, as well
    as slicing the arrays, without fully loading the data.
    """

    @track_kwargs
    def __init__(
        self,
        text: bool = True,
        check: bool = True,
        **kwargs: Any,
    ) -> None:
        """Initialize the Load class."""
        kwargs.pop("check", check)

        self.state = LoadState()

        if text:
            print("Load: Load class initialized.")
