"""Docstring for pyPLUTO.loadfuncs.baseloadtools module."""

from __future__ import annotations

import numpy as np

from pyPLUTO.baseloadmixin import BaseLoadMixin
from pyPLUTO.baseloadstate import BaseLoadState


class BaseLoadTools(BaseLoadMixin[BaseLoadState]):
    """Docstring for BaseLoadTools class."""

    def __init__(self, state: BaseLoadState) -> None:
        """Initialize the BaseLoadTools class."""
        self.state = state

    def check_nout(self, nout: int | str | list[int | str]) -> None:
        """Find the number of datafile to be loaded.

        If nout is a list, the function checks if the list contains the keyword
        'last' or -1. If so, the keyword is replaced with the last file number.
        If nout is a string, the function checks if the string contains the
        keyword 'last' or -1. If so, the keyword is replaced with the last file
        number. If nout is an integer, the function returns a list
        containing the integer. If nout is 'all', the function returns a
        list containing all the file numbers.

        Parameters
        ----------
        - nout (not optional): int | str | list[int|str]
            The output file to be loaded.

        Returns
        -------
        - None

        Examples
        --------
        - Example #1: Load the last file

            >>> _check_nout("last")

        - Example #2: Load the first file

            >>> _check_nout(0)

        - Example #3: Load all the files

            >>> _check_nout("all")

        - Example #4: Load multiple specific files

            >>> _check_nout([0, 1, 2, 3])
        """
        # Assign the last possible output file
        last = self.state.outlist.tolist()[-1]

        # Check if nout is a list and change the keywords
        if not isinstance(nout, list):
            # If nout is a string, get the keywords
            Dnout = {
                nout: nout,
                "last": last,
                -1: last,
                "all": self.state.outlist,
            }[nout]
        else:
            # If nout is a list, replace the keywords
            Dnout = [last if i in {"last", -1} else i for i in nout]

        # Sort the list, compute the corresponding time and store its length
        self.state.noutlist = np.sort(np.unique(np.atleast_1d(Dnout)))

        # Check if the output files are in the list
        if np.any(~np.isin(self.state.noutlist, self.state.outlist)):
            raise ValueError(
                f"Error: Wrong output file(s) {self.state.noutlist} \
                            in path {self.state.pathdir}."
            )

        # End of the function
