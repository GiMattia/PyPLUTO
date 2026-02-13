"""Module that contains the LoadState class."""

from dataclasses import dataclass, field

from numpy.typing import NDArray


@dataclass
class LoadState:
    """Class that stores the state of the Load class.

    Its purpose is to keep track of the current state of the data loading,
    such as the file paths, data arrays, and other properties and update the
    key attributes through all the different classes that handle the data
    loading at runtime.
    """

    # pylint: disable=too-many-instance-attributes

    nout: NDArray = field(init=False)
