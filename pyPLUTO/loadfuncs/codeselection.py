"""Module for code selection functionality."""

from ..baseloadmixin import BaseLoadMixin
from ..baseloadstate import BaseLoadState
from ..utils.inspector import track_kwargs


class CodeManager(BaseLoadMixin):
    """Class that manages the code selection."""

    @track_kwargs
    def __init__(self, state: BaseLoadState, **kwargs) -> None:
        """Initialize the CodeManager class."""
        self.state = state

        code = kwargs.get("code", self.code)
        self.select_code(code=code)

    def select_code(
        self,
        code: str,
    ) -> None:
        """Select the code based on the state."""
        # If not code is provided (or the code is PLUTO/gPLUTO) just skip
        if code.lower() in {"pluto", "gpluto"}:
            self.code = code
        else:
            raise NotImplementedError(f"{code} loading is not implemented!")

    """
        codedict = {"echo": self.echo_load}
        # If not code is provided (or the code is PLUTO/gPLUTO) just skip
        if not code or code.lower() in {"pluto", "gpluto"}:
            pass
        elif code.lower() in codedict:
            init = f"Loading data with alternative method using code: {code}"
            if text is True:
                print(init)
            codedict[code.lower()](nout, path, vars)
            print(self.nout)
            if not isinstance(self.nout, int):
                self.nout = self.nout.astype(int)
            if text is True:
                print(f"Load: folder {path},     output {self.nout}")
            return
        else:
            raise NotImplementedError(f"{code} loading is not implemented!")
    """
