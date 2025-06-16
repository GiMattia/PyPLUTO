from pyPLUTO.mediator import (
    Mediator,
)  # Updated Mediator with generic managers


# --- Minimal stubs to test Mediator logic ---
class DummyState:
    pass


class DummyManagerA:
    exposed_methods = ("method_a",)

    def __init__(self, state: DummyState) -> None:
        self.state = state

    def method_a(self):
        return "A method"


class DummyManagerB:
    exposed_methods = ("method_b",)

    def __init__(self, state: DummyState) -> None:
        self.state = state

    def method_b(self):
        return "B method"


# ------------------ Tests ------------------


def test_delegate_to_first_manager():
    state = DummyState()
    mediator = Mediator(state, manager_classes=[DummyManagerA, DummyManagerB])
    assert mediator.method_a() == "A method"


def test_delegate_to_second_manager():
    state = DummyState()
    mediator = Mediator(state, manager_classes=[DummyManagerA, DummyManagerB])
    assert mediator.method_b() == "B method"


def test_missing_attribute_raises():
    state = DummyState()
    mediator = Mediator(state, manager_classes=[DummyManagerA, DummyManagerB])
    try:
        mediator.non_existent_method()
    except AttributeError as e:
        assert "object has no attribute 'non_existent_method'" in str(e)
    else:
        assert False, "Expected AttributeError"
