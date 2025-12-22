"""Module that contains the LoadState class."""

from dataclasses import dataclass, field
from typing import Any

from numpy.typing import NDArray

from .baseloadstate import BaseLoadState


@dataclass
class LoadState(BaseLoadState):
    """Class that stores the state of the Load class.

    Its purpose is to keep track of the current state of the data loading,
    such as the file paths, data arrays, and other properties and update the
    key attributes through all the different classes that handle the data
    loading at runtime."""

    # pylint: disable=too-many-instance-attributes

    x1: NDArray[Any] = field(init=False)
