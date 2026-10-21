"""Test of the overtyper.py file.

PerOutput is a descriptor whose type follows the call that built the facade:
that half is for the type checkers, and is what pyright and ty check. What
runs is simpler, and is what is tested here: like every property of the
mixins, the descriptor keeps no value of its own, and reads and writes the
field of the same name on the state of whatever object it is read on.
"""

import numpy as np
import pytest

from pyPLUTO.baseloadstate import BaseLoadState
from pyPLUTO.utils.overtyper import PerOutput


class _Holder:
    """The smallest object the descriptor works on: a state and a field."""

    ntime: PerOutput[float, np.ndarray] = PerOutput()

    def __init__(self) -> None:
        """Give the descriptor the one thing it needs, a fresh state."""
        self.state = BaseLoadState()


def test_the_name_is_the_field_it_is_assigned_to() -> None:
    """Check the descriptor knows which field of the state it stands for.

    It is set when the class is built, from the name it is assigned to, so
    the same class serves nout and ntime without being told twice.
    """
    assert _Holder.__dict__["ntime"].name == "ntime"


def test_read_on_the_class_it_gives_itself() -> None:
    """Read the field on the class rather than on an instance.

    There is no state to read from, so the descriptor itself comes back, as
    a property does; it is how the mixin tests list the fields.
    """
    assert isinstance(_Holder.ntime, PerOutput)


@pytest.mark.parametrize(
    "value", [1.5, np.array([0.0, 1.5])], ids=["value", "array"]
)
def test_a_value_reaches_the_state_and_comes_back(
    value: float | np.ndarray,
) -> None:
    """Write the field, then read it from the state and from the holder.

    The state is the one copy, shared by reference, so what is written
    through the descriptor is what the state holds, and what is read back.
    """
    holder = _Holder()

    holder.ntime = value

    assert holder.state.ntime is value
    assert holder.ntime is value


def test_an_unset_field_is_not_softened() -> None:
    """Read the field before anything set it.

    The descriptor passes the state's own AttributeError through, rather
    than return None, so a field read before a load fails as the state's
    does.
    """
    with pytest.raises(AttributeError):
        _ = _Holder().ntime
