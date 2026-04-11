"""The Load class loads the data (fluid) from the output files."""

from typing import Any

from pyPLUTO.loadfuncs.initload import InitLoadManager
from pyPLUTO.loadfuncs.readdefplini import FiledefpliniManager
from pyPLUTO.loadmixin import LoadMixin
from pyPLUTO.loadstate import LoadState
from pyPLUTO.utils.inspector import track_kwargs

# mypy: ignore-errors

#'''
# from pathlib import Path
# from typing import TypedDict, Unpack
# class MyKwargs(TypedDict, total=False):
#    """TypedDict for keyword arguments."""

#    code: str
#    endian: str | None
#    level: int
#    multiple: bool
#    nout: str | int | None
#    path: str | Path
#'''


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
        check: bool = True,
        **kwargs: Any,
    ) -> None:
        """Initialize the Load class."""
        kwargs.pop("kwargscheck", check)

        self.state: LoadState = LoadState()
        self.text: bool | None = kwargs.get("text", self.text)
        self.class_name: str = self.__class__.__name__
        self.full3D: bool = kwargs.get("full3D", self.full3D)
        self.level: int = kwargs.get("level", self.level)
        InitLoadManager(self.state, nout, **kwargs)
        FiledefpliniManager(self.state, **kwargs)

        if self.text is not False:
            print("Load: Load class initialized.")

    def __getattr__(self, name: str) -> object:
        """Get the attribute of the Image class."""
        return getattr(self.state, name)

    def __setattr__(self, name: str, value: object) -> None:
        """Set the attribute of the Image class."""
        if name == "state" or not hasattr(self, "state"):
            return super().__setattr__(name, value)
        return setattr(self.state, name, value)
