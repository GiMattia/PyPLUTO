import pytest
from pyPLUTO.delegator import delegator


# Mock state class to use in delegator tests
class State:
    def __init__(self, value: str):
        self.value = value


# Class with a custom __getattr__ method
class OriginalClass:
    def __getattr__(self, name):
        # Custom behavior for __getattr__
        return f"Custom handling of {name}"


@delegator("state")
class MyClass:
    state = None  # The delegator will look for 'state' attribute


# 1. Test delegation of attributes to 'state'
@pytest.fixture
def state():
    return State("Initial value")


@pytest.fixture
def test_class(state):
    @delegator("state")
    class TestClass:
        def __init__(self, state: State) -> None:
            self.state = state

    return TestClass(state)


def test_delegation(test_class):
    # Create instance of TestClass via fixture
    obj = test_class
    # Test if 'state' is delegated properly
    assert obj.value == "Initial value"  # state.value should be accessible


# 2. Test delegation to another object (assign)
@pytest.fixture
def test_class_with_assign(state):
    @delegator("state")
    class TestClassWithAssign:
        def __init__(self, state: State) -> None:
            self.state = state

    return TestClassWithAssign(state)


def test_assign(test_class_with_assign):
    obj = test_class_with_assign
    # Assign a new value using the assign method
    obj.assign(value="New value")

    # Check if both the object and the state are updated
    assert obj.value == "New value"
    assert obj.state.value == "New value"


# 3. Test overriding __getattr__ when there is no delegation
def test_no_delegation():
    class CustomClass:
        def __init__(self, state: State):
            self.state = state

    custom_obj = CustomClass(State("Custom state"))

    # Try accessing the custom class directly, should not delegate to state
    with pytest.raises(AttributeError):
        custom_obj.value  # Should raise AttributeError


# 4. Test delegation works for additional attributes in the class
@pytest.fixture
def test_class_with_additional_attr(state):
    @delegator("state")
    class TestClassWithAdditionalAttr:
        def __init__(self, state: State, additional_attr: str) -> None:
            self.state = state
            self.additional_attr = additional_attr

    return TestClassWithAdditionalAttr(state, "extra value")


def test_delegation_with_additional_attr(test_class_with_additional_attr):
    obj = test_class_with_additional_attr

    # Check if additional attributes are correctly set
    assert obj.additional_attr == "extra value"
    assert obj.value == "Initial value"  # Delegated to state.value


# Test to check if orig_getattr is used
def test_orig_getattr_called():
    obj = MyClass()
    obj.state = OriginalClass()  # Set the state to an instance of OriginalClass

    # Access an attribute that MyClass does not have, causing __getattr__ in OriginalClass
    result = obj.some_attribute

    # Ensure that the original __getattr__ method is used
    assert result == "Custom handling of some_attribute"


# Test to check if orig_getattr is invoked when no delegated attribute is found
def test_orig_getattr_fallback():
    # Create a class with __getattr__ defined
    @delegator("state")
    class AnotherClass:
        def __getattr__(self, name):
            return f"AnotherClass handling {name}"

        state = State("Some state")

    obj = AnotherClass()

    # Try to access an attribute that doesn't exist on the object, which should invoke __getattr__
    result = obj.some_other_attribute

    # Ensure that the original __getattr__ was used
    assert result == "AnotherClass handling some_other_attribute"
