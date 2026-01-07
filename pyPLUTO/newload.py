"""The Load class loads the data (fluid) from the output files."""

from typing import Any

from .loadfuncs.initload import InitLoadManager
from .loadmixin import LoadMixin
from .loadstate import LoadState
from .utils.inspector import track_kwargs

# mypy: ignore-errors

'''
from pathlib import Path
from typing import TypedDict, Unpack
class MyKwargs(TypedDict, total=False):
    """TypedDict for keyword arguments."""

    code: str
    endian: str | None
    level: int
    multiple: bool
    nout: str | int | None
    path: str | Path
'''


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
        nout: int | str | list[int | str] | None = "last",
        text: bool = True,
        check: bool = True,
        **kwargs: Any,
    ) -> None:
        """Initialize the Load class."""
        kwargs.pop("check", check)

        self.state = LoadState()
        self.class_name = self.__class__.__name__
        self.full3D = kwargs.get("full3D", self.full3D)
        self._init_load = InitLoadManager(self.state, nout, **kwargs)

        if text:
            print("Load: Load class initialized.")

    def __setattr__(self, name, value):
        """Set the attribute of the Load class."""
        if name == "state" or not hasattr(self, "state"):
            # Initialization step: allow everything until state exists
            super().__setattr__(name, value)
        elif hasattr(self.state, name):
            # Write-through to state if attr already defined
            setattr(self.state, name, value)
        else:
            # Set the attribute on the state
            setattr(self.state, name, value)

    def __getattr__(self, name):
        """Get the attribute of the Load class."""
        # Called only if attribute not found in usual places
        if hasattr(self.state, name):
            return getattr(self.state, name)
        raise AttributeError(f"'Load' object has no attribute '{name}'")
