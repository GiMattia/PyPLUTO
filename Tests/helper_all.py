"""Stubs shared by every test file, whatever class family it covers.

The helper_<family> modules hold the expected values of one class family;
this one holds the pieces that belong to none of them.

Everything here is a test double: an object that stands in for a real one so
a test can watch what happens to it. Nothing in this file asserts anything,
and nothing in it is derived from the code under test -- a double that copied
the real behaviour would let a test agree with whatever the code does.
"""


class DummyManager:
    """A manager whose every method returns its own name.

    Image, Load and LoadPart are facades: they hand their calls to a manager.
    Replacing the managers with this stub shows which one answered, without
    loading data or drawing anything.

    The trick is in `__getattr__`, which Python calls only for attributes
    that were not found the normal way. Since this class defines no methods
    at all, every call lands there: `DummyManager().plot(x, y)` looks up
    "plot", gets a function back, and calling it returns the string "plot".
    A test can then assert that the facade reached the method it meant to,
    with no real manager, no figure and no data involved.

    That also means the stub answers to *any* name. It is a deliberate
    trade: a test cannot use it to prove a method exists, only to see which
    one was called. Whether the facade methods match the real managers is
    checked separately, by the completeness guards in the helper tables.
    """

    def __init__(self, *_a: object, **_kw: object) -> None:
        """Accept whatever the real manager's constructor would.

        The managers take a state, and some take other managers too. The
        arguments are swallowed unread: the stub has nothing to build.
        """

    def __getattr__(self, name: str) -> object:
        """Return a function that reports the attribute name it was asked for.

        Called for every attribute, because the class defines none. The
        returned lambda ignores its arguments, so it stands in for a method
        of any signature.
        """
        return lambda *a, **kw: name
