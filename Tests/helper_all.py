"""Stubs shared by every test file, whatever class family it covers.

The helper_<family> modules hold the expected values of one class family;
this one holds the pieces that belong to none of them.
"""


class DummyManager:
    """A manager whose every method returns its own name.

    Image, Load and LoadPart are facades: they hand their calls to a manager.
    Replacing the managers with this stub shows which one answered, without
    loading data or drawing anything.
    """

    def __init__(self, *_a: object, **_kw: object) -> None: ...

    def __getattr__(self, name: str) -> object:
        return lambda *a, **kw: name
