"""Module for initialization loading functions."""

import warnings
from pathlib import Path
from typing import TypedDict, Unpack

from numpy.typing import NDArray

from ..baseloadmixin import BaseLoadMixin
from ..baseloadstate import BaseLoadState
from ..loadstate import LoadState
from ..utils.inspector import track_kwargs
from .codeselection import CodeManager
from .descriptor import DescriptorManager
from .findformat import FindFormat


class MyKwargs(TypedDict):
    """TypedDict for keyword arguments."""

    code: str
    endian: str | None
    multiple: bool
    nout: int | str | list[int | str] | NDArray | None
    path: str | Path


@track_kwargs
class InitLoadManager(BaseLoadMixin):
    """Class that handles the initialization loading process."""

    def __init__(
        self, state: BaseLoadState, **kwargs: Unpack[MyKwargs]
    ) -> None:
        """Initialize the InitLoadManager class."""
        self.state = state

        nout = kwargs.get("nout", "last")
        self.code = kwargs.get("code", self.code)
        self.CodeManager = CodeManager(state)

        if self.code.lower() not in {"pluto", "gpluto"}:
            return
        if nout is None:
            warnings.warn("No output is loaded!", UserWarning, stacklevel=2)
            return

        # Check the endianess
        self.check_endian(kwargs.get("endian", self.endian))

        # Check the input multiple
        self.multiple = kwargs.get("multiple", self.multiple)
        if not isinstance(self.multiple, bool):
            raise TypeError("Invalid data type. 'multiple' must be a boolean.")

        # Check the path
        self.check_path(kwargs.get("path", self.pathdir))
        self.FindFormat = FindFormat(state, **kwargs)

        if self.alone:
            pass
        elif not isinstance(state, LoadState):
            raise TypeError("DescriptorManager requires LoadState")
        else:
            self.Descriptor = DescriptorManager(state)

    def check_endian(self, endian: str | None) -> None:
        """Check the endian format.

        If the endian is given, check if it is valid (either 'little' or
        'big'). If not given, set it to 'little' by default.

        Parameters
        ----------
        endian: str | None
            The endian format. If None, it is set to 'little' by default.

        Returns
        -------
        None

        Examples
        --------
        - Example #1: Set endian to 'big'

            >>> check_endian("big")

        - Example #2: Set endian to 'little'

            >>> check_endian("little")

        - Example #3: Set endian to default ('little')

            >>> check_endian(None)

        - Example #4: Invalid endian value

            >>> check_endian("invalid")
            ValueError: Invalid endian value. Must be 'little' or 'big'.

        """
        # Check the input endianess
        d_end = {
            "big": ">",
            "little": "<",
            ">": ">",
            "<": "<",
            None: None,
        }

        self.endian = endian
        if self.endian not in d_end:
            error = f"Invalid endianess. Valid values are {d_end.keys()}"
            raise ValueError(error)

    def check_path(self, path: str | Path) -> None:
        """Check if the given path is consistent.

        If the path is given through a non- empty string or set to the default
        value, If the path is consistent, it is converted to a Path object.
        Then, a check is performed to see if the path is a directory. The path
        is stored in the class as a Path object self.pathdir.

        Returns
        -------
        - None

        Parameters
        ----------
        - path (not optional): str | Path
            The path to the simulation directory.

        ----

        Examples
        --------
        - Example #1: path is a string

            >>> _check_pathformat("path/to/simulation")

        - Example #2: path is not a string

            >>> _check_pathformat(1)
            TypeError: Invalid data type. 'path' must be a non-empty string.

        - Example #3: path is an empty string

            >>> _check_pathformat("")
            ValueError: 'path' cannot be an empty string.

        - Example #4: path is not a directory

            >>> _check_pathformat("path/to/simulation")
            NotADirectoryError: Directory path/to/simulation not found.

        """
        # Check if the path is a non-empty string.
        if not isinstance(path, str) and not isinstance(path, Path):
            error = TypeError(
                "Invalid data type. 'path' must be path or string"
            )
            raise TypeError(error)
        # Check if the path is not empty
        elif not isinstance(path, Path) and not path.strip():
            raise ValueError("'path' cannot be an empty string.")
        # Convert the path to a Path object and store it
        else:
            self.pathdir = Path(path)

        # Check that the path is a directory
        if not self.pathdir.is_dir():
            raise NotADirectoryError(f"Directory {self.pathdir} not found.")

        # End of the function
