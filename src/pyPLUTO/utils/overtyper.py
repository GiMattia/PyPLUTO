"""Descriptors whose type follows the call that built the object.

A property has one return type, whatever the instance it is read on. Some
fields of pyPLUTO have no single type: what they hold depends on how the
object was built, and the overloads of the facades already state it from
the call. The descriptors here read that answer off the type of the
instance, so the type checkers give the field the type it has at runtime.
The value itself is read from and written to the state, as by every
property of the mixins.

PerOutput is the first: nout and ntime, one value for a single output and
an array for a collection, after the overloads of Load and LoadPart.
"""

from __future__ import annotations

from typing import TYPE_CHECKING, Generic, TypeVar, overload

import numpy as np

from pyPLUTO.baseloadstate import BaseLoadState

if TYPE_CHECKING:
    from pyPLUTO.baseloadmixin import BaseLoadMixin
    from pyPLUTO.load import Load
    from pyPLUTO.loadpart import LoadPart

_OneT = TypeVar("_OneT")
_ManyT = TypeVar("_ManyT")
_S = TypeVar("_S", bound=BaseLoadState)


class PerOutput(Generic[_OneT, _ManyT]):
    """A state field that is one value per output.

    The two type parameters are the field for a single output and for a
    collection: `PerOutput[float, NDArray[np.floating]]` for ntime. Read on
    the class it gives the descriptor itself, as a property does.
    """

    def __set_name__(self, owner: type, name: str) -> None:
        """Remember the name of the field the descriptor stands for."""
        self.name = name

    @overload
    def __get__(
        self, instance: None, owner: type
    ) -> PerOutput[_OneT, _ManyT]: ...
    @overload
    def __get__(self, instance: Load[np.ndarray], owner: type) -> _OneT: ...
    @overload
    def __get__(self, instance: LoadPart[np.ndarray], owner: type) -> _OneT: ...
    @overload
    def __get__(
        self, instance: Load[dict[int, np.ndarray]], owner: type
    ) -> _ManyT: ...
    @overload
    def __get__(
        self, instance: LoadPart[dict[int, np.ndarray]], owner: type
    ) -> _ManyT: ...
    @overload
    def __get__(
        self, instance: BaseLoadMixin[_S], owner: type
    ) -> _OneT | _ManyT: ...
    def __get__(
        self, instance: BaseLoadMixin[_S] | None, owner: type
    ) -> PerOutput[_OneT, _ManyT] | _OneT | _ManyT:
        """Read the field off the state, or give the descriptor itself."""
        if instance is None:
            return self
        return getattr(instance.state, self.name)

    def __set__(
        self, instance: BaseLoadMixin[_S], value: _OneT | _ManyT
    ) -> None:
        """Write the field back to the state."""
        setattr(instance.state, self.name, value)
