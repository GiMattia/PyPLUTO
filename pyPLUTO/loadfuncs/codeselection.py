"""Module for code selection functionality."""

from typing import Any

from pyPLUTO.baseloadmixin import BaseLoadMixin
from pyPLUTO.baseloadstate import BaseLoadState
from pyPLUTO.codes.echo_load import EchoLoadManager
from pyPLUTO.loadstate import LoadState
from pyPLUTO.utils.inspector import track_kwargs


class CodeManager(BaseLoadMixin[BaseLoadState]):
    """Class that manages the code selection."""

    @track_kwargs
    def __init__(
        self,
        state: BaseLoadState,
        nout: int | str | list[int | str] | None,
        **kwargs: Any,
    ) -> None:
        """Initialize the CodeManager class."""
        self.state = state
        if isinstance(state, LoadState):
            self.echomanager = EchoLoadManager(state)

        self.select_code(nout, **kwargs)

    def select_code(
        self, nout: int | str | list[int | str] | None, **kwargs: Any
    ) -> None:
        """Select the code based on the state."""
        # If not code is provided (or the code is PLUTO/gPLUTO) just skip

        codedict = {
            "echo": self.echomanager.load_echo,
        }

        # If not code is provided (or the code is PLUTO/gPLUTO) just skip
        if self.code.lower() in codedict:
            if self.text is not False:
                print(f"Loading data from code: {self.code}")
            codedict[self.code.lower()](nout, **kwargs)

        else:
            raise NotImplementedError(
                f"{self.code} loading is not implemented!"
            )
