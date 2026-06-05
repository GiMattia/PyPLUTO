"""Module for code selection functionality."""

from typing import Any

from pyPLUTO.baseloadmixin import BaseLoadMixin
from pyPLUTO.baseloadstate import BaseLoadState
from pyPLUTO.codes.echo_load import EchoLoadManager
from pyPLUTO.loadstate import LoadState
from pyPLUTO.utils.inspector import track_kwargs


class CodeManager(BaseLoadMixin[BaseLoadState]):
    """Class that manages the code selection.

    Parameters
    ----------
    - nout: int | list | None
        The output number to load.
    - var: str | list[str] | np.ndarray | bool | None, default True
            The variable to be loaded . When loading, it selects the variables
            (True loads all, or pass a string or list for a subset).

    Return
    ------
    - None
    """

    @track_kwargs
    def __init__(
        self,
        state: BaseLoadState,
        nout: int | str | list[int | str] | None,
        var: str | list[str] | bool | None,
        **kwargs: Any,
    ) -> None:
        """Initialize the CodeManager class."""
        self.state = state
        if isinstance(state, LoadState):
            self.echomanager = EchoLoadManager(state)

        self.select_code(nout, var, **kwargs)

    @track_kwargs
    def select_code(
        self,
        nout: int | str | list[int | str] | None,
        var: str | list[str] | bool | None,
        **kwargs: Any,
    ) -> None:
        """Select the code based on the state.

        Parameters
        ----------
        - nout: int | list | None
            The output number to load.
        - var: str | list[str] | np.ndarray | bool | None, default True
            The variable to be loaded . When loading, it selects the variables
            (True loads all, or pass a string or list for a subset).

        Return
        ------
        - None
        """
        codedict = {
            "echo": self.echomanager.load_echo,
        }

        # If not code is provided (or the code is PLUTO/gPLUTO) just skip
        if self.state.code.lower() in codedict:
            if self.state.text is not False:
                print(f"Loading data from code: {self.state.code}")
            codedict[self.state.code.lower()](nout, var, **kwargs)

        else:
            raise NotImplementedError(
                f"{self.state.code} loading is not implemented!"
            )
