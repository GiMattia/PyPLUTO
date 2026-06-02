"""Module for initialization loading functions."""

import warnings
from pathlib import Path
from typing import Any, Unpack, cast

import numpy as np
from numpy.typing import NDArray

from pyPLUTO.baseloadmixin import BaseLoadMixin
from pyPLUTO.baseloadstate import BaseLoadState
from pyPLUTO.loadfuncs.codeselection import CodeManager
from pyPLUTO.loadfuncs.descriptor import DescriptorManager
from pyPLUTO.loadfuncs.findfiles import FindFilesManager
from pyPLUTO.loadfuncs.findformat import FindFormat
from pyPLUTO.loadfuncs.loadvars import LoadVariables
from pyPLUTO.loadfuncs.storepart import StorePart
from pyPLUTO.loadstate import LoadState
from pyPLUTO.utils.annotator import AllKwargs
from pyPLUTO.utils.inspector import track_kwargs


class InitLoadManager(BaseLoadMixin[BaseLoadState]):
    """Class that handles the initialization loading process."""

    @track_kwargs
    def __init__(
        self,
        state: BaseLoadState,
        nout: int | str | list[int | str] | None,
        **kwargs: Unpack[AllKwargs],
    ) -> None:
        """Initialize the InitLoadManager class."""
        self.state = state

        if nout is None:
            warnings.warn("No output is loaded!", UserWarning, stacklevel=2)
            return

        # Check the endianess
        self.check_endian(kwargs.get("endian", self.state.endian))

        # Check the input multiple
        self.state.multiple = kwargs.get("multiple", self.state.multiple)
        if not isinstance(self.state.multiple, bool):
            raise TypeError("Invalid data type. 'multiple' must be a boolean.")

        # Check the path
        self.check_path(kwargs.get("path", self.state.pathdir))

        self.state.code = kwargs.get("code", self.state.code)
        if self.state.code.lower() not in {"pluto", "gpluto"}:
            self.CodeManager = CodeManager(state, nout, **kwargs)
            return

        self.FindFormat = FindFormat(state, **kwargs)

        if isinstance(state, LoadState) and not self.state.alone:
            try:
                self.Descriptor = DescriptorManager(state, nout, **kwargs)
            except UserWarning:
                warnings.warn(
                    "Failed to initialize descriptor manager.", stacklevel=2
                )
                self.state.alone = True

        if not isinstance(state, LoadState) or self.state.alone:
            self.findfile = FindFilesManager(state, nout, **kwargs)

        loadvars = True
        if kwargs.get("vars") is not None:
            warnings.warn(
                "'vars' argument is deprecated. Use 'var' instead.",
                DeprecationWarning,
                stacklevel=2,
            )
            loadvars = kwargs.get("vars", loadvars)
        loadvars = kwargs.get("var", loadvars)

        for i, exout in enumerate(self.state.noutlist):
            LoadVariables(state, loadvars, i, exout)

        if not isinstance(state, LoadState):
            StorePart(state).finalize()

        for key, value in self.state.d_vars.items():
            typed_value = cast(NDArray[Any], value)
            setattr(self.state, str(key), typed_value)

        if (
            isinstance(self.state.ntimelist, np.ndarray)
            and len(self.state.ntimelist) == 1
        ):
            self.state.ntime = self.state.ntimelist[0]
            self.state.nout = self.state.noutlist[0]
        else:
            self.state.ntime = self.state.ntimelist
            self.state.nout = self.state.noutlist

    def check_endian(self, endian: str | None) -> None:
        """Check the endian format.

        If the endian is given, check if it is valid (either 'little' or
        'big'). If not given, set it to 'little' by default.

        Parameters
        ----------
        - endian: str | None
            The endian format. If None, it is set to 'little' by default.

        Returns
        -------
        - None

        ----

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

        self.state.endian = endian
        if endian not in d_end:
            error = f"Invalid endianess. Valid values are {d_end.keys()}"
            raise ValueError(error)
        self.state.endian = d_end[endian]

    def check_path(self, path: str | Path) -> None:
        """Check if the given path is consistent.

        If the path is given through a non- empty string or set to the default
        value, If the path is consistent, it is converted to a Path object.
        Then, a check is performed to see if the path is a directory. The path
        is stored in the class as a Path object self.pathdir.

        Parameters
        ----------
        - path (not optional): str | Path
            The path to the simulation directory.

        Returns
        -------
        - None

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

        self.state.pathdir = Path(path)

        if not isinstance(self.state.pathdir, Path):
            raise TypeError(
                "Invalid data type. 'path' must be or converted to Path object."
            )

        # Check that the path is a directory
        if not self.state.pathdir.is_dir():
            raise NotADirectoryError(
                f"Directory {self.state.pathdir} not found."
            )

        # End of the function
