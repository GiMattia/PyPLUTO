import pyPLUTO    as pp
import pytest

print(f"Testing the LoadPart init and Path find ... ".ljust(50), end='')

# Check if raises erorr with wrong endianess
with pytest.raises(ValueError):
    D = pp.LoadPart(path = "Test_load/particles_cr", text = False, endian = "wrong")

# Check if raises error when the path is not a non-empty string
with pytest.raises(TypeError, match = "Invalid data type. 'path' must be path or string"):
    D = pp.LoadPart(path = 123, text = False)
with pytest.raises(ValueError, match = "'path' cannot be an empty string."):
    D = pp.LoadPart(path = "", text = False)

# Check if raises an error if the path is not a directory
with pytest.raises(NotADirectoryError):
    D = pp.LoadPart(path = "wrong", text = False)

# Check if raises an error with wrong attribute
with pytest.raises(AttributeError):
    D = pp.LoadPart(path = "Test_load/particles_cr", text = False)
    res = D.wrong

print(" ---> \033[32mPASSED!\033[0m")
